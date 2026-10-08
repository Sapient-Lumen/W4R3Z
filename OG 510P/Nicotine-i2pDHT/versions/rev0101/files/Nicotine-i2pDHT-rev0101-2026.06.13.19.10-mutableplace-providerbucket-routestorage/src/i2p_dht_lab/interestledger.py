"""Repeated-round interest/metadata ledger.

rev0018 made single-round liveness-vs-metadata pressure explicit.  The harder
risk shows up over time: a client can stay within a per-round budget while still
leaking the same target to the same families again and again.  On an I2P DHT,
provider confirmation, witness gathering, route gossip, and lookup widening are
all interest signals even when payloads are encrypted.

This module keeps a local rolling ledger of those signals.  It is not a privacy
protocol and not a formal anonymity metric.  It is a deterministic brake: before
another lookup/probe round, ask whether the caller has spent too many points on
one target, exposed too many raw keys, leaned on one family, or failed to carry
enough decoy/cover probes for its chosen mode.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Sequence

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .livenessbudget import LivenessBudgetReport

INTEREST_LEDGER_DOMAIN = DOMAIN + b":interest-ledger-v1:"


class InterestEventKind(str, Enum):
    LOOKUP_QUERY = "lookup_query"
    PROVIDER_PROBE_COMMITMENT = "provider_probe_commitment"
    PROVIDER_PROBE_RAW = "provider_probe_raw"
    DECOY_PROBE = "decoy_probe"
    WITNESS_REQUEST = "witness_request"
    ROUTE_GOSSIP = "route_gossip"


class InterestDecisionKind(str, Enum):
    ALLOW_NEXT_ROUND = "allow_next_round"
    HOLD_WINDOW_EXHAUSTED = "hold_window_exhausted"
    REDUCE_RAW_EXPOSURE = "reduce_raw_exposure"
    REDUCE_RAW_KEY_EXPOSURE = "reduce_raw_exposure"
    ADD_DECOYS = "add_decoys"
    ROTATE_FAMILIES = "rotate_families"
    STOP_TARGET_REPETITION = "stop_target_repetition"
    EMPTY = "empty"


@dataclass(frozen=True)
class InterestEvent:
    target_commitment: bytes
    family_id: str
    kind: InterestEventKind
    occurred_at: int
    points: int
    raw_content_key_exposed: bool = False
    decoy: bool = False
    round_id: bytes = b""
    note: str = ""

    def __post_init__(self) -> None:
        if len(self.target_commitment) != 32:
            raise ValueError("target_commitment must be 32 bytes")
        if self.round_id and len(self.round_id) != 32:
            raise ValueError("round_id must be empty or 32 bytes")
        if not self.family_id:
            raise ValueError("family_id is required")
        if self.points < 0 or self.occurred_at < 0:
            raise ValueError("interest points/times must be non-negative")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"target_commitment": self.target_commitment,
            b"family_id": self.family_id,
            b"kind": self.kind.value,
            b"occurred_at": self.occurred_at,
            b"points": self.points,
            b"raw_content_key_exposed": 1 if self.raw_content_key_exposed else 0,
            b"decoy": 1 if self.decoy else 0,
            b"round_id": self.round_id,
            b"note": self.note[:160],
        }


@dataclass(frozen=True)
class InterestBudgetPolicy:
    window_seconds: int = 3600
    max_total_points: int = 300
    max_target_points: int = 120
    max_family_fraction_ppm: int = 600_000
    max_raw_key_exposures: int = 2
    min_decoy_ratio_ppm: int = 250_000
    max_rounds_per_target: int = 4

    def validate(self) -> None:
        if self.window_seconds <= 0 or self.max_total_points <= 0 or self.max_target_points <= 0:
            raise ValueError("interest budget windows/points must be positive")
        if not 0 <= self.max_family_fraction_ppm <= 1_000_000:
            raise ValueError("max_family_fraction_ppm must be in [0, 1_000_000]")
        if self.max_raw_key_exposures < 0 or self.max_rounds_per_target <= 0:
            raise ValueError("raw exposure and round limits are invalid")
        if not 0 <= self.min_decoy_ratio_ppm <= 1_000_000:
            raise ValueError("min_decoy_ratio_ppm must be in [0, 1_000_000]")


@dataclass(frozen=True)
class InterestDecision:
    kind: InterestDecisionKind
    allow: bool
    reason: str
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class InterestLedgerReport:
    target_commitment: bytes
    event_count: int
    total_points: int
    target_points: int
    family_points: dict[str, int]
    max_family_fraction_ppm: int
    raw_key_exposures: int
    decoy_ratio_ppm: int
    target_round_count: int
    decision: InterestDecision
    transcript_digest: bytes

    @property
    def blocks_next_round(self) -> bool:
        return not self.decision.allow


@dataclass
class InterestLedger:
    events: list[InterestEvent] = field(default_factory=list)

    def ingest(self, events: Iterable[InterestEvent]) -> int:
        before = len(self.events)
        self.events.extend(events)
        self.events.sort(key=lambda item: (item.occurred_at, item.kind.value, item.family_id, item.target_commitment, item.round_id))
        return len(self.events) - before

    def prune(self, *, now: int, policy: InterestBudgetPolicy) -> int:
        threshold = max(0, now - policy.window_seconds)
        before = len(self.events)
        self.events = [event for event in self.events if event.occurred_at >= threshold]
        return before - len(self.events)

    def window(self, *, now: int, policy: InterestBudgetPolicy) -> tuple[InterestEvent, ...]:
        threshold = max(0, now - policy.window_seconds)
        return tuple(event for event in self.events if threshold <= event.occurred_at <= now)

    def assess(self, *, target_commitment: bytes, now: int, policy: InterestBudgetPolicy | None = None) -> InterestLedgerReport:
        policy = policy or InterestBudgetPolicy()
        policy.validate()
        events = self.window(now=now, policy=policy)
        if not events:
            decision = InterestDecision(InterestDecisionKind.EMPTY, True, "no recent interest events in local window")
            digest = sha256(INTEREST_LEDGER_DOMAIN + b":empty:" + target_commitment + now.to_bytes(8, "big", signed=False))
            return InterestLedgerReport(target_commitment, 0, 0, 0, {}, 0, 0, 0, 0, decision, digest)

        target_events = tuple(event for event in events if event.target_commitment == target_commitment)
        total_points = sum(event.points for event in events)
        target_points = sum(event.points for event in target_events)
        family_points: dict[str, int] = {}
        for event in target_events:
            family_points[event.family_id] = family_points.get(event.family_id, 0) + event.points
        max_family_fraction = 0 if target_points == 0 or not family_points else int(max(family_points.values()) * 1_000_000 / target_points)
        raw_key_exposures = sum(1 for event in target_events if event.raw_content_key_exposed)
        probe_events = tuple(event for event in target_events if event.kind in {InterestEventKind.PROVIDER_PROBE_COMMITMENT, InterestEventKind.PROVIDER_PROBE_RAW, InterestEventKind.DECOY_PROBE})
        decoy_count = sum(1 for event in probe_events if event.decoy or event.kind is InterestEventKind.DECOY_PROBE)
        decoy_ratio = 0 if not probe_events else int(decoy_count * 1_000_000 / len(probe_events))
        target_rounds = frozenset(event.round_id for event in target_events if event.round_id)
        target_round_count = len(target_rounds) if target_rounds else sum(1 for event in target_events if event.kind is InterestEventKind.LOOKUP_QUERY)

        if total_points > policy.max_total_points:
            retry_after = max(0, min(event.occurred_at for event in events) + policy.window_seconds - now)
            decision = InterestDecision(InterestDecisionKind.HOLD_WINDOW_EXHAUSTED, False, "rolling interest window exhausted", retry_after)
        elif target_points > policy.max_target_points:
            decision = InterestDecision(InterestDecisionKind.STOP_TARGET_REPETITION, False, "target-specific interest budget exhausted")
        elif raw_key_exposures > policy.max_raw_key_exposures:
            decision = InterestDecision(InterestDecisionKind.REDUCE_RAW_EXPOSURE, False, "raw content-key exposure exceeds local budget")
        elif target_round_count > policy.max_rounds_per_target:
            decision = InterestDecision(InterestDecisionKind.STOP_TARGET_REPETITION, False, "too many repeated rounds for one target in the rolling window")
        elif max_family_fraction > policy.max_family_fraction_ppm and target_points > 0:
            decision = InterestDecision(InterestDecisionKind.ROTATE_FAMILIES, False, "target interest is concentrated in one path/provider family")
        elif probe_events and decoy_ratio < policy.min_decoy_ratio_ppm:
            decision = InterestDecision(InterestDecisionKind.ADD_DECOYS, False, "provider-probe shape has insufficient decoy/cover probes for this local mode")
        else:
            decision = InterestDecision(InterestDecisionKind.ALLOW_NEXT_ROUND, True, "rolling interest budget allows one bounded next round")
        digest = sha256(INTEREST_LEDGER_DOMAIN + b":report:" + bencode({
            b"target_commitment": target_commitment,
            b"now": now,
            b"events": [event.bvalue() for event in events],
            b"total_points": total_points,
            b"target_points": target_points,
            b"family_points": {family: points for family, points in sorted(family_points.items())},
            b"max_family_fraction_ppm": max_family_fraction,
            b"raw_key_exposures": raw_key_exposures,
            b"decoy_ratio_ppm": decoy_ratio,
            b"target_round_count": target_round_count,
            b"decision": decision.kind.value,
        }))
        return InterestLedgerReport(target_commitment, len(events), total_points, target_points, family_points, max_family_fraction, raw_key_exposures, decoy_ratio, target_round_count, decision, digest)


def events_from_liveness_report(
    report: LivenessBudgetReport,
    *,
    target_commitment: bytes,
    now: int,
    query_families: Sequence[str],
    round_id: bytes | None = None,
) -> tuple[InterestEvent, ...]:
    """Lossily translate one liveness-budget report into ledger events.

    This helper intentionally produces a conservative *accounting trace*, not an
    exact network transcript.  It is useful when upper layers have a budget
    report but not yet a full packet transcript.
    """
    if not query_families:
        raise ValueError("query_families must not be empty")
    round_id = round_id or report.transcript_digest
    events: list[InterestEvent] = []
    for index in range(report.spend.lookup_queries):
        family = query_families[index % len(query_families)]
        events.append(InterestEvent(target_commitment, family, InterestEventKind.LOOKUP_QUERY, now, points=3, round_id=round_id))
    probe_families = sorted(report.spend.probe_families) or list(query_families)
    real_families = sorted(report.spend.real_probe_families) or probe_families
    for index in range(report.spend.real_probe_count):
        raw = index < report.spend.raw_key_exposures
        family = real_families[index % len(real_families)]
        events.append(InterestEvent(
            target_commitment,
            family,
            InterestEventKind.PROVIDER_PROBE_RAW if raw else InterestEventKind.PROVIDER_PROBE_COMMITMENT,
            now,
            points=35 if raw else 8,
            raw_content_key_exposed=raw,
            round_id=round_id,
        ))
    for index in range(report.spend.decoy_probe_count):
        family = probe_families[index % len(probe_families)]
        events.append(InterestEvent(target_commitment, family, InterestEventKind.DECOY_PROBE, now, points=5, decoy=True, round_id=round_id))
    return tuple(events)
