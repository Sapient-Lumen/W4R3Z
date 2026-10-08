"""Store mesh pressure for mutable heads, tombstones, and provider claims.

Sibling-cast acknowledgements are useful but narrow: they answer whether a set
of sibling candidates claims to have stored one exact digest. rev0019 joins those
ack reports into a store mesh so higher-risk record families can be judged
together. In particular, mutable-head replication should not outrun tombstone
repair, and useful refusals should slow the mesh rather than be counted as
replica success.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .siblingcast import SiblingAckDecisionKind, SiblingAckKind, SiblingStoreAckReport

STORE_MESH_DOMAIN = DOMAIN + b":store-mesh-v1:"


class StoreRecordKind(str, Enum):
    IMMUTABLE = "immutable"
    PROVIDER = "provider"
    MUTABLE_HEAD = "mutable_head"
    TOMBSTONE = "tombstone"
    CONTACT_LEASE = "contact_lease"


class StoreMeshDecisionKind(str, Enum):
    ACCEPT_MESH_STORED = "accept_mesh_stored"
    CONTINUE_STORE_PRESSURE = "continue_store_pressure"
    CONTINUE_TOMBSTONE_FIRST = "continue_tombstone_first"
    HOLD_USEFUL_REFUSALS = "hold_useful_refusals"
    QUARANTINE_STORE_CONTRADICTION = "quarantine_store_contradiction"
    QUARANTINE_RESURRECTION_PRESSURE = "quarantine_resurrection_pressure"


@dataclass(frozen=True)
class StoreMeshPolicy:
    require_tombstone_before_mutable: bool = True
    max_refusal_share_ppm: int = 500_000
    require_all_rounds_accepted: bool = True

    def validate(self) -> None:
        if not 0 <= self.max_refusal_share_ppm <= 1_000_000:
            raise ValueError("refusal share must be in ppm range")


@dataclass(frozen=True)
class StoreMeshRound:
    kind: StoreRecordKind
    record_digest: bytes
    ack_report: SiblingStoreAckReport
    observed_at: int
    target: bytes = b""
    linked_tombstone_digest: bytes = b""

    def __post_init__(self) -> None:
        if len(self.record_digest) != 32:
            raise ValueError("store mesh round record digest must be 32 bytes")
        if self.target and len(self.target) != 32:
            raise ValueError("store mesh round target must be empty or 32 bytes")
        if self.linked_tombstone_digest and len(self.linked_tombstone_digest) != 32:
            raise ValueError("linked tombstone digest must be empty or 32 bytes")

    @property
    def accepted(self) -> bool:
        return self.ack_report.decision.accept

    @property
    def refusal_count(self) -> int:
        return sum(1 for ack in self.ack_report.acks if ack.kind is SiblingAckKind.REFUSED)

    @property
    def ack_count(self) -> int:
        return len(self.ack_report.acks)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"record_digest": self.record_digest,
            b"ack_report": self.ack_report.transcript_digest,
            b"accepted": 1 if self.accepted else 0,
            b"decision": self.ack_report.decision.kind.value,
            b"refusal_count": self.refusal_count,
            b"ack_count": self.ack_count,
            b"observed_at": self.observed_at,
            b"target": self.target,
            b"linked_tombstone_digest": self.linked_tombstone_digest,
        }


@dataclass(frozen=True)
class StoreMeshDecision:
    kind: StoreMeshDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class StoreMeshReport:
    rounds: tuple[StoreMeshRound, ...]
    accepted_rounds: int
    refusal_count: int
    ack_count: int
    accepted_tombstone_digests: frozenset[bytes]
    blocked_live_tombstone_digests: frozenset[bytes]
    decision: StoreMeshDecision
    transcript_digest: bytes

    @property
    def needs_repair(self) -> bool:
        return not self.decision.accept


class StoreMeshInputError(ValueError):
    """Raised when the test harness constructs an impossible store mesh."""


def assess_store_mesh(
    rounds: Iterable[StoreMeshRound],
    *,
    live_tombstone_digests: Iterable[bytes] = (),
    policy: StoreMeshPolicy | None = None,
) -> StoreMeshReport:
    policy = policy or StoreMeshPolicy()
    policy.validate()
    round_tuple = tuple(rounds)
    for item in round_tuple:
        if item.ack_report.plan.transcript_digest != item.ack_report.plan.transcript_digest:  # pragma: no cover - structural placeholder
            raise StoreMeshInputError("unreachable sanity check")
    live_tombs = frozenset(live_tombstone_digests)
    accepted_tombs = frozenset(item.record_digest for item in round_tuple if item.kind is StoreRecordKind.TOMBSTONE and item.accepted)
    accepted_rounds = sum(1 for item in round_tuple if item.accepted)
    refusal_count = sum(item.refusal_count for item in round_tuple)
    ack_count = sum(item.ack_count for item in round_tuple)
    refusal_share = 0 if ack_count == 0 else int(refusal_count * 1_000_000 / ack_count)

    contradiction = any(item.ack_report.decision.kind is SiblingAckDecisionKind.QUARANTINE_CONTRADICTION for item in round_tuple)
    resurrection_pressure = bool(live_tombs) and any(
        item.kind in {StoreRecordKind.MUTABLE_HEAD, StoreRecordKind.PROVIDER, StoreRecordKind.IMMUTABLE}
        and item.accepted
        and (not item.linked_tombstone_digest or item.linked_tombstone_digest not in accepted_tombs)
        for item in round_tuple
    )
    mutable_without_tomb = any(
        item.kind is StoreRecordKind.MUTABLE_HEAD
        and item.linked_tombstone_digest
        and item.linked_tombstone_digest not in accepted_tombs
        for item in round_tuple
    )
    any_unaccepted = any(not item.accepted for item in round_tuple)

    if contradiction:
        decision = StoreMeshDecision(StoreMeshDecisionKind.QUARANTINE_STORE_CONTRADICTION, False, "sibling store acknowledgements contain exact-digest contradictions")
    elif resurrection_pressure:
        decision = StoreMeshDecision(StoreMeshDecisionKind.QUARANTINE_RESURRECTION_PRESSURE, False, "live tombstone evidence blocks convenient stale/mutable/provider storage")
    elif policy.require_tombstone_before_mutable and mutable_without_tomb:
        decision = StoreMeshDecision(StoreMeshDecisionKind.CONTINUE_TOMBSTONE_FIRST, False, "mutable-head storage is waiting for linked tombstone repair")
    elif refusal_share > policy.max_refusal_share_ppm:
        decision = StoreMeshDecision(StoreMeshDecisionKind.HOLD_USEFUL_REFUSALS, False, "too much of the store mesh is useful refusal/backoff capacity")
    elif policy.require_all_rounds_accepted and any_unaccepted:
        decision = StoreMeshDecision(StoreMeshDecisionKind.CONTINUE_STORE_PRESSURE, False, "at least one store round still lacks diverse exact-digest acknowledgements")
    elif not round_tuple:
        decision = StoreMeshDecision(StoreMeshDecisionKind.CONTINUE_STORE_PRESSURE, False, "no store rounds were provided")
    else:
        decision = StoreMeshDecision(StoreMeshDecisionKind.ACCEPT_MESH_STORED, True, "store mesh has enough exact-digest, family-diverse acknowledgement evidence")

    digest = sha256(STORE_MESH_DOMAIN + b":report:" + bencode({
        b"rounds": [item.bvalue() for item in round_tuple],
        b"live_tombstones": sorted(live_tombs),
        b"accepted_tombstones": sorted(accepted_tombs),
        b"accepted_rounds": accepted_rounds,
        b"refusal_count": refusal_count,
        b"ack_count": ack_count,
        b"refusal_share_ppm": refusal_share,
        b"decision": decision.kind.value,
    }))
    return StoreMeshReport(round_tuple, accepted_rounds, refusal_count, ack_count, accepted_tombs, live_tombs, decision, digest)
