"""rev0070 export receipt restart memory after redacted audit export.

rev0069 prepared redacted audit export bundles, but preparation is not receipt.
A garden/operator/public-summary observer may claim it received a redacted bundle;
that claim is useful only if it carries the same exact boundary, preserves
contradiction memory, avoids raw boundary/payload leakage, and survives local
sequence/replay pressure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .auditexport import AuditExportAudience
from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

EXPORT_RECEIPT_DOMAIN = DOMAIN + b":export-receipt-v1:"


class ExportReceiptKind(str, Enum):
    OPERATOR_RECEIPT = "operator_receipt"
    GARDEN_RECEIPT = "garden_receipt"
    PUBLIC_SUMMARY_RECEIPT = "public_summary_receipt"


class ExportReceiptDecisionKind(str, Enum):
    ACCEPT_EXPORT_RECEIPTED = "accept_export_receipted"
    HOLD_EXPORT_PENDING = "hold_export_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_RAW_LEAK = "quarantine_raw_leak"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ExportReceiptEntry:
    kind: ExportReceiptKind
    audience: AuditExportAudience
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    audit_export_digest: bytes
    accepted_bundle_digest: bytes
    closure_seal_digest: bytes
    retention_proof_digest: bytes
    redacted_receipt_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(EXPORT_RECEIPT_DOMAIN + b":entry:" + bencode({
            b"kind": self.kind.value,
            b"audience": self.audience.value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"export": self.audit_export_digest,
            b"bundle": self.accepted_bundle_digest,
            b"seal": self.closure_seal_digest,
            b"retention": self.retention_proof_digest,
            b"receipt": self.redacted_receipt_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ExportReceiptReport:
    decision_kind: ExportReceiptDecisionKind
    accept: bool
    watch: bool
    export_receipted: bool
    contradiction_carried: bool
    redacted: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    audit_export_digest: bytes
    closure_seal_digest: bytes
    retention_proof_digest: bytes
    accepted_receipt_digest: bytes
    entry_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_bundle_digest", "accepted_entry_digest", "accepted_marker_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(report, "action")),
        getattr(report, "profile_id"),
        getattr(report, "service_name"),
        getattr(report, "scope_digest"),
        getattr(report, "request_digest"),
        getattr(report, "payload_digest"),
        getattr(report, "idempotency_key"),
    )


def _entry_boundary(entry: ExportReceiptEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_export_receipt_entry(*, kind: ExportReceiptKind, sequence: int, audit_export_report: Any, previous_digest: bytes = ZERO_DIGEST, audience: AuditExportAudience | None = None, redacted_receipt_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "export-receipt-family-a", path_family_id: str = "export-receipt-path-a", hard_negative_count: int = 0) -> ExportReceiptEntry:
    receipt_audience = AuditExportAudience(getattr(audit_export_report, "audience", AuditExportAudience.LOCAL_OPERATOR) if audience is None else audience)
    contradiction = bool(getattr(audit_export_report, "contradiction_carried", False)) if contradiction_carried is None else bool(contradiction_carried)
    receipt_digest = redacted_receipt_digest or sha256(EXPORT_RECEIPT_DOMAIN + b":redacted-receipt:" + _digest(audit_export_report) + b":" + receipt_audience.value.encode())
    return ExportReceiptEntry(
        kind=ExportReceiptKind(kind),
        audience=receipt_audience,
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(audit_export_report, "action")),
        profile_id=getattr(audit_export_report, "profile_id"),
        service_name=getattr(audit_export_report, "service_name"),
        scope_digest=getattr(audit_export_report, "scope_digest"),
        request_digest=getattr(audit_export_report, "request_digest"),
        payload_digest=getattr(audit_export_report, "payload_digest"),
        idempotency_key=getattr(audit_export_report, "idempotency_key"),
        retry_idempotency_key=getattr(audit_export_report, "retry_idempotency_key", ZERO_DIGEST),
        audit_export_digest=_digest(audit_export_report),
        accepted_bundle_digest=getattr(audit_export_report, "accepted_bundle_digest", ZERO_DIGEST),
        closure_seal_digest=getattr(audit_export_report, "closure_seal_digest", ZERO_DIGEST),
        retention_proof_digest=getattr(audit_export_report, "retention_proof_digest", ZERO_DIGEST),
        redacted_receipt_digest=receipt_digest,
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: ExportReceiptDecisionKind, accept: bool, watch: bool, receipted: bool, contradiction: bool, redacted: bool, reason: str, *, audit_export_report: Any, entries: tuple[ExportReceiptEntry, ...], accepted_receipt_digest: bytes = ZERO_DIGEST) -> ExportReceiptReport:
    digests = tuple(entry.entry_digest for entry in entries)
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    hard = int(getattr(audit_export_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    report_digest = sha256(EXPORT_RECEIPT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"receipted": 1 if receipted else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(audit_export_report, "action")).value,
        b"profile": getattr(audit_export_report, "profile_id"),
        b"service": getattr(audit_export_report, "service_name"),
        b"scope": getattr(audit_export_report, "scope_digest"),
        b"request": getattr(audit_export_report, "request_digest"),
        b"payload": getattr(audit_export_report, "payload_digest"),
        b"idem": getattr(audit_export_report, "idempotency_key"),
        b"retry_idem": getattr(audit_export_report, "retry_idempotency_key", ZERO_DIGEST),
        b"export": _digest(audit_export_report),
        b"seal": getattr(audit_export_report, "closure_seal_digest", ZERO_DIGEST),
        b"retention": getattr(audit_export_report, "retention_proof_digest", ZERO_DIGEST),
        b"accepted": accepted_receipt_digest,
        b"entries": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return ExportReceiptReport(kind, accept, watch, receipted, contradiction, redacted, reason, SideEffectAction(getattr(audit_export_report, "action")), getattr(audit_export_report, "profile_id"), getattr(audit_export_report, "service_name"), getattr(audit_export_report, "scope_digest"), getattr(audit_export_report, "request_digest"), getattr(audit_export_report, "payload_digest"), getattr(audit_export_report, "idempotency_key"), getattr(audit_export_report, "retry_idempotency_key", ZERO_DIGEST), _digest(audit_export_report), getattr(audit_export_report, "closure_seal_digest", ZERO_DIGEST), getattr(audit_export_report, "retention_proof_digest", ZERO_DIGEST), accepted_receipt_digest, digests, len(families), len(paths), hard, report_digest)


def assess_export_receipts(*, audit_export_report: Any, entries: tuple[ExportReceiptEntry, ...] = (), previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2) -> ExportReceiptReport:
    if not bool(getattr(audit_export_report, "accept", False)) or not bool(getattr(audit_export_report, "export_prepared", False)):
        return _report(ExportReceiptDecisionKind.HOLD_EXPORT_PENDING, False, True, False, False, False, "audit export is not accepted/prepared", audit_export_report=audit_export_report, entries=entries)
    if not entries:
        return _report(ExportReceiptDecisionKind.HOLD_EXPORT_PENDING, False, True, False, False, bool(getattr(audit_export_report, "redacted", False)), "no export receipts", audit_export_report=audit_export_report, entries=entries)
    for entry in entries:
        if _entry_boundary(entry) != _boundary(audit_export_report):
            return _report(ExportReceiptDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "receipt boundary drift", audit_export_report=audit_export_report, entries=entries)
        if entry.audit_export_digest != _digest(audit_export_report) or entry.accepted_bundle_digest != getattr(audit_export_report, "accepted_bundle_digest", ZERO_DIGEST):
            return _report(ExportReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "receipt/export digest drift", audit_export_report=audit_export_report, entries=entries)
        if entry.closure_seal_digest != getattr(audit_export_report, "closure_seal_digest", ZERO_DIGEST) or entry.retention_proof_digest != getattr(audit_export_report, "retention_proof_digest", ZERO_DIGEST):
            return _report(ExportReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "closure/retention digest drift", audit_export_report=audit_export_report, entries=entries)
        if entry.raw_boundary_exposed or entry.raw_payload_exposed:
            return _report(ExportReceiptDecisionKind.QUARANTINE_RAW_LEAK, False, False, False, entry.contradiction_carried, False, "receipt leaked raw boundary/payload", audit_export_report=audit_export_report, entries=entries)
    sorted_entries = sorted(entries, key=lambda entry: entry.sequence)
    if sorted_entries[0].sequence <= 0:
        return _report(ExportReceiptDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "non-positive sequence", audit_export_report=audit_export_report, entries=entries)
    last = previous_digest
    by_seq: dict[int, bytes] = {}
    for entry in sorted_entries:
        digest = entry.entry_digest
        if entry.sequence in by_seq:
            if by_seq[entry.sequence] == digest:
                return _report(ExportReceiptDecisionKind.QUARANTINE_REPLAY, False, False, False, entry.contradiction_carried, True, "duplicate receipt replay", audit_export_report=audit_export_report, entries=entries)
            return _report(ExportReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, entry.contradiction_carried, True, "same sequence different receipt", audit_export_report=audit_export_report, entries=entries)
        by_seq[entry.sequence] = digest
        if entry.previous_digest != last:
            return _report(ExportReceiptDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, entry.contradiction_carried, True, "receipt previous digest mismatch", audit_export_report=audit_export_report, entries=entries)
        last = digest
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    contradiction = any(entry.contradiction_carried for entry in entries)
    if len(families) < min_family_count:
        return _report(ExportReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, contradiction, True, "not enough receipt family diversity", audit_export_report=audit_export_report, entries=entries)
    if len(paths) < min_path_family_count:
        return _report(ExportReceiptDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, contradiction, True, "not enough receipt path diversity", audit_export_report=audit_export_report, entries=entries)
    if bool(getattr(audit_export_report, "contradiction_carried", False)) and not contradiction:
        return _report(ExportReceiptDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, True, "contradiction not carried into export receipt", audit_export_report=audit_export_report, entries=entries)
    if int(getattr(audit_export_report, "hard_negative_count", 0) or 0) or any(entry.hard_negative_count for entry in entries):
        return _report(ExportReceiptDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, contradiction, True, "live hard-negative pressure on export receipt", audit_export_report=audit_export_report, entries=entries)
    return _report(ExportReceiptDecisionKind.ACCEPT_EXPORT_RECEIPTED, True, False, True, contradiction, True, "export receipt accepted", audit_export_report=audit_export_report, entries=entries, accepted_receipt_digest=sorted_entries[-1].entry_digest)
