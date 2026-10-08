"""rev0075 no-network canary before redacted-summary send.

The canary is not a live send. It joins outbox settlement, publish fence,
public ledger, and redaction GC before a future public summary write can even be
considered.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_SEND_CANARY_DOMAIN = DOMAIN + b":summary-send-canary-v2:"


class SummarySendCanaryClass(str, Enum):
    OUTBOX_SETTLEMENT = "outbox_settlement"
    PUBLISH_FENCE = "publish_fence"
    PUBLIC_LEDGER = "public_ledger"
    REDACTION_GC = "redaction_gc"
    REDACTION_OK = "redaction_ok"
    CONTRADICTION_MEMORY = "contradiction_memory"


class SummarySendCanaryDecisionKind(str, Enum):
    ACCEPT_SUMMARY_SEND_CANARY = "accept_summary_send_canary"
    HOLD_OUTBOX_SETTLEMENT_PENDING = "hold_outbox_settlement_pending"
    HOLD_FENCE_PENDING = "hold_fence_pending"
    HOLD_PUBLIC_LEDGER_PENDING = "hold_public_ledger_pending"
    HOLD_REDACTION_GC_PENDING = "hold_redaction_gc_pending"
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
class SummarySendCanaryMarker:
    canary_class: SummarySendCanaryClass
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
    outbox_settlement_digest: bytes
    publish_fence_digest: bytes
    public_ledger_digest: bytes
    redaction_gc_digest: bytes
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
        return sha256(SUMMARY_SEND_CANARY_DOMAIN + b":marker:" + bencode({
            b"class": SummarySendCanaryClass(self.canary_class).value,
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
            b"settlement": self.outbox_settlement_digest,
            b"fence": self.publish_fence_digest,
            b"ledger": self.public_ledger_digest,
            b"gc": self.redaction_gc_digest,
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
class SummarySendCanaryReport:
    decision_kind: SummarySendCanaryDecisionKind
    accept: bool
    watch: bool
    send_canary_ready: bool
    canary_ready: bool
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
    outbox_settlement_digest: bytes
    publish_fence_digest: bytes
    public_ledger_digest: bytes
    redaction_gc_digest: bytes
    accepted_marker_digest: bytes
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


def _marker_boundary(marker: SummarySendCanaryMarker) -> tuple[Any, ...]:
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


def _default_destination_digest(outbox_settlement_report: Any, public_ledger_report: Any) -> bytes:
    return sha256(SUMMARY_SEND_CANARY_DOMAIN + b":destination:" + _digest(outbox_settlement_report) + _digest(public_ledger_report))


def _default_sam_endpoint_digest(outbox_settlement_report: Any, redaction_gc_report: Any) -> bytes:
    return sha256(SUMMARY_SEND_CANARY_DOMAIN + b":sam-endpoint:" + _digest(outbox_settlement_report) + _digest(redaction_gc_report))


def _default_redacted_summary_digest(outbox_settlement_report: Any, public_ledger_report: Any, redaction_gc_report: Any) -> bytes:
    return sha256(SUMMARY_SEND_CANARY_DOMAIN + b":redacted-summary:" + _digest(outbox_settlement_report) + _digest(public_ledger_report) + _digest(redaction_gc_report))


def make_summary_send_canary_marker(
    *,
    canary_class: SummarySendCanaryClass,
    sequence: int,
    outbox_settlement_report: Any,
    publish_fence_report: Any,
    public_ledger_report: Any,
    redaction_gc_report: Any,
    previous_digest: bytes = ZERO_DIGEST,
    destination_digest: bytes | None = None,
    sam_endpoint_digest: bytes | None = None,
    redacted_summary_digest: bytes | None = None,
    contradiction_carried: bool | None = None,
    raw_boundary_exposed: bool = False,
    raw_payload_exposed: bool = False,
    family_id: str = "summary-canary-family-a",
    path_family_id: str = "summary-canary-path-a",
    hard_negative_count: int = 0,
) -> SummarySendCanaryMarker:
    contradiction = bool(
        getattr(outbox_settlement_report, "contradiction_preserved", False)
        and getattr(publish_fence_report, "contradiction_preserved", False)
        and getattr(public_ledger_report, "contradiction_preserved", False)
        and getattr(redaction_gc_report, "contradiction_retained", False)
    ) if contradiction_carried is None else bool(contradiction_carried)
    return SummarySendCanaryMarker(
        canary_class=SummarySendCanaryClass(canary_class),
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(outbox_settlement_report, "action")),
        profile_id=getattr(outbox_settlement_report, "profile_id"),
        service_name=getattr(outbox_settlement_report, "service_name"),
        scope_digest=getattr(outbox_settlement_report, "scope_digest"),
        request_digest=getattr(outbox_settlement_report, "request_digest"),
        payload_digest=getattr(outbox_settlement_report, "payload_digest"),
        idempotency_key=getattr(outbox_settlement_report, "idempotency_key"),
        retry_idempotency_key=getattr(outbox_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        outbox_settlement_digest=_digest(outbox_settlement_report),
        publish_fence_digest=_digest(publish_fence_report),
        public_ledger_digest=_digest(public_ledger_report),
        redaction_gc_digest=_digest(redaction_gc_report),
        accepted_settlement_marker_digest=getattr(outbox_settlement_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_fence_marker_digest=getattr(publish_fence_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_public_ledger_entry_digest=getattr(public_ledger_report, "accepted_entry_digest", ZERO_DIGEST),
        accepted_redaction_gc_proposal_digest=getattr(redaction_gc_report, "accepted_proposal_digest", ZERO_DIGEST),
        destination_digest=destination_digest or _default_destination_digest(outbox_settlement_report, public_ledger_report),
        sam_endpoint_digest=sam_endpoint_digest or _default_sam_endpoint_digest(outbox_settlement_report, redaction_gc_report),
        redacted_summary_digest=redacted_summary_digest or _default_redacted_summary_digest(outbox_settlement_report, public_ledger_report, redaction_gc_report),
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(
    kind: SummarySendCanaryDecisionKind,
    accept: bool,
    watch: bool,
    ready: bool,
    contradiction: bool,
    redacted: bool,
    reason: str,
    *,
    outbox_settlement_report: Any,
    publish_fence_report: Any,
    public_ledger_report: Any,
    redaction_gc_report: Any,
    markers: tuple[SummarySendCanaryMarker, ...],
    accepted_marker_digest: bytes = ZERO_DIGEST,
) -> SummarySendCanaryReport:
    classes = tuple(sorted({marker.canary_class.value for marker in markers}))
    digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (outbox_settlement_report, publish_fence_report, public_ledger_report, redaction_gc_report)) + sum(marker.hard_negative_count for marker in markers)
    first = markers[0] if markers else None
    destination_digest = first.destination_digest if first else _default_destination_digest(outbox_settlement_report, public_ledger_report)
    sam_endpoint_digest = first.sam_endpoint_digest if first else _default_sam_endpoint_digest(outbox_settlement_report, redaction_gc_report)
    redacted_summary_digest = first.redacted_summary_digest if first else _default_redacted_summary_digest(outbox_settlement_report, public_ledger_report, redaction_gc_report)
    report_digest = sha256(SUMMARY_SEND_CANARY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"ready": 1 if ready else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"settlement": _digest(outbox_settlement_report),
        b"fence": _digest(publish_fence_report),
        b"ledger": _digest(public_ledger_report),
        b"gc": _digest(redaction_gc_report),
        b"accepted": accepted_marker_digest,
        b"destination": destination_digest,
        b"sam": sam_endpoint_digest,
        b"redacted_summary": redacted_summary_digest,
        b"classes": list(classes),
        b"markers": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return SummarySendCanaryReport(
        decision_kind=kind,
        accept=accept,
        watch=watch,
        send_canary_ready=ready,
        canary_ready=ready,
        contradiction_preserved=contradiction,
        contradiction_carried=contradiction,
        redacted=redacted,
        reason=reason,
        action=SideEffectAction(getattr(outbox_settlement_report, "action")),
        profile_id=getattr(outbox_settlement_report, "profile_id"),
        service_name=getattr(outbox_settlement_report, "service_name"),
        scope_digest=getattr(outbox_settlement_report, "scope_digest"),
        request_digest=getattr(outbox_settlement_report, "request_digest"),
        payload_digest=getattr(outbox_settlement_report, "payload_digest"),
        idempotency_key=getattr(outbox_settlement_report, "idempotency_key"),
        retry_idempotency_key=getattr(outbox_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        outbox_settlement_digest=_digest(outbox_settlement_report),
        publish_fence_digest=_digest(publish_fence_report),
        public_ledger_digest=_digest(public_ledger_report),
        redaction_gc_digest=_digest(redaction_gc_report),
        accepted_marker_digest=accepted_marker_digest,
        accepted_settlement_marker_digest=getattr(outbox_settlement_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_fence_marker_digest=getattr(publish_fence_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_public_ledger_entry_digest=getattr(public_ledger_report, "accepted_entry_digest", ZERO_DIGEST),
        accepted_redaction_gc_proposal_digest=getattr(redaction_gc_report, "accepted_proposal_digest", ZERO_DIGEST),
        destination_digest=destination_digest,
        sam_endpoint_digest=sam_endpoint_digest,
        redacted_summary_digest=redacted_summary_digest,
        class_values=classes,
        marker_digests=digests,
        family_count=len(families),
        path_family_count=len(paths),
        hard_negative_count=hard,
        report_digest=report_digest,
    )


def assess_summary_send_canary(
    *,
    outbox_settlement_report: Any,
    publish_fence_report: Any,
    public_ledger_report: Any,
    redaction_gc_report: Any,
    markers: tuple[SummarySendCanaryMarker, ...],
    previous_digest: bytes = ZERO_DIGEST,
    required_classes: tuple[SummarySendCanaryClass, ...] = (
        SummarySendCanaryClass.OUTBOX_SETTLEMENT,
        SummarySendCanaryClass.PUBLISH_FENCE,
        SummarySendCanaryClass.PUBLIC_LEDGER,
        SummarySendCanaryClass.REDACTION_GC,
        SummarySendCanaryClass.REDACTION_OK,
        SummarySendCanaryClass.CONTRADICTION_MEMORY,
    ),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SummarySendCanaryReport:
    markers = tuple(markers)
    if not getattr(outbox_settlement_report, "outbox_settled", False):
        return _report(SummarySendCanaryDecisionKind.HOLD_OUTBOX_SETTLEMENT_PENDING, False, True, False, False, False, "outbox settlement pending", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
    if not getattr(publish_fence_report, "summary_publish_fenced", False):
        return _report(SummarySendCanaryDecisionKind.HOLD_FENCE_PENDING, False, True, False, False, False, "publish fence pending", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
    if not getattr(public_ledger_report, "public_summary_ledgered", False):
        return _report(SummarySendCanaryDecisionKind.HOLD_PUBLIC_LEDGER_PENDING, False, True, False, False, False, "public ledger pending", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
    if not getattr(redaction_gc_report, "redaction_gc_guarded", False):
        return _report(SummarySendCanaryDecisionKind.HOLD_REDACTION_GC_PENDING, False, True, False, False, False, "redaction GC pending", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)

    boundary = _boundary(outbox_settlement_report)
    if any(_boundary(report) != boundary for report in (publish_fence_report, public_ledger_report, redaction_gc_report)) or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(SummarySendCanaryDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)

    if (
        getattr(outbox_settlement_report, "publish_fence_digest", ZERO_DIGEST) != _digest(publish_fence_report)
        or getattr(outbox_settlement_report, "public_ledger_digest", ZERO_DIGEST) != _digest(public_ledger_report)
        or getattr(outbox_settlement_report, "redaction_gc_digest", ZERO_DIGEST) != _digest(redaction_gc_report)
    ):
        return _report(SummarySendCanaryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "outbox settlement digest drift", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)

    expected_destination = _default_destination_digest(outbox_settlement_report, public_ledger_report)
    expected_sam = _default_sam_endpoint_digest(outbox_settlement_report, redaction_gc_report)
    expected_redacted = _default_redacted_summary_digest(outbox_settlement_report, public_ledger_report, redaction_gc_report)
    for marker in markers:
        if (
            marker.outbox_settlement_digest != _digest(outbox_settlement_report)
            or marker.publish_fence_digest != _digest(publish_fence_report)
            or marker.public_ledger_digest != _digest(public_ledger_report)
            or marker.redaction_gc_digest != _digest(redaction_gc_report)
            or marker.accepted_settlement_marker_digest != getattr(outbox_settlement_report, "accepted_marker_digest", ZERO_DIGEST)
            or marker.accepted_fence_marker_digest != getattr(publish_fence_report, "accepted_marker_digest", ZERO_DIGEST)
            or marker.accepted_public_ledger_entry_digest != getattr(public_ledger_report, "accepted_entry_digest", ZERO_DIGEST)
            or marker.accepted_redaction_gc_proposal_digest != getattr(redaction_gc_report, "accepted_proposal_digest", ZERO_DIGEST)
        ):
            return _report(SummarySendCanaryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "marker digest drift", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
        if marker.destination_digest != expected_destination or marker.sam_endpoint_digest != expected_sam or marker.redacted_summary_digest != expected_redacted:
            return _report(SummarySendCanaryDecisionKind.QUARANTINE_ENDPOINT_DRIFT, False, True, False, False, False, "endpoint/redacted-summary drift", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
    if any(marker.raw_boundary_exposed or marker.raw_payload_exposed for marker in markers):
        return _report(SummarySendCanaryDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw boundary or payload exposure", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)

    contradiction = bool(
        getattr(outbox_settlement_report, "contradiction_preserved", False)
        and getattr(publish_fence_report, "contradiction_preserved", False)
        and getattr(public_ledger_report, "contradiction_preserved", False)
        and getattr(redaction_gc_report, "contradiction_retained", False)
        and all(marker.contradiction_carried for marker in markers)
    )
    if not contradiction:
        return _report(SummarySendCanaryDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction memory missing", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)

    redacted = bool(
        getattr(redaction_gc_report, "redacted_summary_retained", False)
        and all((not marker.raw_boundary_exposed and not marker.raw_payload_exposed and marker.redacted_summary_digest != ZERO_DIGEST) for marker in markers)
    )
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (outbox_settlement_report, publish_fence_report, public_ledger_report, redaction_gc_report)) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(SummarySendCanaryDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "hard-negative pressure", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)

    present = {marker.canary_class for marker in markers}
    if not set(required_classes).issubset(present):
        return _report(SummarySendCanaryDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing required canary class", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)

    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        marker_digest = marker.marker_digest
        if marker_digest in seen_digests:
            return _report(SummarySendCanaryDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed marker", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
        seen_digests.add(marker_digest)
        if marker.sequence <= 0:
            return _report(SummarySendCanaryDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
        if marker.sequence in seen_sequences and seen_sequences[marker.sequence] != marker_digest:
            return _report(SummarySendCanaryDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
        seen_sequences[marker.sequence] = marker_digest
        if marker.previous_digest != previous:
            return _report(SummarySendCanaryDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous-link mismatch", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
        previous = marker_digest

    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(SummarySendCanaryDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(SummarySendCanaryDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers)

    accepted = previous if markers else ZERO_DIGEST
    return _report(SummarySendCanaryDecisionKind.ACCEPT_SUMMARY_SEND_CANARY, True, False, True, True, redacted, "summary send canary ready", outbox_settlement_report=outbox_settlement_report, publish_fence_report=publish_fence_report, public_ledger_report=public_ledger_report, redaction_gc_report=redaction_gc_report, markers=markers, accepted_marker_digest=accepted)
