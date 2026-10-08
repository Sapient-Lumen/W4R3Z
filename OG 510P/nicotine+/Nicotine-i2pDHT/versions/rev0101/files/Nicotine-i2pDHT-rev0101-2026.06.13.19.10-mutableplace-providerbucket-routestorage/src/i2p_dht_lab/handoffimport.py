"""rev0071 closure handoff import guard after recipient receipt.

Receipt is not import permission.  A recipient can acknowledge a handoff while
local import still needs exact-boundary, contradiction-preserving import markers.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

HANDOFF_IMPORT_DOMAIN = DOMAIN + b":handoff-import-v1:"


class HandoffImportClass(str, Enum):
    HANDOFF_RECEIPT_MARKER = "handoff_receipt_marker"
    CLOSURE_HANDOFF_MARKER = "closure_handoff_marker"
    CONTRADICTION_MEMORY = "contradiction_memory"
    REDACTED_SUMMARY_MEMORY = "redacted_summary_memory"
    LOCAL_RECIPIENT_STATE = "local_recipient_state"


class HandoffImportDecisionKind(str, Enum):
    ACCEPT_HANDOFF_IMPORTED = "accept_handoff_imported"
    HOLD_HANDOFF_RECEIPT_PENDING = "hold_handoff_receipt_pending"
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
class HandoffImportMarker:
    import_class: HandoffImportClass
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
    handoff_receipt_digest: bytes
    closure_handoff_digest: bytes
    export_receipt_digest: bytes
    retention_gc_digest: bytes
    imported_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(HANDOFF_IMPORT_DOMAIN + b":marker:" + bencode({
            b"class": self.import_class.value,
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
            b"receipt": self.handoff_receipt_digest,
            b"handoff": self.closure_handoff_digest,
            b"export_receipt": self.export_receipt_digest,
            b"gc": self.retention_gc_digest,
            b"imported": self.imported_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class HandoffImportReport:
    decision_kind: HandoffImportDecisionKind
    accept: bool
    watch: bool
    handoff_imported: bool
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
    handoff_receipt_digest: bytes
    closure_handoff_digest: bytes
    export_receipt_digest: bytes
    retention_gc_digest: bytes
    accepted_marker_digest: bytes
    imported_classes: tuple[str, ...]
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
    for attr in ("report_digest", "accepted_entry_digest", "accepted_marker_digest", "accepted_packet_digest", "accepted_receipt_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: HandoffImportMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_handoff_import_marker(*, import_class: HandoffImportClass, sequence: int, handoff_receipt_report: Any, previous_digest: bytes = ZERO_DIGEST, imported_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "handoff-import-family-a", path_family_id: str = "handoff-import-path-a", hard_negative_count: int = 0) -> HandoffImportMarker:
    cls = HandoffImportClass(import_class)
    imported = imported_digest or sha256(HANDOFF_IMPORT_DOMAIN + b":imported:" + _digest(handoff_receipt_report) + b":" + cls.value.encode())
    contradiction = bool(getattr(handoff_receipt_report, "contradiction_carried", False)) if contradiction_carried is None else bool(contradiction_carried)
    return HandoffImportMarker(
        import_class=cls,
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(handoff_receipt_report, "action")),
        profile_id=getattr(handoff_receipt_report, "profile_id"),
        service_name=getattr(handoff_receipt_report, "service_name"),
        scope_digest=getattr(handoff_receipt_report, "scope_digest"),
        request_digest=getattr(handoff_receipt_report, "request_digest"),
        payload_digest=getattr(handoff_receipt_report, "payload_digest"),
        idempotency_key=getattr(handoff_receipt_report, "idempotency_key"),
        retry_idempotency_key=getattr(handoff_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        handoff_receipt_digest=_digest(handoff_receipt_report),
        closure_handoff_digest=getattr(handoff_receipt_report, "closure_handoff_digest", ZERO_DIGEST),
        export_receipt_digest=getattr(handoff_receipt_report, "export_receipt_digest", ZERO_DIGEST),
        retention_gc_digest=getattr(handoff_receipt_report, "retention_gc_digest", ZERO_DIGEST),
        imported_digest=imported,
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: HandoffImportDecisionKind, accept: bool, watch: bool, imported: bool, contradiction: bool, redacted: bool, reason: str, *, handoff_receipt_report: Any, markers: tuple[HandoffImportMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> HandoffImportReport:
    digests = tuple(marker.marker_digest for marker in markers)
    classes = tuple(sorted(marker.import_class.value for marker in markers))
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = int(getattr(handoff_receipt_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(HANDOFF_IMPORT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"imported": 1 if imported else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(handoff_receipt_report, "action")).value,
        b"profile": getattr(handoff_receipt_report, "profile_id"),
        b"service": getattr(handoff_receipt_report, "service_name"),
        b"scope": getattr(handoff_receipt_report, "scope_digest"),
        b"request": getattr(handoff_receipt_report, "request_digest"),
        b"payload": getattr(handoff_receipt_report, "payload_digest"),
        b"idem": getattr(handoff_receipt_report, "idempotency_key"),
        b"retry_idem": getattr(handoff_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        b"receipt": _digest(handoff_receipt_report),
        b"handoff": getattr(handoff_receipt_report, "closure_handoff_digest", ZERO_DIGEST),
        b"export_receipt": getattr(handoff_receipt_report, "export_receipt_digest", ZERO_DIGEST),
        b"gc": getattr(handoff_receipt_report, "retention_gc_digest", ZERO_DIGEST),
        b"accepted": accepted_marker_digest,
        b"classes": list(classes),
        b"markers": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return HandoffImportReport(kind, accept, watch, imported, contradiction, redacted, reason, SideEffectAction(getattr(handoff_receipt_report, "action")), getattr(handoff_receipt_report, "profile_id"), getattr(handoff_receipt_report, "service_name"), getattr(handoff_receipt_report, "scope_digest"), getattr(handoff_receipt_report, "request_digest"), getattr(handoff_receipt_report, "payload_digest"), getattr(handoff_receipt_report, "idempotency_key"), getattr(handoff_receipt_report, "retry_idempotency_key", ZERO_DIGEST), _digest(handoff_receipt_report), getattr(handoff_receipt_report, "closure_handoff_digest", ZERO_DIGEST), getattr(handoff_receipt_report, "export_receipt_digest", ZERO_DIGEST), getattr(handoff_receipt_report, "retention_gc_digest", ZERO_DIGEST), accepted_marker_digest, classes, digests, len(families), len(paths), hard, report_digest)


def assess_handoff_import(*, handoff_receipt_report: Any, markers: tuple[HandoffImportMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[HandoffImportClass, ...] = (HandoffImportClass.HANDOFF_RECEIPT_MARKER, HandoffImportClass.CLOSURE_HANDOFF_MARKER, HandoffImportClass.CONTRADICTION_MEMORY, HandoffImportClass.REDACTED_SUMMARY_MEMORY, HandoffImportClass.LOCAL_RECIPIENT_STATE), min_family_count: int = 2, min_path_family_count: int = 2) -> HandoffImportReport:
    if not (getattr(handoff_receipt_report, "accept", False) and getattr(handoff_receipt_report, "handoff_receipted", False)):
        return _report(HandoffImportDecisionKind.HOLD_HANDOFF_RECEIPT_PENDING, False, True, False, False, True, "handoff receipt is not accepted", handoff_receipt_report=handoff_receipt_report, markers=markers)
    if not markers:
        return _report(HandoffImportDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, True, "no import markers", handoff_receipt_report=handoff_receipt_report, markers=markers)
    expected_boundary = _boundary(handoff_receipt_report)
    expected_receipt = _digest(handoff_receipt_report)
    expected_handoff = getattr(handoff_receipt_report, "closure_handoff_digest", ZERO_DIGEST)
    expected_export = getattr(handoff_receipt_report, "export_receipt_digest", ZERO_DIGEST)
    expected_gc = getattr(handoff_receipt_report, "retention_gc_digest", ZERO_DIGEST)
    seen_seq: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    prev = previous_digest
    contradiction = False
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(HandoffImportDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, "duplicate import marker", handoff_receipt_report=handoff_receipt_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(HandoffImportDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive import sequence", handoff_receipt_report=handoff_receipt_report, markers=markers)
        if marker.sequence in seen_seq and seen_seq[marker.sequence] != digest:
            return _report(HandoffImportDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence import fork", handoff_receipt_report=handoff_receipt_report, markers=markers)
        seen_seq[marker.sequence] = digest
        if marker.previous_digest != prev:
            return _report(HandoffImportDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "previous digest mismatch", handoff_receipt_report=handoff_receipt_report, markers=markers)
        if _marker_boundary(marker) != expected_boundary:
            return _report(HandoffImportDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "marker boundary drift", handoff_receipt_report=handoff_receipt_report, markers=markers)
        if marker.handoff_receipt_digest != expected_receipt or marker.closure_handoff_digest != expected_handoff or marker.export_receipt_digest != expected_export or marker.retention_gc_digest != expected_gc:
            return _report(HandoffImportDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", handoff_receipt_report=handoff_receipt_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(HandoffImportDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "import marker leaked raw material", handoff_receipt_report=handoff_receipt_report, markers=markers)
        if marker.hard_negative_count or int(getattr(handoff_receipt_report, "hard_negative_count", 0) or 0):
            return _report(HandoffImportDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, bool(marker.contradiction_carried), True, "hard negative pressure", handoff_receipt_report=handoff_receipt_report, markers=markers)
        if marker.import_class is HandoffImportClass.CONTRADICTION_MEMORY and marker.contradiction_carried:
            contradiction = True
        prev = digest
    required = {cls.value for cls in required_classes}
    actual = {marker.import_class.value for marker in markers}
    if not required.issubset(actual):
        return _report(HandoffImportDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, contradiction, True, "missing required import class", handoff_receipt_report=handoff_receipt_report, markers=markers)
    if not contradiction:
        return _report(HandoffImportDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction memory did not survive import", handoff_receipt_report=handoff_receipt_report, markers=markers)
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(HandoffImportDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low import family diversity", handoff_receipt_report=handoff_receipt_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(HandoffImportDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low import path diversity", handoff_receipt_report=handoff_receipt_report, markers=markers)
    return _report(HandoffImportDecisionKind.ACCEPT_HANDOFF_IMPORTED, True, False, True, True, True, "handoff import accepted", handoff_receipt_report=handoff_receipt_report, markers=markers, accepted_marker_digest=prev)
