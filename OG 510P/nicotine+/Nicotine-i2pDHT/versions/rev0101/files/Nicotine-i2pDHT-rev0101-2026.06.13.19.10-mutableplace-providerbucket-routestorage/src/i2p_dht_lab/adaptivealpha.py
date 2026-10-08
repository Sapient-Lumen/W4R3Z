"""Adaptive alpha/beta lookup pressure for an I2P-shaped DHT.

Vanilla Kademlia has an attractive constant-alpha simplicity.  On an anonymous,
higher-latency substrate, that simplicity can become a trap: a small alpha may
let one fast/captured family dominate early evidence, while a huge alpha turns
every hard lookup into a metadata and bandwidth flood.

This module keeps the guess local and deterministic.  It does not optimize a
real network.  It asks: given recent lookup transcripts, should the next round
hold steady, widen family-diverse concurrency, increase patience for slow honest
paths, respect useful refusals, or refuse to accept because the fast window was
captured?
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .lookuptranscript import LookupEventKind, LookupPressureDecisionKind, LookupPressurePolicy, LookupTranscript, analyze_lookup_pressure

ADAPTIVE_ALPHA_DOMAIN = DOMAIN + b":adaptive-alpha-v1:"


class AdaptiveLookupDecisionKind(str, Enum):
    ACCEPT_READY = "accept_ready"
    WIDEN_FOR_PATH_DIVERSITY = "widen_for_path_diversity"
    WIDEN_FOR_TIMEOUT_PRESSURE = "widen_for_timeout_pressure"
    HOLD_FOR_USEFUL_REFUSAL = "hold_for_useful_refusal"
    QUARANTINE_FAST_CAPTURE = "quarantine_fast_capture"
    QUARANTINE_BAD_PRESSURE = "quarantine_bad_pressure"
    EMPTY = "empty"


@dataclass(frozen=True)
class AdaptiveAlphaPolicy:
    base_alpha: int = 3
    min_alpha: int = 2
    max_alpha: int = 9
    base_beta: int = 3
    max_beta: int = 7
    target_success_families: int = 3
    target_success_paths: int = 3
    max_fast_family_fraction: float = 0.60
    fast_window_ms: int = 250
    timeout_expand_fraction: float = 0.34
    refusal_hold_fraction: float = 0.45
    high_latency_ms: int = 1_800
    timeout_ms: int = 2_500
    max_timeout_ms: int = 9_000
    max_bad_events: int = 0

    def validate(self) -> None:
        if self.min_alpha <= 0 or self.base_alpha <= 0 or self.max_alpha < self.base_alpha:
            raise ValueError("alpha bounds must be positive and ordered")
        if self.base_beta <= 0 or self.max_beta < self.base_beta:
            raise ValueError("beta bounds must be positive and ordered")
        if self.target_success_families <= 0 or self.target_success_paths <= 0:
            raise ValueError("success targets must be positive")
        if not 0 < self.max_fast_family_fraction <= 1:
            raise ValueError("fast family fraction must be in (0, 1]")
        if not 0 <= self.timeout_expand_fraction <= 1 or not 0 <= self.refusal_hold_fraction <= 1:
            raise ValueError("fractions must be in [0, 1]")
        if self.fast_window_ms < 0 or self.high_latency_ms <= 0 or self.timeout_ms <= 0 or self.max_timeout_ms < self.timeout_ms:
            raise ValueError("time windows must be non-negative/ordered")
        if self.max_bad_events < 0:
            raise ValueError("max_bad_events must be non-negative")

    def pressure_policy(self) -> LookupPressurePolicy:
        return LookupPressurePolicy(
            min_success_families=self.target_success_families,
            min_success_paths=self.target_success_paths,
            max_fast_family_fraction=self.max_fast_family_fraction,
            fast_window_ms=self.fast_window_ms,
            max_bad_events=self.max_bad_events,
            max_timeout_fraction=1.0,
            allow_evidence_only=False,
        )


@dataclass(frozen=True)
class AdaptiveRoundStats:
    transcript_digest: bytes
    success_family_count: int
    success_path_count: int
    timeout_fraction: float
    refusal_fraction: float
    bad_event_count: int
    fast_window_family_fraction: float
    max_success_latency_ms: int
    decision_kind: LookupPressureDecisionKind

    @property
    def fast_capture(self) -> bool:
        return self.decision_kind is LookupPressureDecisionKind.QUARANTINE_FAST_WINDOW_CAPTURE

    @property
    def bad_pressure(self) -> bool:
        return self.decision_kind is LookupPressureDecisionKind.QUARANTINE_BAD_RESPONSE_PRESSURE

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"digest": self.transcript_digest,
            b"success_family_count": self.success_family_count,
            b"success_path_count": self.success_path_count,
            b"timeout_fraction_ppm": int(self.timeout_fraction * 1_000_000),
            b"refusal_fraction_ppm": int(self.refusal_fraction * 1_000_000),
            b"bad_event_count": self.bad_event_count,
            b"fast_window_family_fraction_ppm": int(self.fast_window_family_fraction * 1_000_000),
            b"max_success_latency_ms": self.max_success_latency_ms,
            b"decision_kind": self.decision_kind.value,
        }


@dataclass(frozen=True)
class AdaptiveLookupKnobs:
    alpha: int
    beta: int
    timeout_ms: int
    target_success_families: int
    target_success_paths: int
    require_new_family: bool = True
    reason: str = ""

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"alpha": self.alpha,
            b"beta": self.beta,
            b"timeout_ms": self.timeout_ms,
            b"target_success_families": self.target_success_families,
            b"target_success_paths": self.target_success_paths,
            b"require_new_family": 1 if self.require_new_family else 0,
            b"reason": self.reason,
        }


@dataclass(frozen=True)
class AdaptiveLookupDecision:
    kind: AdaptiveLookupDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class AdaptiveLookupReport:
    stats: tuple[AdaptiveRoundStats, ...]
    next_knobs: AdaptiveLookupKnobs
    decision: AdaptiveLookupDecision
    transcript_digest: bytes

    @property
    def needs_more_rounds(self) -> bool:
        return not self.decision.accept

    @property
    def latest_stats(self) -> AdaptiveRoundStats | None:
        return self.stats[-1] if self.stats else None


def _fraction(count: int, total: int) -> float:
    return count / total if total else 0.0


def _round_stats(transcript: LookupTranscript, policy: AdaptiveAlphaPolicy) -> AdaptiveRoundStats:
    pressure = analyze_lookup_pressure(transcript, policy=policy.pressure_policy())
    non_query = tuple(event for event in transcript.events if event.kind is not LookupEventKind.QUERY_SENT)
    refusal_count = sum(1 for event in non_query if event.kind is LookupEventKind.USEFUL_REFUSAL)
    timeout_count = sum(1 for event in non_query if event.kind is LookupEventKind.TIMEOUT)
    success_latencies = [event.latency_ms for event in transcript.successful_events]
    return AdaptiveRoundStats(
        transcript_digest=transcript.digest,
        success_family_count=pressure.success_family_count,
        success_path_count=pressure.success_path_count,
        timeout_fraction=_fraction(timeout_count, len(non_query)),
        refusal_fraction=_fraction(refusal_count, len(non_query)),
        bad_event_count=pressure.bad_event_count,
        fast_window_family_fraction=pressure.fast_window_family_fraction,
        max_success_latency_ms=max(success_latencies) if success_latencies else 0,
        decision_kind=pressure.decision.kind,
    )


def _bounded(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def recommend_adaptive_lookup(transcripts: Iterable[LookupTranscript], *, policy: AdaptiveAlphaPolicy | None = None) -> AdaptiveLookupReport:
    policy = policy or AdaptiveAlphaPolicy()
    policy.validate()
    transcript_tuple = tuple(transcripts)
    stats = tuple(_round_stats(transcript, policy) for transcript in transcript_tuple)

    if not stats:
        knobs = AdaptiveLookupKnobs(
            alpha=policy.base_alpha,
            beta=policy.base_beta,
            timeout_ms=policy.timeout_ms,
            target_success_families=policy.target_success_families,
            target_success_paths=policy.target_success_paths,
            reason="cold start with conservative family-diverse alpha",
        )
        digest = sha256(ADAPTIVE_ALPHA_DOMAIN + b":empty:" + bencode(knobs.bvalue()))
        return AdaptiveLookupReport((), knobs, AdaptiveLookupDecision(AdaptiveLookupDecisionKind.EMPTY, False, "no transcripts yet"), digest)

    latest = stats[-1]
    recent = stats[-3:]
    recent_fast_capture = any(item.fast_capture for item in recent)
    recent_bad = sum(item.bad_event_count for item in recent)
    avg_timeout_fraction = sum(item.timeout_fraction for item in recent) / len(recent)
    avg_refusal_fraction = sum(item.refusal_fraction for item in recent) / len(recent)
    slow_success_seen = any(item.max_success_latency_ms >= policy.high_latency_ms for item in recent)
    low_diversity = latest.success_family_count < policy.target_success_families or latest.success_path_count < policy.target_success_paths

    if recent_fast_capture:
        knobs = AdaptiveLookupKnobs(
            alpha=_bounded(policy.base_alpha + 3, policy.min_alpha, policy.max_alpha),
            beta=_bounded(policy.base_beta + 2, policy.base_beta, policy.max_beta),
            timeout_ms=min(policy.max_timeout_ms, max(policy.timeout_ms, policy.high_latency_ms * 2)),
            target_success_families=min(policy.max_alpha, policy.target_success_families + 1),
            target_success_paths=min(policy.max_alpha, policy.target_success_paths + 1),
            require_new_family=True,
            reason="fast-window capture pressure: widen disjoint paths before accepting",
        )
        decision = AdaptiveLookupDecision(AdaptiveLookupDecisionKind.QUARANTINE_FAST_CAPTURE, False, "recent fast window was dominated by one family")
    elif recent_bad > policy.max_bad_events:
        knobs = AdaptiveLookupKnobs(
            alpha=_bounded(policy.base_alpha + 2, policy.min_alpha, policy.max_alpha),
            beta=_bounded(policy.base_beta + 1, policy.base_beta, policy.max_beta),
            timeout_ms=policy.timeout_ms,
            target_success_families=policy.target_success_families,
            target_success_paths=policy.target_success_paths,
            require_new_family=True,
            reason="bad response pressure: quarantine convenient answers and ask elsewhere",
        )
        decision = AdaptiveLookupDecision(AdaptiveLookupDecisionKind.QUARANTINE_BAD_PRESSURE, False, "bad responses exceeded local budget")
    elif avg_refusal_fraction >= policy.refusal_hold_fraction:
        knobs = AdaptiveLookupKnobs(
            alpha=_bounded(policy.base_alpha, policy.min_alpha, policy.max_alpha),
            beta=policy.base_beta,
            timeout_ms=min(policy.max_timeout_ms, int(policy.timeout_ms * 1.25)),
            target_success_families=policy.target_success_families,
            target_success_paths=policy.target_success_paths,
            require_new_family=True,
            reason="many useful refusals: avoid turning overload into flood pressure",
        )
        decision = AdaptiveLookupDecision(AdaptiveLookupDecisionKind.HOLD_FOR_USEFUL_REFUSAL, False, "useful refusals are capacity evidence, not success")
    elif avg_timeout_fraction >= policy.timeout_expand_fraction:
        knobs = AdaptiveLookupKnobs(
            alpha=_bounded(policy.base_alpha + 2, policy.min_alpha, policy.max_alpha),
            beta=_bounded(policy.base_beta + 1, policy.base_beta, policy.max_beta),
            timeout_ms=min(policy.max_timeout_ms, int(policy.timeout_ms * 1.6)),
            target_success_families=policy.target_success_families,
            target_success_paths=policy.target_success_paths,
            require_new_family=True,
            reason="timeout pressure: increase concurrency and patience, but keep family caps",
        )
        decision = AdaptiveLookupDecision(AdaptiveLookupDecisionKind.WIDEN_FOR_TIMEOUT_PRESSURE, False, "timeouts dominate recent lookup pressure")
    elif low_diversity or slow_success_seen:
        knobs = AdaptiveLookupKnobs(
            alpha=_bounded(policy.base_alpha + (2 if slow_success_seen else 1), policy.min_alpha, policy.max_alpha),
            beta=_bounded(policy.base_beta + (1 if low_diversity else 0), policy.base_beta, policy.max_beta),
            timeout_ms=min(policy.max_timeout_ms, int(policy.timeout_ms * (1.4 if slow_success_seen else 1.0))),
            target_success_families=policy.target_success_families,
            target_success_paths=policy.target_success_paths,
            require_new_family=True,
            reason="slow honest paths or low diversity: ask wider before greedy acceptance",
        )
        decision = AdaptiveLookupDecision(AdaptiveLookupDecisionKind.WIDEN_FOR_PATH_DIVERSITY, False, "not enough diverse successful paths yet")
    else:
        knobs = AdaptiveLookupKnobs(
            alpha=_bounded(policy.base_alpha, policy.min_alpha, policy.max_alpha),
            beta=policy.base_beta,
            timeout_ms=policy.timeout_ms,
            target_success_families=policy.target_success_families,
            target_success_paths=policy.target_success_paths,
            require_new_family=False,
            reason="diverse successes without pressure",
        )
        decision = AdaptiveLookupDecision(AdaptiveLookupDecisionKind.ACCEPT_READY, True, "recent lookup crossed family/path thresholds without poison pressure")

    digest = sha256(ADAPTIVE_ALPHA_DOMAIN + b":report:" + bencode({
        b"stats": [item.bvalue() for item in stats],
        b"knobs": knobs.bvalue(),
        b"decision": decision.kind.value,
        b"accept": 1 if decision.accept else 0,
    }))
    return AdaptiveLookupReport(stats, knobs, decision, digest)
