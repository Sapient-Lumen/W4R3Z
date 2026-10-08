"""Read-repair planning for replica observations.

Read repair is where many DHTs accidentally convert stale cache evidence into
truth.  This module keeps read outcomes typed: exact, missing, stale, wrong,
tombstoned, refused, and timeout.  It then decides whether to accept the replica
set, repair missing/stale families, continue reading, or quarantine the key.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity, select_family_capped
from .ids import DOMAIN, sha256
from .storeflight import StoreClass
from .tombstonecache import TombstoneCache

READ_REPAIR_DOMAIN = DOMAIN + b":read-repair-v1:"


class ReplicaObservationKind(str, Enum):
    EXACT = "exact"
    MISSING = "missing"
    STALE = "stale"
    WRONG_DIGEST = "wrong_digest"
    TOMBSTONED = "tombstoned"
    REFUSED = "refused"
    TIMEOUT = "timeout"


class ReadRepairDecisionKind(str, Enum):
    HEALTHY_DIVERSE_REPLICAS = "healthy_diverse_replicas"
    REPAIR_MISSING_OR_STALE = "repair_missing_or_stale"
    CONTINUE_MORE_READS = "continue_more_reads"
    BLOCKED_BY_TOMBSTONE = "blocked_by_tombstone"
    QUARANTINE_WRONG_DIGEST = "quarantine_wrong_digest"
    QUARANTINE_RESURRECTION_PRESSURE = "quarantine_resurrection_pressure"


@dataclass(frozen=True)
class ReplicaObservation:
    node_id: bytes
    family_id: str
    target: bytes
    expected_digest: bytes
    kind: ReplicaObservationKind
    observed_digest: bytes = b""
    observed_at: int = 0
    lease_expires_at: int = 0
    store_class: StoreClass = StoreClass.CANONICAL

    def __post_init__(self) -> None:
        if len(self.node_id) != 32 or len(self.target) != 32 or len(self.expected_digest) != 32:
            raise ValueError("node_id, target, and expected_digest must be 32 bytes")
        if self.observed_digest and len(self.observed_digest) != 32:
            raise ValueError("observed_digest must be empty or 32 bytes")
        if not self.family_id:
            raise ValueError("family_id is required")
        if self.observed_at < 0 or self.lease_expires_at < 0:
            raise ValueError("observation times must be non-negative")

    @property
    def exact(self) -> bool:
        return self.kind is ReplicaObservationKind.EXACT and self.observed_digest == self.expected_digest

    @property
    def repairable(self) -> bool:
        return self.kind in (ReplicaObservationKind.MISSING, ReplicaObservationKind.STALE, ReplicaObservationKind.TIMEOUT)

    @property
    def contradiction(self) -> bool:
        return self.kind is ReplicaObservationKind.WRONG_DIGEST or (self.kind is ReplicaObservationKind.EXACT and self.observed_digest != self.expected_digest)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"node_id": self.node_id,
            b"family_id": self.family_id,
            b"target": self.target,
            b"expected_digest": self.expected_digest,
            b"kind": self.kind.value,
            b"observed_digest": self.observed_digest,
            b"observed_at": self.observed_at,
            b"lease_expires_at": self.lease_expires_at,
            b"store_class": self.store_class.value,
        }


@dataclass(frozen=True)
class RepairAction:
    node_id: bytes
    family_id: str
    target: bytes
    record_digest: bytes
    reason: str
    priority: int

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"node_id": self.node_id, b"family_id": self.family_id, b"target": self.target, b"digest": self.record_digest, b"reason": self.reason, b"priority": self.priority}


@dataclass(frozen=True)
class ReadRepairPolicy:
    min_exact: int = 4
    min_exact_families: int = 3
    max_per_family: int = 2
    max_repair_actions: int = 4
    min_reads_before_quiet: int = 5

    def validate(self) -> None:
        if self.min_exact <= 0 or self.min_exact_families <= 0 or self.max_per_family <= 0 or self.max_repair_actions < 0:
            raise ValueError("read repair thresholds are invalid")
        if self.min_reads_before_quiet <= 0:
            raise ValueError("min_reads_before_quiet must be positive")


@dataclass(frozen=True)
class ReadRepairDecision:
    kind: ReadRepairDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class ReadRepairReport:
    target: bytes
    expected_digest: bytes
    exact: tuple[ReplicaObservation, ...]
    repairable: tuple[ReplicaObservation, ...]
    repair_actions: tuple[RepairAction, ...]
    exact_families: frozenset[str]
    decision: ReadRepairDecision
    transcript_digest: bytes


def plan_read_repair(
    *,
    target: bytes,
    expected_digest: bytes,
    observations: Iterable[ReplicaObservation],
    now: int,
    policy: ReadRepairPolicy | None = None,
    tombstone_cache: TombstoneCache | None = None,
    tombstone_target: bytes | None = None,
) -> ReadRepairReport:
    policy = policy or ReadRepairPolicy()
    policy.validate()
    if len(target) != 32 or len(expected_digest) != 32:
        raise ValueError("target and expected_digest must be 32 bytes")
    obs = tuple(observations)
    relevant = tuple(item for item in obs if item.target == target and item.expected_digest == expected_digest)
    exact = tuple(item for item in relevant if item.exact)
    repairable = tuple(item for item in relevant if item.repairable)
    contradicted = any(item.contradiction for item in relevant)
    observed_tombstone = any(item.kind is ReplicaObservationKind.TOMBSTONED for item in relevant)
    live_tombstone = False
    if tombstone_cache is not None:
        commitment = tombstone_target or sha256(READ_REPAIR_DOMAIN + b":tombstone-target:" + target + expected_digest)
        live_tombstone = bool(tombstone_cache.live_for(commitment, now=now))
    diversity = analyze_family_diversity(exact, family_of=lambda item: item.family_id, policy=FamilyDiversityPolicy(min_families=policy.min_exact_families, max_per_family=policy.max_per_family)) if exact else None
    exact_families = frozenset(diversity.family_counts) if diversity is not None else frozenset()

    action_candidates = select_family_capped(
        repairable,
        family_of=lambda item: item.family_id,
        sort_key=lambda item: (0 if item.kind is ReplicaObservationKind.STALE else 1 if item.kind is ReplicaObservationKind.MISSING else 2, item.lease_expires_at, item.family_id, item.node_id),
        limit=policy.max_repair_actions,
        max_per_family=1,
    )
    actions = tuple(
        RepairAction(
            node_id=item.node_id,
            family_id=item.family_id,
            target=target,
            record_digest=expected_digest,
            reason=f"repair_{item.kind.value}",
            priority=100 - rank,
        )
        for rank, item in enumerate(action_candidates)
    )

    if live_tombstone and exact:
        decision = ReadRepairDecision(ReadRepairDecisionKind.QUARANTINE_RESURRECTION_PRESSURE, False, "exact cache evidence conflicts with live tombstone")
    elif live_tombstone or observed_tombstone:
        decision = ReadRepairDecision(ReadRepairDecisionKind.BLOCKED_BY_TOMBSTONE, False, "tombstone evidence blocks read-repair acceptance")
    elif contradicted:
        decision = ReadRepairDecision(ReadRepairDecisionKind.QUARANTINE_WRONG_DIGEST, False, "wrong digest observation makes repair unsafe")
    elif len(exact) >= policy.min_exact and len(exact_families) >= policy.min_exact_families:
        decision = ReadRepairDecision(ReadRepairDecisionKind.HEALTHY_DIVERSE_REPLICAS, True, "exact replicas span enough families")
    elif actions:
        decision = ReadRepairDecision(ReadRepairDecisionKind.REPAIR_MISSING_OR_STALE, False, "missing/stale replicas should be repaired before accepting health")
    else:
        decision = ReadRepairDecision(ReadRepairDecisionKind.CONTINUE_MORE_READS, False, "not enough exact diverse reads and no bounded repair action yet")

    digest = sha256(READ_REPAIR_DOMAIN + b":report:" + bencode({
        b"target": target,
        b"expected_digest": expected_digest,
        b"observations": [item.bvalue() for item in relevant],
        b"actions": [item.bvalue() for item in actions],
        b"decision": decision.kind.value,
    }))
    return ReadRepairReport(target, expected_digest, exact, repairable, actions, exact_families, decision, digest)
