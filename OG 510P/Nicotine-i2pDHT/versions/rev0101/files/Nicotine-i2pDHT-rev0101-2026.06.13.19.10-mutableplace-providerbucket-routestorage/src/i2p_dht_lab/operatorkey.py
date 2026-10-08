"""Operator-key rotation and recovery pressure.

A garden operator key is powerful local protocol data: it signs intents,
service exits, router-stop plans, and profile cooldowns.  rev0042 tests the
hardest guessed seam first: old-key compromise and new-key succession must not
silently widen authority after restart or emergency freeze.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

OPERATOR_KEY_DOMAIN = DOMAIN + b":operator-key-v1:"
ZERO_DIGEST = b"\x00" * 32


class OperatorKeyNoticeKind(str, Enum):
    ROTATE = "rotate"
    COMPROMISE = "compromise"
    RECOVER = "recover"
    FREEZE_OLD_KEY = "freeze_old_key"


class OperatorKeyDecisionKind(str, Enum):
    ACCEPT_ROTATION = "accept_rotation"
    ACCEPT_COMPROMISE_FREEZE = "accept_compromise_freeze"
    ACCEPT_RECOVERY = "accept_recovery"
    HOLD_NEEDS_COSIGN = "hold_needs_cosign"
    HOLD_NEEDS_WITNESS_DIVERSITY = "hold_needs_witness_diversity"
    HOLD_NEEDS_COMPROMISE_CONTEXT = "hold_needs_compromise_context"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_BAD_SUCCESSOR_SIGNATURE = "quarantine_bad_successor_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_OLD_KEY_DRIFT = "quarantine_old_key_drift"
    QUARANTINE_SUCCESSOR_KEY_DRIFT = "quarantine_successor_key_drift"
    QUARANTINE_SCOPE_WIDENING = "quarantine_scope_widening"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"


@dataclass(frozen=True)
class OperatorKeyNotice:
    profile_id: str
    kind: OperatorKeyNoticeKind
    sequence: int
    previous_notice_digest: bytes
    scope_digest: bytes
    old_operator_key: bytes
    successor_operator_key: bytes
    issued_at: int
    expires_at: int
    hard_negative_digest: bytes = ZERO_DIGEST
    signer_public_key: bytes = b""
    signature: bytes = b""
    successor_signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("operator-key sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("operator key notice must expire after issue")
        for name, value in (
            ("previous_notice_digest", self.previous_notice_digest),
            ("scope_digest", self.scope_digest),
            ("old_operator_key", self.old_operator_key),
            ("successor_operator_key", self.successor_operator_key),
            ("hard_negative_digest", self.hard_negative_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signer_public_key and len(self.signer_public_key) != 32:
            raise ValueError("signer_public_key must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("operator-key signature must be Ed25519-sized")
        if self.successor_signature and len(self.successor_signature) != 64:
            raise ValueError("successor signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"kind": self.kind.value,
            b"seq": self.sequence,
            b"prev": self.previous_notice_digest,
            b"scope": self.scope_digest,
            b"old": self.old_operator_key,
            b"successor": self.successor_operator_key,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"hard_negative": self.hard_negative_digest,
        }

    @property
    def notice_digest(self) -> bytes:
        return sha256(OPERATOR_KEY_DOMAIN + b":notice-digest:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return OPERATOR_KEY_DOMAIN + b":notice-sig:" + bencode(self.unsigned_bvalue())

    def successor_signature_payload(self) -> bytes:
        return OPERATOR_KEY_DOMAIN + b":successor-sig:" + bencode(self.unsigned_bvalue())

    def primary_signature_verifies(self) -> bool:
        expected = self.old_operator_key if self.kind in (OperatorKeyNoticeKind.ROTATE, OperatorKeyNoticeKind.COMPROMISE, OperatorKeyNoticeKind.FREEZE_OLD_KEY) else self.successor_operator_key
        return self.signer_public_key == expected and verify_signature(expected, self.signature_payload(), self.signature)

    def successor_signature_verifies(self) -> bool:
        if not self.successor_signature:
            return False
        return verify_signature(self.successor_operator_key, self.successor_signature_payload(), self.successor_signature)


@dataclass(frozen=True)
class OperatorKeyWitness:
    profile_id: str
    notice_digest: bytes
    family_id: str
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.notice_digest) != 32 or len(self.signer_public_key) != 32:
            raise ValueError("witness digest and signer must be 32 bytes")
        if not self.profile_id or not self.family_id:
            raise ValueError("witness profile and family must be non-empty")
        if self.expires_at <= self.issued_at:
            raise ValueError("operator-key witness expires_at must be after issued_at")
        if self.signature and len(self.signature) != 64:
            raise ValueError("operator-key witness signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {b"profile": self.profile_id, b"notice": self.notice_digest, b"family": self.family_id, b"issued": self.issued_at, b"expires": self.expires_at, b"signer": self.signer_public_key}

    @property
    def witness_digest(self) -> bytes:
        return sha256(OPERATOR_KEY_DOMAIN + b":witness-digest:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return OPERATOR_KEY_DOMAIN + b":witness-sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class OperatorKeyPolicy:
    min_recovery_witness_families: int = 2
    require_successor_cosign_for_rotation: bool = True
    forbid_scope_widening: bool = True


@dataclass(frozen=True)
class OperatorKeyReport:
    decision_kind: OperatorKeyDecisionKind
    accept: bool
    reason: str
    profile_id: str
    accepted_old_key: bytes | None
    accepted_successor_key: bytes | None
    notice_digests: tuple[bytes, ...]
    witness_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_operator_key_notice(
    *,
    signer: DhtKeypair,
    profile_id: str,
    kind: OperatorKeyNoticeKind,
    sequence: int,
    previous_notice_digest: bytes,
    scope_digest: bytes,
    old_operator_key: bytes,
    successor_operator_key: bytes,
    issued_at: int,
    expires_at: int,
    hard_negative_digest: bytes = ZERO_DIGEST,
    successor: DhtKeypair | None = None,
) -> OperatorKeyNotice:
    notice = OperatorKeyNotice(
        profile_id=profile_id,
        kind=kind,
        sequence=sequence,
        previous_notice_digest=previous_notice_digest,
        scope_digest=scope_digest,
        old_operator_key=old_operator_key,
        successor_operator_key=successor_operator_key,
        issued_at=issued_at,
        expires_at=expires_at,
        hard_negative_digest=hard_negative_digest,
        signer_public_key=signer.public_key_bytes,
    )
    primary = signer.sign(notice.signature_payload())
    successor_sig = successor.sign(notice.successor_signature_payload()) if successor is not None else b""
    return replace(notice, signature=primary, successor_signature=successor_sig)


def make_operator_key_witness(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    notice_digest: bytes,
    family_id: str,
    issued_at: int,
    expires_at: int,
) -> OperatorKeyWitness:
    witness = OperatorKeyWitness(profile_id=profile_id, notice_digest=notice_digest, family_id=family_id, issued_at=issued_at, expires_at=expires_at, signer_public_key=keypair.public_key_bytes)
    return replace(witness, signature=keypair.sign(witness.signature_payload()))


def _report(kind: OperatorKeyDecisionKind, accept: bool, reason: str, profile_id: str, notices: Iterable[OperatorKeyNotice], witnesses: Iterable[OperatorKeyWitness]) -> OperatorKeyReport:
    notice_tuple = tuple(sorted(notices, key=lambda item: (item.sequence, item.notice_digest)))
    witness_tuple = tuple(sorted(witnesses, key=lambda item: (item.family_id, item.witness_digest)))
    latest = notice_tuple[-1] if notice_tuple else None
    notice_digests = tuple(sorted(item.notice_digest for item in notice_tuple))
    witness_digests = tuple(sorted(item.witness_digest for item in witness_tuple))
    digest = sha256(OPERATOR_KEY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"old": latest.old_operator_key if latest else b"",
        b"successor": latest.successor_operator_key if latest else b"",
        b"notices": list(notice_digests),
        b"witnesses": list(witness_digests),
    }))
    return OperatorKeyReport(kind, accept, reason, profile_id, latest.old_operator_key if latest else None, latest.successor_operator_key if latest else None, notice_digests, witness_digests, digest)


def assess_operator_key_transition(
    notices: Iterable[OperatorKeyNotice],
    witnesses: Iterable[OperatorKeyWitness],
    *,
    now: int,
    expected_profile_id: str,
    expected_old_operator_key: bytes,
    expected_scope_digest: bytes,
    previous_sequence: int | None = None,
    previous_notice_digest: bytes | None = None,
    previously_seen_notices: Iterable[bytes] = (),
    required_hard_negative_digest: bytes | None = None,
    policy: OperatorKeyPolicy | None = None,
) -> OperatorKeyReport:
    policy = policy or OperatorKeyPolicy()
    notice_tuple = tuple(sorted(notices, key=lambda item: (item.sequence, item.notice_digest)))
    witness_tuple = tuple(sorted(witnesses, key=lambda item: (item.family_id, item.witness_digest)))
    seen = set(previously_seen_notices)
    for notice in notice_tuple:
        if not notice.primary_signature_verifies():
            return _report(OperatorKeyDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad operator-key primary signature", expected_profile_id, notice_tuple, witness_tuple)
        if notice.profile_id != expected_profile_id:
            return _report(OperatorKeyDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "operator-key profile drift", expected_profile_id, notice_tuple, witness_tuple)
        if notice.old_operator_key != expected_old_operator_key and notice.kind in (OperatorKeyNoticeKind.ROTATE, OperatorKeyNoticeKind.COMPROMISE, OperatorKeyNoticeKind.FREEZE_OLD_KEY):
            return _report(OperatorKeyDecisionKind.QUARANTINE_OLD_KEY_DRIFT, False, "old operator key drift", expected_profile_id, notice_tuple, witness_tuple)
        if notice.scope_digest != expected_scope_digest:
            return _report(OperatorKeyDecisionKind.QUARANTINE_SCOPE_WIDENING, False, "scope digest drift/widening", expected_profile_id, notice_tuple, witness_tuple)
        if notice.issued_at > now or notice.expires_at <= now:
            return _report(OperatorKeyDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "operator-key notice expired or future", expected_profile_id, notice_tuple, witness_tuple)
        if notice.notice_digest in seen:
            return _report(OperatorKeyDecisionKind.QUARANTINE_REPLAY, False, "operator-key notice replay", expected_profile_id, notice_tuple, witness_tuple)
    if not notice_tuple:
        return _report(OperatorKeyDecisionKind.HOLD_NEEDS_COMPROMISE_CONTEXT, False, "no operator-key notices", expected_profile_id, notice_tuple, witness_tuple)
    seq_map: dict[int, bytes] = {}
    for notice in notice_tuple:
        previous = seq_map.setdefault(notice.sequence, notice.notice_digest)
        if previous != notice.notice_digest:
            return _report(OperatorKeyDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence operator-key fork", expected_profile_id, notice_tuple, witness_tuple)
    latest = max(notice_tuple, key=lambda item: (item.sequence, item.issued_at, item.notice_digest))
    if previous_sequence is not None and latest.sequence < previous_sequence:
        return _report(OperatorKeyDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "operator-key sequence rollback", expected_profile_id, notice_tuple, witness_tuple)
    if previous_notice_digest is not None:
        first = min(notice_tuple, key=lambda item: item.sequence)
        if first.previous_notice_digest != previous_notice_digest:
            return _report(OperatorKeyDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "operator-key previous link mismatch", expected_profile_id, notice_tuple, witness_tuple)
    if required_hard_negative_digest is not None and latest.hard_negative_digest != required_hard_negative_digest:
        return _report(OperatorKeyDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, "required hard-negative digest is not preserved", expected_profile_id, notice_tuple, witness_tuple)
    if latest.kind is OperatorKeyNoticeKind.ROTATE:
        if policy.require_successor_cosign_for_rotation and not latest.successor_signature_verifies():
            return _report(OperatorKeyDecisionKind.HOLD_NEEDS_COSIGN, False, "successor key did not cosign rotation", expected_profile_id, notice_tuple, witness_tuple)
        return _report(OperatorKeyDecisionKind.ACCEPT_ROTATION, True, "old and successor keys cosigned rotation", expected_profile_id, notice_tuple, witness_tuple)
    if latest.kind in (OperatorKeyNoticeKind.COMPROMISE, OperatorKeyNoticeKind.FREEZE_OLD_KEY):
        return _report(OperatorKeyDecisionKind.ACCEPT_COMPROMISE_FREEZE, True, "old key compromise/freeze accepted", expected_profile_id, notice_tuple, witness_tuple)
    if latest.kind is OperatorKeyNoticeKind.RECOVER:
        valid_witnesses: list[OperatorKeyWitness] = []
        for witness in witness_tuple:
            if not witness.verifies():
                return _report(OperatorKeyDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad recovery witness signature", expected_profile_id, notice_tuple, witness_tuple)
            if witness.profile_id != expected_profile_id or witness.notice_digest != latest.notice_digest:
                continue
            if witness.issued_at > now or witness.expires_at <= now:
                return _report(OperatorKeyDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "recovery witness expired or future", expected_profile_id, notice_tuple, witness_tuple)
            valid_witnesses.append(witness)
        families = {witness.family_id for witness in valid_witnesses}
        if len(families) < policy.min_recovery_witness_families:
            return _report(OperatorKeyDecisionKind.HOLD_NEEDS_WITNESS_DIVERSITY, False, "low recovery witness family diversity", expected_profile_id, notice_tuple, witness_tuple)
        return _report(OperatorKeyDecisionKind.ACCEPT_RECOVERY, True, "successor recovery accepted with witness diversity", expected_profile_id, notice_tuple, witness_tuple)
    raise ValueError(f"unknown operator key notice kind: {latest.kind}")
