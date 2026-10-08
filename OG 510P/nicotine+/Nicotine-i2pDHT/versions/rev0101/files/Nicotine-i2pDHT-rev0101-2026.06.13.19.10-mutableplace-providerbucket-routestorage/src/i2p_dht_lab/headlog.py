"""History-aware mutable-head memory and garden witness receipts.

This module is where rev0009 starts testing the riskiest mutability guesses
rather than merely documenting them.  A DHT node may return a valid old mutable
record, or a publisher may equivocate by signing two different values at the
same sequence.  Signature validity is therefore necessary but not sufficient for
"latest enough".

The prototype remains intentionally local and subjective:

* clients remember the highest sequence/digest they have accepted per target;
* app heads may carry a previous-head digest to make history traversable;
* equal-sequence forks and rollback attempts are preserved as evidence;
* garden witnesses sign receipts about observations, but do not become truth.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .mutable import MutableRecord

HEADLOG_DOMAIN = DOMAIN + b":headlog-v1:"
MAX_OBSERVED_EVENTS_PER_TARGET = 256


class HeadVerdictKind(str, Enum):
    ACCEPT_FIRST = "accept_first"
    ACCEPT_ADVANCE = "accept_advance"
    ACCEPT_REFRESH = "accept_refresh"
    ADVANCE_WITH_GAP = "advance_with_gap"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_ROLLBACK = "reject_rollback"
    FORK_SAME_SEQUENCE = "fork_same_sequence"
    REJECT_PREV_MISMATCH = "reject_prev_mismatch"
    SUSPICIOUS_MISSING_PREV = "suspicious_missing_prev"


class WitnessClaimKind(str, Enum):
    OBSERVED_HEAD = "observed_head"
    OBSERVED_ROLLBACK = "observed_rollback"
    OBSERVED_FORK = "observed_fork"
    OBSERVED_PREV_MISMATCH = "observed_prev_mismatch"
    OBSERVED_MISSING_PREV = "observed_missing_prev"


@dataclass(frozen=True)
class VersionedHeadValue:
    """Small app-level value for a history-aware mutable pointer.

    It is deliberately generic.  ``pointer`` can be an infohash, manifest digest,
    seed-manifest digest, feed-tip digest, policy capsule digest, or other compact
    content-addressed reference.  ``prev`` should be the record digest of the
    previously accepted head when the publisher knows it.
    """

    kind: str
    pointer: bytes
    seq: int
    prev: bytes = b""
    manifest_digest: bytes = b""
    note: str = ""

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind,
            b"pointer": self.pointer,
            b"seq": self.seq,
            b"prev": self.prev,
            b"manifest": self.manifest_digest,
            b"note": self.note,
        }

    @classmethod
    def from_record(cls, record: MutableRecord) -> "VersionedHeadValue | None":
        value = record.value
        if not isinstance(value, Mapping):
            return None
        try:
            raw_kind = value[b"kind"] if b"kind" in value else value["kind"]  # type: ignore[index]
            raw_pointer = value[b"pointer"] if b"pointer" in value else value["pointer"]  # type: ignore[index]
            raw_seq = value[b"seq"] if b"seq" in value else value["seq"]  # type: ignore[index]
        except Exception:
            return None
        if isinstance(raw_kind, bytes):
            kind = raw_kind.decode("utf-8", errors="replace")
        elif isinstance(raw_kind, str):
            kind = raw_kind
        else:
            return None
        if not isinstance(raw_pointer, bytes) or not isinstance(raw_seq, int):
            return None
        raw_prev = value.get(b"prev", value.get("prev", b""))  # type: ignore[arg-type]
        raw_manifest = value.get(b"manifest", value.get("manifest", b""))  # type: ignore[arg-type]
        raw_note = value.get(b"note", value.get("note", ""))  # type: ignore[arg-type]
        if not isinstance(raw_prev, bytes) or not isinstance(raw_manifest, bytes):
            return None
        if isinstance(raw_note, bytes):
            note = raw_note.decode("utf-8", errors="replace")
        elif isinstance(raw_note, str):
            note = raw_note
        else:
            note = ""
        return cls(kind=kind, pointer=raw_pointer, seq=raw_seq, prev=raw_prev, manifest_digest=raw_manifest, note=note)


def head_record_digest(record: MutableRecord) -> bytes:
    """Digest all fields that should distinguish two signed head versions."""
    return sha256(HEADLOG_DOMAIN + b"record:" + bencode({
        b"target": bytes.fromhex(record.target_hex),
        b"public_key": record.public_key,
        b"salt": record.salt,
        b"seq": record.seq,
        b"kind": record.kind,
        b"value": record.value,
        b"sig": record.signature,
    }))


def make_versioned_head_record(
    *,
    keypair: DhtKeypair,
    kind: str,
    pointer: bytes,
    seq: int,
    salt: bytes,
    prev: bytes = b"",
    manifest_digest: bytes = b"",
    note: str = "",
    now: int | None = None,
    ttl: int = 2 * 60 * 60,
) -> MutableRecord:
    value = VersionedHeadValue(kind=kind, pointer=pointer, seq=seq, prev=prev, manifest_digest=manifest_digest, note=note)
    return MutableRecord.create(
        keypair=keypair,
        seq=seq,
        value=value.bvalue(),
        salt=salt,
        kind=f"headlog.{kind}",
        now=now,
        ttl=ttl,
    )


@dataclass(frozen=True)
class HeadEvent:
    target_hex: str
    seq: int
    value_digest: bytes
    record_digest: bytes
    source_node_id: bytes
    observed_at: int
    signer_public_key: bytes
    salt: bytes
    prev_digest: bytes = b""

    @classmethod
    def from_record(cls, record: MutableRecord, *, source_node_id: bytes, observed_at: int) -> "HeadEvent":
        versioned = VersionedHeadValue.from_record(record)
        return cls(
            target_hex=record.target_hex,
            seq=record.seq,
            value_digest=sha256(record.encoded_value),
            record_digest=head_record_digest(record),
            source_node_id=source_node_id,
            observed_at=observed_at,
            signer_public_key=record.public_key,
            salt=record.salt,
            prev_digest=b"" if versioned is None else versioned.prev,
        )


@dataclass(frozen=True)
class HeadState:
    target_hex: str
    max_seq: int
    accepted_digest: bytes
    accepted_record_digest: bytes
    signer_public_key: bytes
    last_observed_at: int
    fork_digests_at_max: frozenset[bytes] = frozenset()
    stale_sources: tuple[bytes, ...] = ()
    fork_sources: tuple[bytes, ...] = ()
    event_count: int = 1

    @property
    def forked(self) -> bool:
        return bool(self.fork_digests_at_max)


@dataclass(frozen=True)
class HeadVerdict:
    kind: HeadVerdictKind
    accepted: bool
    target_hex: str
    seq: int
    known_seq: int | None
    reason: str
    event: HeadEvent | None = None

    @property
    def risky(self) -> bool:
        return self.kind in {
            HeadVerdictKind.REJECT_ROLLBACK,
            HeadVerdictKind.FORK_SAME_SEQUENCE,
            HeadVerdictKind.REJECT_PREV_MISMATCH,
            HeadVerdictKind.SUSPICIOUS_MISSING_PREV,
        }


@dataclass
class LocalHeadMemory:
    """Local monotonic memory for mutable heads.

    It is deliberately not a consensus object.  It is a client's or garden's
    private memory used to decide when a valid mutable record is stale, forked,
    suspicious, or an acceptable advance.
    """

    states: dict[str, HeadState] = field(default_factory=dict)
    events: dict[str, list[HeadEvent]] = field(default_factory=dict)

    def observe(
        self,
        record: MutableRecord,
        *,
        source_node_id: bytes,
        observed_at: int | None = None,
        require_prev: bool = False,
    ) -> HeadVerdict:
        if observed_at is None:
            observed_at = int(time.time())
        if not record.verify():
            return HeadVerdict(HeadVerdictKind.REJECT_BAD_SIGNATURE, False, record.target_hex, record.seq, self.states.get(record.target_hex, None).max_seq if record.target_hex in self.states else None, "signature verification failed")
        event = HeadEvent.from_record(record, source_node_id=source_node_id, observed_at=observed_at)
        target_events = self.events.setdefault(record.target_hex, [])
        target_events.append(event)
        if len(target_events) > MAX_OBSERVED_EVENTS_PER_TARGET:
            del target_events[:-MAX_OBSERVED_EVENTS_PER_TARGET]

        current = self.states.get(record.target_hex)
        if current is None:
            if require_prev and record.seq > 0 and not event.prev_digest:
                self.states[record.target_hex] = HeadState(record.target_hex, record.seq, event.value_digest, event.record_digest, record.public_key, observed_at)
                return HeadVerdict(HeadVerdictKind.SUSPICIOUS_MISSING_PREV, True, record.target_hex, record.seq, None, "first observation lacks previous-head digest; accepted but flagged", event)
            self.states[record.target_hex] = HeadState(record.target_hex, record.seq, event.value_digest, event.record_digest, record.public_key, observed_at)
            return HeadVerdict(HeadVerdictKind.ACCEPT_FIRST, True, record.target_hex, record.seq, None, "first accepted head", event)

        if record.seq < current.max_seq:
            stale_sources = current.stale_sources + (source_node_id,)
            self.states[record.target_hex] = replace(current, stale_sources=stale_sources, last_observed_at=observed_at, event_count=current.event_count + 1)
            return HeadVerdict(HeadVerdictKind.REJECT_ROLLBACK, False, record.target_hex, record.seq, current.max_seq, "observed sequence is older than local monotonic floor", event)

        if record.seq == current.max_seq:
            if event.value_digest == current.accepted_digest:
                self.states[record.target_hex] = replace(current, last_observed_at=observed_at, event_count=current.event_count + 1)
                return HeadVerdict(HeadVerdictKind.ACCEPT_REFRESH, True, record.target_hex, record.seq, current.max_seq, "same sequence and digest", event)
            forks = frozenset(set(current.fork_digests_at_max) | {event.value_digest, current.accepted_digest})
            fork_sources = current.fork_sources + (source_node_id,)
            self.states[record.target_hex] = replace(current, fork_digests_at_max=forks, fork_sources=fork_sources, last_observed_at=observed_at, event_count=current.event_count + 1)
            return HeadVerdict(HeadVerdictKind.FORK_SAME_SEQUENCE, False, record.target_hex, record.seq, current.max_seq, "same sequence carries a different value digest", event)

        # record.seq > current.max_seq: possible advance.
        if require_prev:
            if not event.prev_digest:
                self.states[record.target_hex] = replace(current, last_observed_at=observed_at, event_count=current.event_count + 1)
                return HeadVerdict(HeadVerdictKind.SUSPICIOUS_MISSING_PREV, False, record.target_hex, record.seq, current.max_seq, "advance lacks previous-head digest", event)
            if event.prev_digest != current.accepted_record_digest:
                self.states[record.target_hex] = replace(current, last_observed_at=observed_at, event_count=current.event_count + 1)
                return HeadVerdict(HeadVerdictKind.REJECT_PREV_MISMATCH, False, record.target_hex, record.seq, current.max_seq, "advance does not link to locally accepted head", event)

        new_state = HeadState(record.target_hex, record.seq, event.value_digest, event.record_digest, record.public_key, observed_at, event_count=current.event_count + 1)
        self.states[record.target_hex] = new_state
        kind = HeadVerdictKind.ACCEPT_ADVANCE if record.seq == current.max_seq + 1 else HeadVerdictKind.ADVANCE_WITH_GAP
        reason = "monotonic advance" if kind is HeadVerdictKind.ACCEPT_ADVANCE else "advance with sequence gap"
        return HeadVerdict(kind, True, record.target_hex, record.seq, current.max_seq, reason, event)

    def state_for(self, target_hex: str) -> HeadState | None:
        return self.states.get(target_hex)

    def events_for(self, target_hex: str) -> tuple[HeadEvent, ...]:
        return tuple(self.events.get(target_hex, ()))


@dataclass(frozen=True)
class WitnessReceipt:
    witness_public_key: bytes
    target_hex: str
    claim: WitnessClaimKind
    observed_seq: int
    observed_digest: bytes
    known_seq: int | None
    known_digest: bytes
    source_node_id: bytes
    issued_at: int
    note: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        witness_keypair: DhtKeypair,
        verdict: HeadVerdict,
        known_state: HeadState | None,
        issued_at: int,
        note: str = "",
    ) -> "WitnessReceipt":
        if verdict.event is None:
            raise ValueError("cannot create witness receipt without an observation event")
        claim = claim_from_verdict(verdict)
        receipt = cls(
            witness_public_key=witness_keypair.public_key_bytes,
            target_hex=verdict.target_hex,
            claim=claim,
            observed_seq=verdict.seq,
            observed_digest=verdict.event.value_digest,
            known_seq=None if known_state is None else known_state.max_seq,
            known_digest=b"" if known_state is None else known_state.accepted_digest,
            source_node_id=verdict.event.source_node_id,
            issued_at=issued_at,
            note=note,
        )
        return replace(receipt, signature=witness_keypair.sign(receipt.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return HEADLOG_DOMAIN + b"receipt:" + bencode({
            b"witness": self.witness_public_key,
            b"target": self.target_hex,
            b"claim": self.claim.value,
            b"observed_seq": self.observed_seq,
            b"observed_digest": self.observed_digest,
            b"known_seq": -1 if self.known_seq is None else self.known_seq,
            b"known_digest": self.known_digest,
            b"source": self.source_node_id,
            b"issued_at": self.issued_at,
            b"note": self.note,
        })

    @property
    def receipt_hash(self) -> bytes:
        return sha256(HEADLOG_DOMAIN + b"receipt-hash:" + self.unsigned_payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.witness_public_key, self.unsigned_payload(), self.signature)


def claim_from_verdict(verdict: HeadVerdict) -> WitnessClaimKind:
    if verdict.kind is HeadVerdictKind.REJECT_ROLLBACK:
        return WitnessClaimKind.OBSERVED_ROLLBACK
    if verdict.kind is HeadVerdictKind.FORK_SAME_SEQUENCE:
        return WitnessClaimKind.OBSERVED_FORK
    if verdict.kind is HeadVerdictKind.REJECT_PREV_MISMATCH:
        return WitnessClaimKind.OBSERVED_PREV_MISMATCH
    if verdict.kind is HeadVerdictKind.SUSPICIOUS_MISSING_PREV:
        return WitnessClaimKind.OBSERVED_MISSING_PREV
    return WitnessClaimKind.OBSERVED_HEAD


def summarize_receipts(receipts: Iterable[WitnessReceipt]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for receipt in receipts:
        if not receipt.verify():
            summary["invalid"] = summary.get("invalid", 0) + 1
            continue
        summary[receipt.claim.value] = summary.get(receipt.claim.value, 0) + 1
    return summary
