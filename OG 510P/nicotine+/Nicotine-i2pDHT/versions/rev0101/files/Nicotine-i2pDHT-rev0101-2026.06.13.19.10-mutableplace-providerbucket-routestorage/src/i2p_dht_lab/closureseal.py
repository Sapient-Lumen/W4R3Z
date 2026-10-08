"""rev0069 closure seal after closure audit.

Closure audit says a repaired duplicate-public-edge trace survived restart/audit.
A seal is one more local boundary: it turns that audited closure into a compact,
previous-linked marker without letting contradiction memory disappear or letting a
single accepted audit report authorize later retention/export work by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

CLOSURE_SEAL_DOMAIN = DOMAIN + b":closure-seal-v1:"


class ClosureSealEntryKind(str, Enum):
    CLOSURE_AUDIT_SEALED = "closure_audit_sealed"
    CONTRADICTION_MEMORY_SEALED = "contradiction_memory_sealed"
    EXPORT_BOUNDARY_SEALED = "export_boundary_sealed"


class ClosureSealDecisionKind(str, Enum):
    ACCEPT_CLOSURE_SEALED = "accept_closure_sealed"
    HOLD_CLOSURE_AUDIT_PENDING = "hold_closure_audit_pending"
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
class ClosureSealEntry:
    kind: ClosureSealEntryKind
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
    closure_audit_digest: bytes
    archive_journal_digest: bytes
    prune_replay_digest: bytes
    accepted_marker_digest: bytes
    contradiction_sealed: bool
    export_boundary_sealed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(CLOSURE_SEAL_DOMAIN + b":entry:" + bencode({
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
            b"closure_audit": self.closure_audit_digest,
            b"journal": self.archive_journal_digest,
            b"replay": self.prune_replay_digest,
            b"marker": self.accepted_marker_digest,
            b"contradiction": 1 if self.contradiction_sealed else 0,
            b"export_boundary": 1 if self.export_boundary_sealed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ClosureSealReport:
    decision_kind: ClosureSealDecisionKind
    accept: bool
    watch: bool
    closure_sealed: bool
    contradiction_sealed: bool
    export_boundary_sealed: bool
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
    closure_audit_digest: bytes
    archive_journal_digest: bytes
    prune_replay_digest: bytes
    accepted_entry_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_observation_digest", "accepted_proposal_digest"):
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
    )


def _entry_boundary(entry: ClosureSealEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_closure_seal_entry(*, kind: ClosureSealEntryKind, sequence: int, closure_audit_report: Any, archive_journal_report: Any, prune_replay_report: Any, previous_digest: bytes = ZERO_DIGEST, restart_generation: int | None = None, contradiction_sealed: bool | None = None, export_boundary_sealed: bool | None = None, family_id: str = "closure-seal-family-a", path_family_id: str = "closure-seal-path-a", hard_negative_count: int = 0) -> ClosureSealEntry:
    generation = int(getattr(closure_audit_report, "restart_generation", 1) if restart_generation is None else restart_generation)
    contradiction = bool(getattr(closure_audit_report, "contradiction_preserved", False)) if contradiction_sealed is None else bool(contradiction_sealed)
    export_boundary = kind is ClosureSealEntryKind.EXPORT_BOUNDARY_SEALED if export_boundary_sealed is None else bool(export_boundary_sealed)
    return ClosureSealEntry(
        kind=ClosureSealEntryKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        restart_generation=generation,
        action=SideEffectAction(getattr(closure_audit_report, "action")),
        profile_id=getattr(closure_audit_report, "profile_id"),
        service_name=getattr(closure_audit_report, "service_name"),
        scope_digest=getattr(closure_audit_report, "scope_digest"),
        request_digest=getattr(closure_audit_report, "request_digest"),
        payload_digest=getattr(closure_audit_report, "payload_digest"),
        idempotency_key=getattr(closure_audit_report, "idempotency_key"),
        retry_idempotency_key=getattr(closure_audit_report, "retry_idempotency_key", ZERO_DIGEST),
        closure_audit_digest=_digest(closure_audit_report),
        archive_journal_digest=_digest(archive_journal_report),
        prune_replay_digest=_digest(prune_replay_report),
        accepted_marker_digest=getattr(closure_audit_report, "accepted_marker_digest", ZERO_DIGEST),
        contradiction_sealed=contradiction,
        export_boundary_sealed=export_boundary,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: ClosureSealDecisionKind, accept: bool, watch: bool, sealed: bool, contradiction: bool, export_boundary: bool, reason: str, *, closure_audit_report: Any, archive_journal_report: Any, prune_replay_report: Any, entries: tuple[ClosureSealEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> ClosureSealReport:
    entry_digests = tuple(entry.entry_digest for entry in entries)
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    hard = sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in (closure_audit_report, archive_journal_report, prune_replay_report)) + sum(entry.hard_negative_count for entry in entries)
    generation = max((entry.restart_generation for entry in entries), default=int(getattr(closure_audit_report, "restart_generation", 0) or 0))
    report_digest = sha256(CLOSURE_SEAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"sealed": 1 if sealed else 0,
        b"contradiction": 1 if contradiction else 0,
        b"export_boundary": 1 if export_boundary else 0,
        b"generation": generation,
        b"action": SideEffectAction(getattr(closure_audit_report, "action")).value,
        b"profile": getattr(closure_audit_report, "profile_id"),
        b"service": getattr(closure_audit_report, "service_name"),
        b"scope": getattr(closure_audit_report, "scope_digest"),
        b"request": getattr(closure_audit_report, "request_digest"),
        b"payload": getattr(closure_audit_report, "payload_digest"),
        b"idem": getattr(closure_audit_report, "idempotency_key"),
        b"retry_idem": getattr(closure_audit_report, "retry_idempotency_key", ZERO_DIGEST),
        b"closure_audit": _digest(closure_audit_report),
        b"journal": _digest(archive_journal_report),
        b"replay": _digest(prune_replay_report),
        b"accepted": accepted_entry_digest,
        b"entries": list(entry_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return ClosureSealReport(kind, accept, watch, sealed, contradiction, export_boundary, reason, generation, SideEffectAction(getattr(closure_audit_report, "action")), getattr(closure_audit_report, "profile_id"), getattr(closure_audit_report, "service_name"), getattr(closure_audit_report, "scope_digest"), getattr(closure_audit_report, "request_digest"), getattr(closure_audit_report, "payload_digest"), getattr(closure_audit_report, "idempotency_key"), getattr(closure_audit_report, "retry_idempotency_key", ZERO_DIGEST), _digest(closure_audit_report), _digest(archive_journal_report), _digest(prune_replay_report), accepted_entry_digest, entry_digests, len(families), len(paths), hard, report_digest)


def assess_closure_seal(*, closure_audit_report: Any, archive_journal_report: Any, prune_replay_report: Any, entries: tuple[ClosureSealEntry, ...] = (), previous_digest: bytes = ZERO_DIGEST, known_by_sequence: Mapping[int, bytes] | None = None, min_family_count: int = 2, min_path_family_count: int = 2) -> ClosureSealReport:
    if not bool(getattr(closure_audit_report, "accept", False)) or not bool(getattr(closure_audit_report, "closure_audited", False)):
        return _report(ClosureSealDecisionKind.HOLD_CLOSURE_AUDIT_PENDING, False, True, False, False, False, "closure audit is not accepted", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    if _boundary(closure_audit_report) != _boundary(archive_journal_report) or _boundary(closure_audit_report) != _boundary(prune_replay_report):
        return _report(ClosureSealDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "component boundary drift", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    if sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in (closure_audit_report, archive_journal_report, prune_replay_report)):
        return _report(ClosureSealDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "component hard-negative pressure", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    if not entries:
        return _report(ClosureSealDecisionKind.HOLD_CLOSURE_AUDIT_PENDING, False, True, False, False, False, "no closure seal entries", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    expected = (_digest(closure_audit_report), _digest(archive_journal_report), _digest(prune_replay_report))
    for entry in entries:
        if _entry_boundary(entry) != _boundary(closure_audit_report):
            return _report(ClosureSealDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "entry boundary drift", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
        if (entry.closure_audit_digest, entry.archive_journal_digest, entry.prune_replay_digest) != expected:
            return _report(ClosureSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "entry component digest drift", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
        if entry.hard_negative_count:
            return _report(ClosureSealDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "entry hard-negative pressure", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    by_seq: dict[int, bytes] = {}
    sorted_entries = sorted(entries, key=lambda entry: entry.sequence)
    last_digest = previous_digest
    for entry in sorted_entries:
        digest = entry.entry_digest
        if entry.sequence in by_seq and by_seq[entry.sequence] != digest:
            return _report(ClosureSealDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same sequence different seal", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
        by_seq[entry.sequence] = digest
        if entry.previous_digest != last_digest:
            return _report(ClosureSealDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous digest mismatch", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
        last_digest = digest
    if known_by_sequence:
        max_known = max(known_by_sequence)
        if max(entry.sequence for entry in sorted_entries) < max_known:
            return _report(ClosureSealDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "sequence rollback against local seal memory", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
        for seq, known_digest in known_by_sequence.items():
            if seq in by_seq and by_seq[seq] != known_digest:
                return _report(ClosureSealDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "replayed sequence with different digest", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    if len(families) < min_family_count:
        return _report(ClosureSealDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, any(e.contradiction_sealed for e in entries), any(e.export_boundary_sealed for e in entries), "not enough seal family diversity", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    if len(paths) < min_path_family_count:
        return _report(ClosureSealDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, any(e.contradiction_sealed for e in entries), any(e.export_boundary_sealed for e in entries), "not enough seal path diversity", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    contradiction = any(entry.contradiction_sealed for entry in entries)
    if bool(getattr(closure_audit_report, "contradiction_preserved", False)) and not contradiction:
        return _report(ClosureSealDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, any(e.export_boundary_sealed for e in entries), "closure contradiction memory not sealed", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries)
    accepted = max(sorted_entries, key=lambda entry: entry.sequence)
    return _report(ClosureSealDecisionKind.ACCEPT_CLOSURE_SEALED, True, False, True, contradiction, any(e.export_boundary_sealed for e in entries), "closure seal accepted", closure_audit_report=closure_audit_report, archive_journal_report=archive_journal_report, prune_replay_report=prune_replay_report, entries=entries, accepted_entry_digest=accepted.entry_digest)
