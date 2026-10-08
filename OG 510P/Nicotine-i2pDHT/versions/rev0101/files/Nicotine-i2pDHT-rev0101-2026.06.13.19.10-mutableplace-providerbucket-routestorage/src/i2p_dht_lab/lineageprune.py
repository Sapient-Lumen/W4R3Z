"""rev0072 lineage prune guard after summary receipt/import archive.

Pruning redacted summary-lineage working material is not cleanup.  It is a
protocol boundary that must preserve contradiction memory, accepted summary
receipt, import archive, and enough redacted state for wake-from-amnesia.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

LINEAGE_PRUNE_DOMAIN = DOMAIN + b":lineage-prune-v1:"


class LineagePruneClass(str, Enum):
    SUMMARY_RECEIPT = "summary_receipt"
    SUMMARY_LINEAGE = "summary_lineage"
    IMPORT_ARCHIVE = "import_archive"
    HANDOFF_IMPORT = "handoff_import"
    CONTRADICTION_MEMORY = "contradiction_memory"
    REDACTED_SUMMARY_MEMORY = "redacted_summary_memory"
    LOCAL_ARCHIVE_MARKER = "local_archive_marker"


class LineagePruneDecisionKind(str, Enum):
    ACCEPT_LINEAGE_PRUNE_GUARDED = "accept_lineage_prune_guarded"
    HOLD_IMPORT_ARCHIVE_PENDING = "hold_import_archive_pending"
    HOLD_SUMMARY_RECEIPT_PENDING = "hold_summary_receipt_pending"
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
class LineagePruneMarker:
    prune_class: LineagePruneClass
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
    summary_receipt_digest: bytes
    import_archive_digest: bytes
    summary_lineage_digest: bytes
    accepted_summary_entry_digest: bytes
    handoff_import_digest: bytes
    handoff_receipt_digest: bytes
    closure_handoff_digest: bytes
    retained_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(LINEAGE_PRUNE_DOMAIN + b":marker:" + bencode({
            b"class": LineagePruneClass(self.prune_class).value,
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
            b"summary_receipt": self.summary_receipt_digest,
            b"import_archive": self.import_archive_digest,
            b"summary_lineage": self.summary_lineage_digest,
            b"summary_entry": self.accepted_summary_entry_digest,
            b"import": self.handoff_import_digest,
            b"receipt": self.handoff_receipt_digest,
            b"handoff": self.closure_handoff_digest,
            b"retained": self.retained_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class LineagePruneReport:
    decision_kind: LineagePruneDecisionKind
    accept: bool
    watch: bool
    lineage_prune_guarded: bool
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
    summary_receipt_digest: bytes
    import_archive_digest: bytes
    summary_lineage_digest: bytes
    accepted_summary_entry_digest: bytes
    handoff_import_digest: bytes
    handoff_receipt_digest: bytes
    closure_handoff_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_packet_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: LineagePruneMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_lineage_prune_marker(*, prune_class: LineagePruneClass, sequence: int, summary_receipt_report: Any, import_archive_report: Any, previous_digest: bytes = ZERO_DIGEST, retained_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "lineage-prune-family-a", path_family_id: str = "lineage-prune-path-a", hard_negative_count: int = 0) -> LineagePruneMarker:
    cls = LineagePruneClass(prune_class)
    digest = retained_digest or sha256(LINEAGE_PRUNE_DOMAIN + b":retained:" + _digest(summary_receipt_report) + b":" + _digest(import_archive_report) + b":" + cls.value.encode())
    contradiction = bool(getattr(summary_receipt_report, "contradiction_carried", False) and getattr(import_archive_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    return LineagePruneMarker(
        prune_class=cls,
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_receipt_report, "action")),
        profile_id=getattr(summary_receipt_report, "profile_id"),
        service_name=getattr(summary_receipt_report, "service_name"),
        scope_digest=getattr(summary_receipt_report, "scope_digest"),
        request_digest=getattr(summary_receipt_report, "request_digest"),
        payload_digest=getattr(summary_receipt_report, "payload_digest"),
        idempotency_key=getattr(summary_receipt_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_receipt_digest=_digest(summary_receipt_report),
        import_archive_digest=_digest(import_archive_report),
        summary_lineage_digest=getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST),
        accepted_summary_entry_digest=getattr(summary_receipt_report, "accepted_summary_entry_digest", ZERO_DIGEST),
        handoff_import_digest=getattr(summary_receipt_report, "handoff_import_digest", ZERO_DIGEST),
        handoff_receipt_digest=getattr(summary_receipt_report, "handoff_receipt_digest", ZERO_DIGEST),
        closure_handoff_digest=getattr(summary_receipt_report, "closure_handoff_digest", ZERO_DIGEST),
        retained_digest=digest,
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: LineagePruneDecisionKind, accept: bool, watch: bool, guarded: bool, contradiction: bool, redacted: bool, reason: str, *, summary_receipt_report: Any, import_archive_report: Any, markers: tuple[LineagePruneMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> LineagePruneReport:
    digests = tuple(marker.marker_digest for marker in markers)
    classes = tuple(sorted({marker.prune_class.value for marker in markers}))
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = int(getattr(summary_receipt_report, "hard_negative_count", 0) or 0) + int(getattr(import_archive_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(LINEAGE_PRUNE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"guarded": 1 if guarded else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(summary_receipt_report, "action")).value,
        b"profile": getattr(summary_receipt_report, "profile_id"),
        b"service": getattr(summary_receipt_report, "service_name"),
        b"scope": getattr(summary_receipt_report, "scope_digest"),
        b"request": getattr(summary_receipt_report, "request_digest"),
        b"payload": getattr(summary_receipt_report, "payload_digest"),
        b"idem": getattr(summary_receipt_report, "idempotency_key"),
        b"retry_idem": getattr(summary_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        b"summary_receipt": _digest(summary_receipt_report),
        b"import_archive": _digest(import_archive_report),
        b"summary_lineage": getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST),
        b"summary_entry": getattr(summary_receipt_report, "accepted_summary_entry_digest", ZERO_DIGEST),
        b"import": getattr(summary_receipt_report, "handoff_import_digest", ZERO_DIGEST),
        b"receipt": getattr(summary_receipt_report, "handoff_receipt_digest", ZERO_DIGEST),
        b"handoff": getattr(summary_receipt_report, "closure_handoff_digest", ZERO_DIGEST),
        b"accepted_marker": accepted_marker_digest,
        b"classes": classes,
        b"markers": digests,
        b"families": sorted(families),
        b"paths": sorted(paths),
        b"hard": hard,
    }))
    return LineagePruneReport(
        kind, accept, watch, guarded, contradiction, redacted, reason,
        SideEffectAction(getattr(summary_receipt_report, "action")),
        getattr(summary_receipt_report, "profile_id"),
        getattr(summary_receipt_report, "service_name"),
        getattr(summary_receipt_report, "scope_digest"),
        getattr(summary_receipt_report, "request_digest"),
        getattr(summary_receipt_report, "payload_digest"),
        getattr(summary_receipt_report, "idempotency_key"),
        getattr(summary_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        _digest(summary_receipt_report),
        _digest(import_archive_report),
        getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST),
        getattr(summary_receipt_report, "accepted_summary_entry_digest", ZERO_DIGEST),
        getattr(summary_receipt_report, "handoff_import_digest", ZERO_DIGEST),
        getattr(summary_receipt_report, "handoff_receipt_digest", ZERO_DIGEST),
        getattr(summary_receipt_report, "closure_handoff_digest", ZERO_DIGEST),
        accepted_marker_digest,
        classes,
        digests,
        len(families),
        len(paths),
        hard,
        report_digest,
    )


def assess_lineage_prune(*, summary_receipt_report: Any, import_archive_report: Any, markers: tuple[LineagePruneMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[LineagePruneClass, ...] = (LineagePruneClass.SUMMARY_RECEIPT, LineagePruneClass.SUMMARY_LINEAGE, LineagePruneClass.IMPORT_ARCHIVE, LineagePruneClass.HANDOFF_IMPORT, LineagePruneClass.CONTRADICTION_MEMORY, LineagePruneClass.REDACTED_SUMMARY_MEMORY, LineagePruneClass.LOCAL_ARCHIVE_MARKER), min_family_count: int = 2, min_path_family_count: int = 2) -> LineagePruneReport:
    if not (getattr(summary_receipt_report, "accept", False) and getattr(summary_receipt_report, "summary_receipted", False)):
        return _report(LineagePruneDecisionKind.HOLD_SUMMARY_RECEIPT_PENDING, False, True, False, False, True, "summary receipt is not accepted", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    if not (getattr(import_archive_report, "accept", False) and getattr(import_archive_report, "import_archived", False)):
        return _report(LineagePruneDecisionKind.HOLD_IMPORT_ARCHIVE_PENDING, False, True, False, False, True, "import archive is not accepted", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    if _boundary(summary_receipt_report) != _boundary(import_archive_report):
        return _report(LineagePruneDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "summary receipt and import archive boundary drift", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    if getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST) != getattr(import_archive_report, "summary_lineage_digest", ZERO_DIGEST):
        return _report(LineagePruneDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "summary lineage digest drift across components", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    if not markers:
        return _report(LineagePruneDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, True, "no lineage prune markers", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    expected_boundary = _boundary(summary_receipt_report)
    expected_summary_receipt = _digest(summary_receipt_report)
    expected_archive = _digest(import_archive_report)
    expected_lineage = getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST)
    expected_entry = getattr(summary_receipt_report, "accepted_summary_entry_digest", ZERO_DIGEST)
    expected_import = getattr(summary_receipt_report, "handoff_import_digest", ZERO_DIGEST)
    expected_receipt = getattr(summary_receipt_report, "handoff_receipt_digest", ZERO_DIGEST)
    expected_handoff = getattr(summary_receipt_report, "closure_handoff_digest", ZERO_DIGEST)
    seen_seq: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    prev = previous_digest
    contradiction = False
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(LineagePruneDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, "duplicate lineage prune marker", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(LineagePruneDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive lineage prune sequence", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
        if marker.sequence in seen_seq and seen_seq[marker.sequence] != digest:
            return _report(LineagePruneDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence lineage prune fork", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
        seen_seq[marker.sequence] = digest
        if marker.previous_digest != prev:
            return _report(LineagePruneDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "previous digest mismatch", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
        if _marker_boundary(marker) != expected_boundary:
            return _report(LineagePruneDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "lineage prune boundary drift", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
        if (marker.summary_receipt_digest != expected_summary_receipt or marker.import_archive_digest != expected_archive or marker.summary_lineage_digest != expected_lineage or marker.accepted_summary_entry_digest != expected_entry or marker.handoff_import_digest != expected_import or marker.handoff_receipt_digest != expected_receipt or marker.closure_handoff_digest != expected_handoff):
            return _report(LineagePruneDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(LineagePruneDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "lineage prune leaked raw boundary or payload", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
        if marker.hard_negative_count or int(getattr(summary_receipt_report, "hard_negative_count", 0) or 0) or int(getattr(import_archive_report, "hard_negative_count", 0) or 0):
            return _report(LineagePruneDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, bool(marker.contradiction_carried), True, "hard negative pressure", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
        contradiction = contradiction or marker.contradiction_carried
        prev = digest
    if not contradiction:
        return _report(LineagePruneDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "lineage prune dropped contradiction memory", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    required = {LineagePruneClass(cls).value for cls in required_classes}
    actual = {marker.prune_class.value for marker in markers}
    if not required.issubset(actual):
        return _report(LineagePruneDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, True, "missing required lineage prune class", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(LineagePruneDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low lineage prune family diversity", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(LineagePruneDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low lineage prune path diversity", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers)
    return _report(LineagePruneDecisionKind.ACCEPT_LINEAGE_PRUNE_GUARDED, True, False, True, True, True, "lineage prune guarded", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, markers=markers, accepted_marker_digest=prev)
