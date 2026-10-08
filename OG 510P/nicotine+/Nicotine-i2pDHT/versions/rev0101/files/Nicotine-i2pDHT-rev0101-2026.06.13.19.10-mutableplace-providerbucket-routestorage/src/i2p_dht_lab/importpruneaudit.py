"""rev0073 import-prune audit after summary publication/redaction witness.

Import/archive/prune state can look locally clean while publication and redaction
witness state disagree.  This audit lane joins summary publication, redaction
witness, import archive, and lineage prune so restart/prune memory cannot split
away from the redacted public summary boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

IMPORT_PRUNE_AUDIT_DOMAIN = DOMAIN + b":import-prune-audit-v1:"


class ImportPruneAuditClass(str, Enum):
    SUMMARY_PUBLICATION = "summary_publication"
    REDACTION_WITNESS = "redaction_witness"
    IMPORT_ARCHIVE = "import_archive"
    LINEAGE_PRUNE = "lineage_prune"
    CONTRADICTION_MEMORY = "contradiction_memory"
    REDACTED_SUMMARY_MEMORY = "redacted_summary_memory"


class ImportPruneAuditDecisionKind(str, Enum):
    ACCEPT_IMPORT_PRUNE_AUDITED = "accept_import_prune_audited"
    HOLD_SUMMARY_PUBLICATION_PENDING = "hold_summary_publication_pending"
    HOLD_REDACTION_WITNESS_PENDING = "hold_redaction_witness_pending"
    HOLD_IMPORT_ARCHIVE_PENDING = "hold_import_archive_pending"
    HOLD_LINEAGE_PRUNE_PENDING = "hold_lineage_prune_pending"
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
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ImportPruneAuditMarker:
    audit_class: ImportPruneAuditClass
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
    summary_publish_digest: bytes
    redaction_witness_digest: bytes
    summary_receipt_digest: bytes
    import_archive_digest: bytes
    lineage_prune_digest: bytes
    accepted_intent_digest: bytes
    accepted_redaction_receipt_digest: bytes
    accepted_import_marker_digest: bytes
    accepted_lineage_prune_marker_digest: bytes
    retained_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(IMPORT_PRUNE_AUDIT_DOMAIN + b":marker:" + bencode({
            b"class": ImportPruneAuditClass(self.audit_class).value,
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
            b"publish": self.summary_publish_digest,
            b"redaction": self.redaction_witness_digest,
            b"summary_receipt": self.summary_receipt_digest,
            b"import_archive": self.import_archive_digest,
            b"lineage_prune": self.lineage_prune_digest,
            b"intent": self.accepted_intent_digest,
            b"redaction_receipt": self.accepted_redaction_receipt_digest,
            b"import_marker": self.accepted_import_marker_digest,
            b"lineage_marker": self.accepted_lineage_prune_marker_digest,
            b"retained": self.retained_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ImportPruneAuditReport:
    decision_kind: ImportPruneAuditDecisionKind
    accept: bool
    watch: bool
    import_prune_audited: bool
    contradiction_preserved: bool
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
    summary_publish_digest: bytes
    redaction_witness_digest: bytes
    summary_receipt_digest: bytes
    import_archive_digest: bytes
    lineage_prune_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest", "accepted_intent_digest", "accepted_entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: ImportPruneAuditMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_import_prune_audit_marker(*, audit_class: ImportPruneAuditClass, sequence: int, summary_publish_report: Any, redaction_witness_report: Any, import_archive_report: Any, lineage_prune_report: Any, previous_digest: bytes = ZERO_DIGEST, retained_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "import-prune-audit-family-a", path_family_id: str = "import-prune-audit-path-a", hard_negative_count: int = 0) -> ImportPruneAuditMarker:
    cls = ImportPruneAuditClass(audit_class)
    digest = retained_digest or sha256(IMPORT_PRUNE_AUDIT_DOMAIN + b":retained:" + _digest(summary_publish_report) + b":" + _digest(redaction_witness_report) + b":" + _digest(import_archive_report) + b":" + _digest(lineage_prune_report) + b":" + cls.value.encode())
    contradiction = bool(getattr(summary_publish_report, "contradiction_carried", False) and getattr(redaction_witness_report, "contradiction_carried", False) and getattr(import_archive_report, "contradiction_preserved", False) and getattr(lineage_prune_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    return ImportPruneAuditMarker(
        audit_class=cls,
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_publish_report, "action")),
        profile_id=getattr(summary_publish_report, "profile_id"),
        service_name=getattr(summary_publish_report, "service_name"),
        scope_digest=getattr(summary_publish_report, "scope_digest"),
        request_digest=getattr(summary_publish_report, "request_digest"),
        payload_digest=getattr(summary_publish_report, "payload_digest"),
        idempotency_key=getattr(summary_publish_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_publish_digest=_digest(summary_publish_report),
        redaction_witness_digest=_digest(redaction_witness_report),
        summary_receipt_digest=getattr(summary_publish_report, "summary_receipt_digest", ZERO_DIGEST),
        import_archive_digest=_digest(import_archive_report),
        lineage_prune_digest=_digest(lineage_prune_report),
        accepted_intent_digest=getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST),
        accepted_redaction_receipt_digest=getattr(redaction_witness_report, "accepted_receipt_digest", ZERO_DIGEST),
        accepted_import_marker_digest=getattr(import_archive_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_lineage_prune_marker_digest=getattr(lineage_prune_report, "accepted_marker_digest", ZERO_DIGEST),
        retained_digest=digest,
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: ImportPruneAuditDecisionKind, accept: bool, watch: bool, audited: bool, contradiction: bool, redacted: bool, reason: str, *, summary_publish_report: Any, redaction_witness_report: Any, import_archive_report: Any, lineage_prune_report: Any, markers: tuple[ImportPruneAuditMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> ImportPruneAuditReport:
    digests = tuple(marker.marker_digest for marker in markers)
    classes = tuple(sorted({marker.audit_class.value for marker in markers}))
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_witness_report, "hard_negative_count", 0) or 0) + int(getattr(import_archive_report, "hard_negative_count", 0) or 0) + int(getattr(lineage_prune_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(IMPORT_PRUNE_AUDIT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"audited": 1 if audited else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(summary_publish_report, "action")).value,
        b"profile": getattr(summary_publish_report, "profile_id"),
        b"service": getattr(summary_publish_report, "service_name"),
        b"scope": getattr(summary_publish_report, "scope_digest"),
        b"request": getattr(summary_publish_report, "request_digest"),
        b"payload": getattr(summary_publish_report, "payload_digest"),
        b"idem": getattr(summary_publish_report, "idempotency_key"),
        b"retry_idem": getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST),
        b"publish": _digest(summary_publish_report),
        b"redaction": _digest(redaction_witness_report),
        b"summary_receipt": getattr(summary_publish_report, "summary_receipt_digest", ZERO_DIGEST),
        b"import_archive": _digest(import_archive_report),
        b"lineage_prune": _digest(lineage_prune_report),
        b"accepted_marker": accepted_marker_digest,
        b"classes": classes,
        b"markers": digests,
        b"families": sorted(families),
        b"paths": sorted(paths),
        b"hard": hard,
    }))
    return ImportPruneAuditReport(
        kind, accept, watch, audited, contradiction, redacted, reason,
        SideEffectAction(getattr(summary_publish_report, "action")),
        getattr(summary_publish_report, "profile_id"),
        getattr(summary_publish_report, "service_name"),
        getattr(summary_publish_report, "scope_digest"),
        getattr(summary_publish_report, "request_digest"),
        getattr(summary_publish_report, "payload_digest"),
        getattr(summary_publish_report, "idempotency_key"),
        getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST),
        _digest(summary_publish_report),
        _digest(redaction_witness_report),
        getattr(summary_publish_report, "summary_receipt_digest", ZERO_DIGEST),
        _digest(import_archive_report),
        _digest(lineage_prune_report),
        accepted_marker_digest,
        classes,
        digests,
        len(families),
        len(paths),
        hard,
        report_digest,
    )


def assess_import_prune_audit(*, summary_publish_report: Any, redaction_witness_report: Any, import_archive_report: Any, lineage_prune_report: Any, markers: tuple[ImportPruneAuditMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[ImportPruneAuditClass, ...] = (ImportPruneAuditClass.SUMMARY_PUBLICATION, ImportPruneAuditClass.REDACTION_WITNESS, ImportPruneAuditClass.IMPORT_ARCHIVE, ImportPruneAuditClass.LINEAGE_PRUNE, ImportPruneAuditClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> ImportPruneAuditReport:
    if not (getattr(summary_publish_report, "accept", False) and getattr(summary_publish_report, "publication_ready", False)):
        return _report(ImportPruneAuditDecisionKind.HOLD_SUMMARY_PUBLICATION_PENDING, False, True, False, False, True, "summary publication is not accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    if not (getattr(redaction_witness_report, "accept", False) and getattr(redaction_witness_report, "redaction_witnessed", False)):
        return _report(ImportPruneAuditDecisionKind.HOLD_REDACTION_WITNESS_PENDING, False, True, False, False, True, "redaction witness is not accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    if not (getattr(import_archive_report, "accept", False) and getattr(import_archive_report, "import_archived", False)):
        return _report(ImportPruneAuditDecisionKind.HOLD_IMPORT_ARCHIVE_PENDING, False, True, False, False, True, "import archive is not accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    if not (getattr(lineage_prune_report, "accept", False) and getattr(lineage_prune_report, "lineage_prune_guarded", False)):
        return _report(ImportPruneAuditDecisionKind.HOLD_LINEAGE_PRUNE_PENDING, False, True, False, False, True, "lineage prune is not accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    expected_boundary = _boundary(summary_publish_report)
    for component in (redaction_witness_report, import_archive_report, lineage_prune_report):
        if _boundary(component) != expected_boundary:
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "component boundary drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    expected_publish = _digest(summary_publish_report)
    expected_redaction = _digest(redaction_witness_report)
    expected_import = _digest(import_archive_report)
    expected_prune = _digest(lineage_prune_report)
    if getattr(redaction_witness_report, "summary_publish_digest", ZERO_DIGEST) != expected_publish or getattr(summary_publish_report, "import_archive_digest", ZERO_DIGEST) != expected_import or getattr(summary_publish_report, "lineage_prune_digest", ZERO_DIGEST) != expected_prune:
        return _report(ImportPruneAuditDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift before audit", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    if not markers:
        return _report(ImportPruneAuditDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, True, "no import-prune audit markers", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    expected_summary = getattr(summary_publish_report, "summary_receipt_digest", ZERO_DIGEST)
    expected_intent = getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST)
    expected_redaction_receipt = getattr(redaction_witness_report, "accepted_receipt_digest", ZERO_DIGEST)
    expected_import_marker = getattr(import_archive_report, "accepted_marker_digest", ZERO_DIGEST)
    expected_lineage_marker = getattr(lineage_prune_report, "accepted_marker_digest", ZERO_DIGEST)
    prev = previous_digest
    seen_seq: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    contradiction = False
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, "duplicate import-prune audit marker", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive import-prune audit sequence", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
        if marker.sequence in seen_seq and seen_seq[marker.sequence] != digest:
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence import-prune audit fork", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
        seen_seq[marker.sequence] = digest
        if marker.previous_digest != prev:
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "previous digest mismatch", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
        if _marker_boundary(marker) != expected_boundary:
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "import-prune audit boundary drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
        if (marker.summary_publish_digest != expected_publish or marker.redaction_witness_digest != expected_redaction or marker.summary_receipt_digest != expected_summary or marker.import_archive_digest != expected_import or marker.lineage_prune_digest != expected_prune or marker.accepted_intent_digest != expected_intent or marker.accepted_redaction_receipt_digest != expected_redaction_receipt or marker.accepted_import_marker_digest != expected_import_marker or marker.accepted_lineage_prune_marker_digest != expected_lineage_marker):
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "audit component digest drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "audit leaked raw boundary or payload", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
        if marker.hard_negative_count or int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) or int(getattr(redaction_witness_report, "hard_negative_count", 0) or 0) or int(getattr(import_archive_report, "hard_negative_count", 0) or 0) or int(getattr(lineage_prune_report, "hard_negative_count", 0) or 0):
            return _report(ImportPruneAuditDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, bool(marker.contradiction_carried), True, "hard negative pressure", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
        contradiction = contradiction or marker.contradiction_carried
        prev = digest
    if not contradiction:
        return _report(ImportPruneAuditDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "audit dropped contradiction memory", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    required = {ImportPruneAuditClass(cls).value for cls in required_classes}
    actual = {marker.audit_class.value for marker in markers}
    if not required.issubset(actual):
        return _report(ImportPruneAuditDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, True, "missing required import-prune audit class", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(ImportPruneAuditDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low import-prune audit family diversity", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(ImportPruneAuditDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low import-prune audit path diversity", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers)
    return _report(ImportPruneAuditDecisionKind.ACCEPT_IMPORT_PRUNE_AUDITED, True, False, True, True, True, "import-prune audited", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, markers=markers, accepted_marker_digest=prev)
