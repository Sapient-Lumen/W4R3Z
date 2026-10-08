"""rev0076 no-network summary outbox drain after summary-send canary.

A summary-send canary is not a drain.  This lane records the exact-boundary
permission to drain a staged redacted summary outbox item without performing a
network write.  It deliberately carries redaction and contradiction memory
forward because those are the first things convenience cleanup tends to lose.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_DRAIN_DOMAIN = DOMAIN + b":summary-drain-v1:"


class SummaryDrainClass(str, Enum):
    SEND_CANARY = "send_canary"
    OUTBOX_SETTLEMENT = "outbox_settlement"
    PUBLIC_LEDGER = "public_ledger"
    REDACTION_GC = "redaction_gc"
    REDACTION_OK = "redaction_ok"
    IDEMPOTENCY = "idempotency"
    CONTRADICTION_MEMORY = "contradiction_memory"


class SummaryDrainDecisionKind(str, Enum):
    ACCEPT_SUMMARY_DRAIN_READY = "accept_summary_drain_ready"
    HOLD_CANARY_PENDING = "hold_canary_pending"
    HOLD_MISSING_REQUIRED_CLASS = "hold_missing_required_class"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_ENDPOINT_DRIFT = "quarantine_endpoint_drift"
    QUARANTINE_RAW_LEAK = "quarantine_raw_leak"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SummaryDrainMarker:
    drain_class: SummaryDrainClass
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
    summary_send_canary_digest: bytes
    outbox_settlement_digest: bytes
    publish_fence_digest: bytes
    public_ledger_digest: bytes
    redaction_gc_digest: bytes
    accepted_canary_marker_digest: bytes
    accepted_settlement_marker_digest: bytes
    accepted_fence_marker_digest: bytes
    accepted_public_ledger_entry_digest: bytes
    accepted_redaction_gc_proposal_digest: bytes
    destination_digest: bytes
    sam_endpoint_digest: bytes
    redacted_summary_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(SUMMARY_DRAIN_DOMAIN + b":marker:" + bencode({
            b"class": SummaryDrainClass(self.drain_class).value,
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
            b"canary": self.summary_send_canary_digest,
            b"settlement": self.outbox_settlement_digest,
            b"fence": self.publish_fence_digest,
            b"ledger": self.public_ledger_digest,
            b"gc": self.redaction_gc_digest,
            b"canary_marker": self.accepted_canary_marker_digest,
            b"settlement_marker": self.accepted_settlement_marker_digest,
            b"fence_marker": self.accepted_fence_marker_digest,
            b"ledger_entry": self.accepted_public_ledger_entry_digest,
            b"gc_proposal": self.accepted_redaction_gc_proposal_digest,
            b"destination": self.destination_digest,
            b"sam_endpoint": self.sam_endpoint_digest,
            b"redacted_summary": self.redacted_summary_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryDrainReport:
    decision_kind: SummaryDrainDecisionKind
    accept: bool
    watch: bool
    summary_drain_ready: bool
    summary_drained: bool
    contradiction_preserved: bool
    contradiction_carried: bool
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
    summary_send_canary_digest: bytes
    outbox_settlement_digest: bytes
    publish_fence_digest: bytes
    public_ledger_digest: bytes
    redaction_gc_digest: bytes
    accepted_marker_digest: bytes
    accepted_canary_marker_digest: bytes
    accepted_settlement_marker_digest: bytes
    accepted_fence_marker_digest: bytes
    accepted_public_ledger_entry_digest: bytes
    accepted_redaction_gc_proposal_digest: bytes
    destination_digest: bytes
    sam_endpoint_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_proposal_digest"):
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


def _marker_boundary(marker: SummaryDrainMarker) -> tuple[Any, ...]:
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


def make_summary_drain_marker(
    *,
    drain_class: SummaryDrainClass,
    sequence: int,
    summary_send_canary_report: Any,
    previous_digest: bytes = ZERO_DIGEST,
    contradiction_carried: bool = True,
    raw_boundary_exposed: bool = False,
    raw_payload_exposed: bool = False,
    family_id: str = "summary-drain-family",
    path_family_id: str = "summary-drain-path",
    hard_negative_count: int = 0,
) -> SummaryDrainMarker:
    return SummaryDrainMarker(
        drain_class=SummaryDrainClass(drain_class),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_send_canary_report, "action")),
        profile_id=getattr(summary_send_canary_report, "profile_id"),
        service_name=getattr(summary_send_canary_report, "service_name"),
        scope_digest=getattr(summary_send_canary_report, "scope_digest"),
        request_digest=getattr(summary_send_canary_report, "request_digest"),
        payload_digest=getattr(summary_send_canary_report, "payload_digest"),
        idempotency_key=getattr(summary_send_canary_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_send_canary_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_send_canary_digest=_digest(summary_send_canary_report),
        outbox_settlement_digest=getattr(summary_send_canary_report, "outbox_settlement_digest", ZERO_DIGEST),
        publish_fence_digest=getattr(summary_send_canary_report, "publish_fence_digest", ZERO_DIGEST),
        public_ledger_digest=getattr(summary_send_canary_report, "public_ledger_digest", ZERO_DIGEST),
        redaction_gc_digest=getattr(summary_send_canary_report, "redaction_gc_digest", ZERO_DIGEST),
        accepted_canary_marker_digest=getattr(summary_send_canary_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_settlement_marker_digest=getattr(summary_send_canary_report, "accepted_settlement_marker_digest", ZERO_DIGEST),
        accepted_fence_marker_digest=getattr(summary_send_canary_report, "accepted_fence_marker_digest", ZERO_DIGEST),
        accepted_public_ledger_entry_digest=getattr(summary_send_canary_report, "accepted_public_ledger_entry_digest", ZERO_DIGEST),
        accepted_redaction_gc_proposal_digest=getattr(summary_send_canary_report, "accepted_redaction_gc_proposal_digest", ZERO_DIGEST),
        destination_digest=getattr(summary_send_canary_report, "destination_digest", ZERO_DIGEST),
        sam_endpoint_digest=getattr(summary_send_canary_report, "sam_endpoint_digest", ZERO_DIGEST),
        redacted_summary_digest=getattr(summary_send_canary_report, "redacted_summary_digest", ZERO_DIGEST),
        contradiction_carried=contradiction_carried,
        raw_boundary_exposed=raw_boundary_exposed,
        raw_payload_exposed=raw_payload_exposed,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(
    kind: SummaryDrainDecisionKind,
    accept: bool,
    watch: bool,
    ready: bool,
    contradiction: bool,
    redacted: bool,
    reason: str,
    *,
    summary_send_canary_report: Any,
    markers: tuple[SummaryDrainMarker, ...],
    accepted_marker_digest: bytes = ZERO_DIGEST,
) -> SummaryDrainReport:
    class_values = tuple(sorted({marker.drain_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = int(getattr(summary_send_canary_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(SUMMARY_DRAIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"ready": 1 if ready else 0,
        b"canary": _digest(summary_send_canary_report),
        b"accepted": accepted_marker_digest,
        b"classes": list(class_values),
        b"markers": list(marker_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"hard": hard,
        b"reason": reason,
    }))
    return SummaryDrainReport(
        decision_kind=kind,
        accept=accept,
        watch=watch,
        summary_drain_ready=ready,
        summary_drained=ready,
        contradiction_preserved=contradiction,
        contradiction_carried=contradiction,
        redacted=redacted,
        reason=reason,
        action=SideEffectAction(getattr(summary_send_canary_report, "action")),
        profile_id=getattr(summary_send_canary_report, "profile_id"),
        service_name=getattr(summary_send_canary_report, "service_name"),
        scope_digest=getattr(summary_send_canary_report, "scope_digest"),
        request_digest=getattr(summary_send_canary_report, "request_digest"),
        payload_digest=getattr(summary_send_canary_report, "payload_digest"),
        idempotency_key=getattr(summary_send_canary_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_send_canary_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_send_canary_digest=_digest(summary_send_canary_report),
        outbox_settlement_digest=getattr(summary_send_canary_report, "outbox_settlement_digest", ZERO_DIGEST),
        publish_fence_digest=getattr(summary_send_canary_report, "publish_fence_digest", ZERO_DIGEST),
        public_ledger_digest=getattr(summary_send_canary_report, "public_ledger_digest", ZERO_DIGEST),
        redaction_gc_digest=getattr(summary_send_canary_report, "redaction_gc_digest", ZERO_DIGEST),
        accepted_marker_digest=accepted_marker_digest,
        accepted_canary_marker_digest=getattr(summary_send_canary_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_settlement_marker_digest=getattr(summary_send_canary_report, "accepted_settlement_marker_digest", ZERO_DIGEST),
        accepted_fence_marker_digest=getattr(summary_send_canary_report, "accepted_fence_marker_digest", ZERO_DIGEST),
        accepted_public_ledger_entry_digest=getattr(summary_send_canary_report, "accepted_public_ledger_entry_digest", ZERO_DIGEST),
        accepted_redaction_gc_proposal_digest=getattr(summary_send_canary_report, "accepted_redaction_gc_proposal_digest", ZERO_DIGEST),
        destination_digest=getattr(summary_send_canary_report, "destination_digest", ZERO_DIGEST),
        sam_endpoint_digest=getattr(summary_send_canary_report, "sam_endpoint_digest", ZERO_DIGEST),
        redacted_summary_digest=getattr(summary_send_canary_report, "redacted_summary_digest", ZERO_DIGEST),
        class_values=class_values,
        marker_digests=marker_digests,
        family_count=len(families),
        path_family_count=len(paths),
        hard_negative_count=hard,
        report_digest=report_digest,
    )


def assess_summary_drain(
    *,
    summary_send_canary_report: Any,
    markers: tuple[SummaryDrainMarker, ...],
    previous_digest: bytes = ZERO_DIGEST,
    required_classes: tuple[SummaryDrainClass, ...] = (
        SummaryDrainClass.SEND_CANARY,
        SummaryDrainClass.OUTBOX_SETTLEMENT,
        SummaryDrainClass.PUBLIC_LEDGER,
        SummaryDrainClass.REDACTION_GC,
        SummaryDrainClass.REDACTION_OK,
        SummaryDrainClass.IDEMPOTENCY,
        SummaryDrainClass.CONTRADICTION_MEMORY,
    ),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SummaryDrainReport:
    markers = tuple(markers)
    if not getattr(summary_send_canary_report, "send_canary_ready", False):
        return _report(SummaryDrainDecisionKind.HOLD_CANARY_PENDING, False, True, False, False, False, "summary send canary pending", summary_send_canary_report=summary_send_canary_report, markers=markers)

    boundary = _boundary(summary_send_canary_report)
    if any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(SummaryDrainDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "marker boundary drift", summary_send_canary_report=summary_send_canary_report, markers=markers)

    expected_canary = _digest(summary_send_canary_report)
    expected = {
        "outbox_settlement_digest": getattr(summary_send_canary_report, "outbox_settlement_digest", ZERO_DIGEST),
        "publish_fence_digest": getattr(summary_send_canary_report, "publish_fence_digest", ZERO_DIGEST),
        "public_ledger_digest": getattr(summary_send_canary_report, "public_ledger_digest", ZERO_DIGEST),
        "redaction_gc_digest": getattr(summary_send_canary_report, "redaction_gc_digest", ZERO_DIGEST),
        "accepted_canary_marker_digest": getattr(summary_send_canary_report, "accepted_marker_digest", ZERO_DIGEST),
        "accepted_settlement_marker_digest": getattr(summary_send_canary_report, "accepted_settlement_marker_digest", ZERO_DIGEST),
        "accepted_fence_marker_digest": getattr(summary_send_canary_report, "accepted_fence_marker_digest", ZERO_DIGEST),
        "accepted_public_ledger_entry_digest": getattr(summary_send_canary_report, "accepted_public_ledger_entry_digest", ZERO_DIGEST),
        "accepted_redaction_gc_proposal_digest": getattr(summary_send_canary_report, "accepted_redaction_gc_proposal_digest", ZERO_DIGEST),
    }
    for marker in markers:
        if marker.summary_send_canary_digest != expected_canary or any(getattr(marker, key) != value for key, value in expected.items()):
            return _report(SummaryDrainDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_send_canary_report=summary_send_canary_report, markers=markers)
        if (
            marker.destination_digest != getattr(summary_send_canary_report, "destination_digest", ZERO_DIGEST)
            or marker.sam_endpoint_digest != getattr(summary_send_canary_report, "sam_endpoint_digest", ZERO_DIGEST)
            or marker.redacted_summary_digest != getattr(summary_send_canary_report, "redacted_summary_digest", ZERO_DIGEST)
        ):
            return _report(SummaryDrainDecisionKind.QUARANTINE_ENDPOINT_DRIFT, False, True, False, False, False, "endpoint or redacted-summary drift", summary_send_canary_report=summary_send_canary_report, markers=markers)
    if any(marker.raw_boundary_exposed or marker.raw_payload_exposed for marker in markers):
        return _report(SummaryDrainDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw boundary or payload exposure", summary_send_canary_report=summary_send_canary_report, markers=markers)

    contradiction = bool(getattr(summary_send_canary_report, "contradiction_preserved", False) and all(marker.contradiction_carried for marker in markers))
    redacted = bool(getattr(summary_send_canary_report, "redacted", False) and all(marker.redacted_summary_digest != ZERO_DIGEST for marker in markers))
    if not contradiction:
        return _report(SummaryDrainDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, redacted, "contradiction memory missing", summary_send_canary_report=summary_send_canary_report, markers=markers)
    hard = int(getattr(summary_send_canary_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(SummaryDrainDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "hard-negative pressure", summary_send_canary_report=summary_send_canary_report, markers=markers)
    if not set(required_classes).issubset({marker.drain_class for marker in markers}):
        return _report(SummaryDrainDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing required drain class", summary_send_canary_report=summary_send_canary_report, markers=markers)

    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(SummaryDrainDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed marker", summary_send_canary_report=summary_send_canary_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(SummaryDrainDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", summary_send_canary_report=summary_send_canary_report, markers=markers)
        if marker.sequence in seen_sequences and seen_sequences[marker.sequence] != digest:
            return _report(SummaryDrainDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", summary_send_canary_report=summary_send_canary_report, markers=markers)
        seen_sequences[marker.sequence] = digest
        if marker.previous_digest != previous:
            return _report(SummaryDrainDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous-link mismatch", summary_send_canary_report=summary_send_canary_report, markers=markers)
        previous = digest

    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(SummaryDrainDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", summary_send_canary_report=summary_send_canary_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(SummaryDrainDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", summary_send_canary_report=summary_send_canary_report, markers=markers)

    accepted = previous if markers else ZERO_DIGEST
    return _report(SummaryDrainDecisionKind.ACCEPT_SUMMARY_DRAIN_READY, True, False, True, True, redacted, "summary drain ready", summary_send_canary_report=summary_send_canary_report, markers=markers, accepted_marker_digest=accepted)
