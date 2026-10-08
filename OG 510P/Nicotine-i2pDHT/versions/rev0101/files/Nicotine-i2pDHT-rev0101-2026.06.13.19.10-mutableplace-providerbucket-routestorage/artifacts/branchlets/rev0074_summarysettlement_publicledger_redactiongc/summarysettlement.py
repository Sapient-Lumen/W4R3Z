"""rev0074 summary settlement after redacted summary publication.

A redacted public-summary publication, redaction witness mesh, and import-prune
restart audit are not yet settled public-summary state.  Settlement is a compact
local marker that binds those reports at one exact boundary while preserving
contradiction memory and redaction evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_SETTLEMENT_DOMAIN = DOMAIN + b":summary-settlement-v1:"


class SummarySettlementClass(str, Enum):
    PUBLICATION_READY = "publication_ready"
    REDACTION_WITNESSED = "redaction_witnessed"
    IMPORT_PRUNE_AUDITED = "import_prune_audited"
    CONTRADICTION_MEMORY = "contradiction_memory"
    REDACTED_SUMMARY_MEMORY = "redacted_summary_memory"
    LOCAL_SETTLEMENT_STATE = "local_settlement_state"


class SummarySettlementDecisionKind(str, Enum):
    ACCEPT_SUMMARY_SETTLED = "accept_summary_settled"
    HOLD_PUBLICATION_PENDING = "hold_publication_pending"
    HOLD_REDACTION_PENDING = "hold_redaction_pending"
    HOLD_IMPORT_PRUNE_AUDIT_PENDING = "hold_import_prune_audit_pending"
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
class SummarySettlementMarker:
    settlement_class: SummarySettlementClass
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
    import_prune_audit_digest: bytes
    accepted_intent_digest: bytes
    accepted_redaction_receipt_digest: bytes
    accepted_import_prune_marker_digest: bytes
    contradiction_carried: bool
    redacted: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(SUMMARY_SETTLEMENT_DOMAIN + b":marker:" + bencode({
            b"class": SummarySettlementClass(self.settlement_class).value,
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
            b"audit": self.import_prune_audit_digest,
            b"intent": self.accepted_intent_digest,
            b"redaction_receipt": self.accepted_redaction_receipt_digest,
            b"audit_marker": self.accepted_import_prune_marker_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"redacted": 1 if self.redacted else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummarySettlementReport:
    decision_kind: SummarySettlementDecisionKind
    accept: bool
    watch: bool
    summary_settled: bool
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_packet_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: SummarySettlementMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_summary_settlement_marker(*, settlement_class: SummarySettlementClass, sequence: int, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_carried: bool | None = None, redacted: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "settle-family-a", path_family_id: str = "settle-path-a", hard_negative_count: int = 0) -> SummarySettlementMarker:
    contradiction = bool(getattr(summary_publish_report, "contradiction_carried", False) and getattr(redaction_witness_report, "contradiction_carried", False) and getattr(import_prune_audit_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    redaction_ok = bool(getattr(summary_publish_report, "redacted", False) and getattr(redaction_witness_report, "redacted", False) and getattr(import_prune_audit_report, "redacted", False)) if redacted is None else bool(redacted)
    return SummarySettlementMarker(
        settlement_class=SummarySettlementClass(settlement_class),
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
        import_prune_audit_digest=_digest(import_prune_audit_report),
        accepted_intent_digest=getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST),
        accepted_redaction_receipt_digest=getattr(redaction_witness_report, "accepted_receipt_digest", ZERO_DIGEST),
        accepted_import_prune_marker_digest=getattr(import_prune_audit_report, "accepted_marker_digest", ZERO_DIGEST),
        contradiction_carried=contradiction,
        redacted=redaction_ok,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=int(hard_negative_count),
    )


def _report(kind: SummarySettlementDecisionKind, accept: bool, watch: bool, settled: bool, contradiction: bool, redacted: bool, reason: str, *, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, markers: tuple[SummarySettlementMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> SummarySettlementReport:
    marker_digests = tuple(marker.marker_digest for marker in markers)
    class_values = tuple(sorted({marker.settlement_class.value for marker in markers}))
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_witness_report, "hard_negative_count", 0) or 0) + int(getattr(import_prune_audit_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    digest = sha256(SUMMARY_SETTLEMENT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"settled": 1 if settled else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"reason": reason,
        b"publish": _digest(summary_publish_report),
        b"redaction": _digest(redaction_witness_report),
        b"audit": _digest(import_prune_audit_report),
        b"accepted": accepted_marker_digest,
        b"classes": list(class_values),
        b"markers": list(marker_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return SummarySettlementReport(kind, accept, watch, settled, contradiction, redacted, reason, SideEffectAction(getattr(summary_publish_report, "action")), getattr(summary_publish_report, "profile_id"), getattr(summary_publish_report, "service_name"), getattr(summary_publish_report, "scope_digest"), getattr(summary_publish_report, "request_digest"), getattr(summary_publish_report, "payload_digest"), getattr(summary_publish_report, "idempotency_key"), getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_publish_report), _digest(redaction_witness_report), _digest(import_prune_audit_report), accepted_marker_digest, class_values, marker_digests, len(families), len(paths), hard, digest)


def assess_summary_settlement(*, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, markers: tuple[SummarySettlementMarker, ...], previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2, required_classes: tuple[SummarySettlementClass, ...] = (SummarySettlementClass.PUBLICATION_READY, SummarySettlementClass.REDACTION_WITNESSED, SummarySettlementClass.IMPORT_PRUNE_AUDITED, SummarySettlementClass.CONTRADICTION_MEMORY, SummarySettlementClass.REDACTED_SUMMARY_MEMORY, SummarySettlementClass.LOCAL_SETTLEMENT_STATE)) -> SummarySettlementReport:
    markers = tuple(markers)
    if not getattr(summary_publish_report, "accept", False) or not getattr(summary_publish_report, "publication_ready", False):
        return _report(SummarySettlementDecisionKind.HOLD_PUBLICATION_PENDING, False, True, False, False, False, "summary publication is not ready", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if not getattr(redaction_witness_report, "accept", False) or not getattr(redaction_witness_report, "redaction_witnessed", False):
        return _report(SummarySettlementDecisionKind.HOLD_REDACTION_PENDING, False, True, False, False, False, "redaction witness not accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if not getattr(import_prune_audit_report, "accept", False) or not getattr(import_prune_audit_report, "import_prune_audited", False):
        return _report(SummarySettlementDecisionKind.HOLD_IMPORT_PRUNE_AUDIT_PENDING, False, True, False, False, False, "import-prune audit not accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    boundary = _boundary(summary_publish_report)
    if _boundary(redaction_witness_report) != boundary or _boundary(import_prune_audit_report) != boundary or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(SummarySettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "component or marker boundary drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    publish_digest = _digest(summary_publish_report)
    redaction_digest = _digest(redaction_witness_report)
    audit_digest = _digest(import_prune_audit_report)
    if getattr(redaction_witness_report, "summary_publish_digest", publish_digest) != publish_digest or getattr(import_prune_audit_report, "summary_publish_digest", publish_digest) != publish_digest or getattr(import_prune_audit_report, "redaction_witness_digest", redaction_digest) != redaction_digest:
        return _report(SummarySettlementDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if any(marker.summary_publish_digest != publish_digest or marker.redaction_witness_digest != redaction_digest or marker.import_prune_audit_digest != audit_digest for marker in markers):
        return _report(SummarySettlementDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "marker digest drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if any(marker.raw_boundary_exposed or marker.raw_payload_exposed for marker in markers):
        return _report(SummarySettlementDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw boundary or payload exposed", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    required = {SummarySettlementClass(item).value for item in required_classes}
    classes = {marker.settlement_class.value for marker in markers}
    if not required.issubset(classes):
        return _report(SummarySettlementDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, False, "missing settlement marker class", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    prev = previous_digest
    seen: dict[int, bytes] = {}
    for marker in sorted(markers, key=lambda item: item.sequence):
        if marker.sequence <= 0:
            return _report(SummarySettlementDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive sequence", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        digest = marker.marker_digest
        old = seen.get(marker.sequence)
        if old is not None and old != digest:
            return _report(SummarySettlementDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence fork", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        if marker.previous_digest != prev:
            return _report(SummarySettlementDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "previous digest mismatch", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        seen[marker.sequence] = digest
        prev = digest
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(SummarySettlementDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, "low settlement family diversity", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(SummarySettlementDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, "low settlement path diversity", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    contradiction = bool(getattr(summary_publish_report, "contradiction_carried", False) and getattr(redaction_witness_report, "contradiction_carried", False) and getattr(import_prune_audit_report, "contradiction_preserved", False) and all(marker.contradiction_carried for marker in markers))
    if not contradiction:
        return _report(SummarySettlementDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, False, "contradiction memory dropped", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    redacted = bool(getattr(summary_publish_report, "redacted", False) and getattr(redaction_witness_report, "redacted", False) and getattr(import_prune_audit_report, "redacted", False) and all(marker.redacted for marker in markers))
    if not redacted:
        return _report(SummarySettlementDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "redaction evidence dropped", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    hard = int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_witness_report, "hard_negative_count", 0) or 0) + int(getattr(import_prune_audit_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(SummarySettlementDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, True, "hard negative pressure", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    return _report(SummarySettlementDecisionKind.ACCEPT_SUMMARY_SETTLED, True, False, True, True, True, "summary settlement accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers, accepted_marker_digest=prev)
