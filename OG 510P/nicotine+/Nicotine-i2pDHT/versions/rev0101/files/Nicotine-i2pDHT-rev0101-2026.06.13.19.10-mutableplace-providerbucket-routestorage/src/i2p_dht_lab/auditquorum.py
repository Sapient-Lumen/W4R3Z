"""Audit quorum evidence for public bridge publication shadows.

Quorum is intentionally a dangerous word here: rev0048 uses it as local pressure,
not as global truth.  A set of signed audit receipts can make a public bridge
shadow easier to accept locally, but a monoculture of receipts, stale public
records, or payload mismatch still blocks publication-shaped side effects.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgeshadow import BridgeShadowReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

AUDIT_QUORUM_DOMAIN = DOMAIN + b":audit-quorum-v1:"


class AuditReceiptKind(str, Enum):
    PUBLICATION_OBSERVED = "publication_observed"
    WITHDRAWAL_OBSERVED = "withdrawal_observed"
    REPAIR_OBSERVED = "repair_observed"
    STALE_PUBLIC_RECORD = "stale_public_record"
    PAYLOAD_MISMATCH = "payload_mismatch"
    REDRESS_GAP = "redress_gap"


class AuditQuorumDecisionKind(str, Enum):
    ACCEPT_AUDITED = "accept_audited"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_SHADOW_NOT_ACCEPTED = "hold_shadow_not_accepted"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_REDRESS_GAP = "hold_redress_gap"
    QUARANTINE_SHADOW = "quarantine_shadow"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SHADOW_DIGEST_DRIFT = "quarantine_shadow_digest_drift"
    QUARANTINE_PAYLOAD_MISMATCH = "quarantine_payload_mismatch"
    QUARANTINE_STALE_PUBLIC_RECORD = "quarantine_stale_public_record"
    QUARANTINE_RECEIPT_MONOCULTURE = "quarantine_receipt_monoculture"


_NEGATIVE_KINDS = {AuditReceiptKind.STALE_PUBLIC_RECORD, AuditReceiptKind.PAYLOAD_MISMATCH}


@dataclass(frozen=True)
class AuditReceipt:
    kind: AuditReceiptKind
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    bridge_shadow_digest: bytes
    public_payload_digest: bytes
    observation_digest: bytes
    accepted: bool
    watch: bool
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", AuditReceiptKind(self.kind))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("audit receipt needs profile/service/family/path")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("bridge_shadow_digest", self.bridge_shadow_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("observation_digest", self.observation_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"shadow": self.bridge_shadow_digest,
            b"payload": self.public_payload_digest,
            b"observation": self.observation_digest,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return AUDIT_QUORUM_DOMAIN + b":receipt-sig:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_digest(self) -> bytes:
        return sha256(AUDIT_QUORUM_DOMAIN + b":receipt-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class AuditQuorumReport:
    decision_kind: AuditQuorumDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    bridge_shadow_digest: bytes
    public_payload_digest: bytes
    receipt_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_audit_receipt(
    *,
    keypair: DhtKeypair,
    kind: AuditReceiptKind,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    bridge_shadow_digest: bytes,
    public_payload_digest: bytes,
    observation_digest: bytes,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    accepted: bool = True,
    watch: bool = False,
) -> AuditReceipt:
    receipt = AuditReceipt(kind, profile_id, service_name, scope_digest, request_digest, bridge_shadow_digest, public_payload_digest, observation_digest, accepted, watch, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(receipt, signature=keypair.sign(receipt.signature_payload()))


def _report(kind: AuditQuorumDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, bridge_shadow_digest: bytes, public_payload_digest: bytes, receipts: Iterable[AuditReceipt] = ()) -> AuditQuorumReport:
    receipt_tuple = tuple(sorted(receipts, key=lambda item: item.receipt_digest))
    digests = tuple(item.receipt_digest for item in receipt_tuple)
    families = len({item.family_id for item in receipt_tuple})
    paths = len({item.path_family for item in receipt_tuple})
    negatives = sum(1 for item in receipt_tuple if item.kind in _NEGATIVE_KINDS or not item.accepted)
    digest = sha256(AUDIT_QUORUM_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"shadow": bridge_shadow_digest,
        b"payload": public_payload_digest,
        b"receipts": list(digests),
        b"families": families,
        b"paths": paths,
        b"negatives": negatives,
    }))
    return AuditQuorumReport(kind, accept, watch, reason, profile_id, service_name, scope_digest, request_digest, bridge_shadow_digest, public_payload_digest, digests, families, paths, negatives, digest)


def assess_audit_quorum(
    receipts: Iterable[AuditReceipt],
    *,
    bridge_shadow: BridgeShadowReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_public_payload_digest: bytes,
    previously_seen_receipts: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_redress_gap_watch: bool = True,
) -> AuditQuorumReport:
    if bridge_shadow.quarantined:
        return _report(AuditQuorumDecisionKind.QUARANTINE_SHADOW, False, True, "bridge shadow quarantined", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest)
    if not bridge_shadow.accept:
        return _report(AuditQuorumDecisionKind.HOLD_SHADOW_NOT_ACCEPTED, False, bridge_shadow.watch, "bridge shadow not accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest)
    receipt_tuple = tuple(sorted(receipts, key=lambda item: item.receipt_digest))
    seen = set(previously_seen_receipts)
    family_to_payloads: dict[str, set[bytes]] = {}
    for receipt in receipt_tuple:
        if not receipt.verifies():
            return _report(AuditQuorumDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad audit receipt signature", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        if receipt.issued_at > now or receipt.expires_at <= now:
            return _report(AuditQuorumDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "audit receipt expired or future", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        if receipt.receipt_digest in seen:
            return _report(AuditQuorumDecisionKind.QUARANTINE_REPLAY, False, True, "audit receipt replay", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        if receipt.profile_id != expected_profile_id:
            return _report(AuditQuorumDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "audit receipt profile drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        if receipt.service_name != expected_service_name:
            return _report(AuditQuorumDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "audit receipt service drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        if receipt.scope_digest != expected_scope_digest:
            return _report(AuditQuorumDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "audit receipt scope drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        if receipt.request_digest != expected_request_digest:
            return _report(AuditQuorumDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "audit receipt request drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        if receipt.bridge_shadow_digest != bridge_shadow.report_digest:
            return _report(AuditQuorumDecisionKind.QUARANTINE_SHADOW_DIGEST_DRIFT, False, True, "audit receipt shadow digest drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        family_to_payloads.setdefault(receipt.family_id, set()).add(receipt.public_payload_digest)
        if receipt.kind is AuditReceiptKind.PAYLOAD_MISMATCH or receipt.public_payload_digest != expected_public_payload_digest:
            return _report(AuditQuorumDecisionKind.QUARANTINE_PAYLOAD_MISMATCH, False, True, "audit receipt reports mismatched payload", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
        if receipt.kind is AuditReceiptKind.STALE_PUBLIC_RECORD:
            return _report(AuditQuorumDecisionKind.QUARANTINE_STALE_PUBLIC_RECORD, False, True, "audit receipt reports stale public record", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
    if any(len(values) > 1 for values in family_to_payloads.values()):
        return _report(AuditQuorumDecisionKind.QUARANTINE_RECEIPT_MONOCULTURE, False, True, "one audit family emitted conflicting payloads", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
    if len({item.family_id for item in receipt_tuple}) < min_family_diversity:
        return _report(AuditQuorumDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, bridge_shadow.watch, "audit receipt family diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
    if len({item.path_family for item in receipt_tuple}) < min_path_diversity:
        return _report(AuditQuorumDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, bridge_shadow.watch, "audit receipt path diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
    redress_gaps = [item for item in receipt_tuple if item.kind is AuditReceiptKind.REDRESS_GAP or item.watch]
    if redress_gaps and not allow_redress_gap_watch:
        return _report(AuditQuorumDecisionKind.HOLD_REDRESS_GAP, False, True, "audit receipt reports redress gap", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
    watch = bridge_shadow.watch or bool(redress_gaps)
    kind = AuditQuorumDecisionKind.ACCEPT_WITH_WATCH if watch else AuditQuorumDecisionKind.ACCEPT_AUDITED
    return _report(kind, True, watch, "audit receipts accepted locally", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_shadow_digest=bridge_shadow.report_digest, public_payload_digest=expected_public_payload_digest, receipts=receipt_tuple)
