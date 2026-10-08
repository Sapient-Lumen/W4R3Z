"""rev0078 redacted-summary export fence after ACK closure.

The ACK closure path is still local memory.  This no-network fence prepares a
future redacted operator/garden/public summary export only if closure, replay,
archive, and prune evidence remain bound to the same exact edge.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_EXPORT_FENCE_DOMAIN = DOMAIN + b":summary-export-fence-v1:"


class SummaryExportClass(str, Enum):
    ACK_CLOSURE = "ack_closure"
    SUMMARY_REPLAY = "summary_replay"
    DELIVERY_ARCHIVE = "delivery_archive"
    SUMMARY_PRUNE_FENCE = "summary_prune_fence"
    REDACTED_SUMMARY = "redacted_summary"
    CONTRADICTION_MEMORY = "contradiction_memory"


class SummaryExportDecisionKind(str, Enum):
    ACCEPT_SUMMARY_EXPORT_FENCED = "accept_summary_export_fenced"
    HOLD_CLOSURE_PENDING = "hold_closure_pending"
    HOLD_REPLAY_PENDING = "hold_replay_pending"
    HOLD_ARCHIVE_PENDING = "hold_archive_pending"
    HOLD_PRUNE_PENDING = "hold_prune_pending"
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
class SummaryExportMarker:
    export_class: SummaryExportClass
    sequence: int
    previous_digest: bytes
    export_channel: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    ack_closure_digest: bytes
    summary_replay_digest: bytes
    delivery_archive_digest: bytes
    summary_prune_fence_digest: bytes
    accepted_closure_marker_digest: bytes
    accepted_replay_marker_digest: bytes
    accepted_archive_marker_digest: bytes
    accepted_prune_proposal_digest: bytes
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
        return sha256(SUMMARY_EXPORT_FENCE_DOMAIN + b":marker:" + bencode({
            b"class": SummaryExportClass(self.export_class).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"channel": self.export_channel,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"closure": self.ack_closure_digest,
            b"replay": self.summary_replay_digest,
            b"archive": self.delivery_archive_digest,
            b"prune": self.summary_prune_fence_digest,
            b"closure_marker": self.accepted_closure_marker_digest,
            b"replay_marker": self.accepted_replay_marker_digest,
            b"archive_marker": self.accepted_archive_marker_digest,
            b"prune_marker": self.accepted_prune_proposal_digest,
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
class SummaryExportFenceReport:
    decision_kind: SummaryExportDecisionKind
    accept: bool
    watch: bool
    summary_export_fenced: bool
    export_ready: bool
    export_channel: str
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
    ack_closure_digest: bytes
    summary_replay_digest: bytes
    delivery_archive_digest: bytes
    summary_prune_fence_digest: bytes
    accepted_marker_digest: bytes
    accepted_closure_marker_digest: bytes
    accepted_replay_marker_digest: bytes
    accepted_archive_marker_digest: bytes
    accepted_prune_proposal_digest: bytes
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


def _marker_boundary(marker: SummaryExportMarker) -> tuple[Any, ...]:
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


def make_summary_export_marker(*, export_class: SummaryExportClass, sequence: int, ack_closure_report: Any, summary_replay_report: Any, delivery_archive_report: Any, summary_prune_fence_report: Any, previous_digest: bytes = ZERO_DIGEST, export_channel: str = "operator", contradiction_carried: bool = True, redaction_carried: bool = True, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "summary-export-family", path_family_id: str = "summary-export-path", hard_negative_count: int = 0) -> SummaryExportMarker:
    return SummaryExportMarker(
        export_class=SummaryExportClass(export_class), sequence=sequence, previous_digest=previous_digest, export_channel=export_channel,
        action=SideEffectAction(getattr(ack_closure_report, "action")), profile_id=getattr(ack_closure_report, "profile_id"), service_name=getattr(ack_closure_report, "service_name"), scope_digest=getattr(ack_closure_report, "scope_digest"), request_digest=getattr(ack_closure_report, "request_digest"), payload_digest=getattr(ack_closure_report, "payload_digest"), idempotency_key=getattr(ack_closure_report, "idempotency_key"), retry_idempotency_key=getattr(ack_closure_report, "retry_idempotency_key", ZERO_DIGEST),
        ack_closure_digest=_digest(ack_closure_report), summary_replay_digest=_digest(summary_replay_report), delivery_archive_digest=_digest(delivery_archive_report), summary_prune_fence_digest=_digest(summary_prune_fence_report), accepted_closure_marker_digest=getattr(ack_closure_report, "accepted_marker_digest", ZERO_DIGEST), accepted_replay_marker_digest=getattr(summary_replay_report, "accepted_marker_digest", ZERO_DIGEST), accepted_archive_marker_digest=getattr(delivery_archive_report, "accepted_marker_digest", ZERO_DIGEST), accepted_prune_proposal_digest=getattr(summary_prune_fence_report, "accepted_proposal_digest", ZERO_DIGEST), redacted_summary_digest=getattr(ack_closure_report, "redacted_summary_digest", ZERO_DIGEST), contradiction_carried=contradiction_carried, redaction_carried=redaction_carried, raw_boundary_exposed=raw_boundary_exposed, raw_payload_exposed=raw_payload_exposed, family_id=family_id, path_family_id=path_family_id, hard_negative_count=hard_negative_count,
    )


def _report(kind: SummaryExportDecisionKind, accept: bool, watch: bool, fenced: bool, contradiction: bool, redacted: bool, reason: str, *, ack_closure_report: Any, summary_replay_report: Any, delivery_archive_report: Any, summary_prune_fence_report: Any, markers: tuple[SummaryExportMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> SummaryExportFenceReport:
    class_values = tuple(sorted({marker.export_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    channels = {marker.export_channel for marker in markers}
    channel = sorted(channels)[0] if len(channels) == 1 else "mixed"
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (ack_closure_report, summary_replay_report, delivery_archive_report, summary_prune_fence_report)) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(SUMMARY_EXPORT_FENCE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0, b"fenced": 1 if fenced else 0, b"channel": channel,
        b"closure": _digest(ack_closure_report), b"replay": _digest(summary_replay_report), b"archive": _digest(delivery_archive_report), b"prune": _digest(summary_prune_fence_report), b"accepted": accepted_marker_digest,
        b"classes": list(class_values), b"markers": list(marker_digests), b"families": len(families), b"paths": len(paths), b"contradiction": 1 if contradiction else 0, b"redacted": 1 if redacted else 0, b"hard": hard, b"reason": reason,
    }))
    return SummaryExportFenceReport(kind, accept, watch, fenced, fenced, channel, contradiction, contradiction, redacted, redacted, reason, SideEffectAction(getattr(ack_closure_report, "action")), getattr(ack_closure_report, "profile_id"), getattr(ack_closure_report, "service_name"), getattr(ack_closure_report, "scope_digest"), getattr(ack_closure_report, "request_digest"), getattr(ack_closure_report, "payload_digest"), getattr(ack_closure_report, "idempotency_key"), getattr(ack_closure_report, "retry_idempotency_key", ZERO_DIGEST), _digest(ack_closure_report), _digest(summary_replay_report), _digest(delivery_archive_report), _digest(summary_prune_fence_report), accepted_marker_digest, getattr(ack_closure_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_replay_report, "accepted_marker_digest", ZERO_DIGEST), getattr(delivery_archive_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_prune_fence_report, "accepted_proposal_digest", ZERO_DIGEST), getattr(ack_closure_report, "redacted_summary_digest", ZERO_DIGEST), class_values, marker_digests, len(families), len(paths), hard, report_digest)


def assess_summary_export_fence(*, ack_closure_report: Any, summary_replay_report: Any, delivery_archive_report: Any, summary_prune_fence_report: Any, markers: tuple[SummaryExportMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[SummaryExportClass, ...] = (SummaryExportClass.ACK_CLOSURE, SummaryExportClass.SUMMARY_REPLAY, SummaryExportClass.DELIVERY_ARCHIVE, SummaryExportClass.SUMMARY_PRUNE_FENCE, SummaryExportClass.REDACTED_SUMMARY, SummaryExportClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryExportFenceReport:
    markers = tuple(markers)
    if not getattr(ack_closure_report, "ack_closed", False):
        return _report(SummaryExportDecisionKind.HOLD_CLOSURE_PENDING, False, True, False, False, False, "closure pending", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    if not getattr(summary_replay_report, "summary_replayed", False):
        return _report(SummaryExportDecisionKind.HOLD_REPLAY_PENDING, False, True, False, False, False, "replay pending", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    if not getattr(delivery_archive_report, "delivery_archived", False):
        return _report(SummaryExportDecisionKind.HOLD_ARCHIVE_PENDING, False, True, False, False, False, "archive pending", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    if not getattr(summary_prune_fence_report, "summary_prune_fenced", False):
        return _report(SummaryExportDecisionKind.HOLD_PRUNE_PENDING, False, True, False, False, False, "prune pending", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    boundary = _boundary(ack_closure_report)
    if any(_boundary(report) != boundary for report in (summary_replay_report, delivery_archive_report, summary_prune_fence_report)) or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(SummaryExportDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    if getattr(ack_closure_report, "summary_replay_digest", ZERO_DIGEST) != _digest(summary_replay_report) or getattr(ack_closure_report, "delivery_archive_digest", ZERO_DIGEST) != _digest(delivery_archive_report) or getattr(ack_closure_report, "summary_prune_fence_digest", ZERO_DIGEST) != _digest(summary_prune_fence_report):
        return _report(SummaryExportDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    for marker in markers:
        if marker.ack_closure_digest != _digest(ack_closure_report) or marker.summary_replay_digest != _digest(summary_replay_report) or marker.delivery_archive_digest != _digest(delivery_archive_report) or marker.summary_prune_fence_digest != _digest(summary_prune_fence_report):
            return _report(SummaryExportDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "marker digest drift", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(SummaryExportDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw leak", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    contradiction = bool(getattr(ack_closure_report, "contradiction_preserved", False) and getattr(summary_replay_report, "contradiction_preserved", False) and getattr(delivery_archive_report, "contradiction_preserved", False) and getattr(summary_prune_fence_report, "contradiction_preserved", False) and all(marker.contradiction_carried for marker in markers))
    if not contradiction:
        return _report(SummaryExportDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction dropped", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    redacted = bool(getattr(ack_closure_report, "redacted", False) and getattr(summary_replay_report, "redacted", False) and getattr(delivery_archive_report, "redacted", False) and getattr(summary_prune_fence_report, "redacted", False) and all(marker.redaction_carried for marker in markers))
    if not redacted:
        return _report(SummaryExportDecisionKind.QUARANTINE_REDACTION_DROPPED, False, True, False, True, False, "redaction dropped", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (ack_closure_report, summary_replay_report, delivery_archive_report, summary_prune_fence_report)) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(SummaryExportDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "hard negatives", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    if len({marker.export_channel for marker in markers}) > 1:
        return _report(SummaryExportDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, True, redacted, "mixed export channels", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    if not set(required_classes).issubset({marker.export_class for marker in markers}):
        return _report(SummaryExportDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing class", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in seen_digests:
            return _report(SummaryExportDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed marker", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
        seen_digests.add(digest)
        if marker.sequence <= 0:
            return _report(SummaryExportDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
        if marker.sequence in seen_sequences and seen_sequences[marker.sequence] != digest:
            return _report(SummaryExportDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
        seen_sequences[marker.sequence] = digest
        if marker.previous_digest != previous:
            return _report(SummaryExportDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous mismatch", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
        previous = digest
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(SummaryExportDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(SummaryExportDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers)
    accepted = previous if markers else ZERO_DIGEST
    return _report(SummaryExportDecisionKind.ACCEPT_SUMMARY_EXPORT_FENCED, True, False, True, True, redacted, "summary export fence accepted", ack_closure_report=ack_closure_report, summary_replay_report=summary_replay_report, delivery_archive_report=delivery_archive_report, summary_prune_fence_report=summary_prune_fence_report, markers=markers, accepted_marker_digest=accepted)
