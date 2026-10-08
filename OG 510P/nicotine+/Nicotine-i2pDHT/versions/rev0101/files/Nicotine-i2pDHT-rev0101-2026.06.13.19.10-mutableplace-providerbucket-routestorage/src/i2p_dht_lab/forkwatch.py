"""Mutable-head fork, rollback, and witness primitives.

This module attacks the riskiest mutability guess first: a DHT can carry small
signed mutable heads, but readers need local memory and witnesses to avoid being
quietly rolled back or split-brained by stale replicas, malicious stores, or a
publisher that equivocates.

The implementation is intentionally a lab surface, not production consensus. It
keeps local highest-seen sequence memory, records same-sequence forks as evidence,
and produces signed witness receipts that gardens or clients can share as
*evidence*, not truth authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .mutable import MutableRecord

FORKWATCH_DOMAIN = DOMAIN + b":forkwatch-v1:"
MAX_RECEIPT_RECORD_HASHES = 8
MAX_RECEIPT_NOTE_BYTES = 240


class ObservationSource(str, Enum):
    LOCAL_STORE = "local_store"
    LOOKUP_REPLY = "lookup_reply"
    LOOKUP_QUORUM = "lookup_quorum"
    GARDEN_WITNESS = "garden_witness"
    SEED_HEAD = "seed_head"
    POLICY_HEAD = "policy_head"
    BRIDGE_REPLY = "bridge_reply"


class HeadVerdictKind(str, Enum):
    ACCEPT_FRESH = "accept_fresh"
    ACCEPT_REFRESH = "accept_refresh"
    STALE_VALID = "stale_valid"
    SAME_SEQ_FORK = "same_seq_fork"
    INVALID_SIGNATURE = "invalid_signature"
    EXPIRED_RECORD = "expired_record"
    TARGET_MISMATCH = "target_mismatch"


class WitnessKind(str, Enum):
    HIGHEST_SEEN = "highest_seen"
    ROLLBACK_SEEN = "rollback_seen"
    SAME_SEQ_FORK_SEEN = "same_seq_fork_seen"
    INVALID_RECORD_SEEN = "invalid_record_seen"
    STALE_REPLICA_SEEN = "stale_replica_seen"


def mutable_record_digest(record: MutableRecord) -> bytes:
    """Hash the verifiable identity of a mutable record version."""
    return sha256(
        FORKWATCH_DOMAIN
        + b":record-digest:"
        + record.public_key
        + record.salt
        + record.seq.to_bytes(8, "big", signed=False)
        + bencode(record.value)
        + record.signature
    )


def mutable_slot_key(record: MutableRecord) -> bytes:
    """Return the native 256-bit mutable-slot key used by this lab."""
    return record.target_i2p256


@dataclass(frozen=True)
class MutableHeadObservation:
    record: MutableRecord
    observer_node_id: bytes
    source: ObservationSource
    at: int
    path_id: bytes = b""
    source_note: str = ""

    @property
    def target(self) -> bytes:
        return mutable_slot_key(self.record)

    @property
    def record_hash(self) -> bytes:
        return mutable_record_digest(self.record)

    def validate_shape(self, *, now: int) -> HeadVerdictKind | None:
        if self.record.target_i2p256 != self.target:
            return HeadVerdictKind.TARGET_MISMATCH
        if not self.record.verify():
            return HeadVerdictKind.INVALID_SIGNATURE
        if self.record.is_expired(now):
            return HeadVerdictKind.EXPIRED_RECORD
        return None


@dataclass(frozen=True)
class HeadVerdict:
    kind: HeadVerdictKind
    target: bytes
    seq: int
    record_hash: bytes
    previous_highest_seq: int | None = None
    highest_seq: int | None = None
    fork_hashes: tuple[bytes, ...] = ()
    reason: str = ""

    @property
    def is_alarm(self) -> bool:
        return self.kind in {
            HeadVerdictKind.SAME_SEQ_FORK,
            HeadVerdictKind.INVALID_SIGNATURE,
            HeadVerdictKind.TARGET_MISMATCH,
        }

    @property
    def is_rollbackish(self) -> bool:
        return self.kind is HeadVerdictKind.STALE_VALID


@dataclass(frozen=True)
class HeadForkEvidence:
    target: bytes
    seq: int
    record_hashes: tuple[bytes, ...]
    first_seen_at: int
    last_seen_at: int
    observer_node_ids: tuple[bytes, ...] = ()

    def with_observation(self, observation: MutableHeadObservation) -> "HeadForkEvidence":
        hashes = tuple(sorted(set(self.record_hashes + (observation.record_hash,))))
        observers = tuple(sorted(set(self.observer_node_ids + (observation.observer_node_id,))))
        return replace(
            self,
            record_hashes=hashes,
            last_seen_at=max(self.last_seen_at, observation.at),
            observer_node_ids=observers,
        )


@dataclass(frozen=True)
class WitnessReceipt:
    """Signed observation receipt for mutable-head history.

    Receipts are not votes and not consensus. They let another client learn that
    some witness claims to have seen a particular highest sequence, stale value,
    invalid record, or same-sequence fork.
    """

    witness_public_key: bytes
    witness_node_id: bytes
    kind: WitnessKind
    target: bytes
    subject_public_key: bytes
    salt: bytes
    highest_seq: int
    observed_seq: int
    record_hashes: tuple[bytes, ...]
    issued_at: int
    expires_at: int
    note: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        witness_keypair: DhtKeypair,
        witness_node_id: bytes,
        kind: WitnessKind,
        target: bytes,
        subject_public_key: bytes,
        salt: bytes,
        highest_seq: int,
        observed_seq: int,
        record_hashes: Iterable[bytes],
        issued_at: int,
        ttl: int = 6 * 3600,
        note: str = "",
    ) -> "WitnessReceipt":
        hashes = tuple(record_hashes)[:MAX_RECEIPT_RECORD_HASHES]
        receipt = cls(
            witness_public_key=witness_keypair.public_key_bytes,
            witness_node_id=witness_node_id,
            kind=kind,
            target=target,
            subject_public_key=subject_public_key,
            salt=salt,
            highest_seq=highest_seq,
            observed_seq=observed_seq,
            record_hashes=hashes,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            note=note[:MAX_RECEIPT_NOTE_BYTES],
        )
        return replace(receipt, signature=witness_keypair.sign(receipt.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"witness_public_key": self.witness_public_key,
            b"witness_node_id": self.witness_node_id,
            b"target": self.target,
            b"subject_public_key": self.subject_public_key,
            b"salt": self.salt,
            b"highest_seq": self.highest_seq,
            b"observed_seq": self.observed_seq,
            b"record_hashes": self.record_hashes,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return FORKWATCH_DOMAIN + b":witness-receipt:" + bencode(self.bvalue())

    @property
    def receipt_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self, *, now: int | None = None) -> bool:
        if len(self.witness_public_key) != 32 or len(self.signature) != 64:
            return False
        if len(self.witness_node_id) != 32 or len(self.target) != 32:
            return False
        if len(self.subject_public_key) != 32:
            return False
        if self.highest_seq < self.observed_seq and self.kind is not WitnessKind.INVALID_RECORD_SEEN:
            return False
        if self.expires_at <= self.issued_at:
            return False
        if len(self.note.encode("utf-8")) > MAX_RECEIPT_NOTE_BYTES:
            return False
        if len(self.record_hashes) > MAX_RECEIPT_RECORD_HASHES:
            return False
        if now is not None and now >= self.expires_at:
            return False
        return verify_signature(self.witness_public_key, self.unsigned_payload(), self.signature)


@dataclass
class MutableHeadMemory:
    """Local monotonic memory for mutable slots."""

    highest_seq_by_target: dict[bytes, int] = field(default_factory=dict)
    best_hash_by_target: dict[bytes, bytes] = field(default_factory=dict)
    versions_by_target_seq: dict[tuple[bytes, int], set[bytes]] = field(default_factory=dict)
    forks: dict[tuple[bytes, int], HeadForkEvidence] = field(default_factory=dict)
    observations: list[MutableHeadObservation] = field(default_factory=list)
    receipts: list[WitnessReceipt] = field(default_factory=list)

    def observe(self, observation: MutableHeadObservation, *, now: int) -> HeadVerdict:
        invalid = observation.validate_shape(now=now)
        target = observation.target
        seq = observation.record.seq
        record_hash = observation.record_hash
        previous_highest = self.highest_seq_by_target.get(target)

        if invalid is not None:
            return HeadVerdict(invalid, target, seq, record_hash, previous_highest, previous_highest, reason=invalid.value)

        self.observations.append(observation)
        seen_hashes = self.versions_by_target_seq.setdefault((target, seq), set())
        seen_hashes.add(record_hash)

        if len(seen_hashes) > 1:
            key = (target, seq)
            evidence = self.forks.get(key)
            if evidence is None:
                evidence = HeadForkEvidence(
                    target=target,
                    seq=seq,
                    record_hashes=tuple(sorted(seen_hashes)),
                    first_seen_at=observation.at,
                    last_seen_at=observation.at,
                    observer_node_ids=(observation.observer_node_id,),
                )
            else:
                evidence = evidence.with_observation(observation)
            self.forks[key] = evidence
            self.highest_seq_by_target[target] = max(seq, previous_highest if previous_highest is not None else seq)
            return HeadVerdict(
                HeadVerdictKind.SAME_SEQ_FORK,
                target,
                seq,
                record_hash,
                previous_highest,
                self.highest_seq_by_target[target],
                fork_hashes=tuple(sorted(seen_hashes)),
                reason="same sequence signed different values",
            )

        if previous_highest is None or seq > previous_highest:
            self.highest_seq_by_target[target] = seq
            self.best_hash_by_target[target] = record_hash
            return HeadVerdict(
                HeadVerdictKind.ACCEPT_FRESH,
                target,
                seq,
                record_hash,
                previous_highest,
                seq,
                reason="new highest sequence",
            )

        if seq == previous_highest:
            self.best_hash_by_target.setdefault(target, record_hash)
            return HeadVerdict(
                HeadVerdictKind.ACCEPT_REFRESH,
                target,
                seq,
                record_hash,
                previous_highest,
                previous_highest,
                reason="refresh of current highest sequence",
            )

        return HeadVerdict(
            HeadVerdictKind.STALE_VALID,
            target,
            seq,
            record_hash,
            previous_highest,
            previous_highest,
            reason="valid record lower than local highest seen sequence",
        )

    def kind_for_verdict(self, verdict: HeadVerdict) -> WitnessKind:
        if verdict.kind is HeadVerdictKind.SAME_SEQ_FORK:
            return WitnessKind.SAME_SEQ_FORK_SEEN
        if verdict.kind is HeadVerdictKind.STALE_VALID:
            return WitnessKind.ROLLBACK_SEEN
        if verdict.kind in {HeadVerdictKind.INVALID_SIGNATURE, HeadVerdictKind.TARGET_MISMATCH, HeadVerdictKind.EXPIRED_RECORD}:
            return WitnessKind.INVALID_RECORD_SEEN
        return WitnessKind.HIGHEST_SEEN

    def make_receipt(
        self,
        *,
        verdict: HeadVerdict,
        record: MutableRecord,
        witness_keypair: DhtKeypair,
        witness_node_id: bytes,
        issued_at: int,
        note: str = "",
    ) -> WitnessReceipt:
        highest = self.highest_seq_by_target.get(verdict.target, verdict.seq)
        hashes = verdict.fork_hashes if verdict.fork_hashes else (verdict.record_hash,)
        receipt = WitnessReceipt.create(
            witness_keypair=witness_keypair,
            witness_node_id=witness_node_id,
            kind=self.kind_for_verdict(verdict),
            target=verdict.target,
            subject_public_key=record.public_key,
            salt=record.salt,
            highest_seq=highest,
            observed_seq=record.seq,
            record_hashes=hashes,
            issued_at=issued_at,
            note=note or verdict.reason,
        )
        self.receipts.append(receipt)
        return receipt


def select_best_mutable_record(records: Iterable[MutableRecord]) -> MutableRecord | None:
    """Select the highest valid mutable record deterministically.

    This is deliberately weaker than consensus. It is the validator/select hook
    for a lookup result set: discard invalid records, choose the highest seq,
    and break same-seq ties by digest only so the caller can still notice forks.
    """
    valid = [record for record in records if record.verify()]
    if not valid:
        return None
    return max(valid, key=lambda record: (record.seq, mutable_record_digest(record)))


def receipts_for_target(receipts: Iterable[WitnessReceipt], target: bytes, *, now: int) -> tuple[WitnessReceipt, ...]:
    return tuple(receipt for receipt in receipts if receipt.target == target and receipt.verify(now=now))
