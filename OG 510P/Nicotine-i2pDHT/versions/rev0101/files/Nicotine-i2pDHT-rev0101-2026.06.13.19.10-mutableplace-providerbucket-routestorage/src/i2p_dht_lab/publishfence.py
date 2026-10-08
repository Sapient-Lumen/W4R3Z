"""rev0074 summary publish fence.

Outbox staging, redaction archiving, and import-prune audit are still separate
local observations.  This fence joins them before any later live/public summary
write can treat the redacted summary edge as restart-safe permission.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_PUBLISH_FENCE_DOMAIN = DOMAIN + b":summary-publish-fence-v1:"


class SummaryPublishFenceClass(str, Enum):
    SUMMARY_OUTBOX = "summary_outbox"
    REDACTION_ARCHIVE = "redaction_archive"
    IMPORT_PRUNE_AUDIT = "import_prune_audit"
    CONTRADICTION_MEMORY = "contradiction_memory"


class SummaryPublishFenceDecisionKind(str, Enum):
    ACCEPT_SUMMARY_PUBLISH_FENCED = "accept_summary_publish_fenced"
    HOLD_OUTBOX_PENDING = "hold_outbox_pending"
    HOLD_REDACTION_ARCHIVE_PENDING = "hold_redaction_archive_pending"
    HOLD_IMPORT_PRUNE_AUDIT_PENDING = "hold_import_prune_audit_pending"
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
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SummaryPublishFenceMarker:
    fence_class: SummaryPublishFenceClass
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
    summary_outbox_digest: bytes
    redaction_archive_digest: bytes
    import_prune_audit_digest: bytes
    accepted_outbox_entry_digest: bytes
    accepted_redaction_archive_marker_digest: bytes
    accepted_import_prune_marker_digest: bytes
    contradiction_carried: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(SUMMARY_PUBLISH_FENCE_DOMAIN + b":marker:" + bencode({
            b"class": SummaryPublishFenceClass(self.fence_class).value,
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
            b"outbox": self.summary_outbox_digest,
            b"archive": self.redaction_archive_digest,
            b"audit": self.import_prune_audit_digest,
            b"outbox_entry": self.accepted_outbox_entry_digest,
            b"archive_marker": self.accepted_redaction_archive_marker_digest,
            b"audit_marker": self.accepted_import_prune_marker_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryPublishFenceReport:
    decision_kind: SummaryPublishFenceDecisionKind
    accept: bool
    watch: bool
    summary_publish_fenced: bool
    contradiction_preserved: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_outbox_digest: bytes
    redaction_archive_digest: bytes
    import_prune_audit_digest: bytes
    accepted_marker_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest", "accepted_entry_digest", "accepted_intent_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: SummaryPublishFenceMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_summary_publish_fence_marker(*, fence_class: SummaryPublishFenceClass, sequence: int, summary_outbox_report: Any, redaction_archive_report: Any, import_prune_audit_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_carried: bool | None = None, family_id: str = "summary-fence-family-a", path_family_id: str = "summary-fence-path-a", hard_negative_count: int = 0) -> SummaryPublishFenceMarker:
    contradiction = bool(getattr(summary_outbox_report, "contradiction_carried", False) and getattr(redaction_archive_report, "contradiction_preserved", False) and getattr(import_prune_audit_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    return SummaryPublishFenceMarker(SummaryPublishFenceClass(fence_class), int(sequence), previous_digest, SideEffectAction(getattr(summary_outbox_report, "action")), getattr(summary_outbox_report, "profile_id"), getattr(summary_outbox_report, "service_name"), getattr(summary_outbox_report, "scope_digest"), getattr(summary_outbox_report, "request_digest"), getattr(summary_outbox_report, "payload_digest"), getattr(summary_outbox_report, "idempotency_key"), getattr(summary_outbox_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_outbox_report), _digest(redaction_archive_report), _digest(import_prune_audit_report), getattr(summary_outbox_report, "accepted_entry_digest", ZERO_DIGEST), getattr(redaction_archive_report, "accepted_marker_digest", ZERO_DIGEST), getattr(import_prune_audit_report, "accepted_marker_digest", ZERO_DIGEST), contradiction, family_id, path_family_id, hard_negative_count)


def _report(kind: SummaryPublishFenceDecisionKind, accept: bool, watch: bool, fenced: bool, contradiction: bool, reason: str, *, summary_outbox_report: Any, redaction_archive_report: Any, import_prune_audit_report: Any, markers: tuple[SummaryPublishFenceMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> SummaryPublishFenceReport:
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    classes = tuple(sorted({marker.fence_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    hard = int(getattr(summary_outbox_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_archive_report, "hard_negative_count", 0) or 0) + int(getattr(import_prune_audit_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(SUMMARY_PUBLISH_FENCE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"fenced": 1 if fenced else 0,
        b"contradiction": 1 if contradiction else 0,
        b"action": SideEffectAction(getattr(summary_outbox_report, "action")).value,
        b"profile": getattr(summary_outbox_report, "profile_id"),
        b"service": getattr(summary_outbox_report, "service_name"),
        b"scope": getattr(summary_outbox_report, "scope_digest"),
        b"request": getattr(summary_outbox_report, "request_digest"),
        b"payload": getattr(summary_outbox_report, "payload_digest"),
        b"idem": getattr(summary_outbox_report, "idempotency_key"),
        b"retry_idem": getattr(summary_outbox_report, "retry_idempotency_key", ZERO_DIGEST),
        b"outbox": _digest(summary_outbox_report),
        b"archive": _digest(redaction_archive_report),
        b"audit": _digest(import_prune_audit_report),
        b"accepted": accepted_marker_digest,
        b"classes": list(classes),
        b"markers": list(marker_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return SummaryPublishFenceReport(kind, accept, watch, fenced, contradiction, reason, SideEffectAction(getattr(summary_outbox_report, "action")), getattr(summary_outbox_report, "profile_id"), getattr(summary_outbox_report, "service_name"), getattr(summary_outbox_report, "scope_digest"), getattr(summary_outbox_report, "request_digest"), getattr(summary_outbox_report, "payload_digest"), getattr(summary_outbox_report, "idempotency_key"), getattr(summary_outbox_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_outbox_report), _digest(redaction_archive_report), _digest(import_prune_audit_report), accepted_marker_digest, classes, marker_digests, len(families), len(paths), hard, report_digest)


def assess_summary_publish_fence(*, summary_outbox_report: Any, redaction_archive_report: Any, import_prune_audit_report: Any, markers: tuple[SummaryPublishFenceMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[SummaryPublishFenceClass, ...] = (SummaryPublishFenceClass.SUMMARY_OUTBOX, SummaryPublishFenceClass.REDACTION_ARCHIVE, SummaryPublishFenceClass.IMPORT_PRUNE_AUDIT, SummaryPublishFenceClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryPublishFenceReport:
    markers = tuple(markers)
    if not getattr(summary_outbox_report, "outbox_staged", False):
        return _report(SummaryPublishFenceDecisionKind.HOLD_OUTBOX_PENDING, False, True, False, False, "summary outbox not staged", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if not getattr(redaction_archive_report, "redaction_archived", False):
        return _report(SummaryPublishFenceDecisionKind.HOLD_REDACTION_ARCHIVE_PENDING, False, True, False, False, "redaction archive missing", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if not getattr(import_prune_audit_report, "import_prune_audited", False):
        return _report(SummaryPublishFenceDecisionKind.HOLD_IMPORT_PRUNE_AUDIT_PENDING, False, True, False, False, "import-prune audit missing", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    boundary = _boundary(summary_outbox_report)
    if _boundary(redaction_archive_report) != boundary or _boundary(import_prune_audit_report) != boundary or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(SummaryPublishFenceDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, "boundary drift", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if any(marker.summary_outbox_digest != _digest(summary_outbox_report) or marker.redaction_archive_digest != _digest(redaction_archive_report) or marker.import_prune_audit_digest != _digest(import_prune_audit_report) for marker in markers):
        return _report(SummaryPublishFenceDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, "component digest drift", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if any(marker.accepted_outbox_entry_digest != getattr(summary_outbox_report, "accepted_entry_digest", ZERO_DIGEST) or marker.accepted_redaction_archive_marker_digest != getattr(redaction_archive_report, "accepted_marker_digest", ZERO_DIGEST) or marker.accepted_import_prune_marker_digest != getattr(import_prune_audit_report, "accepted_marker_digest", ZERO_DIGEST) for marker in markers):
        return _report(SummaryPublishFenceDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, "accepted marker digest drift", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if any(not marker.contradiction_carried for marker in markers) or not (getattr(summary_outbox_report, "contradiction_carried", False) and getattr(redaction_archive_report, "contradiction_preserved", False) and getattr(import_prune_audit_report, "contradiction_preserved", False)):
        return _report(SummaryPublishFenceDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, "contradiction memory missing", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    hard = int(getattr(summary_outbox_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_archive_report, "hard_negative_count", 0) or 0) + int(getattr(import_prune_audit_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(SummaryPublishFenceDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, "hard-negative pressure", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    present = {marker.fence_class for marker in markers}
    if not set(required_classes).issubset(present):
        return _report(SummaryPublishFenceDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, "missing fence class", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    prev = previous_digest
    seen: dict[int, bytes] = {}
    digest_seen: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in digest_seen:
            return _report(SummaryPublishFenceDecisionKind.QUARANTINE_REPLAY, False, True, False, True, "replayed fence marker", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        digest_seen.add(digest)
        if marker.sequence <= 0:
            return _report(SummaryPublishFenceDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, "non-positive sequence", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        if marker.sequence in seen and seen[marker.sequence] != digest:
            return _report(SummaryPublishFenceDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, "same-sequence fork", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        if marker.previous_digest != prev:
            return _report(SummaryPublishFenceDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, "previous digest mismatch", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        seen[marker.sequence] = digest
        prev = digest
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    if len(families) < min_family_count:
        return _report(SummaryPublishFenceDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, "low fence family diversity", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if len(paths) < min_path_family_count:
        return _report(SummaryPublishFenceDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, "low fence path diversity", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    accepted = markers[-1].marker_digest if markers else ZERO_DIGEST
    return _report(SummaryPublishFenceDecisionKind.ACCEPT_SUMMARY_PUBLISH_FENCED, True, False, True, True, "summary publish fenced", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, import_prune_audit_report=import_prune_audit_report, markers=markers, accepted_marker_digest=accepted)
