"""rev0074 redaction witness archive.

Redaction witnessed once is not restart-sticky memory.  This lane creates a
small archive marker surface that carries summary publication, redaction witness,
import-prune audit, and contradiction memory together before later publication
fences may treat redaction as durable local evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REDACTION_ARCHIVE_DOMAIN = DOMAIN + b":redaction-archive-v1:"


class RedactionArchiveClass(str, Enum):
    SUMMARY_PUBLICATION = "summary_publication"
    REDACTION_WITNESS = "redaction_witness"
    IMPORT_PRUNE_AUDIT = "import_prune_audit"
    CONTRADICTION_MEMORY = "contradiction_memory"


class RedactionArchiveDecisionKind(str, Enum):
    ACCEPT_REDACTION_ARCHIVED = "accept_redaction_archived"
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
class RedactionArchiveMarker:
    archive_class: RedactionArchiveClass
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
    retained_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(REDACTION_ARCHIVE_DOMAIN + b":marker:" + bencode({
            b"class": RedactionArchiveClass(self.archive_class).value,
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
            b"retained": self.retained_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RedactionArchiveReport:
    decision_kind: RedactionArchiveDecisionKind
    accept: bool
    watch: bool
    redaction_archived: bool
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest", "accepted_intent_digest", "accepted_entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: RedactionArchiveMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_redaction_archive_marker(*, archive_class: RedactionArchiveClass, sequence: int, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, previous_digest: bytes = ZERO_DIGEST, retained_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "redaction-archive-family-a", path_family_id: str = "redaction-archive-path-a", hard_negative_count: int = 0) -> RedactionArchiveMarker:
    cls = RedactionArchiveClass(archive_class)
    contradiction = bool(getattr(summary_publish_report, "contradiction_carried", False) and getattr(redaction_witness_report, "contradiction_carried", False) and getattr(import_prune_audit_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    retained = retained_digest or sha256(REDACTION_ARCHIVE_DOMAIN + b":retained:" + _digest(summary_publish_report) + b":" + _digest(redaction_witness_report) + b":" + _digest(import_prune_audit_report) + b":" + cls.value.encode())
    return RedactionArchiveMarker(cls, int(sequence), previous_digest, SideEffectAction(getattr(summary_publish_report, "action")), getattr(summary_publish_report, "profile_id"), getattr(summary_publish_report, "service_name"), getattr(summary_publish_report, "scope_digest"), getattr(summary_publish_report, "request_digest"), getattr(summary_publish_report, "payload_digest"), getattr(summary_publish_report, "idempotency_key"), getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_publish_report), _digest(redaction_witness_report), _digest(import_prune_audit_report), getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST), getattr(redaction_witness_report, "accepted_receipt_digest", ZERO_DIGEST), getattr(import_prune_audit_report, "accepted_marker_digest", ZERO_DIGEST), retained, contradiction, bool(raw_boundary_exposed), bool(raw_payload_exposed), family_id, path_family_id, hard_negative_count)


def _report(kind: RedactionArchiveDecisionKind, accept: bool, watch: bool, archived: bool, contradiction: bool, redacted: bool, reason: str, *, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, markers: tuple[RedactionArchiveMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> RedactionArchiveReport:
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    classes = tuple(sorted({marker.archive_class.value for marker in markers}))
    marker_digests = tuple(marker.marker_digest for marker in markers)
    hard = int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_witness_report, "hard_negative_count", 0) or 0) + int(getattr(import_prune_audit_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(REDACTION_ARCHIVE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"archived": 1 if archived else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(summary_publish_report, "action")).value,
        b"profile": getattr(summary_publish_report, "profile_id"),
        b"service": getattr(summary_publish_report, "service_name"),
        b"scope": getattr(summary_publish_report, "scope_digest"),
        b"request": getattr(summary_publish_report, "request_digest"),
        b"payload": getattr(summary_publish_report, "payload_digest"),
        b"idem": getattr(summary_publish_report, "idempotency_key"),
        b"retry_idem": getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST),
        b"publish": _digest(summary_publish_report),
        b"redaction": _digest(redaction_witness_report),
        b"audit": _digest(import_prune_audit_report),
        b"accepted": accepted_marker_digest,
        b"classes": list(classes),
        b"markers": list(marker_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return RedactionArchiveReport(kind, accept, watch, archived, contradiction, redacted, reason, SideEffectAction(getattr(summary_publish_report, "action")), getattr(summary_publish_report, "profile_id"), getattr(summary_publish_report, "service_name"), getattr(summary_publish_report, "scope_digest"), getattr(summary_publish_report, "request_digest"), getattr(summary_publish_report, "payload_digest"), getattr(summary_publish_report, "idempotency_key"), getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_publish_report), _digest(redaction_witness_report), _digest(import_prune_audit_report), accepted_marker_digest, classes, marker_digests, len(families), len(paths), hard, report_digest)


def assess_redaction_archive(*, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, markers: tuple[RedactionArchiveMarker, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[RedactionArchiveClass, ...] = (RedactionArchiveClass.SUMMARY_PUBLICATION, RedactionArchiveClass.REDACTION_WITNESS, RedactionArchiveClass.IMPORT_PRUNE_AUDIT, RedactionArchiveClass.CONTRADICTION_MEMORY), min_family_count: int = 2, min_path_family_count: int = 2) -> RedactionArchiveReport:
    markers = tuple(markers)
    if not getattr(summary_publish_report, "publication_ready", False):
        return _report(RedactionArchiveDecisionKind.HOLD_PUBLICATION_PENDING, False, True, False, False, False, "summary publication not ready", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if not getattr(redaction_witness_report, "redaction_witnessed", False):
        return _report(RedactionArchiveDecisionKind.HOLD_REDACTION_PENDING, False, True, False, False, False, "redaction witness missing", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if not getattr(import_prune_audit_report, "import_prune_audited", False):
        return _report(RedactionArchiveDecisionKind.HOLD_IMPORT_PRUNE_AUDIT_PENDING, False, True, False, False, False, "import-prune audit missing", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    boundary = _boundary(summary_publish_report)
    if _boundary(redaction_witness_report) != boundary or _boundary(import_prune_audit_report) != boundary or any(_marker_boundary(marker) != boundary for marker in markers):
        return _report(RedactionArchiveDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if any(marker.summary_publish_digest != _digest(summary_publish_report) or marker.redaction_witness_digest != _digest(redaction_witness_report) or marker.import_prune_audit_digest != _digest(import_prune_audit_report) for marker in markers):
        return _report(RedactionArchiveDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if any(marker.raw_boundary_exposed or marker.raw_payload_exposed for marker in markers):
        return _report(RedactionArchiveDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw leak", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if any(not marker.contradiction_carried for marker in markers):
        return _report(RedactionArchiveDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction memory missing", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    hard = int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_witness_report, "hard_negative_count", 0) or 0) + int(getattr(import_prune_audit_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    if hard:
        return _report(RedactionArchiveDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, True, "hard-negative pressure", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    present = {marker.archive_class for marker in markers}
    if not set(required_classes).issubset(present):
        return _report(RedactionArchiveDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, True, "missing archive class", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    seen: dict[int, bytes] = {}
    digest_seen: set[bytes] = set()
    prev = previous_digest
    for marker in sorted(markers, key=lambda item: item.sequence):
        digest = marker.marker_digest
        if digest in digest_seen:
            return _report(RedactionArchiveDecisionKind.QUARANTINE_REPLAY, False, True, False, True, True, "replayed archive marker", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        digest_seen.add(digest)
        if marker.sequence <= 0:
            return _report(RedactionArchiveDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, True, "non-positive sequence", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        if marker.sequence in seen and seen[marker.sequence] != digest:
            return _report(RedactionArchiveDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, True, "same-sequence fork", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        if marker.previous_digest != prev:
            return _report(RedactionArchiveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, True, "previous digest mismatch", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
        seen[marker.sequence] = digest
        prev = digest
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    if len(families) < min_family_count:
        return _report(RedactionArchiveDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low archive family diversity", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    if len(paths) < min_path_family_count:
        return _report(RedactionArchiveDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low archive path diversity", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers)
    accepted = markers[-1].marker_digest if markers else ZERO_DIGEST
    return _report(RedactionArchiveDecisionKind.ACCEPT_REDACTION_ARCHIVED, True, False, True, True, True, "redaction archived", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, markers=markers, accepted_marker_digest=accepted)
