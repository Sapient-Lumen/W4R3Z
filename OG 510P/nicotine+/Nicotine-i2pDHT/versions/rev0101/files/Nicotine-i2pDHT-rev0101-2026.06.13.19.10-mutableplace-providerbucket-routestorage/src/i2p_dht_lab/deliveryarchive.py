"""rev0077 delivery archive after ACK settlement.

ACK settlement still is not durable restart memory.  This lane records a compact
archive marker that preserves ACK-ledger, settlement-fence, redaction, and
contradiction evidence before pruning or later publication cleanup can proceed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

DELIVERY_ARCHIVE_DOMAIN = DOMAIN + b":delivery-archive-v1:"


class DeliveryArchiveClass(str, Enum):
    ACK_LEDGER = "ack_ledger"
    SETTLEMENT_FENCE = "settlement_fence"
    REDACTION_MEMORY = "redaction_memory"
    CONTRADICTION_MEMORY = "contradiction_memory"
    RESTART_GENERATION = "restart_generation"
    IDEMPOTENCY = "idempotency"


class DeliveryArchiveDecisionKind(str, Enum):
    ACCEPT_DELIVERY_ARCHIVED = "accept_delivery_archived"
    HOLD_ACK_PENDING = "hold_ack_pending"
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
    QUARANTINE_REDACTION_DROPPED = "quarantine_redaction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class DeliveryArchiveMarker:
    archive_class: DeliveryArchiveClass
    sequence: int
    previous_digest: bytes
    restart_generation: int
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_ack_ledger_digest: bytes
    settlement_fence_digest: bytes
    accepted_ack_marker_digest: bytes
    accepted_fence_marker_digest: bytes
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
        return sha256(DELIVERY_ARCHIVE_DOMAIN + b":marker:" + bencode({
            b"class": DeliveryArchiveClass(self.archive_class).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"restart": self.restart_generation,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"ack": self.summary_ack_ledger_digest,
            b"fence": self.settlement_fence_digest,
            b"ack_marker": self.accepted_ack_marker_digest,
            b"fence_marker": self.accepted_fence_marker_digest,
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
class DeliveryArchiveReport:
    decision_kind: DeliveryArchiveDecisionKind
    accept: bool
    watch: bool
    delivery_archived: bool
    restart_sticky: bool
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
    summary_ack_ledger_digest: bytes
    settlement_fence_digest: bytes
    accepted_marker_digest: bytes
    accepted_ack_marker_digest: bytes
    accepted_fence_marker_digest: bytes
    redacted_summary_digest: bytes
    class_values: tuple[str, ...]
    marker_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    restart_generations: tuple[int, ...]
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_marker_digest"):
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


def _marker_boundary(marker: DeliveryArchiveMarker) -> tuple[Any, ...]:
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


def make_delivery_archive_marker(
    *,
    archive_class: DeliveryArchiveClass,
    sequence: int,
    summary_ack_ledger_report: Any,
    settlement_fence_report: Any,
    previous_digest: bytes = ZERO_DIGEST,
    restart_generation: int = 1,
    contradiction_carried: bool = True,
    redaction_carried: bool = True,
    raw_boundary_exposed: bool = False,
    raw_payload_exposed: bool = False,
    family_id: str = "delivery-archive-family",
    path_family_id: str = "delivery-archive-path",
    hard_negative_count: int = 0,
) -> DeliveryArchiveMarker:
    return DeliveryArchiveMarker(
        archive_class=DeliveryArchiveClass(archive_class),
        sequence=sequence,
        previous_digest=previous_digest,
        restart_generation=restart_generation,
        action=SideEffectAction(getattr(summary_ack_ledger_report, "action")),
        profile_id=getattr(summary_ack_ledger_report, "profile_id"),
        service_name=getattr(summary_ack_ledger_report, "service_name"),
        scope_digest=getattr(summary_ack_ledger_report, "scope_digest"),
        request_digest=getattr(summary_ack_ledger_report, "request_digest"),
        payload_digest=getattr(summary_ack_ledger_report, "payload_digest"),
        idempotency_key=getattr(summary_ack_ledger_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_ack_ledger_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_ack_ledger_digest=_digest(summary_ack_ledger_report),
        settlement_fence_digest=_digest(settlement_fence_report),
        accepted_ack_marker_digest=getattr(summary_ack_ledger_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_fence_marker_digest=getattr(settlement_fence_report, "accepted_marker_digest", ZERO_DIGEST),
        redacted_summary_digest=getattr(summary_ack_ledger_report, "redacted_summary_digest", ZERO_DIGEST),
        contradiction_carried=contradiction_carried,
        redaction_carried=redaction_carried,
        raw_boundary_exposed=raw_boundary_exposed,
        raw_payload_exposed=raw_payload_exposed,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(
    kind: DeliveryArchiveDecisionKind,
    accept: bool,
    watch: bool,
    archived: bool,
    contradiction: bool,
    redacted: bool,
    reason: str,
    *,
    summary_ack_ledger_report: Any,
    settlement_fence_report: Any,
    markers: tuple[DeliveryArchiveMarker, ...],
    accepted_marker_digest: bytes = ZERO_DIGEST,
) -> DeliveryArchiveReport:
    class_values = tuple(sorted({marker.archive_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    restarts = tuple(sorted({marker.restart_generation for marker in markers}))
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_ack_ledger_report, settlement_fence_report)) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(DELIVERY_ARCHIVE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"archived": 1 if archived else 0,
        b"ack": _digest(summary_ack_ledger_report),
        b"fence": _digest(settlement_fence_report),
        b"accepted": accepted_marker_digest,
        b"classes": list(class_values),
        b"markers": list(marker_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"restarts": list(restarts),
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"hard": hard,
        b"reason": reason,
    }))
    return DeliveryArchiveReport(
        decision_kind=kind,
        accept=accept,
        watch=watch,
        delivery_archived=archived,
        restart_sticky=archived,
        contradiction_preserved=contradiction,
        contradiction_carried=contradiction,
        redacted=redacted,
        redaction_carried=redacted,
        reason=reason,
        action=SideEffectAction(getattr(summary_ack_ledger_report, "action")),
        profile_id=getattr(summary_ack_ledger_report, "profile_id"),
        service_name=getattr(summary_ack_ledger_report, "service_name"),
        scope_digest=getattr(summary_ack_ledger_report, "scope_digest"),
        request_digest=getattr(summary_ack_ledger_report, "request_digest"),
        payload_digest=getattr(summary_ack_ledger_report, "payload_digest"),
        idempotency_key=getattr(summary_ack_ledger_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_ack_ledger_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_ack_ledger_digest=_digest(summary_ack_ledger_report),
        settlement_fence_digest=_digest(settlement_fence_report),
        accepted_marker_digest=accepted_marker_digest,
        accepted_ack_marker_digest=getattr(summary_ack_ledger_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_fence_marker_digest=getattr(settlement_fence_report, "accepted_marker_digest", ZERO_DIGEST),
        redacted_summary_digest=getattr(summary_ack_ledger_report, "redacted_summary_digest", ZERO_DIGEST),
        class_values=class_values,
        marker_digests=marker_digests,
        family_count=len(families),
        path_family_count=len(paths),
        restart_generations=restarts,
        hard_negative_count=hard,
        report_digest=report_digest,
    )


def assess_delivery_archive(
    *,
    summary_ack_ledger_report: Any,
    settlement_fence_report: Any,
    markers: tuple[DeliveryArchiveMarker, ...],
    previous_digest: bytes = ZERO_DIGEST,
    required_classes: tuple[DeliveryArchiveClass, ...] = (
        DeliveryArchiveClass.ACK_LEDGER,
        DeliveryArchiveClass.SETTLEMENT_FENCE,
        DeliveryArchiveClass.REDACTION_MEMORY,
        DeliveryArchiveClass.CONTRADICTION_MEMORY,
        DeliveryArchiveClass.RESTART_GENERATION,
        DeliveryArchiveClass.IDEMPOTENCY,
    ),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> DeliveryArchiveReport:
    markers = tuple(markers)
    if not getattr(summary_ack_ledger_report, "summary_ack_settled", False):
        return _report(DeliveryArchiveDecisionKind.HOLD_ACK_PENDING, False, True, False, False, False, "ACK settlement pending", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)

    boundary = _boundary(summary_ack_ledger_report)
    if _boundary(settlement_fence_report) != boundary or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(DeliveryArchiveDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
    if getattr(summary_ack_ledger_report, "settlement_fence_digest", ZERO_DIGEST) != _digest(settlement_fence_report):
        return _report(DeliveryArchiveDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)

    for marker in markers:
        if (
            marker.summary_ack_ledger_digest != _digest(summary_ack_ledger_report)
            or marker.settlement_fence_digest != _digest(settlement_fence_report)
            or marker.accepted_ack_marker_digest != getattr(summary_ack_ledger_report, "accepted_marker_digest", ZERO_DIGEST)
            or marker.accepted_fence_marker_digest != getattr(settlement_fence_report, "accepted_marker_digest", ZERO_DIGEST)
            or marker.redacted_summary_digest != getattr(summary_ack_ledger_report, "redacted_summary_digest", ZERO_DIGEST)
        ):
            return _report(DeliveryArchiveDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "marker digest drift", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(DeliveryArchiveDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw leak", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)

    contradiction = bool(getattr(summary_ack_ledger_report, "contradiction_preserved", False) and getattr(settlement_fence_report, "contradiction_preserved", False) and all(marker.contradiction_carried for marker in markers))
    if not contradiction:
        return _report(DeliveryArchiveDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction memory missing", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
    redacted = bool(getattr(summary_ack_ledger_report, "redacted", False) and getattr(settlement_fence_report, "redacted", False) and all(marker.redaction_carried for marker in markers))
    if not redacted:
        return _report(DeliveryArchiveDecisionKind.QUARANTINE_REDACTION_DROPPED, False, True, False, True, False, "redaction memory missing", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_ack_ledger_report, settlement_fence_report)) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(DeliveryArchiveDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "hard-negative pressure", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
    if not set(required_classes).issubset({marker.archive_class for marker in markers}):
        return _report(DeliveryArchiveDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing required archive class", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)

    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(DeliveryArchiveDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed marker", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(DeliveryArchiveDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
        if marker.sequence in seen_sequences and seen_sequences[marker.sequence] != digest:
            return _report(DeliveryArchiveDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
        seen_sequences[marker.sequence] = digest
        if marker.previous_digest != previous:
            return _report(DeliveryArchiveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous mismatch", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
        previous = digest

    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(DeliveryArchiveDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(DeliveryArchiveDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers)

    accepted = previous if markers else ZERO_DIGEST
    return _report(DeliveryArchiveDecisionKind.ACCEPT_DELIVERY_ARCHIVED, True, False, True, True, redacted, "delivery archive accepted", summary_ack_ledger_report=summary_ack_ledger_report, settlement_fence_report=settlement_fence_report, markers=markers, accepted_marker_digest=accepted)
