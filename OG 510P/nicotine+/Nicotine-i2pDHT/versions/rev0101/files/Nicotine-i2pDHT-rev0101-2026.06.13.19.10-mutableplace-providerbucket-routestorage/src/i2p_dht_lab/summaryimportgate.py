"""rev0079 redacted summary import gate after export receipt.

A local/export recipient receipt still cannot mutate a local import surface.  The
import gate demands exact boundary agreement, carried redaction, and carried
contradiction memory before a redacted summary becomes import-ready.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_IMPORT_GATE_DOMAIN = DOMAIN + b":summary-import-gate-v1:"


class SummaryImportClass(str, Enum):
    EXPORT_RECEIPT = "export_receipt"
    EXPORT_FENCE = "export_fence"
    IMPORT_SCOPE = "import_scope"
    REDACTION_MEMORY = "redaction_memory"
    CONTRADICTION_MEMORY = "contradiction_memory"


class SummaryImportDecisionKind(str, Enum):
    ACCEPT_SUMMARY_IMPORT_GATED = "accept_summary_import_gated"
    HOLD_RECEIPT_PENDING = "hold_receipt_pending"
    HOLD_EXPORT_PENDING = "hold_export_pending"
    HOLD_IMPORT_NOT_PERMITTED = "hold_import_not_permitted"
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
class SummaryImportMarker:
    import_class: SummaryImportClass
    sequence: int
    previous_digest: bytes
    importer_kind: str
    import_permitted: bool
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_export_receipt_digest: bytes
    summary_export_fence_digest: bytes
    accepted_receipt_marker_digest: bytes
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
        return sha256(SUMMARY_IMPORT_GATE_DOMAIN + b":marker:" + bencode({
            b"class": SummaryImportClass(self.import_class).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"importer": self.importer_kind,
            b"permitted": 1 if self.import_permitted else 0,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"receipt": self.summary_export_receipt_digest,
            b"export": self.summary_export_fence_digest,
            b"receipt_marker": self.accepted_receipt_marker_digest,
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
class SummaryImportGateReport:
    decision_kind: SummaryImportDecisionKind
    accept: bool
    watch: bool
    summary_import_gated: bool
    import_ready: bool
    importer_kind: str
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
    summary_export_fence_digest: bytes
    accepted_marker_digest: bytes
    accepted_receipt_marker_digest: bytes
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
        SideEffectAction(getattr(report, "action")),
        getattr(report, "profile_id"),
        getattr(report, "service_name"),
        getattr(report, "scope_digest"),
        getattr(report, "request_digest"),
        getattr(report, "payload_digest"),
        getattr(report, "idempotency_key"),
        getattr(report, "retry_idempotency_key", ZERO_DIGEST),
    )


def _marker_boundary(marker: SummaryImportMarker) -> tuple[Any, ...]:
    return (
        SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key, marker.retry_idempotency_key
    )


def make_summary_import_marker(*, import_class: SummaryImportClass, sequence: int, summary_export_receipt_report: Any, summary_export_fence_report: Any, previous_digest: bytes = ZERO_DIGEST, importer_kind: str = "local_operator", import_permitted: bool = True, contradiction_carried: bool = True, redaction_carried: bool = True, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "summary-import-family", path_family_id: str = "summary-import-path", hard_negative_count: int = 0) -> SummaryImportMarker:
    return SummaryImportMarker(
        import_class=SummaryImportClass(import_class), sequence=sequence, previous_digest=previous_digest, importer_kind=importer_kind, import_permitted=import_permitted,
        action=SideEffectAction(getattr(summary_export_receipt_report, "action")), profile_id=getattr(summary_export_receipt_report, "profile_id"), service_name=getattr(summary_export_receipt_report, "service_name"), scope_digest=getattr(summary_export_receipt_report, "scope_digest"), request_digest=getattr(summary_export_receipt_report, "request_digest"), payload_digest=getattr(summary_export_receipt_report, "payload_digest"), idempotency_key=getattr(summary_export_receipt_report, "idempotency_key"), retry_idempotency_key=getattr(summary_export_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_export_receipt_digest=_digest(summary_export_receipt_report), summary_export_fence_digest=_digest(summary_export_fence_report), accepted_receipt_marker_digest=getattr(summary_export_receipt_report, "accepted_marker_digest", ZERO_DIGEST), accepted_export_marker_digest=getattr(summary_export_fence_report, "accepted_marker_digest", ZERO_DIGEST), redacted_summary_digest=getattr(summary_export_receipt_report, "redacted_summary_digest", ZERO_DIGEST), contradiction_carried=contradiction_carried, redaction_carried=redaction_carried, raw_boundary_exposed=raw_boundary_exposed, raw_payload_exposed=raw_payload_exposed, family_id=family_id, path_family_id=path_family_id, hard_negative_count=hard_negative_count,
    )


def _report(kind: SummaryImportDecisionKind, accept: bool, watch: bool, gated: bool, contradiction: bool, redacted: bool, reason: str, *, summary_export_receipt_report: Any, summary_export_fence_report: Any, markers: tuple[SummaryImportMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> SummaryImportGateReport:
    class_values = tuple(sorted({marker.import_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    importers = {marker.importer_kind for marker in markers}
    importer = sorted(importers)[0] if len(importers) == 1 else "mixed"
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_export_receipt_report, summary_export_fence_report)) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(SUMMARY_IMPORT_GATE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0, b"gated": 1 if gated else 0, b"importer": importer,
        b"receipt": _digest(summary_export_receipt_report), b"export": _digest(summary_export_fence_report), b"accepted": accepted_marker_digest, b"classes": list(class_values), b"markers": list(marker_digests), b"families": len(families), b"paths": len(paths), b"contradiction": 1 if contradiction else 0, b"redacted": 1 if redacted else 0, b"hard": hard, b"reason": reason,
    }))
    return SummaryImportGateReport(kind, accept, watch, gated, gated, importer, contradiction, contradiction, redacted, redacted, reason, SideEffectAction(getattr(summary_export_receipt_report, "action")), getattr(summary_export_receipt_report, "profile_id"), getattr(summary_export_receipt_report, "service_name"), getattr(summary_export_receipt_report, "scope_digest"), getattr(summary_export_receipt_report, "request_digest"), getattr(summary_export_receipt_report, "payload_digest"), getattr(summary_export_receipt_report, "idempotency_key"), getattr(summary_export_receipt_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_export_receipt_report), _digest(summary_export_fence_report), accepted_marker_digest, getattr(summary_export_receipt_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_export_fence_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_export_receipt_report, "redacted_summary_digest", ZERO_DIGEST), class_values, marker_digests, len(families), len(paths), hard, report_digest)


def assess_summary_import_gate(*, summary_export_receipt_report: Any, summary_export_fence_report: Any, markers: tuple[SummaryImportMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[SummaryImportClass, ...] = (SummaryImportClass.EXPORT_RECEIPT, SummaryImportClass.EXPORT_FENCE, SummaryImportClass.IMPORT_SCOPE, SummaryImportClass.REDACTION_MEMORY, SummaryImportClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryImportGateReport:
    markers = tuple(markers)
    if not getattr(summary_export_receipt_report, "summary_export_receipted", False) or not getattr(summary_export_receipt_report, "recipient_acknowledged", False):
        return _report(SummaryImportDecisionKind.HOLD_RECEIPT_PENDING, False, True, False, False, False, "receipt pending", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if not getattr(summary_export_fence_report, "summary_export_fenced", False):
        return _report(SummaryImportDecisionKind.HOLD_EXPORT_PENDING, False, True, False, False, False, "export pending", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    boundary = _boundary(summary_export_receipt_report)
    if _boundary(summary_export_fence_report) != boundary or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(SummaryImportDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if getattr(summary_export_receipt_report, "summary_export_fence_digest", ZERO_DIGEST) != _digest(summary_export_fence_report):
        return _report(SummaryImportDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "receipt/export digest drift", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    for marker in markers:
        if marker.summary_export_receipt_digest != _digest(summary_export_receipt_report) or marker.summary_export_fence_digest != _digest(summary_export_fence_report):
            return _report(SummaryImportDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "marker digest drift", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(SummaryImportDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw leak", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if any(not marker.import_permitted for marker in markers):
        return _report(SummaryImportDecisionKind.HOLD_IMPORT_NOT_PERMITTED, False, True, False, True, True, "import not permitted", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    contradiction = bool(getattr(summary_export_receipt_report, "contradiction_preserved", False) and getattr(summary_export_fence_report, "contradiction_preserved", False) and all(marker.contradiction_carried for marker in markers))
    if not contradiction:
        return _report(SummaryImportDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction dropped", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    redacted = bool(getattr(summary_export_receipt_report, "redacted", False) and getattr(summary_export_fence_report, "redacted", False) and all(marker.redaction_carried for marker in markers))
    if not redacted:
        return _report(SummaryImportDecisionKind.QUARANTINE_REDACTION_DROPPED, False, True, False, True, False, "redaction dropped", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_export_receipt_report, summary_export_fence_report)) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(SummaryImportDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "hard negatives", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if not set(required_classes).issubset({marker.import_class for marker in markers}):
        return _report(SummaryImportDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing class", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(SummaryImportDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed marker", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(SummaryImportDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        if marker.sequence in seen_sequences and seen_sequences[marker.sequence] != digest:
            return _report(SummaryImportDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        seen_sequences[marker.sequence] = digest
        if marker.previous_digest != previous:
            return _report(SummaryImportDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous mismatch", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
        previous = digest
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(SummaryImportDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(SummaryImportDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers)
    accepted = previous if markers else ZERO_DIGEST
    return _report(SummaryImportDecisionKind.ACCEPT_SUMMARY_IMPORT_GATED, True, False, True, True, redacted, "summary import gate accepted", summary_export_receipt_report=summary_export_receipt_report, summary_export_fence_report=summary_export_fence_report, markers=markers, accepted_marker_digest=accepted)
