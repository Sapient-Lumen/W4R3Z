"""Storage-lease quorum pressure.

Store receipts are momentary. Long-lived mutable heads, provider manifests,
contact leases, tombstones, and garden catalogs need storage leases that can be
renewed, refused, or allowed to expire without confusing stale evidence for
availability. This module turns that guess into deterministic local policy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .storeflight import StoreClass, StoreRecordKind
from .tombstonecache import TombstoneCache, TombstoneKind

STORAGE_LEASE_DOMAIN = DOMAIN + b":storage-lease-v1:"


class StorageLeaseReceiptKind(str, Enum):
    GRANTED = "granted"
    RENEWED = "renewed"
    REFUSED_CAPACITY = "refused_capacity"
    REFUSED_POLICY = "refused_policy"
    EVICTING = "evicting"


class StorageLeaseDecisionKind(str, Enum):
    LIVE_DIVERSE_LEASES = "live_diverse_leases"
    LIVE_BUT_RENEW_SOON = "live_but_renew_soon"
    CONTINUE_LOW_DIVERSITY = "continue_low_diversity"
    CONTINUE_TOO_FEW_LIVE_LEASES = "continue_too_few_live_leases"
    CONTINUE_RENEWAL_GAP = "continue_renewal_gap"
    BLOCKED_BY_TOMBSTONE = "blocked_by_tombstone"
    QUARANTINE_LEASE_FORK = "quarantine_lease_fork"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"


@dataclass(frozen=True)
class StorageLeaseReceipt:
    storage_node_id: bytes
    storage_public_key: bytes
    family_id: str
    target: bytes
    record_digest: bytes
    record_kind: StoreRecordKind
    store_class: StoreClass
    lease_sequence: int
    kind: StorageLeaseReceiptKind
    issued_at: int
    lease_expires_at: int
    renewal_after: int
    note: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        storage_node_id: bytes,
        family_id: str,
        target: bytes,
        record_digest: bytes,
        record_kind: StoreRecordKind,
        store_class: StoreClass,
        lease_sequence: int,
        kind: StorageLeaseReceiptKind,
        issued_at: int,
        lease_expires_at: int,
        renewal_after: int,
        note: str = "",
    ) -> "StorageLeaseReceipt":
        unsigned = cls(
            storage_node_id=storage_node_id,
            storage_public_key=keypair.public_key_bytes,
            family_id=family_id,
            target=target,
            record_digest=record_digest,
            record_kind=record_kind,
            store_class=store_class,
            lease_sequence=lease_sequence,
            kind=kind,
            issued_at=issued_at,
            lease_expires_at=lease_expires_at,
            renewal_after=renewal_after,
            note=note[:160],
        )
        return cls(**{**unsigned.__dict__, "signature": keypair.sign(unsigned.unsigned_payload())})

    def __post_init__(self) -> None:
        if len(self.storage_node_id) != 32 or len(self.storage_public_key) != 32:
            raise ValueError("storage node id/public key must be 32 bytes")
        if len(self.target) != 32 or len(self.record_digest) != 32:
            raise ValueError("target and record_digest must be 32 bytes")
        if not self.family_id:
            raise ValueError("family_id is required")
        if self.lease_sequence < 0 or self.issued_at < 0 or self.lease_expires_at < 0 or self.renewal_after < 0:
            raise ValueError("lease counters/times must be non-negative")

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"storage_node_id": self.storage_node_id,
            b"storage_public_key": self.storage_public_key,
            b"family_id": self.family_id,
            b"target": self.target,
            b"record_digest": self.record_digest,
            b"record_kind": self.record_kind.value,
            b"store_class": self.store_class.value,
            b"lease_sequence": self.lease_sequence,
            b"kind": self.kind.value,
            b"issued_at": self.issued_at,
            b"lease_expires_at": self.lease_expires_at,
            b"renewal_after": self.renewal_after,
            b"note": self.note,
        })

    @property
    def lease_id(self) -> bytes:
        return sha256(STORAGE_LEASE_DOMAIN + b":lease-id:" + self.storage_node_id + self.target + self.record_digest)

    @property
    def receipt_hash(self) -> bytes:
        return sha256(STORAGE_LEASE_DOMAIN + b":receipt:" + self.unsigned_payload() + self.signature)

    @property
    def live_kind(self) -> bool:
        return self.kind in (StorageLeaseReceiptKind.GRANTED, StorageLeaseReceiptKind.RENEWED)

    def live(self, *, now: int, min_remaining: int = 0) -> bool:
        return self.live_kind and self.issued_at <= now < self.lease_expires_at and self.lease_expires_at >= now + min_remaining

    def verify(self) -> bool:
        return verify_signature(self.storage_public_key, self.unsigned_payload(), self.signature)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"node_id": self.storage_node_id,
            b"family_id": self.family_id,
            b"kind": self.kind.value,
            b"seq": self.lease_sequence,
            b"expires": self.lease_expires_at,
            b"renewal_after": self.renewal_after,
            b"hash": self.receipt_hash,
        }


@dataclass(frozen=True)
class StorageLeasePolicy:
    min_live_leases: int = 4
    min_families: int = 3
    max_per_family: int = 2
    min_remaining_seconds: int = 3_600
    renew_within_seconds: int = 7_200

    def validate(self) -> None:
        if self.min_live_leases <= 0 or self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("lease quorum thresholds must be positive")
        if self.min_remaining_seconds < 0 or self.renew_within_seconds < 0:
            raise ValueError("lease timing thresholds must be non-negative")


@dataclass(frozen=True)
class StorageLeaseDecision:
    kind: StorageLeaseDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class StorageLeaseReport:
    target: bytes
    record_digest: bytes
    live_leases: tuple[StorageLeaseReceipt, ...]
    useful_refusals: tuple[StorageLeaseReceipt, ...]
    invalid_receipts: tuple[StorageLeaseReceipt, ...]
    family_counts: dict[str, int]
    fork_pressure: tuple[tuple[bytes, int], ...]
    renewal_gap_count: int
    decision: StorageLeaseDecision
    transcript_digest: bytes

    @property
    def needs_renewal(self) -> bool:
        return self.decision.kind in (StorageLeaseDecisionKind.LIVE_BUT_RENEW_SOON, StorageLeaseDecisionKind.CONTINUE_RENEWAL_GAP)


@dataclass
class StorageLeaseMemory:
    highest: dict[bytes, StorageLeaseReceipt] = field(default_factory=dict)
    forks: dict[tuple[bytes, int], tuple[bytes, ...]] = field(default_factory=dict)

    def observe(self, receipt: StorageLeaseReceipt) -> None:
        existing = self.highest.get(receipt.lease_id)
        if existing is None or receipt.lease_sequence > existing.lease_sequence:
            self.highest[receipt.lease_id] = receipt
            return
        if receipt.lease_sequence == existing.lease_sequence and receipt.receipt_hash != existing.receipt_hash:
            key = (receipt.lease_id, receipt.lease_sequence)
            hashes = set(self.forks.get(key, ()))
            hashes.update((existing.receipt_hash, receipt.receipt_hash))
            self.forks[key] = tuple(sorted(hashes))


def storage_tombstone_target(target: bytes, record_digest: bytes) -> bytes:
    if len(target) != 32 or len(record_digest) != 32:
        raise ValueError("target and record_digest must be 32 bytes")
    return sha256(STORAGE_LEASE_DOMAIN + b":tombstone-target:" + target + record_digest)


def assess_storage_lease_quorum(
    *,
    target: bytes,
    record_digest: bytes,
    receipts: Iterable[StorageLeaseReceipt],
    now: int,
    policy: StorageLeasePolicy | None = None,
    tombstone_cache: TombstoneCache | None = None,
    memory: StorageLeaseMemory | None = None,
) -> StorageLeaseReport:
    policy = policy or StorageLeasePolicy()
    policy.validate()
    if len(target) != 32 or len(record_digest) != 32:
        raise ValueError("target and record_digest must be 32 bytes")
    memory = memory or StorageLeaseMemory()
    live: list[StorageLeaseReceipt] = []
    refusals: list[StorageLeaseReceipt] = []
    invalid: list[StorageLeaseReceipt] = []
    renewal_gap_count = 0
    bad_signature = False

    tombstone_block = False
    if tombstone_cache is not None:
        live_tombs = tombstone_cache.live_for(storage_tombstone_target(target, record_digest), now=now)
        tombstone_block = any(record.kind in (TombstoneKind.PROVIDER_WITHDRAWN, TombstoneKind.MUTABLE_DELETED, TombstoneKind.KEY_COMPROMISED, TombstoneKind.GRANT_REVOKED) for record in live_tombs)

    for receipt in tuple(receipts):
        if receipt.target != target or receipt.record_digest != record_digest:
            invalid.append(receipt)
            continue
        if not receipt.verify():
            bad_signature = True
            invalid.append(receipt)
            continue
        memory.observe(receipt)
        if receipt.live(now=now, min_remaining=policy.min_remaining_seconds):
            live.append(receipt)
            if receipt.lease_expires_at <= now + policy.renew_within_seconds:
                renewal_gap_count += 1
        elif receipt.live_kind and receipt.lease_expires_at > now:
            renewal_gap_count += 1
            invalid.append(receipt)
        elif receipt.kind in (StorageLeaseReceiptKind.REFUSED_CAPACITY, StorageLeaseReceiptKind.REFUSED_POLICY, StorageLeaseReceiptKind.EVICTING):
            refusals.append(receipt)
        else:
            invalid.append(receipt)

    live_tuple = tuple(sorted(live, key=lambda item: (item.family_id, item.storage_node_id, -item.lease_sequence)))
    diversity = analyze_family_diversity(live_tuple, family_of=lambda item: item.family_id, policy=FamilyDiversityPolicy(min_families=policy.min_families, max_per_family=policy.max_per_family)) if live_tuple else None
    family_counts = diversity.family_counts if diversity is not None else {}
    fork_pressure = tuple(sorted(memory.forks))

    if tombstone_block:
        decision = StorageLeaseDecision(StorageLeaseDecisionKind.BLOCKED_BY_TOMBSTONE, False, "live tombstone blocks lease acceptance")
    elif bad_signature:
        decision = StorageLeaseDecision(StorageLeaseDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad lease signature observed")
    elif fork_pressure:
        decision = StorageLeaseDecision(StorageLeaseDecisionKind.QUARANTINE_LEASE_FORK, False, "same lease sequence fork observed")
    elif len(live_tuple) < policy.min_live_leases:
        decision = StorageLeaseDecision(StorageLeaseDecisionKind.CONTINUE_TOO_FEW_LIVE_LEASES, False, "too few live leases with sufficient remaining lifetime")
    elif len(family_counts) < policy.min_families:
        decision = StorageLeaseDecision(StorageLeaseDecisionKind.CONTINUE_LOW_DIVERSITY, False, "live leases are not family-diverse enough")
    elif renewal_gap_count:
        decision = StorageLeaseDecision(StorageLeaseDecisionKind.LIVE_BUT_RENEW_SOON, True, "lease quorum is live but renewal gap is near")
    else:
        decision = StorageLeaseDecision(StorageLeaseDecisionKind.LIVE_DIVERSE_LEASES, True, "live leases span enough families")

    digest = sha256(STORAGE_LEASE_DOMAIN + b":report:" + bencode({
        b"target": target,
        b"record_digest": record_digest,
        b"live": [item.bvalue() for item in live_tuple],
        b"refusals": [item.bvalue() for item in refusals],
        b"invalid": [item.bvalue() for item in invalid],
        b"forks": [[lease_id, seq] for lease_id, seq in fork_pressure],
        b"decision": decision.kind.value,
    }))
    return StorageLeaseReport(target, record_digest, live_tuple, tuple(refusals), tuple(invalid), family_counts, fork_pressure, renewal_gap_count, decision, digest)
