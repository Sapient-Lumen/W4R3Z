"""Garden STORE-flight admission and custody receipts.

The DHT has spent many revisions judging provider claims, mutable heads,
witnesses, tombstones, contacts, and garden refusals.  rev0019 starts pressure
on the next hard surface: what happens when a garden actually agrees to store
records for others?

A STORE response must not be a vague yes.  It should be a bounded local contract:
which digest was stored, under what budget window, until when, with which useful
refusals, and which lower-priority records were evicted.  This module does not
implement a network STORE protocol.  It gives the baby cube deterministic
admission, eviction, and custody-receipt semantics before live transport hides
bad guesses.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

STORE_FLIGHT_DOMAIN = DOMAIN + b":store-flight-v1:"


class StoreRecordKind(str, Enum):
    TOMBSTONE = "tombstone"
    MUTABLE_HEAD = "mutable_head"
    WITNESS_RECEIPT = "witness_receipt"
    CONTACT_LEASE = "contact_lease"
    PROVIDER_RECORD = "provider_record"
    SIBLING_ACK = "sibling_ack"
    BULK_MANIFEST = "bulk_manifest"
    SLOPPY_CACHE = "sloppy_cache"




class StoreClass(str, Enum):
    CANONICAL = "canonical"
    SIBLING = "sibling"
    SLOPPY = "sloppy"
    GARDEN_LEASE = "garden_lease"
    READ_REPAIR = "read_repair"


CONTROL_PLANE_KINDS = frozenset({
    StoreRecordKind.TOMBSTONE,
    StoreRecordKind.MUTABLE_HEAD,
    StoreRecordKind.WITNESS_RECEIPT,
    StoreRecordKind.CONTACT_LEASE,
})

EVICTION_ORDER = {
    StoreRecordKind.SLOPPY_CACHE: 0,
    StoreRecordKind.PROVIDER_RECORD: 1,
    StoreRecordKind.BULK_MANIFEST: 2,
    StoreRecordKind.SIBLING_ACK: 3,
    StoreRecordKind.WITNESS_RECEIPT: 4,
    StoreRecordKind.CONTACT_LEASE: 5,
    StoreRecordKind.MUTABLE_HEAD: 6,
    StoreRecordKind.TOMBSTONE: 7,
}


class StoreFlightDecisionKind(str, Enum):
    ACCEPT_STORE = "accept_store"
    ACCEPT_WITH_EVICTION = "accept_with_eviction"
    REFUSE_OVER_BUDGET = "refuse_over_budget"
    REFUSE_FAMILY_CAP = "refuse_family_cap"
    REJECT_INVALID = "reject_invalid"
    REJECT_EXPIRED = "reject_expired"
    QUARANTINE_BAD_PROOF = "quarantine_bad_proof"
    QUARANTINE_TOMBSTONED = "quarantine_tombstoned"


class StoreFlightSummaryKind(str, Enum):
    STORED_ALL = "stored_all"
    STORED_WITH_REFUSALS = "stored_with_refusals"
    CONTROL_PLANE_PROTECTED = "control_plane_protected"
    QUARANTINE_PRESSURE = "quarantine_pressure"
    NO_ACCEPTED_RECORDS = "no_accepted_records"


@dataclass(frozen=True)
class StoreFlightPolicy:
    max_records: int = 128
    max_bytes: int = 512_000
    max_candidate_size: int = 64_000
    max_per_source_family: int = 32
    max_bulk_per_source_family: int = 12
    control_plane_reserve_records: int = 16
    control_plane_reserve_bytes: int = 64_000
    min_ttl_remaining: int = 60
    custody_ttl: int = 6 * 3600

    def validate(self) -> None:
        if self.max_records <= 0 or self.max_bytes <= 0:
            raise ValueError("store limits must be positive")
        if self.max_candidate_size <= 0 or self.max_per_source_family <= 0 or self.max_bulk_per_source_family <= 0:
            raise ValueError("candidate/family limits must be positive")
        if self.control_plane_reserve_records < 0 or self.control_plane_reserve_bytes < 0:
            raise ValueError("control plane reserves must be non-negative")
        if self.min_ttl_remaining < 0 or self.custody_ttl <= 0:
            raise ValueError("ttl thresholds must be non-negative/positive")


@dataclass(frozen=True)
class StoreCandidate:
    key: bytes
    record_digest: bytes
    kind: StoreRecordKind
    namespace: str
    source_family: str
    size_bytes: int
    issued_at: int
    expires_at: int
    priority: int = 0
    proof_ok: bool = True
    tombstone_target: bytes = b""
    note: str = ""

    def __post_init__(self) -> None:
        if len(self.key) != 32 or len(self.record_digest) != 32:
            raise ValueError("store candidate key and digest must be 32 bytes")
        if not self.namespace or not self.source_family:
            raise ValueError("store candidate namespace and source family are required")
        if self.size_bytes <= 0:
            raise ValueError("store candidate size must be positive")
        if self.expires_at <= self.issued_at:
            raise ValueError("store candidate expires_at must follow issued_at")
        if self.tombstone_target and len(self.tombstone_target) != 32:
            raise ValueError("tombstone target must be empty or 32 bytes")

    @property
    def control_plane(self) -> bool:
        return self.kind in CONTROL_PLANE_KINDS

    @property
    def bulkish(self) -> bool:
        return self.kind in {StoreRecordKind.PROVIDER_RECORD, StoreRecordKind.BULK_MANIFEST, StoreRecordKind.SLOPPY_CACHE}

    @property
    def identity(self) -> tuple[str, str, bytes, bytes]:
        return (self.namespace, self.kind.value, self.key, self.record_digest)

    def live(self, *, now: int, policy: StoreFlightPolicy) -> bool:
        return self.issued_at <= now and self.expires_at - now >= policy.min_ttl_remaining

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"key": self.key,
            b"record_digest": self.record_digest,
            b"kind": self.kind.value,
            b"namespace": self.namespace,
            b"source_family": self.source_family,
            b"size_bytes": self.size_bytes,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"priority": self.priority,
            b"proof_ok": 1 if self.proof_ok else 0,
            b"tombstone_target": self.tombstone_target,
            b"note": self.note,
        }


@dataclass(frozen=True)
class StoreSlot:
    candidate: StoreCandidate
    stored_at: int
    custody_until: int
    last_verified_at: int = 0

    @property
    def size_bytes(self) -> int:
        return self.candidate.size_bytes

    @property
    def source_family(self) -> str:
        return self.candidate.source_family

    @property
    def control_plane(self) -> bool:
        return self.candidate.control_plane

    @property
    def evict_rank(self) -> tuple[int, int, int, bytes]:
        return (EVICTION_ORDER[self.candidate.kind], self.candidate.priority, self.stored_at, self.candidate.record_digest)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"candidate": self.candidate.bvalue(),
            b"stored_at": self.stored_at,
            b"custody_until": self.custody_until,
            b"last_verified_at": self.last_verified_at,
        }


@dataclass(frozen=True)
class CustodyReceipt:
    garden_node_id: bytes
    record_digest: bytes
    record_kind: StoreRecordKind
    accepted_at: int
    custody_until: int
    size_bytes: int
    source_family: str
    service_window: str
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.garden_node_id) != 32 or len(self.record_digest) != 32:
            raise ValueError("custody receipt node id and digest must be 32 bytes")
        if self.custody_until <= self.accepted_at:
            raise ValueError("custody receipt custody_until must follow accepted_at")
        if self.size_bytes <= 0 or not self.source_family or not self.service_window:
            raise ValueError("custody receipt needs size, source_family, and service_window")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"garden_node_id": self.garden_node_id,
            b"record_digest": self.record_digest,
            b"record_kind": self.record_kind.value,
            b"accepted_at": self.accepted_at,
            b"custody_until": self.custody_until,
            b"size_bytes": self.size_bytes,
            b"source_family": self.source_family,
            b"service_window": self.service_window,
        }

    def unsigned_payload(self) -> bytes:
        return STORE_FLIGHT_DOMAIN + b":custody-receipt:" + bencode(self.bvalue())

    @classmethod
    def create(
        cls,
        *,
        garden_keypair: DhtKeypair,
        garden_node_id: bytes,
        candidate: StoreCandidate,
        accepted_at: int,
        custody_until: int,
        service_window: str = "store-v1",
    ) -> "CustodyReceipt":
        unsigned = cls(
            garden_node_id=garden_node_id,
            record_digest=candidate.record_digest,
            record_kind=candidate.kind,
            accepted_at=accepted_at,
            custody_until=custody_until,
            size_bytes=candidate.size_bytes,
            source_family=candidate.source_family,
            service_window=service_window,
        )
        return replace(unsigned, signature=garden_keypair.sign(unsigned.unsigned_payload()))

    def verify(self, garden_public_key: bytes) -> bool:
        return verify_signature(garden_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class StoreFlightAction:
    candidate: StoreCandidate
    kind: StoreFlightDecisionKind
    accepted: bool
    reason: str
    evicted: tuple[StoreSlot, ...] = ()
    receipt: CustodyReceipt | None = None

    @property
    def refused(self) -> bool:
        return self.kind in {StoreFlightDecisionKind.REFUSE_OVER_BUDGET, StoreFlightDecisionKind.REFUSE_FAMILY_CAP}

    @property
    def quarantined(self) -> bool:
        return self.kind in {StoreFlightDecisionKind.QUARANTINE_BAD_PROOF, StoreFlightDecisionKind.QUARANTINE_TOMBSTONED}

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"candidate": self.candidate.bvalue(),
            b"kind": self.kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"reason": self.reason,
            b"evicted": [slot.bvalue() for slot in self.evicted],
            b"receipt_digest": b"" if self.receipt is None else sha256(self.receipt.unsigned_payload() + self.receipt.signature),
        }


@dataclass(frozen=True)
class StoreFlightSummary:
    kind: StoreFlightSummaryKind
    ok: bool
    reason: str


@dataclass(frozen=True)
class StoreFlightReport:
    actions: tuple[StoreFlightAction, ...]
    final_slots: tuple[StoreSlot, ...]
    evicted_slots: tuple[StoreSlot, ...]
    summary: StoreFlightSummary
    transcript_digest: bytes

    @property
    def accepted(self) -> tuple[StoreFlightAction, ...]:
        return tuple(action for action in self.actions if action.accepted)

    @property
    def refused(self) -> tuple[StoreFlightAction, ...]:
        return tuple(action for action in self.actions if action.refused)

    @property
    def quarantined(self) -> tuple[StoreFlightAction, ...]:
        return tuple(action for action in self.actions if action.quarantined)

    @property
    def final_bytes(self) -> int:
        return sum(slot.size_bytes for slot in self.final_slots)


def _candidate_sort_key(candidate: StoreCandidate) -> tuple[int, int, int, int, bytes]:
    # Tombstones first, then other control-plane records, then priority, then smaller items.
    control_rank = 0 if candidate.kind is StoreRecordKind.TOMBSTONE else (1 if candidate.control_plane else 2)
    return (control_rank, -candidate.priority, candidate.size_bytes, candidate.expires_at, candidate.record_digest)


def _family_counts(slots: Iterable[StoreSlot]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for slot in slots:
        counts[slot.source_family] = counts.get(slot.source_family, 0) + 1
    return counts


def _bulk_family_counts(slots: Iterable[StoreSlot]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for slot in slots:
        if slot.candidate.bulkish:
            counts[slot.source_family] = counts.get(slot.source_family, 0) + 1
    return counts


def _capacity_ok(slots: Iterable[StoreSlot], *, policy: StoreFlightPolicy) -> bool:
    slots_tuple = tuple(slots)
    return len(slots_tuple) <= policy.max_records and sum(slot.size_bytes for slot in slots_tuple) <= policy.max_bytes


def _control_reserve_ok(candidate: StoreCandidate, slots: Iterable[StoreSlot], *, policy: StoreFlightPolicy) -> bool:
    if candidate.control_plane:
        return True
    slots_tuple = tuple(slots)
    control_records = sum(1 for slot in slots_tuple if slot.control_plane)
    control_bytes = sum(slot.size_bytes for slot in slots_tuple if slot.control_plane)
    record_budget = max(0, policy.max_records - policy.control_plane_reserve_records)
    byte_budget = max(0, policy.max_bytes - policy.control_plane_reserve_bytes)
    # If a local operator reserves more control-plane capacity than the total
    # store can hold, do not make the garden refuse *all* bulk forever while the
    # store is empty.  Capacity and eviction still protect the store, and future
    # control-plane candidates may evict lower-priority bulk.
    record_ok = True if record_budget == 0 and control_records == 0 else control_records < record_budget
    byte_ok = True if byte_budget == 0 and control_bytes == 0 else control_bytes < byte_budget
    return record_ok and byte_ok


def _find_evictions(candidate: StoreCandidate, slots: list[StoreSlot], *, policy: StoreFlightPolicy) -> tuple[StoreSlot, ...]:
    trial = list(slots)
    evicted: list[StoreSlot] = []
    # Bulk records may not evict control-plane records in the prototype.
    eviction_pool = [slot for slot in trial if candidate.control_plane or not slot.control_plane]
    for slot in sorted(eviction_pool, key=lambda item: item.evict_rank):
        trial.remove(slot)
        evicted.append(slot)
        if _capacity_ok([*trial, StoreSlot(candidate, 0, 1)], policy=policy):
            return tuple(evicted)
    return ()


def plan_store_flight(
    candidates: Iterable[StoreCandidate],
    *,
    garden_keypair: DhtKeypair,
    garden_node_id: bytes,
    now: int,
    existing_slots: Iterable[StoreSlot] = (),
    tombstoned_digests: Iterable[bytes] = (),
    policy: StoreFlightPolicy | None = None,
    service_window: str = "store-v1",
) -> StoreFlightReport:
    policy = policy or StoreFlightPolicy()
    policy.validate()
    tombstoned = set(tombstoned_digests)
    slots = list(existing_slots)
    actions: list[StoreFlightAction] = []
    evicted_all: list[StoreSlot] = []

    for candidate in sorted(tuple(candidates), key=_candidate_sort_key):
        if candidate.size_bytes > policy.max_candidate_size:
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.REJECT_INVALID, False, "candidate exceeds maximum single-record size"))
            continue
        if not candidate.live(now=now, policy=policy):
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.REJECT_EXPIRED, False, "candidate is expired, premature, or too close to expiry"))
            continue
        if not candidate.proof_ok:
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.QUARANTINE_BAD_PROOF, False, "candidate failed proof/signature/semantic precondition"))
            continue
        if candidate.record_digest in tombstoned or candidate.tombstone_target in tombstoned:
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.QUARANTINE_TOMBSTONED, False, "candidate conflicts with live tombstone evidence"))
            continue

        family_counts = _family_counts(slots)
        bulk_counts = _bulk_family_counts(slots)
        if family_counts.get(candidate.source_family, 0) >= policy.max_per_source_family:
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.REFUSE_FAMILY_CAP, False, "source family store cap reached"))
            continue
        if candidate.bulkish and bulk_counts.get(candidate.source_family, 0) >= policy.max_bulk_per_source_family:
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.REFUSE_FAMILY_CAP, False, "source family bulk store cap reached"))
            continue
        if not _control_reserve_ok(candidate, slots, policy=policy):
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.REFUSE_OVER_BUDGET, False, "bulk record would consume control-plane reserve"))
            continue

        proposed_slot = StoreSlot(candidate, now, min(candidate.expires_at, now + policy.custody_ttl), now)
        if _capacity_ok([*slots, proposed_slot], policy=policy):
            receipt = CustodyReceipt.create(garden_keypair=garden_keypair, garden_node_id=garden_node_id, candidate=candidate, accepted_at=now, custody_until=proposed_slot.custody_until, service_window=service_window)
            slots.append(proposed_slot)
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.ACCEPT_STORE, True, "record admitted within current budget", receipt=receipt))
            continue

        evictions = _find_evictions(candidate, slots, policy=policy)
        if not evictions:
            actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.REFUSE_OVER_BUDGET, False, "no safe eviction set can fit candidate"))
            continue
        for evicted in evictions:
            slots.remove(evicted)
        evicted_all.extend(evictions)
        receipt = CustodyReceipt.create(garden_keypair=garden_keypair, garden_node_id=garden_node_id, candidate=candidate, accepted_at=now, custody_until=proposed_slot.custody_until, service_window=service_window)
        slots.append(proposed_slot)
        actions.append(StoreFlightAction(candidate, StoreFlightDecisionKind.ACCEPT_WITH_EVICTION, True, "record admitted after evicting lower-priority storage", tuple(evictions), receipt))

    if not any(action.accepted for action in actions):
        summary = StoreFlightSummary(StoreFlightSummaryKind.NO_ACCEPTED_RECORDS, False, "no candidates were accepted")
    elif any(action.quarantined for action in actions):
        summary = StoreFlightSummary(StoreFlightSummaryKind.QUARANTINE_PRESSURE, False, "some candidates were quarantined while store flight continued")
    elif any(action.refused for action in actions):
        summary = StoreFlightSummary(StoreFlightSummaryKind.STORED_WITH_REFUSALS, True, "accepted bounded work and issued useful refusals")
    elif evicted_all:
        summary = StoreFlightSummary(StoreFlightSummaryKind.CONTROL_PLANE_PROTECTED, True, "accepted work after protecting higher-priority storage")
    else:
        summary = StoreFlightSummary(StoreFlightSummaryKind.STORED_ALL, True, "all candidates accepted")

    digest = sha256(STORE_FLIGHT_DOMAIN + b":report:" + bencode({
        b"now": now,
        b"actions": [action.bvalue() for action in actions],
        b"final_slots": [slot.bvalue() for slot in slots],
        b"summary": summary.kind.value,
    }))
    return StoreFlightReport(tuple(actions), tuple(slots), tuple(evicted_all), summary, digest)
