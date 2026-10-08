"""rev0079 retention audit after summary export receipt and import gate.

Export/import readiness can tempt cleanup.  This lane makes retention explicit:
redaction memory, contradiction memory, and export/import evidence must survive
before any future local compaction treats the redacted export edge as safe.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

EXPORT_RETENTION_AUDIT_DOMAIN = DOMAIN + b":export-retention-audit-v1:"


class ExportRetentionClass(str, Enum):
    EXPORT_RECEIPT = "export_receipt"
    IMPORT_GATE = "import_gate"
    EXPORT_FENCE = "export_fence"
    RETENTION_POLICY = "retention_policy"
    REDACTION_MEMORY = "redaction_memory"
    CONTRADICTION_MEMORY = "contradiction_memory"


class ExportRetentionDecisionKind(str, Enum):
    ACCEPT_EXPORT_RETENTION_AUDITED = "accept_export_retention_audited"
    HOLD_RECEIPT_PENDING = "hold_receipt_pending"
    HOLD_IMPORT_PENDING = "hold_import_pending"
    HOLD_EXPORT_PENDING = "hold_export_pending"
    HOLD_MISSING_REQUIRED_CLASS = "hold_missing_required_class"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_RAW_LEAK = "quarantine_raw_leak"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_REDACTION_DROPPED = "quarantine_redaction_dropped"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ExportRetentionMarker:
    retention_class: ExportRetentionClass
    sequence: int
    previous_digest: bytes
    retention_action: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_export_receipt_digest: bytes
    summary_import_gate_digest: bytes
    summary_export_fence_digest: bytes
    accepted_receipt_marker_digest: bytes
    accepted_import_marker_digest: bytes
    accepted_export_marker_digest: bytes
    redacted_summary_digest: bytes
    contradiction_carried: bool
    redaction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(EXPORT_RETENTION_AUDIT_DOMAIN + b":marker:" + bencode({
            b"class": ExportRetentionClass(self.retention_class).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"retention_action": self.retention_action,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"receipt": self.summary_export_receipt_digest,
            b"import": self.summary_import_gate_digest,
            b"export": self.summary_export_fence_digest,
            b"receipt_marker": self.accepted_receipt_marker_digest,
            b"import_marker": self.accepted_import_marker_digest,
            b"export_marker": self.accepted_export_marker_digest,
            b"redacted_summary": self.redacted_summary_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"redaction": 1 if self.redaction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ExportRetentionAuditReport:
    decision_kind: ExportRetentionDecisionKind
    accept: bool
    watch: bool
    export_retention_audited: bool
    retention_safe: bool
    retention_action: str
    contradiction_preserved: bool
    contradiction_carried: bool
    redacted: bool
    redaction_carried: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_export_receipt_digest: bytes
    summary_import_gate_digest: bytes
    summary_export_fence_digest: bytes
    accepted_marker_digest: bytes
    accepted_receipt_marker_digest: bytes
    accepted_import_marker_digest: bytes
    accepted_export_marker_digest: bytes
    redacted_summary_digest: bytes
    class_values: tuple[str, ...]
    marker_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_proposal_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"), getattr(report, "retry_idempotency_key", ZERO_DIGEST)
    )


def _marker_boundary(marker: ExportRetentionMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key, marker.retry_idempotency_key)


def make_export_retention_marker(*, retention_class: ExportRetentionClass, sequence: int, summary_export_receipt_report: Any, summary_import_gate_report: Any, summary_export_fence_report: Any, previous_digest: bytes = ZERO_DIGEST, retention_action: str = "retain_redacted", contradiction_carried: bool = True, redaction_carried: bool = True, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "export-retention-family", path_family_id: str = "export-retention-path", hard_negative_count: int = 0) -> ExportRetentionMarker:
    return ExportRetentionMarker(
        retention_class=ExportRetentionClass(retention_class), sequence=sequence, previous_digest=previous_digest, retention_action=retention_action,
        action=SideEffectAction(getattr(summary_import_gate_report, "action")), profile_id=getattr(summary_import_gate_report, "profile_id"), service_name=getattr(summary_import_gate_report, "service_name"), scope_digest=getattr(summary_import_gate_report, "scope_digest"), request_digest=getattr(summary_import_gate_report, "request_digest"), payload_digest=getattr(summary_import_gate_report, "payload_digest"), idempotency_key=getattr(summary_import_gate_report, "idempotency_key"), retry_idempotency_key=getattr(summary_import_gate_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_export_receipt_digest=_digest(summary_export_receipt_report), summary_import_gate_digest=_digest(summary_import_gate_report), summary_export_fence_digest=_digest(summary_export_fence_report), accepted_receipt_marker_digest=getattr(summary_export_receipt_report, "accepted_marker_digest", ZERO_DIGEST), accepted_import_marker_digest=getattr(summary_import_gate_report, "accepted_marker_digest", ZERO_DIGEST), accepted_export_marker_digest=getattr(summary_export_fence_report, "accepted_marker_digest", ZERO_DIGEST), redacted_summary_digest=getattr(summary_import_gate_report, "redacted_summary_digest", ZERO_DIGEST), contradiction_carried=contradiction_carried, redaction_carried=redaction_carried, raw_boundary_exposed=raw_boundary_exposed, raw_payload_exposed=raw_payload_exposed, family_id=family_id, path_family_id=path_family_id, hard_negative_count=hard_negative_count,
    )


def _report(kind: ExportRetentionDecisionKind, accept: bool, watch: bool, audited: bool, contradiction: bool, redacted: bool, reason: str, *, summary_export_receipt_report: Any, summary_import_gate_report: Any, summary_export_fence_report: Any, markers: tuple[ExportRetentionMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> ExportRetentionAuditReport:
    class_values = tuple(sorted({marker.retention_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    actions = {marker.retention_action for marker in markers}
    retention_action = sorted(actions)[0] if len(actions) == 1 else "mixed"
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_export_receipt_report, summary_import_gate_report, summary_export_fence_report)) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(EXPORT_RETENTION_AUDIT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0, b"audited": 1 if audited else 0, b"retention_action": retention_action,
        b"receipt": _digest(summary_export_receipt_report), b"import": _digest(summary_import_gate_report), b"export": _digest(summary_export_fence_report), b"accepted": accepted_marker_digest, b"classes": list(class_values), b"markers": list(marker_digests), b"families": len(families), b"paths": len(paths), b"contradiction": 1 if contradiction else 0, b"redacted": 1 if redacted else 0, b"hard": hard, b"reason": reason,
    }))
    return ExportRetentionAuditReport(kind, accept, watch, audited, audited, retention_action, contradiction, contradiction, redacted, redacted, reason, SideEffectAction(getattr(summary_import_gate_report, "action")), getattr(summary_import_gate_report, "profile_id"), getattr(summary_import_gate_report, "service_name"), getattr(summary_import_gate_report, "scope_digest"), getattr(summary_import_gate_report, "request_digest"), getattr(summary_import_gate_report, "payload_digest"), getattr(summary_import_gate_report, "idempotency_key"), getattr(summary_import_gate_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_export_receipt_report), _digest(summary_import_gate_report), _digest(summary_export_fence_report), accepted_marker_digest, getattr(summary_export_receipt_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_import_gate_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_export_fence_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_import_gate_report, "redacted_summary_digest", ZERO_DIGEST), class_values, marker_digests, len(families), len(paths), hard, report_digest)


def assess_export_retention_audit(*, summary_export_receipt_report: Any, summary_import_gate_report: Any, summary_export_fence_report: Any, markers: tuple[ExportRetentionMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[ExportRetentionClass, ...] = (ExportRetentionClass.EXPORT_RECEIPT, ExportRetentionClass.IMPORT_GATE, ExportRetentionClass.EXPORT_FENCE, ExportRetentionClass.RETENTION_POLICY, ExportRetentionClass.REDACTION_MEMORY, ExportRetentionClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> ExportRetentionAuditReport:
    markers = tuple(markers)
    if not getattr(summary_export_receipt_report, "summary_export_receipted", False):
        return _report(ExportRetentionDecisionKind.HOLD_RECEIPT_PENDING, False, True, False, False, False, "receipt pending", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if not getattr(summary_import_gate_report, "summary_import_gated", False):
        return _report(ExportRetentionDecisionKind.HOLD_IMPORT_PENDING, False, True, False, False, False, "import pending", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if not getattr(summary_export_fence_report, "summary_export_fenced", False):
        return _report(ExportRetentionDecisionKind.HOLD_EXPORT_PENDING, False, True, False, False, False, "export pending", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    boundary = _boundary(summary_import_gate_report)
    if _boundary(summary_export_receipt_report) != boundary or _boundary(summary_export_fence_report) != boundary or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(ExportRetentionDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if getattr(summary_import_gate_report, "summary_export_receipt_digest", ZERO_DIGEST) != _digest(summary_export_receipt_report) or getattr(summary_import_gate_report, "summary_export_fence_digest", ZERO_DIGEST) != _digest(summary_export_fence_report) or getattr(summary_export_receipt_report, "summary_export_fence_digest", ZERO_DIGEST) != _digest(summary_export_fence_report):
        return _report(ExportRetentionDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    for marker in markers:
        if marker.summary_export_receipt_digest != _digest(summary_export_receipt_report) or marker.summary_import_gate_digest != _digest(summary_import_gate_report) or marker.summary_export_fence_digest != _digest(summary_export_fence_report):
            return _report(ExportRetentionDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "marker digest drift", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(ExportRetentionDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw leak", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    contradiction = bool(getattr(summary_export_receipt_report, "contradiction_preserved", False) and getattr(summary_import_gate_report, "contradiction_preserved", False) and getattr(summary_export_fence_report, "contradiction_preserved", False) and all(marker.contradiction_carried for marker in markers))
    if not contradiction:
        return _report(ExportRetentionDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction dropped", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    redacted = bool(getattr(summary_export_receipt_report, "redacted", False) and getattr(summary_import_gate_report, "redacted", False) and getattr(summary_export_fence_report, "redacted", False) and all(marker.redaction_carried for marker in markers))
    if not redacted:
        return _report(ExportRetentionDecisionKind.QUARANTINE_REDACTION_DROPPED, False, True, False, True, False, "redaction dropped", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_export_receipt_report, summary_import_gate_report, summary_export_fence_report)) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(ExportRetentionDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "hard negatives", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if not set(required_classes).issubset({marker.retention_class for marker in markers}):
        return _report(ExportRetentionDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing class", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(ExportRetentionDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed marker", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(ExportRetentionDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        if marker.sequence in seen_sequences and seen_sequences[marker.sequence] != digest:
            return _report(ExportRetentionDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        seen_sequences[marker.sequence] = digest
        if marker.previous_digest != previous:
            return _report(ExportRetentionDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous mismatch", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        previous = digest
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(ExportRetentionDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(ExportRetentionDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    accepted = previous if markers else ZERO_DIGEST
    return _report(ExportRetentionDecisionKind.ACCEPT_EXPORT_RETENTION_AUDITED, True, False, True, True, redacted, "export retention audit accepted", summary_export_receipt_report=summary_export_receipt_report, summary_import_gate_report=summary_import_gate_report, summary_export_fence_report=summary_export_fence_report, markers=markers, accepted_marker_digest=accepted)
