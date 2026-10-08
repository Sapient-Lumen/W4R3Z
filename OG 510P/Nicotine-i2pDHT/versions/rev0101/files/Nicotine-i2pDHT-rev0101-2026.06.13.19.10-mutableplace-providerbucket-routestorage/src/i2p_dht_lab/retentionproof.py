"""rev0069 retention proof after closure seal.

A closure seal is compact.  Retention proof checks that the compact seal did not
become a reason to delete the minimal evidence classes that make the sealed
closure meaningful after restart: closure audit, archive journal, prune replay,
contradiction memory, and hard-negative memory when present.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

RETENTION_PROOF_DOMAIN = DOMAIN + b":retention-proof-v1:"


class RetentionItemKind(str, Enum):
    CLOSURE_SEAL = "closure_seal"
    CLOSURE_AUDIT = "closure_audit"
    ARCHIVE_JOURNAL = "archive_journal"
    PRUNE_REPLAY = "prune_replay"
    CONTRADICTION_MEMORY = "contradiction_memory"
    HARD_NEGATIVE_MEMORY = "hard_negative_memory"
    REDACTED_OPERATOR_SUMMARY = "redacted_operator_summary"


class RetentionProofDecisionKind(str, Enum):
    ACCEPT_RETENTION_PROVED = "accept_retention_proved"
    HOLD_CLOSURE_SEAL_PENDING = "hold_closure_seal_pending"
    HOLD_MISSING_REQUIRED_CLASS = "hold_missing_required_class"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_DROPPED = "quarantine_hard_negative_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RetentionProofItem:
    kind: RetentionItemKind
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
    closure_seal_digest: bytes
    retained_digest: bytes
    retained: bool
    contradiction_carried: bool
    hard_negative_carried: bool
    redacted: bool
    retained_bytes: int
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def item_digest(self) -> bytes:
        return sha256(RETENTION_PROOF_DOMAIN + b":item:" + bencode({
            b"kind": self.kind.value,
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
            b"seal": self.closure_seal_digest,
            b"retained_digest": self.retained_digest,
            b"retained": 1 if self.retained else 0,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"hard_carried": 1 if self.hard_negative_carried else 0,
            b"redacted": 1 if self.redacted else 0,
            b"bytes": self.retained_bytes,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RetentionProofReport:
    decision_kind: RetentionProofDecisionKind
    accept: bool
    watch: bool
    retention_proved: bool
    contradiction_preserved: bool
    hard_negative_preserved: bool
    redacted_summary_present: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    closure_seal_digest: bytes
    accepted_item_digest: bytes
    item_digests: tuple[bytes, ...]
    retained_kinds: tuple[str, ...]
    retained_bytes: int
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
    for attr in ("report_digest", "accepted_entry_digest", "accepted_marker_digest", "accepted_observation_digest", "accepted_proposal_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _item_boundary(item: RetentionProofItem) -> tuple[Any, ...]:
    return (SideEffectAction(item.action), item.profile_id, item.service_name, item.scope_digest, item.request_digest, item.payload_digest, item.idempotency_key)


def make_retention_item(*, kind: RetentionItemKind, sequence: int, closure_seal_report: Any, retained_digest: bytes | None = None, previous_digest: bytes = ZERO_DIGEST, retained: bool = True, contradiction_carried: bool | None = None, hard_negative_carried: bool = False, redacted: bool = True, retained_bytes: int = 128, family_id: str = "retention-family-a", path_family_id: str = "retention-path-a", hard_negative_count: int = 0) -> RetentionProofItem:
    contradiction = bool(getattr(closure_seal_report, "contradiction_sealed", False)) if contradiction_carried is None and RetentionItemKind(kind) is RetentionItemKind.CONTRADICTION_MEMORY else bool(contradiction_carried or False)
    digest = retained_digest or sha256(RETENTION_PROOF_DOMAIN + b":retained:" + RetentionItemKind(kind).value.encode() + b":" + _digest(closure_seal_report))
    return RetentionProofItem(
        kind=RetentionItemKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(closure_seal_report, "action")),
        profile_id=getattr(closure_seal_report, "profile_id"),
        service_name=getattr(closure_seal_report, "service_name"),
        scope_digest=getattr(closure_seal_report, "scope_digest"),
        request_digest=getattr(closure_seal_report, "request_digest"),
        payload_digest=getattr(closure_seal_report, "payload_digest"),
        idempotency_key=getattr(closure_seal_report, "idempotency_key"),
        retry_idempotency_key=getattr(closure_seal_report, "retry_idempotency_key", ZERO_DIGEST),
        closure_seal_digest=_digest(closure_seal_report),
        retained_digest=digest,
        retained=bool(retained),
        contradiction_carried=bool(contradiction),
        hard_negative_carried=bool(hard_negative_carried),
        redacted=bool(redacted),
        retained_bytes=int(retained_bytes),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RetentionProofDecisionKind, accept: bool, watch: bool, proved: bool, contradiction: bool, hard_preserved: bool, summary: bool, reason: str, *, closure_seal_report: Any, items: tuple[RetentionProofItem, ...], accepted_item_digest: bytes = ZERO_DIGEST) -> RetentionProofReport:
    item_digests = tuple(item.item_digest for item in items)
    families = {item.family_id for item in items}
    paths = {item.path_family_id for item in items}
    retained_kinds = tuple(sorted({item.kind.value for item in items if item.retained}))
    retained_bytes = sum(item.retained_bytes for item in items if item.retained)
    hard = int(getattr(closure_seal_report, "hard_negative_count", 0) or 0) + sum(item.hard_negative_count for item in items)
    report_digest = sha256(RETENTION_PROOF_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"proved": 1 if proved else 0,
        b"contradiction": 1 if contradiction else 0,
        b"hard_preserved": 1 if hard_preserved else 0,
        b"summary": 1 if summary else 0,
        b"action": SideEffectAction(getattr(closure_seal_report, "action")).value,
        b"profile": getattr(closure_seal_report, "profile_id"),
        b"service": getattr(closure_seal_report, "service_name"),
        b"scope": getattr(closure_seal_report, "scope_digest"),
        b"request": getattr(closure_seal_report, "request_digest"),
        b"payload": getattr(closure_seal_report, "payload_digest"),
        b"idem": getattr(closure_seal_report, "idempotency_key"),
        b"retry_idem": getattr(closure_seal_report, "retry_idempotency_key", ZERO_DIGEST),
        b"seal": _digest(closure_seal_report),
        b"accepted": accepted_item_digest,
        b"items": list(item_digests),
        b"kinds": list(retained_kinds),
        b"bytes": retained_bytes,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return RetentionProofReport(kind, accept, watch, proved, contradiction, hard_preserved, summary, reason, SideEffectAction(getattr(closure_seal_report, "action")), getattr(closure_seal_report, "profile_id"), getattr(closure_seal_report, "service_name"), getattr(closure_seal_report, "scope_digest"), getattr(closure_seal_report, "request_digest"), getattr(closure_seal_report, "payload_digest"), getattr(closure_seal_report, "idempotency_key"), getattr(closure_seal_report, "retry_idempotency_key", ZERO_DIGEST), _digest(closure_seal_report), accepted_item_digest, item_digests, retained_kinds, retained_bytes, len(families), len(paths), hard, report_digest)


def assess_retention_proof(*, closure_seal_report: Any, items: tuple[RetentionProofItem, ...] = (), previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2, require_redacted_summary: bool = True) -> RetentionProofReport:
    if not bool(getattr(closure_seal_report, "accept", False)) or not bool(getattr(closure_seal_report, "closure_sealed", False)):
        return _report(RetentionProofDecisionKind.HOLD_CLOSURE_SEAL_PENDING, False, True, False, False, False, False, "closure seal is not accepted", closure_seal_report=closure_seal_report, items=items)
    if not items:
        return _report(RetentionProofDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, False, False, "no retention items", closure_seal_report=closure_seal_report, items=items)
    for item in items:
        if _item_boundary(item) != _boundary(closure_seal_report):
            return _report(RetentionProofDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "item boundary drift", closure_seal_report=closure_seal_report, items=items)
        if item.closure_seal_digest != _digest(closure_seal_report):
            return _report(RetentionProofDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "closure seal digest drift", closure_seal_report=closure_seal_report, items=items)
    sorted_items = sorted(items, key=lambda item: item.sequence)
    last_digest = previous_digest
    by_seq: dict[int, bytes] = {}
    for item in sorted_items:
        digest = item.item_digest
        if item.sequence in by_seq and by_seq[item.sequence] != digest:
            return _report(RetentionProofDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, False, "same sequence different retention item", closure_seal_report=closure_seal_report, items=items)
        by_seq[item.sequence] = digest
        if item.previous_digest != last_digest:
            return _report(RetentionProofDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, "previous digest mismatch", closure_seal_report=closure_seal_report, items=items)
        last_digest = digest
    families = {item.family_id for item in items}
    paths = {item.path_family_id for item in items}
    if len(families) < min_family_count:
        return _report(RetentionProofDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, any(i.contradiction_carried for i in items), any(i.hard_negative_carried for i in items), any(i.kind is RetentionItemKind.REDACTED_OPERATOR_SUMMARY for i in items), "not enough retention family diversity", closure_seal_report=closure_seal_report, items=items)
    if len(paths) < min_path_family_count:
        return _report(RetentionProofDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, any(i.contradiction_carried for i in items), any(i.hard_negative_carried for i in items), any(i.kind is RetentionItemKind.REDACTED_OPERATOR_SUMMARY for i in items), "not enough retention path diversity", closure_seal_report=closure_seal_report, items=items)
    retained = {item.kind for item in items if item.retained}
    required = {RetentionItemKind.CLOSURE_SEAL, RetentionItemKind.CLOSURE_AUDIT, RetentionItemKind.ARCHIVE_JOURNAL, RetentionItemKind.PRUNE_REPLAY}
    if bool(getattr(closure_seal_report, "contradiction_sealed", False)):
        required.add(RetentionItemKind.CONTRADICTION_MEMORY)
    if require_redacted_summary:
        required.add(RetentionItemKind.REDACTED_OPERATOR_SUMMARY)
    if not required.issubset(retained):
        return _report(RetentionProofDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, any(i.contradiction_carried for i in items), any(i.hard_negative_carried for i in items), RetentionItemKind.REDACTED_OPERATOR_SUMMARY in retained, "missing required retention class", closure_seal_report=closure_seal_report, items=items)
    contradiction = any(item.contradiction_carried and item.retained for item in items)
    if bool(getattr(closure_seal_report, "contradiction_sealed", False)) and not contradiction:
        return _report(RetentionProofDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, any(i.hard_negative_carried for i in items), RetentionItemKind.REDACTED_OPERATOR_SUMMARY in retained, "contradiction memory dropped", closure_seal_report=closure_seal_report, items=items)
    component_hard = int(getattr(closure_seal_report, "hard_negative_count", 0) or 0)
    if component_hard and not any(item.hard_negative_carried and item.retained for item in items):
        return _report(RetentionProofDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED, False, False, False, contradiction, False, RetentionItemKind.REDACTED_OPERATOR_SUMMARY in retained, "hard-negative memory dropped", closure_seal_report=closure_seal_report, items=items)
    if any(item.hard_negative_count for item in items):
        return _report(RetentionProofDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, contradiction, True, RetentionItemKind.REDACTED_OPERATOR_SUMMARY in retained, "live hard-negative pressure on retention item", closure_seal_report=closure_seal_report, items=items)
    return _report(RetentionProofDecisionKind.ACCEPT_RETENTION_PROVED, True, False, True, contradiction, component_hard == 0 or any(i.hard_negative_carried for i in items), RetentionItemKind.REDACTED_OPERATOR_SUMMARY in retained, "retention proof accepted", closure_seal_report=closure_seal_report, items=items, accepted_item_digest=sorted_items[-1].item_digest)
