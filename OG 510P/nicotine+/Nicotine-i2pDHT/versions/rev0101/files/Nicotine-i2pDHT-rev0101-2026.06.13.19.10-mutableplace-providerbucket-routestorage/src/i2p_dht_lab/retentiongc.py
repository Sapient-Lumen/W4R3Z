"""rev0070 retention-GC after export receipt.

Retention proof in rev0069 says important evidence is retained.  After an export
is actually receipted, some soft working material may be compacted, but required
markers, contradiction memory, and hard-negative memory cannot be deleted by a
convenient GC pass.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

RETENTION_GC_DOMAIN = DOMAIN + b":retention-gc-v1:"


class RetentionGcClass(str, Enum):
    CLOSURE_SEAL_MARKER = "closure_seal_marker"
    RETENTION_PROOF_MARKER = "retention_proof_marker"
    EXPORT_RECEIPT_MARKER = "export_receipt_marker"
    CONTRADICTION_MEMORY = "contradiction_memory"
    REDACTED_EXPORT_SUMMARY = "redacted_export_summary"
    HARD_NEGATIVE_MARKER = "hard_negative_marker"
    SOFT_WORKING_SET = "soft_working_set"


class RetentionGcDecisionKind(str, Enum):
    ACCEPT_RETENTION_GC = "accept_retention_gc"
    HOLD_EXPORT_RECEIPT_PENDING = "hold_export_receipt_pending"
    HOLD_RETENTION_PROOF_PENDING = "hold_retention_proof_pending"
    HOLD_MISSING_REQUIRED_CLASS = "hold_missing_required_class"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_DROPPED = "quarantine_hard_negative_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RetentionGcMarker:
    gc_class: RetentionGcClass
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
    export_receipt_digest: bytes
    retention_proof_digest: bytes
    closure_seal_digest: bytes
    retained: bool
    retained_digest: bytes
    contradiction_carried: bool
    hard_negative_carried: bool
    family_id: str
    path_family_id: str
    reclaimed_bytes: int = 0
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(RETENTION_GC_DOMAIN + b":marker:" + bencode({
            b"class": self.gc_class.value,
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
            b"receipt": self.export_receipt_digest,
            b"retention": self.retention_proof_digest,
            b"seal": self.closure_seal_digest,
            b"retained": 1 if self.retained else 0,
            b"retained_digest": self.retained_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"hard_carried": 1 if self.hard_negative_carried else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"reclaimed": self.reclaimed_bytes,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RetentionGcReport:
    decision_kind: RetentionGcDecisionKind
    accept: bool
    watch: bool
    retention_gc_applied: bool
    contradiction_preserved: bool
    hard_negative_preserved: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    export_receipt_digest: bytes
    retention_proof_digest: bytes
    closure_seal_digest: bytes
    accepted_marker_digest: bytes
    retained_classes: tuple[str, ...]
    reclaimed_bytes: int
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
    for attr in ("report_digest", "accepted_receipt_digest", "accepted_item_digest", "accepted_entry_digest", "accepted_marker_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: RetentionGcMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_retention_gc_marker(*, gc_class: RetentionGcClass, sequence: int, export_receipt_report: Any, retention_proof_report: Any, previous_digest: bytes = ZERO_DIGEST, retained: bool | None = None, retained_digest: bytes | None = None, contradiction_carried: bool | None = None, hard_negative_carried: bool = False, family_id: str = "retention-gc-family-a", path_family_id: str = "retention-gc-path-a", reclaimed_bytes: int = 0, hard_negative_count: int = 0) -> RetentionGcMarker:
    cls = RetentionGcClass(gc_class)
    keep = cls is not RetentionGcClass.SOFT_WORKING_SET if retained is None else bool(retained)
    contradiction = bool(getattr(export_receipt_report, "contradiction_carried", False)) if cls is RetentionGcClass.CONTRADICTION_MEMORY and contradiction_carried is None else bool(contradiction_carried or False)
    digest = retained_digest or sha256(RETENTION_GC_DOMAIN + b":retained:" + cls.value.encode() + b":" + _digest(export_receipt_report))
    return RetentionGcMarker(
        gc_class=cls,
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(export_receipt_report, "action")),
        profile_id=getattr(export_receipt_report, "profile_id"),
        service_name=getattr(export_receipt_report, "service_name"),
        scope_digest=getattr(export_receipt_report, "scope_digest"),
        request_digest=getattr(export_receipt_report, "request_digest"),
        payload_digest=getattr(export_receipt_report, "payload_digest"),
        idempotency_key=getattr(export_receipt_report, "idempotency_key"),
        retry_idempotency_key=getattr(export_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        export_receipt_digest=_digest(export_receipt_report),
        retention_proof_digest=_digest(retention_proof_report),
        closure_seal_digest=getattr(export_receipt_report, "closure_seal_digest", getattr(retention_proof_report, "closure_seal_digest", ZERO_DIGEST)),
        retained=keep,
        retained_digest=digest,
        contradiction_carried=contradiction,
        hard_negative_carried=bool(hard_negative_carried),
        family_id=family_id,
        path_family_id=path_family_id,
        reclaimed_bytes=int(reclaimed_bytes),
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RetentionGcDecisionKind, accept: bool, watch: bool, applied: bool, contradiction: bool, hard_preserved: bool, reason: str, *, export_receipt_report: Any, retention_proof_report: Any, markers: tuple[RetentionGcMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> RetentionGcReport:
    digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    retained = tuple(sorted(marker.gc_class.value for marker in markers if marker.retained))
    reclaimed = sum(marker.reclaimed_bytes for marker in markers)
    hard = int(getattr(export_receipt_report, "hard_negative_count", 0) or 0) + int(getattr(retention_proof_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(RETENTION_GC_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"applied": 1 if applied else 0,
        b"contradiction": 1 if contradiction else 0,
        b"hard_preserved": 1 if hard_preserved else 0,
        b"action": SideEffectAction(getattr(export_receipt_report, "action")).value,
        b"profile": getattr(export_receipt_report, "profile_id"),
        b"service": getattr(export_receipt_report, "service_name"),
        b"scope": getattr(export_receipt_report, "scope_digest"),
        b"request": getattr(export_receipt_report, "request_digest"),
        b"payload": getattr(export_receipt_report, "payload_digest"),
        b"idem": getattr(export_receipt_report, "idempotency_key"),
        b"retry_idem": getattr(export_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        b"receipt": _digest(export_receipt_report),
        b"retention": _digest(retention_proof_report),
        b"seal": getattr(export_receipt_report, "closure_seal_digest", getattr(retention_proof_report, "closure_seal_digest", ZERO_DIGEST)),
        b"accepted": accepted_marker_digest,
        b"retained": list(retained),
        b"markers": list(digests),
        b"reclaimed": reclaimed,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return RetentionGcReport(kind, accept, watch, applied, contradiction, hard_preserved, reason, SideEffectAction(getattr(export_receipt_report, "action")), getattr(export_receipt_report, "profile_id"), getattr(export_receipt_report, "service_name"), getattr(export_receipt_report, "scope_digest"), getattr(export_receipt_report, "request_digest"), getattr(export_receipt_report, "payload_digest"), getattr(export_receipt_report, "idempotency_key"), getattr(export_receipt_report, "retry_idempotency_key", ZERO_DIGEST), _digest(export_receipt_report), _digest(retention_proof_report), getattr(export_receipt_report, "closure_seal_digest", getattr(retention_proof_report, "closure_seal_digest", ZERO_DIGEST)), accepted_marker_digest, retained, reclaimed, digests, len(families), len(paths), hard, report_digest)


def assess_retention_gc(*, export_receipt_report: Any, retention_proof_report: Any, markers: tuple[RetentionGcMarker, ...] = (), previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2) -> RetentionGcReport:
    if not bool(getattr(export_receipt_report, "accept", False)) or not bool(getattr(export_receipt_report, "export_receipted", False)):
        return _report(RetentionGcDecisionKind.HOLD_EXPORT_RECEIPT_PENDING, False, True, False, False, False, "export receipt not accepted", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    if not bool(getattr(retention_proof_report, "accept", False)) or not bool(getattr(retention_proof_report, "retention_proved", False)):
        return _report(RetentionGcDecisionKind.HOLD_RETENTION_PROOF_PENDING, False, True, False, False, False, "retention proof not accepted", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    if _boundary(export_receipt_report) != _boundary(retention_proof_report):
        return _report(RetentionGcDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "receipt/retention boundary drift", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    if not markers:
        return _report(RetentionGcDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, False, "no GC markers", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    for marker in markers:
        if _marker_boundary(marker) != _boundary(export_receipt_report):
            return _report(RetentionGcDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "marker boundary drift", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
        if marker.export_receipt_digest != _digest(export_receipt_report) or marker.retention_proof_digest != _digest(retention_proof_report):
            return _report(RetentionGcDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "marker component digest drift", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    sorted_markers = sorted(markers, key=lambda marker: marker.sequence)
    last = previous_digest
    by_seq: dict[int, bytes] = {}
    for marker in sorted_markers:
        digest = marker.marker_digest
        if marker.sequence <= 0:
            return _report(RetentionGcDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "non-positive marker sequence", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
        if marker.sequence in by_seq:
            if by_seq[marker.sequence] == digest:
                return _report(RetentionGcDecisionKind.QUARANTINE_REPLAY, False, False, False, marker.contradiction_carried, False, "duplicate marker replay", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
            return _report(RetentionGcDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, marker.contradiction_carried, False, "same sequence different marker", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
        by_seq[marker.sequence] = digest
        if marker.previous_digest != last:
            return _report(RetentionGcDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, marker.contradiction_carried, False, "marker previous digest mismatch", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
        last = digest
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    contradiction = any(marker.gc_class is RetentionGcClass.CONTRADICTION_MEMORY and marker.retained and marker.contradiction_carried for marker in markers)
    hard_preserved = any(marker.gc_class is RetentionGcClass.HARD_NEGATIVE_MARKER and marker.retained and marker.hard_negative_carried for marker in markers)
    if len(families) < min_family_count:
        return _report(RetentionGcDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, contradiction, hard_preserved, "not enough GC family diversity", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    if len(paths) < min_path_family_count:
        return _report(RetentionGcDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, contradiction, hard_preserved, "not enough GC path diversity", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    retained = {marker.gc_class for marker in markers if marker.retained}
    required = {RetentionGcClass.CLOSURE_SEAL_MARKER, RetentionGcClass.RETENTION_PROOF_MARKER, RetentionGcClass.EXPORT_RECEIPT_MARKER, RetentionGcClass.REDACTED_EXPORT_SUMMARY}
    if bool(getattr(export_receipt_report, "contradiction_carried", False)) or bool(getattr(retention_proof_report, "contradiction_preserved", False)):
        required.add(RetentionGcClass.CONTRADICTION_MEMORY)
    if not required.issubset(retained):
        return _report(RetentionGcDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, contradiction, hard_preserved, "GC proposal missing required retained class", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    if RetentionGcClass.CONTRADICTION_MEMORY in required and not contradiction:
        return _report(RetentionGcDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, hard_preserved, "contradiction memory dropped by GC", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    component_hard = int(getattr(export_receipt_report, "hard_negative_count", 0) or 0) + int(getattr(retention_proof_report, "hard_negative_count", 0) or 0)
    if component_hard and not hard_preserved:
        return _report(RetentionGcDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED, False, False, False, contradiction, False, "hard negative marker not preserved", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    if any(marker.hard_negative_count for marker in markers):
        return _report(RetentionGcDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, contradiction, hard_preserved, "live hard-negative pressure on GC marker", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers)
    return _report(RetentionGcDecisionKind.ACCEPT_RETENTION_GC, True, False, True, contradiction, component_hard == 0 or hard_preserved, "retention GC accepted", export_receipt_report=export_receipt_report, retention_proof_report=retention_proof_report, markers=markers, accepted_marker_digest=sorted_markers[-1].marker_digest)
