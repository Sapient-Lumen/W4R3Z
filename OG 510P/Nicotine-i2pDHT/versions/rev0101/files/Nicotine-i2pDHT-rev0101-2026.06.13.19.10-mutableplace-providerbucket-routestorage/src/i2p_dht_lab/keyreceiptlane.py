"""Operator/key authority receipts for public bridge epochs.

rev0045 keeps key authority separate from public bridge state.  An epoch notice
can be correctly signed by a service signer while the operator key succession,
compartment, or bridge-authority receipt lane is stale, forked, or collapsed
into one family.  These receipts are local evidence only; they do not create a
global ban or global reputation table.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

KEY_RECEIPT_DOMAIN = DOMAIN + b":key-receipt-lane-v1:"
ZERO_DIGEST = b"\x00" * 32


class KeyReceiptKind(str, Enum):
    KEY_COMPARTMENT = "key_compartment"
    OPERATOR_ROTATION = "operator_rotation"
    SUCCESSION_REPAIR = "succession_repair"
    BRIDGE_EPOCH_AUTH = "bridge_epoch_auth"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"


class KeyReceiptStatus(str, Enum):
    ACCEPT = "accept"
    WATCH = "watch"
    REFUSE = "refuse"
    QUARANTINE = "quarantine"


class KeyReceiptDecisionKind(str, Enum):
    ACCEPT_KEY_RECEIPTS = "accept_key_receipts"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MISSING_RECEIPT = "hold_missing_receipt"
    HOLD_RECEIPT_WATCH = "hold_receipt_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_OPERATOR_DRIFT = "quarantine_operator_drift"
    QUARANTINE_SUCCESSOR_DRIFT = "quarantine_successor_drift"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_REFUSAL = "quarantine_refusal"
    QUARANTINE_STATUS_CONFLICT = "quarantine_status_conflict"


@dataclass(frozen=True)
class KeyAuthorityReceipt:
    kind: KeyReceiptKind
    status: KeyReceiptStatus
    profile_id: str
    service_name: str
    subject_key_digest: bytes
    operator_key_digest: bytes
    successor_key_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    evidence_digest: bytes
    sequence: int
    previous_receipt_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    reason: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("receipt sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("receipt expires_at must be after issued_at")
        if len(self.reason.encode("utf-8")) > 160:
            raise ValueError("reason must be short")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("subject_key_digest", self.subject_key_digest),
            ("operator_key_digest", self.operator_key_digest),
            ("successor_key_digest", self.successor_key_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("evidence_digest", self.evidence_digest),
            ("previous_receipt_digest", self.previous_receipt_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "kind", KeyReceiptKind(self.kind))
        object.__setattr__(self, "status", KeyReceiptStatus(self.status))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"status": self.status.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"subject": self.subject_key_digest,
            b"operator": self.operator_key_digest,
            b"successor": self.successor_key_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"prev": self.previous_receipt_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"reason": self.reason,
        }

    def signature_payload(self) -> bytes:
        return KEY_RECEIPT_DOMAIN + b":receipt-sig:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_digest(self) -> bytes:
        return sha256(KEY_RECEIPT_DOMAIN + b":receipt-digest:" + bencode(self.unsigned_bvalue()))

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class KeyReceiptReport:
    decision_kind: KeyReceiptDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    accepted_receipt_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_key_authority_receipt(
    *,
    keypair: DhtKeypair,
    kind: KeyReceiptKind,
    status: KeyReceiptStatus,
    profile_id: str,
    service_name: str,
    subject_key_digest: bytes,
    operator_key_digest: bytes,
    successor_key_digest: bytes,
    scope_digest: bytes,
    request_digest: bytes,
    evidence_digest: bytes,
    sequence: int,
    previous_receipt_digest: bytes,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    reason: str = "",
) -> KeyAuthorityReceipt:
    receipt = KeyAuthorityReceipt(kind=kind, status=status, profile_id=profile_id, service_name=service_name, subject_key_digest=subject_key_digest, operator_key_digest=operator_key_digest, successor_key_digest=successor_key_digest, scope_digest=scope_digest, request_digest=request_digest, evidence_digest=evidence_digest, sequence=sequence, previous_receipt_digest=previous_receipt_digest, issued_at=issued_at, expires_at=expires_at, family_id=family_id, path_family=path_family, signer_public_key=keypair.public_key_bytes, reason=reason)
    return replace(receipt, signature=keypair.sign(receipt.signature_payload()))


def _report(kind: KeyReceiptDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, receipts: Iterable[KeyAuthorityReceipt], family_count: int = 0, path_family_count: int = 0, highest_sequence: int = -1) -> KeyReceiptReport:
    receipt_tuple = tuple(sorted(receipts, key=lambda item: (item.kind.value, item.sequence, item.receipt_digest)))
    digests = tuple(sorted(item.receipt_digest for item in receipt_tuple if accept or watch))
    digest = sha256(KEY_RECEIPT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"receipts": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"highest": highest_sequence,
    }))
    return KeyReceiptReport(kind, accept, watch, reason, profile_id, service_name, digests, family_count, path_family_count, highest_sequence, digest)


def assess_key_authority_receipts(
    receipts: Iterable[KeyAuthorityReceipt],
    *,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_subject_key_digest: bytes,
    expected_operator_key_digest: bytes,
    expected_successor_key_digest: bytes,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    required_kinds: Iterable[KeyReceiptKind],
    previous_sequence: int | None = None,
    previous_receipt_digest: bytes | None = None,
    previously_seen_receipts: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_watch: bool = False,
) -> KeyReceiptReport:
    receipt_tuple = tuple(sorted(receipts, key=lambda item: (item.kind.value, item.sequence, item.receipt_digest)))
    seen = set(previously_seen_receipts)
    families: set[str] = set()
    paths: set[str] = set()
    fork_guard: dict[tuple[KeyReceiptKind, int], bytes] = {}
    status_guard: dict[KeyReceiptKind, KeyReceiptStatus] = {}
    by_kind: dict[KeyReceiptKind, KeyAuthorityReceipt] = {}
    highest = -1
    for receipt in receipt_tuple:
        if not receipt.verifies():
            return _report(KeyReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad key receipt signature", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.issued_at > now or receipt.expires_at <= now:
            return _report(KeyReceiptDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "key receipt expired or future", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.receipt_digest in seen:
            return _report(KeyReceiptDecisionKind.QUARANTINE_REPLAY, False, False, "key receipt replay", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.profile_id != expected_profile_id:
            return _report(KeyReceiptDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "key receipt profile drift", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.service_name != expected_service_name:
            return _report(KeyReceiptDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "key receipt service drift", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.scope_digest != expected_scope_digest:
            return _report(KeyReceiptDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "key receipt scope drift", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.request_digest != expected_request_digest:
            return _report(KeyReceiptDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "key receipt request drift", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.subject_key_digest != expected_subject_key_digest:
            return _report(KeyReceiptDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, False, "key receipt subject drift", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.operator_key_digest != expected_operator_key_digest:
            return _report(KeyReceiptDecisionKind.QUARANTINE_OPERATOR_DRIFT, False, False, "operator key digest drift", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if receipt.successor_key_digest != expected_successor_key_digest:
            return _report(KeyReceiptDecisionKind.QUARANTINE_SUCCESSOR_DRIFT, False, False, "successor key digest drift", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        if previous_sequence is not None and receipt.sequence < previous_sequence:
            return _report(KeyReceiptDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "key receipt rollback", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        prior = fork_guard.get((receipt.kind, receipt.sequence))
        if prior is not None and prior != receipt.receipt_digest:
            return _report(KeyReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-kind same-sequence key receipt fork", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        fork_guard[(receipt.kind, receipt.sequence)] = receipt.receipt_digest
        previous_status = status_guard.get(receipt.kind)
        if previous_status is not None and previous_status is not receipt.status:
            return _report(KeyReceiptDecisionKind.QUARANTINE_STATUS_CONFLICT, False, False, "conflicting key receipt statuses", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        status_guard[receipt.kind] = receipt.status
        if receipt.status in (KeyReceiptStatus.REFUSE, KeyReceiptStatus.QUARANTINE):
            return _report(KeyReceiptDecisionKind.QUARANTINE_REFUSAL, False, False, "key receipt refusal/quarantine", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple)
        families.add(receipt.family_id)
        paths.add(receipt.path_family)
        highest = max(highest, receipt.sequence)
        current = by_kind.get(receipt.kind)
        if current is None or receipt.sequence > current.sequence:
            by_kind[receipt.kind] = receipt
    required = tuple(KeyReceiptKind(kind) for kind in required_kinds)
    missing = tuple(kind for kind in required if kind not in by_kind)
    if missing:
        return _report(KeyReceiptDecisionKind.HOLD_MISSING_RECEIPT, False, False, "required key receipt missing", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    latest_required = tuple(by_kind[kind] for kind in required)
    if previous_sequence is not None and highest > previous_sequence and previous_receipt_digest is not None:
        if not any(item.previous_receipt_digest == previous_receipt_digest for item in latest_required):
            return _report(KeyReceiptDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "key receipt previous-link mismatch", profile_id=expected_profile_id, service_name=expected_service_name, receipts=receipt_tuple, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if any(item.status is KeyReceiptStatus.WATCH for item in latest_required):
        if not allow_watch:
            return _report(KeyReceiptDecisionKind.HOLD_RECEIPT_WATCH, False, True, "key receipt watch requires explicit allowance", profile_id=expected_profile_id, service_name=expected_service_name, receipts=latest_required, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
        kind = KeyReceiptDecisionKind.ACCEPT_WITH_WATCH
        accepted = True
        watch = True
    else:
        kind = KeyReceiptDecisionKind.ACCEPT_KEY_RECEIPTS
        accepted = True
        watch = False
    if len(families) < min_family_diversity:
        return _report(KeyReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, watch, "key receipt family diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, receipts=latest_required, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if len(paths) < min_path_diversity:
        return _report(KeyReceiptDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, watch, "key receipt path diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, receipts=latest_required, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    return _report(kind, accepted, watch, "key receipts accepted at exact boundary", profile_id=expected_profile_id, service_name=expected_service_name, receipts=latest_required, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
