"""Key succession records for mutable-control-plane keys.

Mutable heads make keys precious. rev0010 starts the hard part early: how does a
publisher rotate a key without turning a single old key into an eternal point of
failure? The conservative lab guess is a co-signed succession record: old key
signs the transfer and new key countersigns acceptance. Local memory rejects
rollback and preserves same-sequence fork evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .mutable import MutableRecord

SUCCESSION_DOMAIN = DOMAIN + b":succession-v1:"


class SuccessionVerdictKind(str, Enum):
    ACCEPT_FIRST = "accept_first"
    ACCEPT_ADVANCE = "accept_advance"
    ACCEPT_REFRESH = "accept_refresh"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_ROLLBACK = "reject_rollback"
    SAME_SEQUENCE_FORK = "same_sequence_fork"


@dataclass(frozen=True)
class KeySuccessionRecord:
    old_public_key: bytes
    new_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    reason: str = "rotation"
    previous_record_hash: bytes = b""
    old_signature: bytes = b""
    new_signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        old_keypair: DhtKeypair,
        new_keypair: DhtKeypair,
        sequence: int,
        issued_at: int,
        ttl: int,
        reason: str = "rotation",
        previous_record_hash: bytes = b"",
    ) -> "KeySuccessionRecord":
        record = cls(
            old_public_key=old_keypair.public_key_bytes,
            new_public_key=new_keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            reason=reason,
            previous_record_hash=previous_record_hash,
        )
        old_sig = old_keypair.sign(record.unsigned_payload(role=b"old"))
        new_sig = new_keypair.sign(record.unsigned_payload(role=b"new"))
        return replace(record, old_signature=old_sig, new_signature=new_sig)

    def bvalue_unsigned(self) -> dict[bytes, BValue]:
        return {
            b"old": self.old_public_key,
            b"new": self.new_public_key,
            b"seq": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"reason": self.reason,
            b"prev": self.previous_record_hash,
        }

    def unsigned_payload(self, *, role: bytes) -> bytes:
        return SUCCESSION_DOMAIN + b":" + role + b":" + bencode(self.bvalue_unsigned())

    def bvalue(self) -> dict[bytes, BValue]:
        value = dict(self.bvalue_unsigned())
        value[b"old_sig"] = self.old_signature
        value[b"new_sig"] = self.new_signature
        return value

    @property
    def record_hash(self) -> bytes:
        return sha256(SUCCESSION_DOMAIN + b":record-hash:" + bencode(self.bvalue()))

    def verify(self, *, now: int | None = None) -> bool:
        if len(self.old_public_key) != 32 or len(self.new_public_key) != 32:
            return False
        if self.sequence < 0 or self.expires_at <= self.issued_at:
            return False
        if now is not None and now >= self.expires_at:
            return False
        return (
            verify_signature(self.old_public_key, self.unsigned_payload(role=b"old"), self.old_signature)
            and verify_signature(self.new_public_key, self.unsigned_payload(role=b"new"), self.new_signature)
        )

    def make_mutable_head(self, *, old_keypair: DhtKeypair, now: int | None = None) -> MutableRecord:
        if old_keypair.public_key_bytes != self.old_public_key:
            raise ValueError("old keypair must sign the succession mutable slot")
        return MutableRecord.create(
            keypair=old_keypair,
            seq=self.sequence,
            value={b"kind": b"key_succession", b"record": self.bvalue(), b"record_hash": self.record_hash},
            salt=b"key-succession:" + self.old_public_key[:16],
            kind="succession.key_rotation",
            now=now or self.issued_at,
            ttl=max(1, self.expires_at - self.issued_at),
        )


@dataclass(frozen=True)
class SuccessionVerdict:
    kind: SuccessionVerdictKind
    old_public_key: bytes
    sequence: int
    known_sequence: int | None
    current_public_key: bytes
    reason: str

    @property
    def accepted(self) -> bool:
        return self.kind in {SuccessionVerdictKind.ACCEPT_FIRST, SuccessionVerdictKind.ACCEPT_ADVANCE, SuccessionVerdictKind.ACCEPT_REFRESH}


@dataclass(frozen=True)
class SuccessionState:
    root_public_key: bytes
    current_public_key: bytes
    highest_sequence: int
    accepted_record_hash: bytes
    fork_hashes: frozenset[bytes] = frozenset()


@dataclass
class SuccessionMemory:
    states: dict[bytes, SuccessionState] = field(default_factory=dict)

    def observe(self, record: KeySuccessionRecord, *, now: int) -> SuccessionVerdict:
        root = record.old_public_key
        current = self.states.get(root)
        known = None if current is None else current.highest_sequence
        if not record.verify(now=now):
            return SuccessionVerdict(SuccessionVerdictKind.REJECT_BAD_SIGNATURE, root, record.sequence, known, b"" if current is None else current.current_public_key, "succession record failed co-signature validation")
        if current is None:
            self.states[root] = SuccessionState(root, record.new_public_key, record.sequence, record.record_hash)
            return SuccessionVerdict(SuccessionVerdictKind.ACCEPT_FIRST, root, record.sequence, None, record.new_public_key, "first accepted succession")
        if record.sequence < current.highest_sequence:
            return SuccessionVerdict(SuccessionVerdictKind.REJECT_ROLLBACK, root, record.sequence, current.highest_sequence, current.current_public_key, "older succession replayed")
        if record.sequence == current.highest_sequence:
            if record.record_hash == current.accepted_record_hash:
                return SuccessionVerdict(SuccessionVerdictKind.ACCEPT_REFRESH, root, record.sequence, current.highest_sequence, current.current_public_key, "same succession refreshed")
            forks = frozenset(set(current.fork_hashes) | {current.accepted_record_hash, record.record_hash})
            self.states[root] = replace(current, fork_hashes=forks)
            return SuccessionVerdict(SuccessionVerdictKind.SAME_SEQUENCE_FORK, root, record.sequence, current.highest_sequence, current.current_public_key, "same succession sequence points at a different new key")
        self.states[root] = SuccessionState(root, record.new_public_key, record.sequence, record.record_hash)
        return SuccessionVerdict(SuccessionVerdictKind.ACCEPT_ADVANCE, root, record.sequence, current.highest_sequence, record.new_public_key, "succession advanced")

    def current_key_for(self, root_public_key: bytes) -> bytes | None:
        state = self.states.get(root_public_key)
        return None if state is None else state.current_public_key

    def observe_many(self, records: Iterable[KeySuccessionRecord], *, now: int) -> tuple[SuccessionVerdict, ...]:
        return tuple(self.observe(record, now=now) for record in records)
