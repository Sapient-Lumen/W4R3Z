"""rev0075 redaction-GC join after archive/fence/canary.

Redaction evidence is useful only if it can be compacted without forgetting why
it was safe.  This lane models no-network, exact-boundary redaction GC: it may
compact soft working material, but it must preserve the outbox, archive, fence,
send-canary, and contradiction-memory digests before later summary settlement.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REDACTION_GC_JOIN_DOMAIN = DOMAIN + b":redaction-gc-join-v1:"


class RedactionGCClass(str, Enum):
    SUMMARY_OUTBOX = "summary_outbox"
    REDACTION_ARCHIVE = "redaction_archive"
    PUBLISH_FENCE = "publish_fence"
    SEND_CANARY = "send_canary"
    CONTRADICTION_MEMORY = "contradiction_memory"


class RedactionGCDecisionKind(str, Enum):
    ACCEPT_REDACTION_GC_JOINED = "accept_redaction_gced"
    HOLD_OUTBOX_PENDING = "hold_outbox_pending"
    HOLD_ARCHIVE_PENDING = "hold_archive_pending"
    HOLD_FENCE_PENDING = "hold_fence_pending"
    HOLD_CANARY_PENDING = "hold_canary_pending"
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
class RedactionGCMarker:
    gc_class: RedactionGCClass
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
    summary_outbox_digest: bytes
    redaction_archive_digest: bytes
    publish_fence_digest: bytes
    send_canary_digest: bytes
    accepted_outbox_entry_digest: bytes
    accepted_archive_marker_digest: bytes
    accepted_fence_marker_digest: bytes
    accepted_canary_marker_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    soft_bytes_reclaimed: int
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(REDACTION_GC_JOIN_DOMAIN + b":marker:" + bencode({
            b"class": RedactionGCClass(self.gc_class).value,
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
            b"outbox": self.summary_outbox_digest,
            b"archive": self.redaction_archive_digest,
            b"fence": self.publish_fence_digest,
            b"canary": self.send_canary_digest,
            b"outbox_entry": self.accepted_outbox_entry_digest,
            b"archive_marker": self.accepted_archive_marker_digest,
            b"fence_marker": self.accepted_fence_marker_digest,
            b"canary_marker": self.accepted_canary_marker_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"soft_bytes": self.soft_bytes_reclaimed,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RedactionGCReport:
    decision_kind: RedactionGCDecisionKind
    accept: bool
    watch: bool
    redaction_gced: bool
    contradiction_preserved: bool
    soft_bytes_reclaimed: int
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_outbox_digest: bytes
    redaction_archive_digest: bytes
    publish_fence_digest: bytes
    send_canary_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_receipt_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: RedactionGCMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_redaction_gc_marker(*, gc_class: RedactionGCClass, sequence: int, summary_outbox_report: Any, redaction_archive_report: Any, publish_fence_report: Any, send_canary_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, soft_bytes_reclaimed: int = 0, family_id: str = "redaction-gc-family-a", path_family_id: str = "redaction-gc-path-a", hard_negative_count: int = 0) -> RedactionGCMarker:
    contradiction = bool(getattr(summary_outbox_report, "contradiction_carried", False) and getattr(redaction_archive_report, "contradiction_preserved", False) and getattr(publish_fence_report, "contradiction_preserved", False) and getattr(send_canary_report, "contradiction_carried", False)) if contradiction_carried is None else bool(contradiction_carried)
    return RedactionGCMarker(
        gc_class=RedactionGCClass(gc_class),
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_outbox_report, "action")),
        profile_id=getattr(summary_outbox_report, "profile_id"),
        service_name=getattr(summary_outbox_report, "service_name"),
        scope_digest=getattr(summary_outbox_report, "scope_digest"),
        request_digest=getattr(summary_outbox_report, "request_digest"),
        payload_digest=getattr(summary_outbox_report, "payload_digest"),
        idempotency_key=getattr(summary_outbox_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_outbox_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_outbox_digest=_digest(summary_outbox_report),
        redaction_archive_digest=_digest(redaction_archive_report),
        publish_fence_digest=_digest(publish_fence_report),
        send_canary_digest=_digest(send_canary_report),
        accepted_outbox_entry_digest=getattr(summary_outbox_report, "accepted_entry_digest", ZERO_DIGEST),
        accepted_archive_marker_digest=getattr(redaction_archive_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_fence_marker_digest=getattr(publish_fence_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_canary_marker_digest=getattr(send_canary_report, "accepted_marker_digest", ZERO_DIGEST),
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        soft_bytes_reclaimed=max(0, int(soft_bytes_reclaimed)),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=int(hard_negative_count),
    )


def _report(kind: RedactionGCDecisionKind, accept: bool, watch: bool, joined: bool, contradiction: bool, reason: str, *, summary_outbox_report: Any, redaction_archive_report: Any, publish_fence_report: Any, send_canary_report: Any, markers: tuple[RedactionGCMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> RedactionGCReport:
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    classes = tuple(sorted({marker.gc_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    hard = int(getattr(summary_outbox_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_archive_report, "hard_negative_count", 0) or 0) + int(getattr(publish_fence_report, "hard_negative_count", 0) or 0) + int(getattr(send_canary_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    soft = sum(marker.soft_bytes_reclaimed for marker in markers)
    report_digest = sha256(REDACTION_GC_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"joined": 1 if joined else 0,
        b"contradiction": 1 if contradiction else 0,
        b"soft": soft,
        b"action": SideEffectAction(getattr(summary_outbox_report, "action")).value,
        b"profile": getattr(summary_outbox_report, "profile_id"),
        b"service": getattr(summary_outbox_report, "service_name"),
        b"scope": getattr(summary_outbox_report, "scope_digest"),
        b"request": getattr(summary_outbox_report, "request_digest"),
        b"payload": getattr(summary_outbox_report, "payload_digest"),
        b"idem": getattr(summary_outbox_report, "idempotency_key"),
        b"retry_idem": getattr(summary_outbox_report, "retry_idempotency_key", ZERO_DIGEST),
        b"outbox": _digest(summary_outbox_report),
        b"archive": _digest(redaction_archive_report),
        b"fence": _digest(publish_fence_report),
        b"canary": _digest(send_canary_report),
        b"accepted": accepted_marker_digest,
        b"classes": list(classes),
        b"markers": list(marker_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return RedactionGCReport(kind, accept, watch, joined, contradiction, soft, reason, SideEffectAction(getattr(summary_outbox_report, "action")), getattr(summary_outbox_report, "profile_id"), getattr(summary_outbox_report, "service_name"), getattr(summary_outbox_report, "scope_digest"), getattr(summary_outbox_report, "request_digest"), getattr(summary_outbox_report, "payload_digest"), getattr(summary_outbox_report, "idempotency_key"), getattr(summary_outbox_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_outbox_report), _digest(redaction_archive_report), _digest(publish_fence_report), _digest(send_canary_report), accepted_marker_digest, classes, marker_digests, len(families), len(paths), hard, report_digest)


def assess_redaction_gc(*, summary_outbox_report: Any, redaction_archive_report: Any, publish_fence_report: Any, send_canary_report: Any, markers: tuple[RedactionGCMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[RedactionGCClass, ...] = (RedactionGCClass.SUMMARY_OUTBOX, RedactionGCClass.REDACTION_ARCHIVE, RedactionGCClass.PUBLISH_FENCE, RedactionGCClass.SEND_CANARY, RedactionGCClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> RedactionGCReport:
    markers = tuple(markers)
    if not getattr(summary_outbox_report, "outbox_staged", False):
        return _report(RedactionGCDecisionKind.HOLD_OUTBOX_PENDING, False, True, False, False, "outbox pending", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    if not getattr(redaction_archive_report, "redaction_archived", False):
        return _report(RedactionGCDecisionKind.HOLD_ARCHIVE_PENDING, False, True, False, False, "archive pending", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    if not getattr(publish_fence_report, "summary_publish_fenced", False):
        return _report(RedactionGCDecisionKind.HOLD_FENCE_PENDING, False, True, False, False, "fence pending", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    if not getattr(send_canary_report, "canary_ready", False):
        return _report(RedactionGCDecisionKind.HOLD_CANARY_PENDING, False, True, False, False, "canary pending", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    base = _boundary(summary_outbox_report)
    if _boundary(redaction_archive_report) != base or _boundary(publish_fence_report) != base or _boundary(send_canary_report) != base:
        return _report(RedactionGCDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, "component boundary drift", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    for marker in markers:
        if _marker_boundary(marker) != base:
            return _report(RedactionGCDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, "marker boundary drift", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
        if marker.summary_outbox_digest != _digest(summary_outbox_report) or marker.redaction_archive_digest != _digest(redaction_archive_report) or marker.publish_fence_digest != _digest(publish_fence_report) or marker.send_canary_digest != _digest(send_canary_report):
            return _report(RedactionGCDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, "digest drift", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
        if marker.raw_boundary_exposed or marker.raw_payload_exposed:
            return _report(RedactionGCDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, "raw leak", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
        if not marker.contradiction_carried:
            return _report(RedactionGCDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, "contradiction missing", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    hard = int(getattr(summary_outbox_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_archive_report, "hard_negative_count", 0) or 0) + int(getattr(publish_fence_report, "hard_negative_count", 0) or 0) + int(getattr(send_canary_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(RedactionGCDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, "hard-negative pressure", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    present = {marker.gc_class for marker in markers}
    if not set(required_classes).issubset(present):
        return _report(RedactionGCDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, "missing redaction-GC class", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    prev = previous_digest
    seen: dict[int, bytes] = {}
    digest_seen: set[bytes] = set()
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in digest_seen:
            return _report(RedactionGCDecisionKind.QUARANTINE_REPLAY, False, True, False, True, "replayed marker", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
        digest_seen.add(digest)
        if marker.sequence <= 0:
            return _report(RedactionGCDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, "non-positive sequence", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
        if marker.sequence in seen and seen[marker.sequence] != digest:
            return _report(RedactionGCDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, "same-sequence fork", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
        if marker.previous_digest != prev:
            return _report(RedactionGCDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, "previous mismatch", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
        seen[marker.sequence] = digest
        prev = digest
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    if len(families) < min_family_count:
        return _report(RedactionGCDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, "low family diversity", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    if len(paths) < min_path_family_count:
        return _report(RedactionGCDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, "low path diversity", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers)
    accepted = markers[-1].marker_digest if markers else ZERO_DIGEST
    return _report(RedactionGCDecisionKind.ACCEPT_REDACTION_GC_JOINED, True, False, True, True, "redaction GC joined", summary_outbox_report=summary_outbox_report, redaction_archive_report=redaction_archive_report, publish_fence_report=publish_fence_report, send_canary_report=send_canary_report, markers=markers, accepted_marker_digest=accepted)
