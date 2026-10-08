"""Authority receipt mesh for scoped policy/control decisions.

Receipts are not global reputation and not consensus. They are signed local
memory that a node can use after a policy/key/control gate has already made a
component decision. rev0044 tests that receipts cannot be replayed, widened to
a new scope, collapsed into one family, or used to hide disagreement.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .policyfirebreak import PolicyAction, ZERO_DIGEST

AUTHORITY_RECEIPT_DOMAIN = DOMAIN + b":authority-receipt-v1:"


class AuthorityReceiptKind(str, Enum):
    POLICY_FIREBREAK = "policy_firebreak"
    KEY_COMPARTMENT = "key_compartment"
    AUTHORITY_SPLIT = "authority_split"
    CONTROL_INTENT = "control_intent"
    BRIDGE_FIREWALL = "bridge_firewall"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"


class ReceiptStatus(str, Enum):
    ACCEPT = "accept"
    WATCH = "watch"
    REFUSE = "refuse"
    QUARANTINE = "quarantine"


class AuthorityReceiptDecisionKind(str, Enum):
    ACCEPT_RECEIPT_MESH = "accept_receipt_mesh"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MISSING_RECEIPT = "hold_missing_receipt"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_RECEIPT_WATCH = "hold_receipt_watch"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_RECEIPT_REFUSAL = "quarantine_receipt_refusal"
    QUARANTINE_CONFLICTING_STATUS = "quarantine_conflicting_status"


@dataclass(frozen=True)
class AuthorityReceipt:
    kind: AuthorityReceiptKind
    status: ReceiptStatus
    profile_id: str
    action: PolicyAction
    subject_key_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    evidence_digest: bytes
    sequence: int
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    path_family: str
    reason: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        for name, value in (("subject_key_digest", self.subject_key_digest), ("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("evidence_digest", self.evidence_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if len(self.signer_public_key) != 32:
            raise ValueError("signer public key must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        if len(self.reason.encode("utf-8")) > 160:
            raise ValueError("reason must be short")
        object.__setattr__(self, "kind", AuthorityReceiptKind(self.kind))
        object.__setattr__(self, "status", ReceiptStatus(self.status))
        object.__setattr__(self, "action", PolicyAction(self.action))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"status": self.status.value,
            b"profile": self.profile_id,
            b"action": self.action.value,
            b"subject": self.subject_key_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"reason": self.reason,
        }

    def payload(self) -> bytes:
        return AUTHORITY_RECEIPT_DOMAIN + b":receipt:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_digest(self) -> bytes:
        return sha256(AUTHORITY_RECEIPT_DOMAIN + b":receipt-digest:" + self.payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "AuthorityReceipt":
        return replace(self, signature=signature)


@dataclass(frozen=True)
class AuthorityReceiptMeshReport:
    decision_kind: AuthorityReceiptDecisionKind
    accepted: bool
    watch: bool
    accepted_receipt_digests: tuple[bytes, ...] = ()
    family_count: int = 0
    path_family_count: int = 0
    reasons: tuple[str, ...] = ()
    report_digest: bytes = ZERO_DIGEST


def make_authority_receipt(
    *,
    keypair: DhtKeypair,
    kind: AuthorityReceiptKind,
    status: ReceiptStatus,
    profile_id: str,
    action: PolicyAction,
    subject_key_digest: bytes,
    scope_digest: bytes,
    request_digest: bytes,
    evidence_digest: bytes,
    sequence: int,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    reason: str = "",
) -> AuthorityReceipt:
    receipt = AuthorityReceipt(
        kind=kind,
        status=status,
        profile_id=profile_id,
        action=action,
        subject_key_digest=subject_key_digest,
        scope_digest=scope_digest,
        request_digest=request_digest,
        evidence_digest=evidence_digest,
        sequence=sequence,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
        family_id=family_id,
        path_family=path_family,
        reason=reason,
    )
    return receipt.with_signature(keypair.sign(receipt.payload()))


def _report(kind: AuthorityReceiptDecisionKind, *, accepted: bool = False, watch: bool = False, receipts: Iterable[AuthorityReceipt] = (), family_count: int = 0, path_family_count: int = 0, reasons: Iterable[str] = ()) -> AuthorityReceiptMeshReport:
    receipt_tuple = tuple(receipts)
    reason_tuple = tuple(reasons)
    digests = tuple(item.receipt_digest for item in receipt_tuple)
    digest = sha256(AUTHORITY_RECEIPT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": 1 if accepted else 0,
        b"watch": 1 if watch else 0,
        b"receipts": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"reasons": list(reason_tuple),
    }))
    return AuthorityReceiptMeshReport(kind, accepted, watch, digests, family_count, path_family_count, reason_tuple, digest)


def assess_authority_receipt_mesh(
    receipts: Iterable[AuthorityReceipt],
    *,
    now: int,
    expected_profile_id: str,
    expected_action: PolicyAction,
    expected_subject_key_digest: bytes,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    required_kinds: Iterable[AuthorityReceiptKind],
    min_family_diversity: int = 3,
    min_path_diversity: int = 2,
    allow_watch: bool = False,
    previously_seen_receipt_digests: Iterable[bytes] = (),
) -> AuthorityReceiptMeshReport:
    expected_action = PolicyAction(expected_action)
    required = frozenset(AuthorityReceiptKind(kind) for kind in required_kinds)
    seen = set(previously_seen_receipt_digests)
    receipt_tuple = tuple(receipts)
    valid: list[AuthorityReceipt] = []
    by_kind_seq: dict[tuple[AuthorityReceiptKind, int], bytes] = {}
    by_kind_status: dict[AuthorityReceiptKind, ReceiptStatus] = {}
    for receipt in receipt_tuple:
        if not receipt.verify():
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE, receipts=(receipt,), reasons=("bad_signature",))
        if receipt.issued_at > now or receipt.expires_at <= now:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, receipts=(receipt,), reasons=("time_window",))
        if receipt.receipt_digest in seen:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_REPLAY, receipts=(receipt,), reasons=("receipt_replay",))
        if receipt.profile_id != expected_profile_id:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_PROFILE_DRIFT, receipts=(receipt,), reasons=("profile_drift",))
        if receipt.scope_digest != expected_scope_digest:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_SCOPE_DRIFT, receipts=(receipt,), reasons=("scope_drift",))
        if receipt.request_digest != expected_request_digest:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_REQUEST_DRIFT, receipts=(receipt,), reasons=("request_drift",))
        if receipt.action is not expected_action:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_ACTION_DRIFT, receipts=(receipt,), reasons=("action_drift",))
        if receipt.subject_key_digest != expected_subject_key_digest:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_SUBJECT_DRIFT, receipts=(receipt,), reasons=("subject_drift",))
        key = (receipt.kind, receipt.sequence)
        existing = by_kind_seq.setdefault(key, receipt.receipt_digest)
        if existing != receipt.receipt_digest:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, receipts=(receipt,), reasons=("same_kind_sequence_fork",))
        if receipt.kind in by_kind_status and by_kind_status[receipt.kind] is not receipt.status:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_CONFLICTING_STATUS, receipts=(receipt,), reasons=("conflicting_status",))
        by_kind_status[receipt.kind] = receipt.status
        if receipt.status is ReceiptStatus.QUARANTINE:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_RECEIPT_REFUSAL, receipts=(receipt,), reasons=(receipt.reason or "receipt_quarantined",))
        if receipt.status is ReceiptStatus.REFUSE:
            return _report(AuthorityReceiptDecisionKind.QUARANTINE_RECEIPT_REFUSAL, receipts=(receipt,), reasons=(receipt.reason or "receipt_refused",))
        valid.append(receipt)
    present = {receipt.kind for receipt in valid}
    missing = sorted(kind.value for kind in required - present)
    if missing:
        return _report(AuthorityReceiptDecisionKind.HOLD_MISSING_RECEIPT, receipts=valid, reasons=("missing:" + ",".join(missing),))
    watch = any(receipt.status is ReceiptStatus.WATCH for receipt in valid if receipt.kind in required)
    if watch and not allow_watch:
        return _report(AuthorityReceiptDecisionKind.HOLD_RECEIPT_WATCH, receipts=valid, reasons=("watch_receipt_present",))
    relevant = [receipt for receipt in valid if receipt.kind in required]
    families = {receipt.family_id for receipt in relevant}
    paths = {receipt.path_family for receipt in relevant}
    if len(families) < min_family_diversity:
        return _report(AuthorityReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, receipts=valid, family_count=len(families), path_family_count=len(paths), reasons=("receipt_family_diversity",))
    if len(paths) < min_path_diversity:
        return _report(AuthorityReceiptDecisionKind.HOLD_LOW_PATH_DIVERSITY, receipts=valid, family_count=len(families), path_family_count=len(paths), reasons=("receipt_path_diversity",))
    kind = AuthorityReceiptDecisionKind.ACCEPT_WITH_WATCH if watch else AuthorityReceiptDecisionKind.ACCEPT_RECEIPT_MESH
    return _report(kind, accepted=True, watch=watch, receipts=valid, family_count=len(families), path_family_count=len(paths))
