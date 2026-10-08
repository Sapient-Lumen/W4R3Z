"""rev0080 restart-sticky archive after redacted-summary import settlement.

Import settlement is a local decision.  This lane makes it durable by demanding
an archive marker chain that still carries export-retention, redaction, and
contradiction evidence after restart.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

IMPORT_ARCHIVE_LEDGER_DOMAIN = DOMAIN + b":import-archive-ledger-v1:"


class ImportArchiveClass(str, Enum):
    IMPORT_SETTLEMENT = "import_settlement"
    RETENTION_AUDIT = "retention_audit"
    IMPORT_GATE = "import_gate"
    ARCHIVE_STATE = "archive_state"
    REDACTION_MEMORY = "redaction_memory"
    CONTRADICTION_MEMORY = "contradiction_memory"


class ImportArchiveDecisionKind(str, Enum):
    ACCEPT_IMPORT_ARCHIVED = "accept_import_archived"
    HOLD_IMPORT_SETTLEMENT_PENDING = "hold_import_settlement_pending"
    HOLD_RETENTION_PENDING = "hold_retention_pending"
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
class ImportArchiveMarker:
    archive_class: ImportArchiveClass
    sequence: int
    previous_digest: bytes
    archive_generation: int
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_import_settlement_digest: bytes
    export_retention_audit_digest: bytes
    summary_import_gate_digest: bytes
    accepted_settlement_marker_digest: bytes
    accepted_retention_marker_digest: bytes
    accepted_import_marker_digest: bytes
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
        return sha256(IMPORT_ARCHIVE_LEDGER_DOMAIN + b":marker:" + bencode({
            b"class": ImportArchiveClass(self.archive_class).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"generation": self.archive_generation,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"settlement": self.summary_import_settlement_digest,
            b"retention": self.export_retention_audit_digest,
            b"import_gate": self.summary_import_gate_digest,
            b"settlement_marker": self.accepted_settlement_marker_digest,
            b"retention_marker": self.accepted_retention_marker_digest,
            b"import_marker": self.accepted_import_marker_digest,
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
class ImportArchiveReport:
    decision_kind: ImportArchiveDecisionKind
    accept: bool
    watch: bool
    import_archived: bool
    archive_restart_sticky: bool
    archive_generation: int
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
    summary_import_settlement_digest: bytes
    export_retention_audit_digest: bytes
    summary_import_gate_digest: bytes
    accepted_marker_digest: bytes
    accepted_settlement_marker_digest: bytes
    accepted_retention_marker_digest: bytes
    accepted_import_marker_digest: bytes
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


def _marker_boundary(marker: ImportArchiveMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key, marker.retry_idempotency_key)


def make_import_archive_marker(*, archive_class: ImportArchiveClass, sequence: int, summary_import_settlement_report: Any, export_retention_audit_report: Any, summary_import_gate_report: Any, previous_digest: bytes = ZERO_DIGEST, archive_generation: int = 1, contradiction_carried: bool = True, redaction_carried: bool = True, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "import-archive-family", path_family_id: str = "import-archive-path", hard_negative_count: int = 0) -> ImportArchiveMarker:
    return ImportArchiveMarker(
        archive_class=ImportArchiveClass(archive_class), sequence=sequence, previous_digest=previous_digest, archive_generation=archive_generation,
        action=SideEffectAction(getattr(summary_import_settlement_report, "action")), profile_id=getattr(summary_import_settlement_report, "profile_id"), service_name=getattr(summary_import_settlement_report, "service_name"), scope_digest=getattr(summary_import_settlement_report, "scope_digest"), request_digest=getattr(summary_import_settlement_report, "request_digest"), payload_digest=getattr(summary_import_settlement_report, "payload_digest"), idempotency_key=getattr(summary_import_settlement_report, "idempotency_key"), retry_idempotency_key=getattr(summary_import_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_import_settlement_digest=_digest(summary_import_settlement_report), export_retention_audit_digest=_digest(export_retention_audit_report), summary_import_gate_digest=_digest(summary_import_gate_report), accepted_settlement_marker_digest=getattr(summary_import_settlement_report, "accepted_marker_digest", ZERO_DIGEST), accepted_retention_marker_digest=getattr(export_retention_audit_report, "accepted_marker_digest", ZERO_DIGEST), accepted_import_marker_digest=getattr(summary_import_gate_report, "accepted_marker_digest", ZERO_DIGEST), redacted_summary_digest=getattr(summary_import_settlement_report, "redacted_summary_digest", ZERO_DIGEST), contradiction_carried=contradiction_carried, redaction_carried=redaction_carried, raw_boundary_exposed=raw_boundary_exposed, raw_payload_exposed=raw_payload_exposed, family_id=family_id, path_family_id=path_family_id, hard_negative_count=hard_negative_count,
    )


def _report(kind: ImportArchiveDecisionKind, accept: bool, watch: bool, archived: bool, contradiction: bool, redacted: bool, reason: str, *, summary_import_settlement_report: Any, export_retention_audit_report: Any, summary_import_gate_report: Any, markers: tuple[ImportArchiveMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> ImportArchiveReport:
    class_values = tuple(sorted({marker.archive_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    generation = max((marker.archive_generation for marker in markers), default=0)
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_import_settlement_report, export_retention_audit_report, summary_import_gate_report)) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(IMPORT_ARCHIVE_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0, b"archived": 1 if archived else 0, b"generation": generation,
        b"settlement": _digest(summary_import_settlement_report), b"retention": _digest(export_retention_audit_report), b"import": _digest(summary_import_gate_report), b"accepted": accepted_marker_digest, b"classes": list(class_values), b"markers": list(marker_digests), b"families": len(families), b"paths": len(paths), b"contradiction": 1 if contradiction else 0, b"redacted": 1 if redacted else 0, b"hard": hard, b"reason": reason,
    }))
    return ImportArchiveReport(kind, accept, watch, archived, archived, generation, contradiction, contradiction, redacted, redacted, reason, SideEffectAction(getattr(summary_import_settlement_report, "action")), getattr(summary_import_settlement_report, "profile_id"), getattr(summary_import_settlement_report, "service_name"), getattr(summary_import_settlement_report, "scope_digest"), getattr(summary_import_settlement_report, "request_digest"), getattr(summary_import_settlement_report, "payload_digest"), getattr(summary_import_settlement_report, "idempotency_key"), getattr(summary_import_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_import_settlement_report), _digest(export_retention_audit_report), _digest(summary_import_gate_report), accepted_marker_digest, getattr(summary_import_settlement_report, "accepted_marker_digest", ZERO_DIGEST), getattr(export_retention_audit_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_import_gate_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_import_settlement_report, "redacted_summary_digest", ZERO_DIGEST), class_values, marker_digests, len(families), len(paths), hard, report_digest)


def assess_import_archive(*, summary_import_settlement_report: Any, export_retention_audit_report: Any, summary_import_gate_report: Any, markers: tuple[ImportArchiveMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[ImportArchiveClass, ...] = (ImportArchiveClass.IMPORT_SETTLEMENT, ImportArchiveClass.RETENTION_AUDIT, ImportArchiveClass.IMPORT_GATE, ImportArchiveClass.ARCHIVE_STATE, ImportArchiveClass.REDACTION_MEMORY, ImportArchiveClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> ImportArchiveReport:
    markers = tuple(markers)
    if not getattr(summary_import_settlement_report, "summary_import_settled", False):
        return _report(ImportArchiveDecisionKind.HOLD_IMPORT_SETTLEMENT_PENDING, False, True, False, False, False, "settlement pending", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    if not getattr(export_retention_audit_report, "export_retention_audited", False):
        return _report(ImportArchiveDecisionKind.HOLD_RETENTION_PENDING, False, True, False, False, False, "retention pending", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    boundary = _boundary(summary_import_settlement_report)
    if _boundary(export_retention_audit_report) != boundary or _boundary(summary_import_gate_report) != boundary or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(ImportArchiveDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    if getattr(summary_import_settlement_report, "export_retention_audit_digest", ZERO_DIGEST) != _digest(export_retention_audit_report) or getattr(summary_import_settlement_report, "summary_import_gate_digest", ZERO_DIGEST) != _digest(summary_import_gate_report):
        return _report(ImportArchiveDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    for marker in markers:
        if marker.summary_import_settlement_digest != _digest(summary_import_settlement_report) or marker.export_retention_audit_digest != _digest(export_retention_audit_report) or marker.summary_import_gate_digest != _digest(summary_import_gate_report):
            return _report(ImportArchiveDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "marker digest drift", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(ImportArchiveDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw leak", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    contradiction = bool(getattr(summary_import_settlement_report, "contradiction_preserved", False) and getattr(export_retention_audit_report, "contradiction_preserved", False) and getattr(summary_import_gate_report, "contradiction_preserved", False) and all(marker.contradiction_carried for marker in markers))
    if not contradiction:
        return _report(ImportArchiveDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction dropped", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    redacted = bool(getattr(summary_import_settlement_report, "redacted", False) and getattr(export_retention_audit_report, "redacted", False) and getattr(summary_import_gate_report, "redacted", False) and all(marker.redaction_carried for marker in markers))
    if not redacted:
        return _report(ImportArchiveDecisionKind.QUARANTINE_REDACTION_DROPPED, False, True, False, True, False, "redaction dropped", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_import_settlement_report, export_retention_audit_report, summary_import_gate_report)) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(ImportArchiveDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "hard negatives", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    if not set(required_classes).issubset({marker.archive_class for marker in markers}):
        return _report(ImportArchiveDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing class", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(ImportArchiveDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed marker", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(ImportArchiveDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
        if marker.sequence in seen_sequences and seen_sequences[marker.sequence] != digest:
            return _report(ImportArchiveDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
        seen_sequences[marker.sequence] = digest
        if marker.previous_digest != previous:
            return _report(ImportArchiveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous mismatch", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
        previous = digest
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(ImportArchiveDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(ImportArchiveDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers)
    accepted = previous if markers else ZERO_DIGEST
    return _report(ImportArchiveDecisionKind.ACCEPT_IMPORT_ARCHIVED, True, False, True, True, redacted, "import archive accepted", summary_import_settlement_report=summary_import_settlement_report, export_retention_audit_report=export_retention_audit_report, summary_import_gate_report=summary_import_gate_report, markers=markers, accepted_marker_digest=accepted)
