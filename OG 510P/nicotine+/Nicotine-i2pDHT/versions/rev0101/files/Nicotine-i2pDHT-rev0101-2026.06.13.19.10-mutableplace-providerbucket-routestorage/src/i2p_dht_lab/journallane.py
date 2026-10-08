"""Crash-cut journal replay pressure for local DHT state.

``persistlane.py`` signs whole snapshots.  That is useful, but a real node will
also want a small append-only journal between snapshots: mutable-head memories,
tombstones, revocations, provider-false evidence, custody facts, and witness
receipts arrive one at a time.  The hard boundary is restart.

This module is deliberately toy-sized and local.  It tests the dangerous shapes
first: canonical signed entries, monotonic sequence/previous-digest links,
crash-cut tails, same-sequence forks, rollback attempts, and compaction that
keeps hard negative evidence even when soft evidence is old.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .parseguard import ParseGuardError, as_bytes, as_int, as_text, bdecode_guarded
from .persistlane import HARD_NEGATIVE_KINDS, PersistRecord, PersistRecordKind, ZERO_DIGEST

JOURNAL_LANE_DOMAIN = DOMAIN + b":journal-lane-v1:"
ENTRY_SEPARATOR = b"\n--i2p-dht-journal-entry--\n"


class JournalReplayDecisionKind(str, Enum):
    ACCEPT_REPLAYED_PREFIX = "accept_replayed_prefix"
    ACCEPT_REPLAYED_WITH_CRASH_TAIL = "accept_replayed_with_crash_tail"
    ACCEPT_COMPACTED_PREFIX = "accept_compacted_prefix"
    CONTINUE_NEEDS_SNAPSHOT = "continue_needs_snapshot"
    QUARANTINE_PARSE_ERROR = "quarantine_parse_error"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREV_MISMATCH = "quarantine_prev_mismatch"
    EMPTY_NO_ENTRIES = "empty_no_entries"


@dataclass(frozen=True)
class JournalEntry:
    public_key: bytes
    sequence: int
    prev_entry_digest: bytes
    record: PersistRecord
    issued_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.public_key) != 32 or len(self.prev_entry_digest) != 32:
            raise ValueError("journal entry public key/prev digest must be 32 bytes")
        if self.sequence <= 0:
            raise ValueError("journal entry sequence must be positive")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        sequence: int,
        prev_entry_digest: bytes,
        record: PersistRecord,
        issued_at: int,
    ) -> "JournalEntry":
        unsigned = cls(
            public_key=keypair.public_key_bytes,
            sequence=sequence,
            prev_entry_digest=prev_entry_digest,
            record=record,
            issued_at=issued_at,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(JOURNAL_LANE_DOMAIN + b":entry:" + self.unsigned_payload() + self.signature)

    @property
    def object_key(self) -> tuple[PersistRecordKind, bytes, bytes]:
        return self.record.object_key

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"public_key": self.public_key,
            b"sequence": self.sequence,
            b"prev_entry_digest": self.prev_entry_digest,
            b"record": self.record.bvalue(),
            b"issued_at": self.issued_at,
        }

    def unsigned_payload(self) -> bytes:
        return JOURNAL_LANE_DOMAIN + b":entry-unsigned:" + bencode(self.unsigned_bvalue())

    def to_bytes(self) -> bytes:
        return bencode({b"unsigned": self.unsigned_bvalue(), b"signature": self.signature})

    def verify(self) -> bool:
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)

    @classmethod
    def from_bytes(cls, data: bytes) -> "JournalEntry":
        parsed = bdecode_guarded(data).expect_dict()
        unsigned = parsed.get(b"unsigned")
        signature = parsed.get(b"signature")
        if not isinstance(unsigned, dict) or not isinstance(signature, bytes):
            raise ValueError("journal entry needs unsigned dict and signature")
        record_value = unsigned.get(b"record")
        if not isinstance(record_value, dict):
            raise ValueError("journal entry record must be a dict")
        return cls(
            public_key=as_bytes(unsigned, b"public_key", length=32),
            sequence=as_int(unsigned, b"sequence", min_value=1),
            prev_entry_digest=as_bytes(unsigned, b"prev_entry_digest", length=32),
            record=PersistRecord.from_bvalue(record_value),
            issued_at=as_int(unsigned, b"issued_at", min_value=0),
            signature=signature,
        )


@dataclass(frozen=True)
class JournalReplayReport:
    decision_kind: JournalReplayDecisionKind
    accept: bool
    reason: str
    accepted_entries: tuple[JournalEntry, ...]
    quarantined_entry_digests: tuple[bytes, ...]
    last_entry_digest: bytes
    highest_sequence: int
    hard_negative_count: int
    soft_count: int
    crash_tail_bytes: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def encode_journal_stream(entries: Iterable[JournalEntry]) -> bytes:
    return ENTRY_SEPARATOR.join(entry.to_bytes() for entry in entries)


def _split_stream(data: bytes) -> tuple[bytes, ...]:
    if not data:
        return ()
    return tuple(chunk for chunk in data.split(ENTRY_SEPARATOR) if chunk)


def assess_journal_stream(
    data: bytes,
    *,
    previous_entry_digest: bytes = ZERO_DIGEST,
    previous_highest_sequence: int = 0,
    now: int,
    allow_crash_tail: bool = True,
) -> JournalReplayReport:
    if len(previous_entry_digest) != 32 or previous_highest_sequence < 0:
        raise ValueError("journal previous state invalid")
    chunks = _split_stream(data)
    if not chunks:
        decision = JournalReplayDecisionKind.EMPTY_NO_ENTRIES
        digest = sha256(JOURNAL_LANE_DOMAIN + b":report:empty")
        return JournalReplayReport(decision, True, "no journal entries supplied", (), (), previous_entry_digest, previous_highest_sequence, 0, 0, 0, digest)

    accepted: list[JournalEntry] = []
    quarantined: list[bytes] = []
    current_prev = previous_entry_digest
    highest = previous_highest_sequence
    seen_by_sequence: dict[int, bytes] = {}
    crash_tail_bytes = 0
    decision = JournalReplayDecisionKind.ACCEPT_REPLAYED_PREFIX
    accept = True
    reason = "journal replayed as a linked signed prefix"

    for index, chunk in enumerate(chunks):
        try:
            entry = JournalEntry.from_bytes(chunk)
        except (ParseGuardError, ValueError) as exc:
            crash_tail_bytes = len(chunk)
            if allow_crash_tail and index == len(chunks) - 1 and accepted:
                decision = JournalReplayDecisionKind.ACCEPT_REPLAYED_WITH_CRASH_TAIL
                reason = f"journal replayed prefix and ignored crash-cut tail: {type(exc).__name__}"
                break
            decision = JournalReplayDecisionKind.QUARANTINE_PARSE_ERROR
            accept = False
            reason = f"journal parse failed before safe tail boundary: {type(exc).__name__}"
            break
        if not entry.verify():
            quarantined.append(entry.entry_digest)
            decision = JournalReplayDecisionKind.QUARANTINE_BAD_SIGNATURE
            accept = False
            reason = "journal entry signature is invalid"
            break
        if entry.sequence < highest:
            quarantined.append(entry.entry_digest)
            decision = JournalReplayDecisionKind.QUARANTINE_ROLLBACK
            accept = False
            reason = "journal entry sequence rolls back below local memory"
            break
        if entry.sequence == highest and accepted:
            # Duplicate replay of the last accepted entry is tolerated only if it
            # is byte-identical to the last digest already seen in this replay.
            if seen_by_sequence.get(entry.sequence) != entry.entry_digest:
                quarantined.append(entry.entry_digest)
                decision = JournalReplayDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
                accept = False
                reason = "journal has two different entries at the same sequence"
                break
        if entry.sequence in seen_by_sequence and seen_by_sequence[entry.sequence] != entry.entry_digest:
            quarantined.append(entry.entry_digest)
            decision = JournalReplayDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
            accept = False
            reason = "journal has same-sequence fork pressure"
            break
        if entry.prev_entry_digest != current_prev:
            quarantined.append(entry.entry_digest)
            decision = JournalReplayDecisionKind.QUARANTINE_PREV_MISMATCH
            accept = False
            reason = "journal entry previous digest does not match local replay tip"
            break
        if entry.sequence <= previous_highest_sequence:
            quarantined.append(entry.entry_digest)
            decision = JournalReplayDecisionKind.QUARANTINE_ROLLBACK
            accept = False
            reason = "journal entry does not advance beyond previous local sequence"
            break
        accepted.append(entry)
        seen_by_sequence[entry.sequence] = entry.entry_digest
        highest = entry.sequence
        current_prev = entry.entry_digest

    hard_negative_count = sum(1 for entry in accepted if entry.record.kind in HARD_NEGATIVE_KINDS)
    soft_count = len(accepted) - hard_negative_count
    if accept and accepted and decision is JournalReplayDecisionKind.ACCEPT_REPLAYED_PREFIX and soft_count > hard_negative_count and len(accepted) >= 8:
        decision = JournalReplayDecisionKind.CONTINUE_NEEDS_SNAPSHOT
        reason = "journal replayed, but prefix is long enough to request a compacting snapshot"
    digest = sha256(JOURNAL_LANE_DOMAIN + b":report:" + bencode({
        b"decision": decision.value,
        b"accept": 1 if accept else 0,
        b"accepted": [entry.entry_digest for entry in accepted],
        b"quarantined": list(quarantined),
        b"tip": current_prev,
        b"highest": highest,
        b"crash_tail_bytes": crash_tail_bytes,
    }))
    return JournalReplayReport(decision, accept, reason, tuple(accepted), tuple(quarantined), current_prev, highest, hard_negative_count, soft_count, crash_tail_bytes, digest)


def compact_journal_entries(entries: Iterable[JournalEntry], *, now: int, soft_retention_seconds: int = 3600) -> tuple[JournalEntry, ...]:
    """Return latest entries per object while preserving hard negatives.

    This is not a storage engine.  It is a deterministic compaction rule for the
    tests: hard-negative records survive expiry pressure; soft records survive
    only when fresh or newest for their object.
    """
    if soft_retention_seconds <= 0:
        raise ValueError("soft retention must be positive")
    entry_tuple = tuple(entries)
    latest_by_object: dict[tuple[PersistRecordKind, bytes, bytes], JournalEntry] = {}
    for entry in entry_tuple:
        previous = latest_by_object.get(entry.object_key)
        if previous is None or entry.record.sequence > previous.record.sequence:
            latest_by_object[entry.object_key] = entry
    kept: list[JournalEntry] = []
    for entry in entry_tuple:
        if entry.record.kind in HARD_NEGATIVE_KINDS:
            kept.append(entry)
            continue
        if latest_by_object.get(entry.object_key) is entry and entry.record.expires_at >= now - soft_retention_seconds:
            kept.append(entry)
    return tuple(sorted(kept, key=lambda item: item.sequence))
