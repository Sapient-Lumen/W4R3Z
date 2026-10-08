"""Repeated-round witness/cache poisoning pressure lab.

A single lookup transcript can look healthy after enough slow diverse answers
arrive.  A witness cache can look healthy after enough signed receipts arrive.
The risky guess is that repeated rounds expose another class of failure:
replayed evidence, fresh-looking monoculture, and captured fast windows that keep
feeding the same cache summary.

This module deliberately joins two surfaces from earlier revisions — explicit
lookup transcripts and witness-cache summaries — without claiming consensus or
private retrieval.  It answers only a local question: should this client keep
trusting the cached evidence as useful, ask more path families, or quarantine a
view as replay/capture pressure?
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .lookuptranscript import LookupPressureDecisionKind, LookupPressurePolicy, LookupPressureReport, LookupTranscript, analyze_lookup_pressure
from .witnesscache import WitnessCacheDecisionKind, WitnessCacheSummary

CACHE_POISON_DOMAIN = DOMAIN + b":cache-poison-v1:"


class CachePoisonDecisionKind(str, Enum):
    ACCEPT_STABLE_DIVERSE_CACHE = "accept_stable_diverse_cache"
    CONTINUE_MORE_ROUNDS = "continue_more_rounds"
    CONTINUE_LOW_WITNESS_DIVERSITY = "continue_low_witness_diversity"
    QUARANTINE_CONTRADICTION = "quarantine_contradiction"
    QUARANTINE_REPLAY_MONOCULTURE = "quarantine_replay_monoculture"
    QUARANTINE_FAST_CAPTURE_REINFORCED = "quarantine_fast_capture_reinforced"


@dataclass(frozen=True)
class CachePoisonPolicy:
    min_rounds: int = 3
    min_distinct_transcripts: int = 2
    min_witness_families: int = 3
    max_replay_fraction: float = 0.67
    max_fast_capture_round_fraction: float = 0.50
    lookup_policy: LookupPressurePolicy | None = None

    def validate(self) -> None:
        if self.min_rounds <= 0 or self.min_distinct_transcripts <= 0 or self.min_witness_families <= 0:
            raise ValueError("cache poison thresholds must be positive")
        if not 0.0 < self.max_replay_fraction <= 1.0:
            raise ValueError("max replay fraction must be in (0, 1]")
        if not 0.0 <= self.max_fast_capture_round_fraction <= 1.0:
            raise ValueError("fast capture fraction must be in [0, 1]")


@dataclass(frozen=True)
class CacheRound:
    round_id: str
    observed_at: int
    transcript: LookupTranscript
    witness_summary: WitnessCacheSummary

    def __post_init__(self) -> None:
        if not self.round_id:
            raise ValueError("round_id is required")

    def bvalue(self, lookup_report: LookupPressureReport) -> dict[bytes, BValue]:
        return {
            b"round_id": self.round_id,
            b"observed_at": self.observed_at,
            b"lookup_digest": self.transcript.digest,
            b"lookup_decision": lookup_report.decision.kind.value,
            b"witness_digest": self.witness_summary.transcript_digest,
            b"witness_decision": self.witness_summary.decision.kind.value,
            b"witness_families": sorted(family.encode("utf-8") for family in self.witness_summary.family_weights),
        }


@dataclass(frozen=True)
class CachePoisonDecision:
    kind: CachePoisonDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class CachePoisonReport:
    rounds: tuple[CacheRound, ...]
    lookup_reports: tuple[LookupPressureReport, ...]
    distinct_transcript_count: int
    replay_fraction: float
    accepted_witness_families: frozenset[str]
    fast_capture_rounds: int
    transcript_digest: bytes
    decision: CachePoisonDecision

    @property
    def needs_more_rounds(self) -> bool:
        return not self.decision.accept


def _largest_fraction(values: Iterable[bytes]) -> float:
    values = tuple(values)
    if not values:
        return 0.0
    counts: dict[bytes, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return max(counts.values()) / len(values)


def analyze_cache_poison_rounds(rounds: Iterable[CacheRound], *, policy: CachePoisonPolicy | None = None) -> CachePoisonReport:
    policy = policy or CachePoisonPolicy()
    policy.validate()
    round_tuple = tuple(rounds)
    lookup_reports = tuple(analyze_lookup_pressure(item.transcript, policy=policy.lookup_policy) for item in round_tuple)
    transcript_digests = tuple(item.transcript.digest for item in round_tuple)
    distinct_transcripts = len(set(transcript_digests))
    replay_fraction = _largest_fraction(transcript_digests)
    accepted_families: set[str] = set()
    contradiction = False
    for item in round_tuple:
        if item.witness_summary.decision.kind is WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION or item.witness_summary.contradictions:
            contradiction = True
        if item.witness_summary.decision.kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE:
            accepted_families.update(item.witness_summary.family_weights)
    fast_capture_rounds = sum(1 for report in lookup_reports if report.decision.kind is LookupPressureDecisionKind.QUARANTINE_FAST_WINDOW_CAPTURE)
    fast_fraction = fast_capture_rounds / len(round_tuple) if round_tuple else 0.0

    if not round_tuple or len(round_tuple) < policy.min_rounds:
        decision = CachePoisonDecision(CachePoisonDecisionKind.CONTINUE_MORE_ROUNDS, False, "not enough repeated lookup rounds to assess cache pressure")
    elif contradiction:
        decision = CachePoisonDecision(CachePoisonDecisionKind.QUARANTINE_CONTRADICTION, False, "witness cache preserved contradiction evidence")
    elif replay_fraction > policy.max_replay_fraction or distinct_transcripts < policy.min_distinct_transcripts:
        decision = CachePoisonDecision(CachePoisonDecisionKind.QUARANTINE_REPLAY_MONOCULTURE, False, "same lookup transcript/evidence shape replayed too often")
    elif fast_fraction > policy.max_fast_capture_round_fraction:
        decision = CachePoisonDecision(CachePoisonDecisionKind.QUARANTINE_FAST_CAPTURE_REINFORCED, False, "captured fast windows repeatedly reinforce this cache view")
    elif len(accepted_families) < policy.min_witness_families:
        decision = CachePoisonDecision(CachePoisonDecisionKind.CONTINUE_LOW_WITNESS_DIVERSITY, False, "accepted cache summaries do not cover enough witness families")
    else:
        decision = CachePoisonDecision(CachePoisonDecisionKind.ACCEPT_STABLE_DIVERSE_CACHE, True, "repeated rounds stayed diverse enough for local cache use")

    digest = sha256(CACHE_POISON_DOMAIN + b":report:" + bencode({
        b"rounds": [round_item.bvalue(report) for round_item, report in zip(round_tuple, lookup_reports)],
        b"distinct_transcript_count": distinct_transcripts,
        b"replay_fraction": str(round(replay_fraction, 4)),
        b"accepted_witness_families": sorted(family.encode("utf-8") for family in accepted_families),
        b"fast_capture_rounds": fast_capture_rounds,
        b"decision": decision.kind.value,
    }))
    return CachePoisonReport(
        rounds=round_tuple,
        lookup_reports=lookup_reports,
        distinct_transcript_count=distinct_transcripts,
        replay_fraction=replay_fraction,
        accepted_witness_families=frozenset(accepted_families),
        fast_capture_rounds=fast_capture_rounds,
        transcript_digest=digest,
        decision=decision,
    )
