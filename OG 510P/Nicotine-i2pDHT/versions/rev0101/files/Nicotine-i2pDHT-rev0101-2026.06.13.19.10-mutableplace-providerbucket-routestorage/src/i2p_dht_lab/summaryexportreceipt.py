"""rev0079 recipient receipt after the redacted-summary export fence.

The rev0078 export fence says a redacted summary edge is locally export-ready.
It does not say an operator, garden, or public-summary receiver acknowledged it.
This no-network lane makes receipt/refusal explicit restart-visible evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_EXPORT_RECEIPT_DOMAIN = DOMAIN + b":summary-export-receipt-v1:"


class SummaryExportReceiptClass(str, Enum):
    EXPORT_FENCE = "export_fence"
    RECIPIENT_ACK = "recipient_ack"
    CHANNEL_POLICY = "channel_policy"
    REDACTION_MEMORY = "redaction_memory"
    CONTRADICTION_MEMORY = "contradiction_memory"


class SummaryExportReceiptDecisionKind(str, Enum):
    ACCEPT_SUMMARY_EXPORT_RECEIPTED = "accept_summary_export_receipted"
    HOLD_EXPORT_PENDING = "hold_export_pending"
    HOLD_RECIPIENT_REFUSED = "hold_recipient_refused"
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
class SummaryExportReceiptMarker:
    receipt_class: SummaryExportReceiptClass
    sequence: int
    previous_digest: bytes
    receipt_kind: str
    recipient_kind: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_export_fence_digest: bytes
    accepted_export_marker_digest: bytes
    redacted_summary_digest: bytes
    export_channel: str
    contradiction_carried: bool
    redaction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(SUMMARY_EXPORT_RECEIPT_DOMAIN + b":marker:" + bencode({
            b"class": SummaryExportReceiptClass(self.receipt_class).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"receipt_kind": self.receipt_kind,
            b"recipient_kind": self.recipient_kind,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"export_fence": self.summary_export_fence_digest,
            b"export_marker": self.accepted_export_marker_digest,
            b"redacted_summary": self.redacted_summary_digest,
            b"channel": self.export_channel,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"redaction": 1 if self.redaction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryExportReceiptReport:
    decision_kind: SummaryExportReceiptDecisionKind
    accept: bool
    watch: bool
    summary_export_receipted: bool
    recipient_acknowledged: bool
    recipient_kind: str
    receipt_kind: str
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
    summary_export_fence_digest: bytes
    accepted_marker_digest: bytes
    accepted_export_marker_digest: bytes
    redacted_summary_digest: bytes
    export_channel: str
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


def _marker_boundary(marker: SummaryExportReceiptMarker) -> tuple[Any, ...]:
    return (
        SideEffectAction(marker.action),
        marker.profile_id,
        marker.service_name,
        marker.scope_digest,
        marker.request_digest,
        marker.payload_digest,
        marker.idempotency_key,
        marker.retry_idempotency_key,
    )


def make_summary_export_receipt_marker(*, receipt_class: SummaryExportReceiptClass, sequence: int, summary_export_fence_report: Any, previous_digest: bytes = ZERO_DIGEST, receipt_kind: str = "accepted", recipient_kind: str = "operator", contradiction_carried: bool = True, redaction_carried: bool = True, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "summary-export-receipt-family", path_family_id: str = "summary-export-receipt-path", hard_negative_count: int = 0) -> SummaryExportReceiptMarker:
    return SummaryExportReceiptMarker(
        receipt_class=SummaryExportReceiptClass(receipt_class), sequence=sequence, previous_digest=previous_digest, receipt_kind=receipt_kind, recipient_kind=recipient_kind,
        action=SideEffectAction(getattr(summary_export_fence_report, "action")), profile_id=getattr(summary_export_fence_report, "profile_id"), service_name=getattr(summary_export_fence_report, "service_name"), scope_digest=getattr(summary_export_fence_report, "scope_digest"), request_digest=getattr(summary_export_fence_report, "request_digest"), payload_digest=getattr(summary_export_fence_report, "payload_digest"), idempotency_key=getattr(summary_export_fence_report, "idempotency_key"), retry_idempotency_key=getattr(summary_export_fence_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_export_fence_digest=_digest(summary_export_fence_report), accepted_export_marker_digest=getattr(summary_export_fence_report, "accepted_marker_digest", ZERO_DIGEST), redacted_summary_digest=getattr(summary_export_fence_report, "redacted_summary_digest", ZERO_DIGEST), export_channel=getattr(summary_export_fence_report, "export_channel", "operator"), contradiction_carried=contradiction_carried, redaction_carried=redaction_carried, raw_boundary_exposed=raw_boundary_exposed, raw_payload_exposed=raw_payload_exposed, family_id=family_id, path_family_id=path_family_id, hard_negative_count=hard_negative_count,
    )


def _report(kind: SummaryExportReceiptDecisionKind, accept: bool, watch: bool, receipted: bool, contradiction: bool, redacted: bool, reason: str, *, summary_export_fence_report: Any, markers: tuple[SummaryExportReceiptMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> SummaryExportReceiptReport:
    class_values = tuple(sorted({marker.receipt_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    kinds = {marker.receipt_kind for marker in markers}
    recipients = {marker.recipient_kind for marker in markers}
    receipt_kind = sorted(kinds)[0] if len(kinds) == 1 else "mixed"
    recipient_kind = sorted(recipients)[0] if len(recipients) == 1 else "mixed"
    hard = int(getattr(summary_export_fence_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(SUMMARY_EXPORT_RECEIPT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0, b"receipted": 1 if receipted else 0, b"receipt_kind": receipt_kind, b"recipient": recipient_kind,
        b"export": _digest(summary_export_fence_report), b"accepted": accepted_marker_digest, b"classes": list(class_values), b"markers": list(marker_digests), b"families": len(families), b"paths": len(paths), b"contradiction": 1 if contradiction else 0, b"redacted": 1 if redacted else 0, b"hard": hard, b"reason": reason,
    }))
    return SummaryExportReceiptReport(kind, accept, watch, receipted, receipted and receipt_kind == "accepted", recipient_kind, receipt_kind, contradiction, contradiction, redacted, redacted, reason, SideEffectAction(getattr(summary_export_fence_report, "action")), getattr(summary_export_fence_report, "profile_id"), getattr(summary_export_fence_report, "service_name"), getattr(summary_export_fence_report, "scope_digest"), getattr(summary_export_fence_report, "request_digest"), getattr(summary_export_fence_report, "payload_digest"), getattr(summary_export_fence_report, "idempotency_key"), getattr(summary_export_fence_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_export_fence_report), accepted_marker_digest, getattr(summary_export_fence_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_export_fence_report, "redacted_summary_digest", ZERO_DIGEST), getattr(summary_export_fence_report, "export_channel", "operator"), class_values, marker_digests, len(families), len(paths), hard, report_digest)


def assess_summary_export_receipt(*, summary_export_fence_report: Any, markers: tuple[SummaryExportReceiptMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[SummaryExportReceiptClass, ...] = (SummaryExportReceiptClass.EXPORT_FENCE, SummaryExportReceiptClass.RECIPIENT_ACK, SummaryExportReceiptClass.CHANNEL_POLICY, SummaryExportReceiptClass.REDACTION_MEMORY, SummaryExportReceiptClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryExportReceiptReport:
    markers = tuple(markers)
    if not getattr(summary_export_fence_report, "summary_export_fenced", False) or not getattr(summary_export_fence_report, "export_ready", False):
        return _report(SummaryExportReceiptDecisionKind.HOLD_EXPORT_PENDING, False, True, False, False, False, "export fence pending", summary_export_fence_report=summary_export_fence_report, markers=markers)
    boundary = _boundary(summary_export_fence_report)
    if any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(SummaryExportReceiptDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", summary_export_fence_report=summary_export_fence_report, markers=markers)
    for marker in markers:
        if marker.summary_export_fence_digest != _digest(summary_export_fence_report) or marker.accepted_export_marker_digest != getattr(summary_export_fence_report, "accepted_marker_digest", ZERO_DIGEST):
            return _report(SummaryExportReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_export_fence_report=summary_export_fence_report, markers=markers)
        if marker.export_channel != getattr(summary_export_fence_report, "export_channel", "operator"):
            return _report(SummaryExportReceiptDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "channel drift", summary_export_fence_report=summary_export_fence_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(SummaryExportReceiptDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw leak", summary_export_fence_report=summary_export_fence_report, markers=markers)
    if any(marker.receipt_kind == "refused" for marker in markers):
        return _report(SummaryExportReceiptDecisionKind.HOLD_RECIPIENT_REFUSED, False, True, False, True, True, "recipient refused", summary_export_fence_report=summary_export_fence_report, markers=markers)
    contradiction = bool(getattr(summary_export_fence_report, "contradiction_preserved", False) and all(marker.contradiction_carried for marker in markers))
    if not contradiction:
        return _report(SummaryExportReceiptDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction dropped", summary_export_fence_report=summary_export_fence_report, markers=markers)
    redacted = bool(getattr(summary_export_fence_report, "redacted", False) and all(marker.redaction_carried for marker in markers))
    if not redacted:
        return _report(SummaryExportReceiptDecisionKind.QUARANTINE_REDACTION_DROPPED, False, True, False, True, False, "redaction dropped", summary_export_fence_report=summary_export_fence_report, markers=markers)
    hard = int(getattr(summary_export_fence_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(SummaryExportReceiptDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "hard negatives", summary_export_fence_report=summary_export_fence_report, markers=markers)
    if not set(required_classes).issubset({marker.receipt_class for marker in markers}):
        return _report(SummaryExportReceiptDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing class", summary_export_fence_report=summary_export_fence_report, markers=markers)
    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(SummaryExportReceiptDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed marker", summary_export_fence_report=summary_export_fence_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(SummaryExportReceiptDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", summary_export_fence_report=summary_export_fence_report, markers=markers)
        if marker.sequence in seen_sequences and seen_sequences[marker.sequence] != digest:
            return _report(SummaryExportReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", summary_export_fence_report=summary_export_fence_report, markers=markers)
        seen_sequences[marker.sequence] = digest
        if marker.previous_digest != previous:
            return _report(SummaryExportReceiptDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous mismatch", summary_export_fence_report=summary_export_fence_report, markers=markers)
        previous = digest
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(SummaryExportReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", summary_export_fence_report=summary_export_fence_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(SummaryExportReceiptDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", summary_export_fence_report=summary_export_fence_report, markers=markers)
    accepted = previous if markers else ZERO_DIGEST
    return _report(SummaryExportReceiptDecisionKind.ACCEPT_SUMMARY_EXPORT_RECEIPTED, True, False, True, True, redacted, "summary export receipt accepted", summary_export_fence_report=summary_export_fence_report, markers=markers, accepted_marker_digest=accepted)
