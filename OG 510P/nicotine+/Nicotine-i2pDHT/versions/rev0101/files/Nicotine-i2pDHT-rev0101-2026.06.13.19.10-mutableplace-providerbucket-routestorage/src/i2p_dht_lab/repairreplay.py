"""Repair-market replay and colluding-family pressure across windows.

``repairmarket.py`` can select a diverse set of garden repair offers for one
workload.  The harder failure mode is repetition: the same offer digests,
sequence windows, or introducer families can keep winning across rounds and
quietly turn a voluntary garden-capacity layer into a captured repair path.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .ids import DOMAIN, sha256
from .repairmarket import GardenRepairOffer, RepairSelectionReport

REPAIR_REPLAY_DOMAIN = DOMAIN + b":repair-replay-v1:"


class RepairReplayDecisionKind(str, Enum):
    ACCEPT_FRESH_DIVERSE_REPAIR_WINDOWS = "accept_fresh_diverse_repair_windows"
    CONTINUE_NEED_MORE_WINDOWS = "continue_need_more_windows"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    HOLD_USEFUL_REFUSAL_BACKOFF = "hold_useful_refusal_backoff"
    QUARANTINE_REPLAYED_OFFERS = "quarantine_replayed_offers"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_COLLUDING_FAMILIES = "quarantine_colluding_families"


@dataclass(frozen=True)
class RepairReplayPolicy:
    min_windows: int = 2
    min_distinct_families: int = 3
    max_per_family: int = 1
    max_offer_replay_count: int = 1
    useful_refusal_backoff_floor_seconds: int = 300

    def validate(self) -> None:
        if self.min_windows <= 0 or self.min_distinct_families <= 0 or self.max_per_family <= 0 or self.max_offer_replay_count <= 0:
            raise ValueError("repair replay thresholds must be positive")
        if self.useful_refusal_backoff_floor_seconds < 0:
            raise ValueError("repair replay backoff threshold must be non-negative")


@dataclass(frozen=True)
class RepairReplayWindow:
    report: RepairSelectionReport
    window_index: int
    observed_at: int

    def __post_init__(self) -> None:
        if self.window_index < 0 or self.observed_at < 0:
            raise ValueError("repair replay window counters must be non-negative")

    @property
    def selected_offers(self) -> tuple[GardenRepairOffer, ...]:
        return self.report.selected

    @property
    def useful_refusals(self) -> tuple[GardenRepairOffer, ...]:
        return self.report.useful_refusals


@dataclass(frozen=True)
class RepairReplayDecision:
    kind: RepairReplayDecisionKind
    accept: bool
    reason: str
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class RepairReplayReport:
    windows: tuple[RepairReplayWindow, ...]
    offer_replay_counts: dict[bytes, int]
    family_counts: dict[str, int]
    rollback_count: int
    decision: RepairReplayDecision
    transcript_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def analyze_repair_replay(windows: Iterable[RepairReplayWindow], *, policy: RepairReplayPolicy | None = None) -> RepairReplayReport:
    policy = policy or RepairReplayPolicy()
    policy.validate()
    window_tuple = tuple(sorted(windows, key=lambda item: item.window_index))
    offer_replay_counts: dict[bytes, int] = {}
    offer_sequences: dict[bytes, int] = {}
    selected: list[GardenRepairOffer] = []
    rollback_count = 0
    max_refusal_retry = 0

    for window in window_tuple:
        for offer in window.selected_offers:
            selected.append(offer)
            offer_replay_counts[offer.offer_digest] = offer_replay_counts.get(offer.offer_digest, 0) + 1
            previous = offer_sequences.get(offer.garden_public_key)
            if previous is not None and offer.sequence < previous:
                rollback_count += 1
            offer_sequences[offer.garden_public_key] = max(previous or 0, offer.sequence)
        for refusal in window.useful_refusals:
            max_refusal_retry = max(max_refusal_retry, refusal.retry_after_seconds)

    diversity = analyze_family_diversity(selected, family_of=lambda offer: offer.family_id, policy=FamilyDiversityPolicy(min_families=policy.min_distinct_families, max_per_family=policy.max_per_family))
    replayed = {digest: count for digest, count in offer_replay_counts.items() if count > policy.max_offer_replay_count}

    if len(window_tuple) < policy.min_windows:
        decision = RepairReplayDecision(RepairReplayDecisionKind.CONTINUE_NEED_MORE_WINDOWS, False, "not enough repair windows observed yet")
    elif rollback_count:
        decision = RepairReplayDecision(RepairReplayDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "repair offer sequence moved backward for a garden key")
    elif replayed:
        decision = RepairReplayDecision(RepairReplayDecisionKind.QUARANTINE_REPLAYED_OFFERS, False, "same repair offer digest replayed across too many windows")
    elif not diversity.passes(FamilyDiversityPolicy(min_families=policy.min_distinct_families, max_per_family=policy.max_per_family)):
        kind = RepairReplayDecisionKind.QUARANTINE_COLLUDING_FAMILIES if diversity.is_monoculture else RepairReplayDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY
        decision = RepairReplayDecision(kind, False, "repair windows lack family diversity")
    elif max_refusal_retry >= policy.useful_refusal_backoff_floor_seconds:
        decision = RepairReplayDecision(RepairReplayDecisionKind.HOLD_USEFUL_REFUSAL_BACKOFF, False, "useful refusal backoff should be honored", retry_after_seconds=max_refusal_retry)
    else:
        decision = RepairReplayDecision(RepairReplayDecisionKind.ACCEPT_FRESH_DIVERSE_REPAIR_WINDOWS, True, "repair windows are fresh enough and family-diverse")

    digest = sha256(REPAIR_REPLAY_DOMAIN + b":report:" + bencode({
        b"windows": [window.report.transcript_digest for window in window_tuple],
        b"offer_replay_counts": [{b"offer": key, b"count": value} for key, value in sorted(offer_replay_counts.items())],
        b"families": [{b"family": key, b"count": value} for key, value in sorted(diversity.uncapped_family_counts.items())],
        b"rollback_count": rollback_count,
        b"decision": decision.kind.value,
    }))
    return RepairReplayReport(window_tuple, offer_replay_counts, diversity.uncapped_family_counts, rollback_count, decision, digest)
