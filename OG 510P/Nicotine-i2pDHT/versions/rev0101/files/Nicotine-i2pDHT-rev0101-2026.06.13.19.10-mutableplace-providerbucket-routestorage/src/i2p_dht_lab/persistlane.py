"""Crash/reload pressure for local DHT evidence lanes.

A DHT over I2P will lean heavily on local memory: highest-seen mutable heads,
revocations, tombstones, route leases, witness receipts, custody challenges, and
provider probes.  That memory is a safety boundary.  If a restart silently drops
hard negative evidence, accepts a lower persisted sequence, or reloads a forked
snapshot as authoritative, the node can be tricked into resurrecting old state.

This module is still a toy local model.  It does not define a production disk
format.  It tests the dangerous shape first: signed canonical snapshots,
monotonic previous-digest links, compaction that preserves hard negatives, and
parse-guarded reload before any persisted bytes are trusted.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .parseguard import ParseGuardError, bdecode_guarded

PERSIST_LANE_DOMAIN = DOMAIN + b":persist-lane-v1:"
ZERO_DIGEST = b"\x00" * 32


class PersistRecordKind(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    TOMBSTONE = "tombstone"
    REVOCATION = "revocation"
    PROVIDER_TRUE = "provider_true"
    PROVIDER_FALSE = "provider_false"
    WITNESS_RECEIPT = "witness_receipt"
    CONTACT_LEASE = "contact_lease"
    CUSTODY_PROOF = "custody_proof"


HARD_NEGATIVE_KINDS = frozenset({
    PersistRecordKind.TOMBSTONE,
    PersistRecordKind.REVOCATION,
    PersistRecordKind.PROVIDER_FALSE,
})

POSITIVE_KINDS = frozenset({
    PersistRecordKind.MUTABLE_HEAD,
    PersistRecordKind.PROVIDER_TRUE,
    PersistRecordKind.WITNESS_RECEIPT,
    PersistRecordKind.CONTACT_LEASE,
    PersistRecordKind.CUSTODY_PROOF,
})


class PersistLoadDecisionKind(str, Enum):
    ACCEPT_RELOADED_STATE = "accept_reloaded_state"
    ACCEPT_COMPACTED_WITH_NEGATIVES = "accept_compacted_with_negatives"
    CONTINUE_NEEDS_REPAIR = "continue_needs_repair"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_PARSE_ERROR = "quarantine_parse_error"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREV_MISMATCH = "quarantine_prev_mismatch"
    QUARANTINE_HARD_NEGATIVE_DROPPED = "quarantine_hard_negative_dropped"
    EMPTY_NO_SNAPSHOT = "empty_no_snapshot"


@dataclass(frozen=True)
class PersistRecord:
    kind: PersistRecordKind
    scope_id: bytes
    subject_digest: bytes
    value_digest: bytes
    sequence: int
    source_family: str
    path_family: str
    issued_at: int
    expires_at: int
    byte_cost: int = 128

    def __post_init__(self) -> None:
        for name, value in (("scope_id", self.scope_id), ("subject_digest", self.subject_digest), ("value_digest", self.value_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0 or self.byte_cost <= 0:
            raise ValueError("persist record counters invalid")
        if not self.source_family or not self.path_family:
            raise ValueError("persist record needs source/path family hints")
        if self.expires_at <= self.issued_at:
            raise ValueError("persist record expires_at must follow issued_at")

    @property
    def object_key(self) -> tuple[PersistRecordKind, bytes, bytes]:
        return (self.kind, self.scope_id, self.subject_digest)

    @property
    def is_hard_negative(self) -> bool:
        return self.kind in HARD_NEGATIVE_KINDS

    @property
    def record_digest(self) -> bytes:
        return sha256(PERSIST_LANE_DOMAIN + b":record:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"scope_id": self.scope_id,
            b"subject_digest": self.subject_digest,
            b"value_digest": self.value_digest,
            b"sequence": self.sequence,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"byte_cost": self.byte_cost,
        }

    @classmethod
    def from_bvalue(cls, value: dict[bytes, BValue]) -> "PersistRecord":
        try:
            return cls(
                kind=PersistRecordKind(value[b"kind"].decode("utf-8") if isinstance(value[b"kind"], bytes) else value[b"kind"]),
                scope_id=value[b"scope_id"],  # type: ignore[arg-type]
                subject_digest=value[b"subject_digest"],  # type: ignore[arg-type]
                value_digest=value[b"value_digest"],  # type: ignore[arg-type]
                sequence=value[b"sequence"],  # type: ignore[arg-type]
                source_family=value[b"source_family"].decode("utf-8") if isinstance(value[b"source_family"], bytes) else value[b"source_family"],
                path_family=value[b"path_family"].decode("utf-8") if isinstance(value[b"path_family"], bytes) else value[b"path_family"],
                issued_at=value[b"issued_at"],  # type: ignore[arg-type]
                expires_at=value[b"expires_at"],  # type: ignore[arg-type]
                byte_cost=value[b"byte_cost"],  # type: ignore[arg-type]
            )
        except Exception as exc:  # pragma: no cover - defensive parser boundary
            raise ValueError("invalid persist record bvalue") from exc


@dataclass(frozen=True)
class PersistSnapshot:
    node_public_key: bytes
    sequence: int
    prev_snapshot_digest: bytes
    records: tuple[PersistRecord, ...]
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.node_public_key) != 32 or len(self.prev_snapshot_digest) != 32:
            raise ValueError("persist snapshot keys/digests must be 32 bytes")
        if self.sequence < 0 or self.expires_at <= self.issued_at:
            raise ValueError("persist snapshot counters invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        sequence: int,
        prev_snapshot_digest: bytes,
        records: Iterable[PersistRecord],
        issued_at: int,
        ttl: int = 86_400,
    ) -> "PersistSnapshot":
        if ttl <= 0:
            raise ValueError("persist snapshot ttl must be positive")
        unsigned = cls(
            node_public_key=keypair.public_key_bytes,
            sequence=sequence,
            prev_snapshot_digest=prev_snapshot_digest,
            records=tuple(records),
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def snapshot_digest(self) -> bytes:
        return sha256(PERSIST_LANE_DOMAIN + b":snapshot:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"node_public_key": self.node_public_key,
            b"sequence": self.sequence,
            b"prev_snapshot_digest": self.prev_snapshot_digest,
            b"records": [record.bvalue() for record in self.records],
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return PERSIST_LANE_DOMAIN + b":snapshot-unsigned:" + bencode(self.unsigned_bvalue())

    def to_bytes(self) -> bytes:
        return bencode({
            b"unsigned": self.unsigned_bvalue(),
            b"signature": self.signature,
        })

    @classmethod
    def from_bytes(cls, data: bytes) -> "PersistSnapshot":
        parsed = bdecode_guarded(data).expect_dict()
        unsigned = parsed.get(b"unsigned")
        signature = parsed.get(b"signature")
        if not isinstance(unsigned, dict) or not isinstance(signature, bytes):
            raise ValueError("persist snapshot bytes need unsigned dict and signature")
        records_value = unsigned.get(b"records")
        if not isinstance(records_value, list):
            raise ValueError("persist snapshot records must be a list")
        records = tuple(PersistRecord.from_bvalue(item) for item in records_value if isinstance(item, dict))
        if len(records) != len(records_value):
            raise ValueError("persist snapshot record list contains non-dict item")
        return cls(
            node_public_key=unsigned[b"node_public_key"],  # type: ignore[arg-type]
            sequence=unsigned[b"sequence"],  # type: ignore[arg-type]
            prev_snapshot_digest=unsigned[b"prev_snapshot_digest"],  # type: ignore[arg-type]
            records=records,
            issued_at=unsigned[b"issued_at"],  # type: ignore[arg-type]
            expires_at=unsigned[b"expires_at"],  # type: ignore[arg-type]
            signature=signature,
        )

    def verify(self, *, now: int) -> bool:
        if now < self.issued_at or now >= self.expires_at:
            return False
        return verify_signature(self.node_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class PersistLoadPolicy:
    max_records: int = 512
    max_total_bytes: int = 128_000
    require_hard_negative_preservation: bool = True

    def validate(self) -> None:
        if self.max_records <= 0 or self.max_total_bytes <= 0:
            raise ValueError("persist load policy invalid")


@dataclass(frozen=True)
class PersistLoadReport:
    decision_kind: PersistLoadDecisionKind
    accept: bool
    reason: str
    loaded: PersistSnapshot | None
    compacted_records: tuple[PersistRecord, ...]
    quarantine_digests: tuple[bytes, ...]
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _compact_records(records: Iterable[PersistRecord], *, max_records: int) -> tuple[PersistRecord, ...]:
    by_key: dict[tuple[PersistRecordKind, bytes, bytes], PersistRecord] = {}
    hard_negatives: list[PersistRecord] = []
    for record in records:
        current = by_key.get(record.object_key)
        if current is None or (record.sequence, record.expires_at, record.record_digest) > (current.sequence, current.expires_at, current.record_digest):
            by_key[record.object_key] = record
        if record.is_hard_negative:
            hard_negatives.append(record)
    selected = list(by_key.values())
    # Hard negatives get a second preservation pass in case a byte/record budget
    # would otherwise prefer a convenient positive record with a later expiry.
    selected_keys = {record.record_digest for record in selected}
    for record in hard_negatives:
        if record.record_digest not in selected_keys:
            selected.append(record)
            selected_keys.add(record.record_digest)
    selected.sort(key=lambda item: (not item.is_hard_negative, -item.sequence, item.kind.value, item.subject_digest))
    return tuple(selected[:max_records])


def assess_persist_reload(
    snapshot_bytes: bytes | None,
    *,
    previous_snapshot: PersistSnapshot | None,
    now: int,
    policy: PersistLoadPolicy | None = None,
) -> PersistLoadReport:
    policy = policy or PersistLoadPolicy()
    policy.validate()
    quarantine: list[bytes] = []
    loaded: PersistSnapshot | None = None
    compacted: tuple[PersistRecord, ...] = ()
    if snapshot_bytes is None:
        decision = PersistLoadDecisionKind.EMPTY_NO_SNAPSHOT
        reason = "no persisted snapshot bytes were supplied"
        accept = True
    else:
        try:
            loaded = PersistSnapshot.from_bytes(snapshot_bytes)
        except (ValueError, ParseGuardError):
            decision = PersistLoadDecisionKind.QUARANTINE_PARSE_ERROR
            reason = "persisted bytes failed parseguard or snapshot structure checks"
            accept = False
        else:
            if not loaded.verify(now=now):
                quarantine.append(loaded.snapshot_digest)
                decision = PersistLoadDecisionKind.QUARANTINE_BAD_SIGNATURE
                reason = "persisted snapshot signature or time window is invalid"
                accept = False
            elif previous_snapshot is not None and loaded.sequence < previous_snapshot.sequence:
                quarantine.append(loaded.snapshot_digest)
                decision = PersistLoadDecisionKind.QUARANTINE_ROLLBACK
                reason = "persisted snapshot sequence rolls back local memory"
                accept = False
            elif previous_snapshot is not None and loaded.sequence == previous_snapshot.sequence and loaded.snapshot_digest != previous_snapshot.snapshot_digest:
                quarantine.append(loaded.snapshot_digest)
                decision = PersistLoadDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
                reason = "same-sequence persisted snapshot forked local memory"
                accept = False
            elif previous_snapshot is not None and loaded.sequence > previous_snapshot.sequence and loaded.prev_snapshot_digest != previous_snapshot.snapshot_digest:
                quarantine.append(loaded.snapshot_digest)
                decision = PersistLoadDecisionKind.QUARANTINE_PREV_MISMATCH
                reason = "persisted snapshot does not link to previous local snapshot"
                accept = False
            else:
                total_bytes = sum(record.byte_cost for record in loaded.records)
                compacted = _compact_records(loaded.records, max_records=policy.max_records)
                compacted_bytes = sum(record.byte_cost for record in compacted)
                previous_hard = set()
                if previous_snapshot is not None:
                    previous_hard = {record.object_key for record in previous_snapshot.records if record.is_hard_negative}
                loaded_hard = {record.object_key for record in compacted if record.is_hard_negative}
                if policy.require_hard_negative_preservation and previous_hard and not previous_hard.issubset(loaded_hard):
                    decision = PersistLoadDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED
                    reason = "persisted compaction would drop hard negative evidence known before restart"
                    accept = False
                elif len(loaded.records) > policy.max_records or total_bytes > policy.max_total_bytes or compacted_bytes != total_bytes:
                    decision = PersistLoadDecisionKind.ACCEPT_COMPACTED_WITH_NEGATIVES
                    reason = "persisted snapshot accepted after local compaction; hard negatives preserved"
                    accept = True
                else:
                    decision = PersistLoadDecisionKind.ACCEPT_RELOADED_STATE
                    reason = "persisted snapshot is signed, linked, parse-safe, and locally compact"
                    accept = True
    hard_negative_count = sum(1 for record in compacted if record.is_hard_negative)
    digest = sha256(PERSIST_LANE_DOMAIN + b":load-report:" + bencode({
        b"decision": decision.value,
        b"accept": 1 if accept else 0,
        b"loaded": b"" if loaded is None else loaded.snapshot_digest,
        b"compacted": [record.record_digest for record in compacted],
        b"quarantine": sorted(quarantine),
        b"hard_negative_count": hard_negative_count,
    }))
    return PersistLoadReport(decision, accept, reason, loaded, compacted, tuple(sorted(quarantine)), hard_negative_count, digest)
