"""Sibling-cast planning and store-ack pressure.

Kademlia-style stores usually target the k closest nodes. On an anonymous,
high-latency substrate with garden nodes and captured families, blindly taking
the nearest k is a gift to eclipse and route-poison pressure. This module makes
one harder guess executable: store/announce work should first try canonical
siblings, then deliberately pay a little distance to buy family diversity and
reserve capacity, and then require diverse exact-digest acknowledgements before
assuming the record survived.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity, select_family_capped
from .ids import DOMAIN, sha256, xor_distance

SIBLING_CAST_DOMAIN = DOMAIN + b":sibling-cast-v1:"


class SiblingCastPurpose(str, Enum):
    STORE_IMMUTABLE = "store_immutable"
    STORE_MUTABLE_HEAD = "store_mutable_head"
    PROVIDER_ANNOUNCE = "provider_announce"
    TOMBSTONE_REPAIR = "tombstone_repair"
    CONTACT_LEASE = "contact_lease"


class SiblingCastDecisionKind(str, Enum):
    PLAN_READY = "plan_ready"
    PLAN_READY_WITH_RESERVES = "plan_ready_with_reserves"
    CONTINUE_NO_WRITABLE_SIBLINGS = "continue_no_writable_siblings"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    CONTINUE_TOO_FEW_SIBLINGS = "continue_too_few_siblings"


class SiblingAckKind(str, Enum):
    STORED = "stored"
    REFUSED = "refused"
    TIMEOUT = "timeout"
    WRONG_DIGEST = "wrong_digest"


class SiblingAckDecisionKind(str, Enum):
    STORED_DIVERSE = "stored_diverse"
    CONTINUE_ACK_PRESSURE = "continue_ack_pressure"
    CONTINUE_TIMEOUT_PRESSURE = "continue_timeout_pressure"
    QUARANTINE_CONTRADICTION = "quarantine_contradiction"


@dataclass(frozen=True)
class SiblingCandidate:
    node_id: bytes
    family_id: str
    writable: bool = True
    garden: bool = False
    latency_ms: int = 0
    capacity_score: int = 0
    last_success_at: int = 0
    refusal_until: int = 0
    note: str = ""

    def __post_init__(self) -> None:
        if len(self.node_id) != 32:
            raise ValueError("sibling candidate node_id must be 32 bytes")
        if not self.family_id:
            raise ValueError("sibling candidate family_id is required")
        if self.latency_ms < 0 or self.last_success_at < 0 or self.refusal_until < 0:
            raise ValueError("candidate times must be non-negative")

    def distance_to(self, target: bytes) -> int:
        return xor_distance(self.node_id, target)

    def available(self, *, now: int) -> bool:
        return self.writable and self.refusal_until <= now

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"node_id": self.node_id,
            b"family_id": self.family_id,
            b"writable": 1 if self.writable else 0,
            b"garden": 1 if self.garden else 0,
            b"latency_ms": self.latency_ms,
            b"capacity_score": self.capacity_score,
            b"last_success_at": self.last_success_at,
            b"refusal_until": self.refusal_until,
            b"note": self.note[:160],
        }


@dataclass(frozen=True)
class SiblingCastPolicy:
    desired_siblings: int = 8
    min_siblings: int = 4
    min_families: int = 3
    max_per_family: int = 2
    reserve_count: int = 2
    allow_garden_reserves: bool = True
    max_latency_ms: int = 120_000

    def validate(self) -> None:
        if self.desired_siblings <= 0 or self.min_siblings <= 0 or self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("sibling thresholds must be positive")
        if self.min_siblings > self.desired_siblings:
            raise ValueError("min_siblings cannot exceed desired_siblings")
        if self.reserve_count < 0 or self.max_latency_ms <= 0:
            raise ValueError("reserve_count must be non-negative and max_latency positive")


@dataclass(frozen=True)
class SiblingCastDecision:
    kind: SiblingCastDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class SiblingCastPlan:
    target: bytes
    purpose: SiblingCastPurpose
    primary: tuple[SiblingCandidate, ...]
    reserves: tuple[SiblingCandidate, ...]
    refused_or_unavailable: tuple[SiblingCandidate, ...]
    family_counts: dict[str, int]
    decision: SiblingCastDecision
    transcript_digest: bytes

    @property
    def needs_more_lookup(self) -> bool:
        return not self.decision.accept

    @property
    def total_targets(self) -> int:
        return len(self.primary) + len(self.reserves)


def plan_sibling_cast(candidates: Iterable[SiblingCandidate], *, target: bytes, purpose: SiblingCastPurpose, now: int, policy: SiblingCastPolicy | None = None) -> SiblingCastPlan:
    policy = policy or SiblingCastPolicy()
    policy.validate()
    if len(target) != 32:
        raise ValueError("sibling target must be 32 bytes")
    all_candidates = tuple(candidates)
    writable = tuple(item for item in all_candidates if item.available(now=now) and item.latency_ms <= policy.max_latency_ms)
    unavailable = tuple(item for item in all_candidates if item not in writable)
    primary = select_family_capped(
        writable,
        family_of=lambda item: item.family_id,
        sort_key=lambda item: (item.distance_to(target), 0 if item.garden else 1, -item.capacity_score, item.latency_ms, item.node_id),
        limit=policy.desired_siblings,
        max_per_family=policy.max_per_family,
    )
    selected_ids = {item.node_id for item in primary}
    reserve_pool = [item for item in writable if item.node_id not in selected_ids]
    reserves = select_family_capped(
        reserve_pool,
        family_of=lambda item: item.family_id,
        sort_key=lambda item: (0 if policy.allow_garden_reserves and item.garden else 1, item.distance_to(target), -item.capacity_score, item.latency_ms, item.node_id),
        limit=policy.reserve_count,
        max_per_family=policy.max_per_family,
    )
    diversity_policy = FamilyDiversityPolicy(min_families=policy.min_families, max_per_family=policy.max_per_family)
    diversity = analyze_family_diversity(primary, family_of=lambda item: item.family_id, policy=diversity_policy)
    if not writable:
        decision = SiblingCastDecision(SiblingCastDecisionKind.CONTINUE_NO_WRITABLE_SIBLINGS, False, "no writable sibling candidates are available")
    elif len(primary) < policy.min_siblings:
        decision = SiblingCastDecision(SiblingCastDecisionKind.CONTINUE_TOO_FEW_SIBLINGS, False, "not enough writable siblings after family caps")
    elif not diversity.passes(diversity_policy):
        decision = SiblingCastDecision(SiblingCastDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, False, "selected siblings are not family-diverse enough")
    elif reserves:
        decision = SiblingCastDecision(SiblingCastDecisionKind.PLAN_READY_WITH_RESERVES, True, "sibling-cast plan has diverse primaries and reserves")
    else:
        decision = SiblingCastDecision(SiblingCastDecisionKind.PLAN_READY, True, "sibling-cast plan has diverse primaries")
    digest = sha256(SIBLING_CAST_DOMAIN + b":plan:" + bencode({
        b"target": target,
        b"purpose": purpose.value,
        b"primary": [item.bvalue() for item in primary],
        b"reserves": [item.bvalue() for item in reserves],
        b"unavailable": [item.bvalue() for item in unavailable],
        b"families": {family: count for family, count in sorted(diversity.family_counts.items())},
        b"decision": decision.kind.value,
    }))
    return SiblingCastPlan(target, purpose, tuple(primary), tuple(reserves), tuple(unavailable), diversity.family_counts, decision, digest)


@dataclass(frozen=True)
class SiblingAckPolicy:
    min_store_acks: int = 4
    min_store_families: int = 3
    timeout_limit: int = 3

    def validate(self) -> None:
        if self.min_store_acks <= 0 or self.min_store_families <= 0 or self.timeout_limit < 0:
            raise ValueError("sibling ack thresholds are invalid")


@dataclass(frozen=True)
class SiblingStoreAck:
    node_id: bytes
    family_id: str
    kind: SiblingAckKind
    record_digest: bytes
    replica_rank: int
    observed_at: int
    rtt_ms: int = 0

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"node_id": self.node_id,
            b"family_id": self.family_id,
            b"kind": self.kind.value,
            b"record_digest": self.record_digest,
            b"replica_rank": self.replica_rank,
            b"observed_at": self.observed_at,
            b"rtt_ms": self.rtt_ms,
        }


@dataclass(frozen=True)
class SiblingAckDecision:
    kind: SiblingAckDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class SiblingStoreAckReport:
    plan: SiblingCastPlan
    acks: tuple[SiblingStoreAck, ...]
    stored_count: int
    stored_families: frozenset[str]
    timeout_count: int
    decision: SiblingAckDecision
    transcript_digest: bytes


def analyze_sibling_store_acks(plan: SiblingCastPlan, *, record_digest: bytes, acks: Iterable[SiblingStoreAck], policy: SiblingAckPolicy | None = None) -> SiblingStoreAckReport:
    policy = policy or SiblingAckPolicy()
    policy.validate()
    ack_tuple = tuple(acks)
    by_node: dict[bytes, set[bytes]] = {}
    for ack in ack_tuple:
        if ack.kind is SiblingAckKind.STORED:
            by_node.setdefault(ack.node_id, set()).add(ack.record_digest)
    contradiction = any(len(digests) > 1 for digests in by_node.values()) or any(ack.kind is SiblingAckKind.WRONG_DIGEST for ack in ack_tuple)
    stored = tuple(ack for ack in ack_tuple if ack.kind is SiblingAckKind.STORED and ack.record_digest == record_digest)
    timeouts = tuple(ack for ack in ack_tuple if ack.kind is SiblingAckKind.TIMEOUT)
    stored_families = frozenset(ack.family_id for ack in stored)
    if contradiction:
        decision = SiblingAckDecision(SiblingAckDecisionKind.QUARANTINE_CONTRADICTION, False, "one sibling emitted contradictory store evidence")
    elif len(timeouts) > policy.timeout_limit:
        decision = SiblingAckDecision(SiblingAckDecisionKind.CONTINUE_TIMEOUT_PRESSURE, False, "too many sibling stores timed out")
    elif len(stored) >= policy.min_store_acks and len(stored_families) >= policy.min_store_families:
        decision = SiblingAckDecision(SiblingAckDecisionKind.STORED_DIVERSE, True, "enough family-diverse siblings stored the exact record digest")
    else:
        decision = SiblingAckDecision(SiblingAckDecisionKind.CONTINUE_ACK_PRESSURE, False, "not enough diverse exact-digest sibling acknowledgements")
    digest = sha256(SIBLING_CAST_DOMAIN + b":acks:" + bencode({
        b"plan": plan.transcript_digest,
        b"record_digest": record_digest,
        b"acks": [ack.bvalue() for ack in ack_tuple],
        b"decision": decision.kind.value,
    }))
    return SiblingStoreAckReport(plan, ack_tuple, len(stored), stored_families, len(timeouts), decision, digest)
