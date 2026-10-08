"""rev0068 closure audit across archive journal and prune replay.

This lane is intentionally redundant: settlement, archive, prune, journal, and
replay may each be locally valid. Closure audit asks whether they are valid for
one exact object after restart, without losing contradiction memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

CLOSURE_AUDIT_DOMAIN = DOMAIN + b":closure-audit-v1:"


class ClosureAuditMarkerKind(str, Enum):
    RESTART_CLOSURE_AUDITED = "restart_closure_audited"
    PRUNE_REPLAY_AUDITED = "prune_replay_audited"
    CONTRADICTION_MEMORY_AUDITED = "contradiction_memory_audited"


class ClosureAuditDecisionKind(str, Enum):
    ACCEPT_CLOSURE_AUDITED = "accept_closure_audited"
    HOLD_JOURNAL_PENDING = "hold_journal_pending"
    HOLD_REPLAY_PENDING = "hold_replay_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ClosureAuditMarker:
    kind: ClosureAuditMarkerKind
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
    repair_settlement_digest: bytes
    closure_archive_digest: bytes
    repair_prune_digest: bytes
    archive_journal_digest: bytes
    prune_replay_digest: bytes
    contradiction_preserved: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(CLOSURE_AUDIT_DOMAIN + b":marker:" + bencode({
            b"kind": self.kind.value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"generation": self.restart_generation,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"settlement": self.repair_settlement_digest,
            b"archive": self.closure_archive_digest,
            b"prune": self.repair_prune_digest,
            b"journal": self.archive_journal_digest,
            b"replay": self.prune_replay_digest,
            b"contradiction": 1 if self.contradiction_preserved else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ClosureAuditReport:
    decision_kind: ClosureAuditDecisionKind
    accept: bool
    watch: bool
    closure_audited: bool
    contradiction_preserved: bool
    reason: str
    restart_generation: int
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    repair_settlement_digest: bytes
    closure_archive_digest: bytes
    repair_prune_digest: bytes
    archive_journal_digest: bytes
    prune_replay_digest: bytes
    accepted_marker_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_observation_digest", "accepted_proposal_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: ClosureAuditMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_closure_audit_marker(*, kind: ClosureAuditMarkerKind, sequence: int, repair_settlement_report: Any, closure_archive_report: Any, repair_prune_report: Any, archive_journal_report: Any, prune_replay_report: Any, previous_digest: bytes = ZERO_DIGEST, restart_generation: int | None = None, contradiction_preserved: bool | None = None, family_id: str = "closure-audit-family-a", path_family_id: str = "closure-audit-path-a", hard_negative_count: int = 0) -> ClosureAuditMarker:
    generation = int(getattr(prune_replay_report, "restart_generation", 1) if restart_generation is None else restart_generation)
    preserved = bool(getattr(archive_journal_report, "contradiction_preserved", False)) and bool(getattr(prune_replay_report, "contradiction_preserved", False)) if contradiction_preserved is None else bool(contradiction_preserved)
    return ClosureAuditMarker(
        kind=ClosureAuditMarkerKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        restart_generation=generation,
        action=SideEffectAction(getattr(repair_settlement_report, "action")),
        profile_id=getattr(repair_settlement_report, "profile_id"),
        service_name=getattr(repair_settlement_report, "service_name"),
        scope_digest=getattr(repair_settlement_report, "scope_digest"),
        request_digest=getattr(repair_settlement_report, "request_digest"),
        payload_digest=getattr(repair_settlement_report, "payload_digest"),
        idempotency_key=getattr(repair_settlement_report, "idempotency_key"),
        retry_idempotency_key=getattr(repair_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        repair_settlement_digest=_digest(repair_settlement_report),
        closure_archive_digest=_digest(closure_archive_report),
        repair_prune_digest=_digest(repair_prune_report),
        archive_journal_digest=_digest(archive_journal_report),
        prune_replay_digest=_digest(prune_replay_report),
        contradiction_preserved=preserved,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: ClosureAuditDecisionKind, accept: bool, watch: bool, audited: bool, contradiction: bool, reason: str, *, repair_settlement_report: Any, closure_archive_report: Any, repair_prune_report: Any, archive_journal_report: Any, prune_replay_report: Any, markers: tuple[ClosureAuditMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> ClosureAuditReport:
    digests = tuple(m.marker_digest for m in markers)
    families = {m.family_id for m in markers}
    paths = {m.path_family_id for m in markers}
    hard = sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in (repair_settlement_report, closure_archive_report, repair_prune_report, archive_journal_report, prune_replay_report)) + sum(m.hard_negative_count for m in markers)
    generation = max((m.restart_generation for m in markers), default=int(getattr(prune_replay_report, "restart_generation", 0) or 0))
    report_digest = sha256(CLOSURE_AUDIT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"audited": 1 if audited else 0,
        b"contradiction": 1 if contradiction else 0,
        b"generation": generation,
        b"settlement": _digest(repair_settlement_report),
        b"archive": _digest(closure_archive_report),
        b"prune": _digest(repair_prune_report),
        b"journal": _digest(archive_journal_report),
        b"replay": _digest(prune_replay_report),
        b"markers": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return ClosureAuditReport(kind, accept, watch, audited, contradiction, reason, generation, SideEffectAction(getattr(repair_settlement_report, "action")), getattr(repair_settlement_report, "profile_id"), getattr(repair_settlement_report, "service_name"), getattr(repair_settlement_report, "scope_digest"), getattr(repair_settlement_report, "request_digest"), getattr(repair_settlement_report, "payload_digest"), getattr(repair_settlement_report, "idempotency_key"), getattr(repair_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(repair_settlement_report), _digest(closure_archive_report), _digest(repair_prune_report), _digest(archive_journal_report), _digest(prune_replay_report), accepted_marker_digest, digests, len(families), len(paths), hard, report_digest)


def assess_closure_audit(*, repair_settlement_report: Any, closure_archive_report: Any, repair_prune_report: Any, archive_journal_report: Any, prune_replay_report: Any, markers: Iterable[ClosureAuditMarker] = (), previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> ClosureAuditReport:
    marker_tuple = tuple(markers)
    if bool(getattr(archive_journal_report, "quarantined", False)) or not bool(getattr(archive_journal_report, "archive_journaled", False)):
        return _report(ClosureAuditDecisionKind.HOLD_JOURNAL_PENDING, False, True, False, False, "archive journal pending", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if bool(getattr(prune_replay_report, "quarantined", False)) or not bool(getattr(prune_replay_report, "replay_stable", False)):
        return _report(ClosureAuditDecisionKind.HOLD_REPLAY_PENDING, False, True, False, False, "prune replay pending", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    components = (closure_archive_report, repair_prune_report, archive_journal_report, prune_replay_report)
    if any(_boundary(c) != _boundary(repair_settlement_report) for c in components):
        return _report(ClosureAuditDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, "component boundary drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if any(int(getattr(c, "hard_negative_count", 0) or 0) for c in (repair_settlement_report, closure_archive_report, repair_prune_report, archive_journal_report, prune_replay_report)):
        return _report(ClosureAuditDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, "hard-negative pressure", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if not (bool(getattr(closure_archive_report, "contradiction_archived", False)) and bool(getattr(repair_prune_report, "contradiction_preserved", False)) and bool(getattr(archive_journal_report, "contradiction_preserved", False)) and bool(getattr(prune_replay_report, "contradiction_preserved", False))):
        return _report(ClosureAuditDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, "component contradiction memory missing", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if not marker_tuple:
        return _report(ClosureAuditDecisionKind.HOLD_REPLAY_PENDING, False, True, False, True, "closure audit markers pending", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    digests = [m.marker_digest for m in marker_tuple]
    if any(d in set(seen_marker_digests) for d in digests) or len(set(digests)) != len(digests):
        return _report(ClosureAuditDecisionKind.QUARANTINE_REPLAY, False, False, False, False, "closure audit replay", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if any(m.sequence <= 0 or m.restart_generation <= 0 for m in marker_tuple):
        return _report(ClosureAuditDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, "non-positive audit sequence/generation", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for marker in marker_tuple:
        by_seq.setdefault(marker.sequence, set()).add(marker.marker_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(ClosureAuditDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, "same-sequence audit fork", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    ordered = sorted(marker_tuple, key=lambda m: m.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(ClosureAuditDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, "previous-link mismatch", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.marker_digest:
            return _report(ClosureAuditDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, "audit marker chain mismatch", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if any(_marker_boundary(m) != _boundary(repair_settlement_report) for m in marker_tuple):
        return _report(ClosureAuditDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, "marker boundary drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if any(m.repair_settlement_digest != _digest(repair_settlement_report) or m.closure_archive_digest != _digest(closure_archive_report) or m.repair_prune_digest != _digest(repair_prune_report) or m.archive_journal_digest != _digest(archive_journal_report) or m.prune_replay_digest != _digest(prune_replay_report) for m in marker_tuple):
        return _report(ClosureAuditDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, "marker digest drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if any(not m.contradiction_preserved for m in marker_tuple):
        return _report(ClosureAuditDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, "marker dropped contradiction memory", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if len({m.family_id for m in marker_tuple}) < min_family_count:
        return _report(ClosureAuditDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, "low closure audit family diversity", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    if len({m.path_family_id for m in marker_tuple}) < min_path_family_count:
        return _report(ClosureAuditDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, "low closure audit path diversity", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple)
    accepted = ordered[-1]
    return _report(ClosureAuditDecisionKind.ACCEPT_CLOSURE_AUDITED, True, False, True, True, "closure audited across restart/prune replay", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, markers=marker_tuple, accepted_marker_digest=accepted.marker_digest)
