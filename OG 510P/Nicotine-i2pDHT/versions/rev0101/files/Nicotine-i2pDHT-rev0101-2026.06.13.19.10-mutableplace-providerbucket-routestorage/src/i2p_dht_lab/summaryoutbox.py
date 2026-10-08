"""rev0074 redacted-summary outbox staging.

A redacted summary publication report is still no-network readiness.  This lane
models the next exact-boundary step: staging a public/operator/garden summary
entry in a local outbox while preserving redaction, contradiction memory,
component digests, replay/fork pressure, and family/path diversity.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_OUTBOX_DOMAIN = DOMAIN + b":summary-outbox-v1:"


class SummaryOutboxTarget(str, Enum):
    OPERATOR = "operator"
    GARDEN = "garden"
    PUBLIC = "public"


class SummaryOutboxDecisionKind(str, Enum):
    ACCEPT_SUMMARY_OUTBOX_STAGED = "accept_summary_outbox_staged"
    HOLD_PUBLICATION_PENDING = "hold_publication_pending"
    HOLD_REDACTION_PENDING = "hold_redaction_pending"
    HOLD_IMPORT_PRUNE_AUDIT_PENDING = "hold_import_prune_audit_pending"
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
class SummaryOutboxEntry:
    target: SummaryOutboxTarget
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
    redacted_summary_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(SUMMARY_OUTBOX_DOMAIN + b":entry:" + bencode({
            b"target": SummaryOutboxTarget(self.target).value,
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
            b"redacted_summary": self.redacted_summary_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryOutboxReport:
    decision_kind: SummaryOutboxDecisionKind
    accept: bool
    watch: bool
    outbox_staged: bool
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
    summary_publish_digest: bytes
    redaction_witness_digest: bytes
    import_prune_audit_digest: bytes
    accepted_entry_digest: bytes
    target_values: tuple[str, ...]
    entry_digests: tuple[bytes, ...]
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


def _entry_boundary(entry: SummaryOutboxEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_summary_outbox_entry(*, target: SummaryOutboxTarget, sequence: int, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, previous_digest: bytes = ZERO_DIGEST, redacted_summary_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "summary-outbox-family-a", path_family_id: str = "summary-outbox-path-a", hard_negative_count: int = 0) -> SummaryOutboxEntry:
    contradiction = bool(getattr(summary_publish_report, "contradiction_carried", False) and getattr(redaction_witness_report, "contradiction_carried", False) and getattr(import_prune_audit_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    redacted_digest = redacted_summary_digest or sha256(SUMMARY_OUTBOX_DOMAIN + b":redacted-summary:" + _digest(summary_publish_report) + b":" + _digest(redaction_witness_report) + b":" + _digest(import_prune_audit_report) + b":" + SummaryOutboxTarget(target).value.encode())
    return SummaryOutboxEntry(
        target=SummaryOutboxTarget(target),
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
        redacted_summary_digest=redacted_digest,
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: SummaryOutboxDecisionKind, accept: bool, watch: bool, staged: bool, contradiction: bool, redacted: bool, reason: str, *, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, entries: tuple[SummaryOutboxEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> SummaryOutboxReport:
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    targets = tuple(sorted({entry.target.value for entry in entries}))
    entry_digests = tuple(entry.entry_digest for entry in entries)
    hard = int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_witness_report, "hard_negative_count", 0) or 0) + int(getattr(import_prune_audit_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    report_digest = sha256(SUMMARY_OUTBOX_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"staged": 1 if staged else 0,
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
        b"accepted": accepted_entry_digest,
        b"targets": list(targets),
        b"entries": list(entry_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return SummaryOutboxReport(kind, accept, watch, staged, contradiction, redacted, reason, SideEffectAction(getattr(summary_publish_report, "action")), getattr(summary_publish_report, "profile_id"), getattr(summary_publish_report, "service_name"), getattr(summary_publish_report, "scope_digest"), getattr(summary_publish_report, "request_digest"), getattr(summary_publish_report, "payload_digest"), getattr(summary_publish_report, "idempotency_key"), getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_publish_report), _digest(redaction_witness_report), _digest(import_prune_audit_report), accepted_entry_digest, targets, entry_digests, len(families), len(paths), hard, report_digest)


def assess_summary_outbox(*, summary_publish_report: Any, redaction_witness_report: Any, import_prune_audit_report: Any, entries: tuple[SummaryOutboxEntry, ...], previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryOutboxReport:
    entries = tuple(entries)
    if not getattr(summary_publish_report, "publication_ready", False):
        return _report(SummaryOutboxDecisionKind.HOLD_PUBLICATION_PENDING, False, True, False, False, False, "summary publication not ready", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    if not getattr(redaction_witness_report, "redaction_witnessed", False):
        return _report(SummaryOutboxDecisionKind.HOLD_REDACTION_PENDING, False, True, False, False, False, "redaction witness not accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    if not getattr(import_prune_audit_report, "import_prune_audited", False):
        return _report(SummaryOutboxDecisionKind.HOLD_IMPORT_PRUNE_AUDIT_PENDING, False, True, False, False, False, "import-prune audit not accepted", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    boundary = _boundary(summary_publish_report)
    if _boundary(redaction_witness_report) != boundary or _boundary(import_prune_audit_report) != boundary or any(_entry_boundary(entry) != boundary for entry in entries):
        return _report(SummaryOutboxDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "component or entry boundary drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    if any(entry.summary_publish_digest != _digest(summary_publish_report) or entry.redaction_witness_digest != _digest(redaction_witness_report) or entry.import_prune_audit_digest != _digest(import_prune_audit_report) for entry in entries):
        return _report(SummaryOutboxDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    if any(entry.accepted_intent_digest != getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST) or entry.accepted_redaction_receipt_digest != getattr(redaction_witness_report, "accepted_receipt_digest", ZERO_DIGEST) or entry.accepted_import_prune_marker_digest != getattr(import_prune_audit_report, "accepted_marker_digest", ZERO_DIGEST) for entry in entries):
        return _report(SummaryOutboxDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "accepted component digest drift", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    if any(entry.raw_boundary_exposed or entry.raw_payload_exposed for entry in entries):
        return _report(SummaryOutboxDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw boundary or payload surfaced", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    if any(not entry.contradiction_carried for entry in entries) or not (getattr(summary_publish_report, "contradiction_carried", False) and getattr(redaction_witness_report, "contradiction_carried", False) and getattr(import_prune_audit_report, "contradiction_preserved", False)):
        return _report(SummaryOutboxDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction memory missing", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    hard = int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) + int(getattr(redaction_witness_report, "hard_negative_count", 0) or 0) + int(getattr(import_prune_audit_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    if hard:
        return _report(SummaryOutboxDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, True, "hard-negative pressure", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    seen: dict[int, bytes] = {}
    prev = previous_digest
    digest_seen: set[bytes] = set()
    for entry in sorted(entries, key=lambda item: item.sequence):
        digest = entry.entry_digest
        if digest in digest_seen:
            return _report(SummaryOutboxDecisionKind.QUARANTINE_REPLAY, False, True, False, True, True, "replayed outbox entry", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
        digest_seen.add(digest)
        if entry.sequence <= 0:
            return _report(SummaryOutboxDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, True, "non-positive sequence", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
        if entry.sequence in seen and seen[entry.sequence] != digest:
            return _report(SummaryOutboxDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, True, "same-sequence fork", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
        if entry.previous_digest != prev:
            return _report(SummaryOutboxDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, True, "previous digest mismatch", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
        seen[entry.sequence] = digest
        prev = digest
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    if len(families) < min_family_count:
        return _report(SummaryOutboxDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low outbox family diversity", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    if len(paths) < min_path_family_count:
        return _report(SummaryOutboxDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low outbox path diversity", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries)
    accepted = entries[-1].entry_digest if entries else ZERO_DIGEST
    return _report(SummaryOutboxDecisionKind.ACCEPT_SUMMARY_OUTBOX_STAGED, True, False, True, True, True, "summary outbox staged", summary_publish_report=summary_publish_report, redaction_witness_report=redaction_witness_report, import_prune_audit_report=import_prune_audit_report, entries=entries, accepted_entry_digest=accepted)
