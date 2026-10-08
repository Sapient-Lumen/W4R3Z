"""Churn-frontier pressure for path-family lookup candidates.

rev0011 keeps this deliberately smaller than a full simulator. It asks one hard
question before live I2P transport exists: when latency/churn make a fast set
look good, can a client avoid selecting a monoculture of one operator/family?
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .ids import sha256, xor_distance
from .routing import Contact


class ChurnState(str, Enum):
    UP = "up"
    SLOW = "slow"
    REFUSING = "refusing"
    DOWN = "down"
    LYING = "lying"


class ChurnDecisionKind(str, Enum):
    ENOUGH_DIVERSITY = "enough_diversity"
    CONTINUE_TOO_FEW_FAMILIES = "continue_too_few_families"
    CONTINUE_TOO_MANY_BAD = "continue_too_many_bad"
    CONTINUE_FAST_WINDOW_CAPTURED = "continue_fast_window_captured"


@dataclass(frozen=True)
class ChurnContact:
    contact: Contact
    family_id: str
    state: ChurnState = ChurnState.UP
    delay_ms: int = 100
    last_seen_at: int = 0

    @property
    def selectable(self) -> bool:
        return self.state in {ChurnState.UP, ChurnState.SLOW, ChurnState.REFUSING}

    @property
    def bad(self) -> bool:
        return self.state in {ChurnState.DOWN, ChurnState.LYING}


@dataclass(frozen=True)
class ChurnFrontier:
    target: bytes
    contacts: tuple[ChurnContact, ...]

    @property
    def families(self) -> frozenset[str]:
        return frozenset(contact.family_id for contact in self.contacts)

    @property
    def bad_count(self) -> int:
        return sum(1 for contact in self.contacts if contact.bad)


@dataclass(frozen=True)
class ChurnDecision:
    kind: ChurnDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class ChurnWireEvent:
    request_id: bytes
    target: bytes
    node_id: bytes
    family_id: str
    state: ChurnState
    delay_ms: int
    event: str = "probe"

    @property
    def digest(self) -> bytes:
        return sha256(b"churn-wire-event-v1|" + b"|".join((
            self.request_id,
            self.target,
            self.node_id,
            self.family_id.encode("utf-8"),
            self.state.value.encode("utf-8"),
            str(self.delay_ms).encode("ascii"),
            self.event.encode("utf-8"),
        )))


@dataclass(frozen=True)
class ChurnWireTranscript:
    events: tuple[ChurnWireEvent, ...]

    @property
    def digest(self) -> bytes:
        material = b"".join(event.digest for event in sorted(self.events, key=lambda event: (event.request_id, event.family_id, event.node_id, event.event)))
        return sha256(b"churn-wire-transcript-v1|" + material)


def select_churn_frontier(
    candidates: Iterable[ChurnContact],
    *,
    target: bytes,
    count: int,
    max_per_family: int = 1,
    now: int = 0,
) -> ChurnFrontier:
    """Select by family rotation first, then freshness/latency/distance."""
    if count <= 0:
        return ChurnFrontier(target, ())
    remaining = [candidate for candidate in candidates if candidate.selectable]
    selected: list[ChurnContact] = []
    family_counts: dict[str, int] = {}

    def sort_key(candidate: ChurnContact) -> tuple[int, int, int, int, int, bytes]:
        freshness_age = max(0, now - candidate.last_seen_at)
        state_penalty = {ChurnState.UP: 0, ChurnState.SLOW: 1, ChurnState.REFUSING: 2, ChurnState.DOWN: 9, ChurnState.LYING: 9}[candidate.state]
        return (
            family_counts.get(candidate.family_id, 0),
            state_penalty,
            freshness_age,
            candidate.delay_ms,
            xor_distance(candidate.contact.node_id, target) // (2**248),
            candidate.contact.node_id,
        )

    while remaining and len(selected) < count:
        remaining.sort(key=sort_key)
        picked = None
        for idx, candidate in enumerate(remaining):
            if family_counts.get(candidate.family_id, 0) < max_per_family:
                picked = remaining.pop(idx)
                break
        if picked is None:
            break
        selected.append(picked)
        family_counts[picked.family_id] = family_counts.get(picked.family_id, 0) + 1
    return ChurnFrontier(target, tuple(selected))


def assess_churn_frontier(
    frontier: ChurnFrontier,
    *,
    min_families: int = 3,
    max_bad_fraction: float = 0.25,
    fast_window_ms: int = 75,
    max_fast_single_family_fraction: float = 0.67,
) -> ChurnDecision:
    if len(frontier.families) < min_families:
        return ChurnDecision(ChurnDecisionKind.CONTINUE_TOO_FEW_FAMILIES, False, "frontier has too few independent families")
    total = len(frontier.contacts)
    if total and frontier.bad_count / total > max_bad_fraction:
        return ChurnDecision(ChurnDecisionKind.CONTINUE_TOO_MANY_BAD, False, "frontier has too many down/lying contacts")
    fast = [contact for contact in frontier.contacts if contact.delay_ms <= fast_window_ms]
    if fast:
        by_family: dict[str, int] = {}
        for contact in fast:
            by_family[contact.family_id] = by_family.get(contact.family_id, 0) + 1
        if max(by_family.values()) / len(fast) > max_fast_single_family_fraction:
            return ChurnDecision(ChurnDecisionKind.CONTINUE_FAST_WINDOW_CAPTURED, False, "fastest window is dominated by one family")
    return ChurnDecision(ChurnDecisionKind.ENOUGH_DIVERSITY, True, "frontier passes lab churn thresholds")


def make_churn_transcript(frontier: ChurnFrontier, *, request_id: bytes, event: str = "lookup_frontier_probe") -> ChurnWireTranscript:
    return ChurnWireTranscript(tuple(
        ChurnWireEvent(request_id, frontier.target, item.contact.node_id, item.family_id, item.state, item.delay_ms, event)
        for item in frontier.contacts
    ))
