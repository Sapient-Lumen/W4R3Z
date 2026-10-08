"""Signed receipt lane for joined control/firewall decisions.

rev0044 treats a successful joined control/firewall report as still only an
observation. Before restart memory or later side effects can lean on it, the
node records a scoped receipt that is sequence-checked, previous-linked, and
bound to the exact joined report digest.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .compartmentfirewall import CompartmentFirewallReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

CONTROL_RECEIPT_DOMAIN = DOMAIN + b":control-receipt-v1:"
ZERO_DIGEST = b"\x00" * 32


class ControlReceiptKind(str, Enum):
    COMPARTMENT_FIREWALL = "compartment_firewall"
    PUBLIC_BRIDGE_SIDE_EFFECT = "public_bridge_side_effect"
    PRIVATE_GARDEN_SIDE_EFFECT = "private_garden_side_effect"
    CLOSED_BRIDGE_SIDE_EFFECT = "closed_bridge_side_effect"


class ControlReceiptDecisionKind(str, Enum):
    ACCEPT_CONTROL_RECEIPT = "accept_control_receipt"
    HOLD_UNACCEPTED_REPORT = "hold_unaccepted_report"
    HOLD_MISSING_PREVIOUS_LINK = "hold_missing_previous_link"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_KIND_MISMATCH = "quarantine_kind_mismatch"
    QUARANTINE_REPORT_DIGEST_DRIFT = "quarantine_report_digest_drift"
    QUARANTINE_PREVIOUS_LINK = "quarantine_previous_link"


@dataclass(frozen=True)
class ControlReceipt:
    kind: ControlReceiptKind
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    joined_report_digest: bytes
    joined_report_accepted: bool
    sequence: int
    previous_receipt_digest: bytes
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        for name, value in (("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("joined_report_digest", self.joined_report_digest), ("previous_receipt_digest", self.previous_receipt_digest), ("signer_public_key", self.signer_public_key)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("receipt expires_at must be after issued_at")
        if not self.family_id:
            raise ValueError("family_id must be non-empty")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"joined": self.joined_report_digest,
            b"joined_accept": 1 if self.joined_report_accepted else 0,
            b"seq": self.sequence,
            b"prev": self.previous_receipt_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
        }

    def signature_payload(self) -> bytes:
        return CONTROL_RECEIPT_DOMAIN + b":sig:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_digest(self) -> bytes:
        return sha256(CONTROL_RECEIPT_DOMAIN + b":digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


def make_control_receipt(
    *,
    keypair: DhtKeypair,
    kind: ControlReceiptKind,
    joined_report: CompartmentFirewallReport,
    sequence: int,
    previous_receipt_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
) -> ControlReceipt:
    receipt = ControlReceipt(kind, joined_report.profile_id, joined_report.service_name, joined_report.scope_digest, joined_report.request_digest, joined_report.report_digest, joined_report.accept, sequence, previous_receipt_digest, issued_at, expires_at, keypair.public_key_bytes, family_id)
    return replace(receipt, signature=keypair.sign(receipt.signature_payload()))


@dataclass(frozen=True)
class ControlReceiptAssessment:
    decision_kind: ControlReceiptDecisionKind
    accept: bool
    reason: str
    accepted_receipt_digest: bytes = ZERO_DIGEST
    highest_sequence: int = -1
    family_count: int = 0
    report_digest: bytes = ZERO_DIGEST

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _assessment(kind: ControlReceiptDecisionKind, accept: bool, reason: str, *, receipt: ControlReceipt | None = None, family_count: int = 0, highest_sequence: int = -1) -> ControlReceiptAssessment:
    digest = sha256(CONTROL_RECEIPT_DOMAIN + b":assessment:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"receipt": receipt.receipt_digest if receipt else ZERO_DIGEST,
        b"families": family_count,
        b"highest_seq": highest_sequence,
    }))
    return ControlReceiptAssessment(kind, accept, reason, receipt.receipt_digest if receipt else ZERO_DIGEST, highest_sequence, family_count, digest)


def assess_control_receipts(
    receipts: Iterable[ControlReceipt],
    *,
    now: int,
    kind: ControlReceiptKind,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_joined_report_digest: bytes,
    minimum_sequence: int = 0,
    previous_receipt_digest: bytes | None = None,
    previously_seen_receipts: Iterable[bytes] = (),
    min_family_diversity: int = 1,
) -> ControlReceiptAssessment:
    if len(expected_scope_digest) != 32 or len(expected_request_digest) != 32 or len(expected_joined_report_digest) != 32:
        raise ValueError("expected digests must be 32 bytes")
    seen = set(previously_seen_receipts)
    latest: ControlReceipt | None = None
    fork_guard: dict[int, bytes] = {}
    families: set[str] = set()
    for receipt in sorted(receipts, key=lambda item: (item.sequence, item.receipt_digest)):
        if receipt.receipt_digest in seen:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_REPLAY, False, "receipt replay", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        if not receipt.verifies():
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "receipt signature failed", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        if receipt.issued_at > now or receipt.expires_at <= now:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "receipt outside local time window", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        if receipt.kind is not kind:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_KIND_MISMATCH, False, "receipt kind mismatch", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        if receipt.profile_id != expected_profile_id:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "receipt profile drift", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        if receipt.service_name != expected_service_name:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "receipt service drift", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        if receipt.scope_digest != expected_scope_digest:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "receipt scope drift", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        if receipt.request_digest != expected_request_digest:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "receipt request drift", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        if receipt.joined_report_digest != expected_joined_report_digest:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_REPORT_DIGEST_DRIFT, False, "receipt joined-report digest drift", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        prior = fork_guard.get(receipt.sequence)
        if prior is not None and prior != receipt.receipt_digest:
            return _assessment(ControlReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence control receipt fork", receipt=receipt, family_count=len(families), highest_sequence=receipt.sequence)
        fork_guard[receipt.sequence] = receipt.receipt_digest
        families.add(receipt.family_id)
        if latest is None or receipt.sequence > latest.sequence:
            latest = receipt
    if latest is None:
        return _assessment(ControlReceiptDecisionKind.HOLD_MISSING_PREVIOUS_LINK, False, "no receipt candidates")
    if latest.sequence < minimum_sequence:
        return _assessment(ControlReceiptDecisionKind.QUARANTINE_ROLLBACK, False, "receipt sequence below local minimum", receipt=latest, family_count=len(families), highest_sequence=latest.sequence)
    if previous_receipt_digest is not None and latest.sequence > 0 and latest.previous_receipt_digest != previous_receipt_digest:
        return _assessment(ControlReceiptDecisionKind.QUARANTINE_PREVIOUS_LINK, False, "receipt previous link mismatch", receipt=latest, family_count=len(families), highest_sequence=latest.sequence)
    if latest.sequence > 0 and latest.previous_receipt_digest == ZERO_DIGEST:
        return _assessment(ControlReceiptDecisionKind.HOLD_MISSING_PREVIOUS_LINK, False, "nonzero receipt missing previous link", receipt=latest, family_count=len(families), highest_sequence=latest.sequence)
    if not latest.joined_report_accepted:
        return _assessment(ControlReceiptDecisionKind.HOLD_UNACCEPTED_REPORT, False, "receipt records an unaccepted joined report", receipt=latest, family_count=len(families), highest_sequence=latest.sequence)
    if len(families) < min_family_diversity:
        return _assessment(ControlReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "receipt lacks family diversity", receipt=latest, family_count=len(families), highest_sequence=latest.sequence)
    return _assessment(ControlReceiptDecisionKind.ACCEPT_CONTROL_RECEIPT, True, "control receipt accepted for exact joined report", receipt=latest, family_count=len(families), highest_sequence=latest.sequence)
