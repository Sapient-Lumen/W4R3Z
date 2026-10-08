"""Redress and appeal lane for subjective moderation capsules.

The DHT should not pretend that maintainer/operator bans are global truth.  It
also should not make redress a hidden override that silently bypasses hard
negative evidence.  rev0046 models redress as a signed, scoped, family-diverse
local evidence lane that can lift, narrow, or watch a moderation quarantine only
at the exact subject/profile/service/scope/request boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ModerationAction, ModerationQuarantineReport, ZERO_DIGEST

REDRESS_LANE_DOMAIN = DOMAIN + b":redress-lane-v1:"


class RedressKind(str, Enum):
    SUBJECT_COUNTERSIGN = "subject_countersign"
    MODERATOR_ACK = "moderator_ack"
    WITNESS_OBSERVATION = "witness_observation"
    REMEDIATION_PROOF = "remediation_proof"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"


class RedressPurpose(str, Enum):
    LIFT = "lift"
    NARROW = "narrow"
    WATCH_ONLY = "watch_only"


class RedressStatus(str, Enum):
    SUPPORT = "support"
    WATCH = "watch"
    REFUSE = "refuse"


class RedressDecisionKind(str, Enum):
    ACCEPT_NOT_NEEDED = "accept_not_needed"
    ACCEPT_LIFT = "accept_lift"
    ACCEPT_NARROW = "accept_narrow"
    ACCEPT_WATCH_ONLY = "accept_watch_only"
    HOLD_APPEAL_NOT_ALLOWED = "hold_appeal_not_allowed"
    HOLD_MISSING_REDRESS_EVIDENCE = "hold_missing_redress_evidence"
    HOLD_REDRESS_WATCH = "hold_redress_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_REFUSAL = "quarantine_refusal"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_QUARANTINE_DIGEST_DRIFT = "quarantine_quarantine_digest_drift"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_LIVE = "quarantine_hard_negative_live"


@dataclass(frozen=True)
class RedressReceipt:
    kind: RedressKind
    purpose: RedressPurpose
    status: RedressStatus
    profile_id: str
    service_name: str
    subject_key_digest: bytes
    action: ModerationAction
    scope_digest: bytes
    request_digest: bytes
    quarantine_report_digest: bytes
    evidence_digest: bytes
    sequence: int
    previous_redress_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    reason_code: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 96:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("redress sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if len(self.reason_code.encode("utf-8")) > 160:
            raise ValueError("reason code must be short")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("subject_key_digest", self.subject_key_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("quarantine_report_digest", self.quarantine_report_digest),
            ("evidence_digest", self.evidence_digest),
            ("previous_redress_digest", self.previous_redress_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "kind", RedressKind(self.kind))
        object.__setattr__(self, "purpose", RedressPurpose(self.purpose))
        object.__setattr__(self, "status", RedressStatus(self.status))
        object.__setattr__(self, "action", ModerationAction(self.action))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"purpose": self.purpose.value,
            b"status": self.status.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"subject": self.subject_key_digest,
            b"action": self.action.value,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"quarantine": self.quarantine_report_digest,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"prev": self.previous_redress_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"reason": self.reason_code,
        }

    def signature_payload(self) -> bytes:
        return REDRESS_LANE_DOMAIN + b":receipt-sig:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_core_digest(self) -> bytes:
        return sha256(REDRESS_LANE_DOMAIN + b":receipt-core:" + bencode({
            b"kind": self.kind.value,
            b"purpose": self.purpose.value,
            b"status": self.status.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"subject": self.subject_key_digest,
            b"action": self.action.value,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"quarantine": self.quarantine_report_digest,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"prev": self.previous_redress_digest,
            b"reason": self.reason_code,
        }))

    @property
    def receipt_digest(self) -> bytes:
        return sha256(REDRESS_LANE_DOMAIN + b":receipt-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class RedressReport:
    decision_kind: RedressDecisionKind
    accept: bool
    lifted: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: ModerationAction
    subject_key_digest: bytes
    quarantine_report_digest: bytes
    receipt_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")



def make_redress_receipt(
    *,
    keypair: DhtKeypair,
    kind: RedressKind,
    purpose: RedressPurpose,
    status: RedressStatus,
    profile_id: str,
    service_name: str,
    subject_key_digest: bytes,
    action: ModerationAction,
    scope_digest: bytes,
    request_digest: bytes,
    quarantine_report_digest: bytes,
    evidence_digest: bytes,
    sequence: int,
    previous_redress_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    reason_code: str = "",
) -> RedressReceipt:
    receipt = RedressReceipt(kind, purpose, status, profile_id, service_name, subject_key_digest, action, scope_digest, request_digest, quarantine_report_digest, evidence_digest, sequence, previous_redress_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes, reason_code)
    return replace(receipt, signature=keypair.sign(receipt.signature_payload()))



def _report(kind: RedressDecisionKind, accept: bool, lifted: bool, watch: bool, reason: str, *, moderation: ModerationQuarantineReport, receipts: Iterable[RedressReceipt] = (), family_count: int = 0, path_family_count: int = 0, highest_sequence: int = -1) -> RedressReport:
    receipt_tuple = tuple(sorted(receipts, key=lambda item: (item.sequence, item.receipt_digest)))
    digests = tuple(sorted(item.receipt_digest for item in receipt_tuple if accept or watch or kind.value.startswith("hold_")))
    digest = sha256(REDRESS_LANE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"lifted": 1 if lifted else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": moderation.profile_id,
        b"service": moderation.service_name,
        b"action": moderation.action.value,
        b"subject": moderation.subject_key_digest,
        b"quarantine": moderation.report_digest,
        b"receipts": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"highest": highest_sequence,
    }))
    return RedressReport(kind, accept, lifted, watch, reason, moderation.profile_id, moderation.service_name, moderation.action, moderation.subject_key_digest, moderation.report_digest, digests, family_count, path_family_count, highest_sequence, digest)



def _required_for_purpose(purpose: RedressPurpose) -> set[RedressKind]:
    if purpose is RedressPurpose.LIFT:
        return {RedressKind.SUBJECT_COUNTERSIGN, RedressKind.MODERATOR_ACK, RedressKind.WITNESS_OBSERVATION, RedressKind.HARD_NEGATIVE_SCAN}
    if purpose is RedressPurpose.NARROW:
        return {RedressKind.SUBJECT_COUNTERSIGN, RedressKind.MODERATOR_ACK, RedressKind.HARD_NEGATIVE_SCAN}
    return {RedressKind.SUBJECT_COUNTERSIGN, RedressKind.HARD_NEGATIVE_SCAN}



def assess_redress(
    receipts: Iterable[RedressReceipt],
    *,
    moderation: ModerationQuarantineReport,
    now: int,
    purpose: RedressPurpose = RedressPurpose.LIFT,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previous_sequence: int | None = None,
    previous_redress_digest: bytes | None = None,
    previously_seen_receipts: Iterable[bytes] = (),
    live_hard_negative_digests: Iterable[bytes] = (),
    min_family_diversity: int = 3,
    min_path_diversity: int = 2,
    allow_watch: bool = False,
) -> RedressReport:
    purpose = RedressPurpose(purpose)
    if not moderation.blocked:
        return _report(RedressDecisionKind.ACCEPT_NOT_NEEDED, True, False, moderation.watch, "moderation is not blocking", moderation=moderation)
    if not moderation.appeal_allowed:
        return _report(RedressDecisionKind.HOLD_APPEAL_NOT_ALLOWED, False, False, False, "moderation capsule does not allow local redress", moderation=moderation)
    if tuple(live_hard_negative_digests):
        return _report(RedressDecisionKind.QUARANTINE_HARD_NEGATIVE_LIVE, False, False, False, "live hard-negative evidence blocks redress", moderation=moderation)
    receipt_tuple = tuple(sorted(receipts, key=lambda item: (item.kind.value, item.sequence, item.receipt_digest)))
    seen = set(previously_seen_receipts)
    families: set[str] = set()
    paths: set[str] = set()
    fork_guard: dict[tuple[RedressKind, int], bytes] = {}
    by_kind: dict[RedressKind, RedressReceipt] = {}
    highest = -1
    watch = False
    for receipt in receipt_tuple:
        if not receipt.verifies():
            return _report(RedressDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, False, "bad redress receipt signature", moderation=moderation, receipts=receipt_tuple)
        if receipt.issued_at > now or receipt.expires_at <= now:
            return _report(RedressDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, False, "redress receipt expired or future", moderation=moderation, receipts=receipt_tuple)
        if receipt.receipt_digest in seen:
            return _report(RedressDecisionKind.QUARANTINE_REPLAY, False, False, False, "redress receipt replay", moderation=moderation, receipts=receipt_tuple)
        if receipt.profile_id != moderation.profile_id:
            return _report(RedressDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, False, "redress profile drift", moderation=moderation, receipts=receipt_tuple)
        if receipt.service_name != moderation.service_name:
            return _report(RedressDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, False, "redress service drift", moderation=moderation, receipts=receipt_tuple)
        if receipt.subject_key_digest != moderation.subject_key_digest:
            return _report(RedressDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, False, False, "redress subject drift", moderation=moderation, receipts=receipt_tuple)
        if receipt.action is not moderation.action:
            return _report(RedressDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, False, "redress action drift", moderation=moderation, receipts=receipt_tuple)
        if receipt.scope_digest != expected_scope_digest:
            return _report(RedressDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, "redress scope drift", moderation=moderation, receipts=receipt_tuple)
        if receipt.request_digest != expected_request_digest:
            return _report(RedressDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, False, "redress request drift", moderation=moderation, receipts=receipt_tuple)
        if receipt.quarantine_report_digest != moderation.report_digest:
            return _report(RedressDecisionKind.QUARANTINE_QUARANTINE_DIGEST_DRIFT, False, False, False, "redress does not bind moderation report", moderation=moderation, receipts=receipt_tuple)
        if receipt.purpose is not purpose:
            # Purpose drift is semantically equivalent to missing required evidence for this exact redress action.
            continue
        if previous_sequence is not None and receipt.sequence < previous_sequence:
            return _report(RedressDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, "redress sequence rollback", moderation=moderation, receipts=receipt_tuple)
        prior = fork_guard.get((receipt.kind, receipt.sequence))
        if prior is not None and prior != receipt.receipt_core_digest:
            return _report(RedressDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, "same-kind same-sequence redress fork", moderation=moderation, receipts=receipt_tuple)
        fork_guard[(receipt.kind, receipt.sequence)] = receipt.receipt_core_digest
        if receipt.status is RedressStatus.REFUSE:
            return _report(RedressDecisionKind.QUARANTINE_REFUSAL, False, False, False, "redress receipt refuses the request", moderation=moderation, receipts=receipt_tuple)
        if receipt.status is RedressStatus.WATCH:
            watch = True
        families.add(receipt.family_id)
        paths.add(receipt.path_family)
        highest = max(highest, receipt.sequence)
        current = by_kind.get(receipt.kind)
        if current is None or receipt.sequence > current.sequence:
            by_kind[receipt.kind] = receipt
    required = _required_for_purpose(purpose)
    selected = tuple(by_kind[kind] for kind in sorted(required, key=lambda item: item.value) if kind in by_kind)
    if len(selected) != len(required):
        return _report(RedressDecisionKind.HOLD_MISSING_REDRESS_EVIDENCE, False, False, watch, "missing redress evidence kind", moderation=moderation, receipts=selected, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if previous_sequence is not None and highest > previous_sequence and previous_redress_digest is not None:
        if not any(item.previous_redress_digest == previous_redress_digest for item in selected):
            return _report(RedressDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, watch, "redress previous-link mismatch", moderation=moderation, receipts=selected, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if watch and not allow_watch:
        return _report(RedressDecisionKind.HOLD_REDRESS_WATCH, False, False, True, "redress contains watch evidence", moderation=moderation, receipts=selected, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if len(families) < min_family_diversity:
        return _report(RedressDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, False, watch, "redress lacks family diversity", moderation=moderation, receipts=selected, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if len(paths) < min_path_diversity:
        return _report(RedressDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, False, watch, "redress lacks path diversity", moderation=moderation, receipts=selected, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if purpose is RedressPurpose.LIFT:
        return _report(RedressDecisionKind.ACCEPT_LIFT, True, True, watch, "redress lifts the subjective local block", moderation=moderation, receipts=selected, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if purpose is RedressPurpose.NARROW:
        return _report(RedressDecisionKind.ACCEPT_NARROW, True, False, True, "redress narrows block to watch pressure", moderation=moderation, receipts=selected, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    return _report(RedressDecisionKind.ACCEPT_WATCH_ONLY, True, False, True, "redress converts block to watch-only pressure", moderation=moderation, receipts=selected, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
