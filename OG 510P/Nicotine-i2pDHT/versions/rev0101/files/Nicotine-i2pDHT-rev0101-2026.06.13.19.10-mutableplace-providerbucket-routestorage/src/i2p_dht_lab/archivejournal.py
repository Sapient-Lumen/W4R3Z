"""rev0068 archive journal after repair prune.

Repair prune is intentionally weak: it may allow soft trace deletion only after
settlement/archive evidence survived.  This lane writes a previous-linked local
journal after prune acceptance so restart cannot reinterpret "pruned" as "never
existed" and cannot lose contradiction memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

ARCHIVE_JOURNAL_DOMAIN = DOMAIN + b":archive-journal-v1:"


class ArchiveJournalEntryKind(str, Enum):
    SETTLEMENT_ARCHIVE_PRUNE_JOURNALED = "settlement_archive_prune_journaled"
    CONTRADICTION_MEMORY_JOURNALED = "contradiction_memory_journaled"
    PRUNE_BOUNDARY_JOURNALED = "prune_boundary_journaled"


class ArchiveJournalDecisionKind(str, Enum):
    ACCEPT_ARCHIVE_JOURNALED = "accept_archive_journaled"
    HOLD_ARCHIVE_PENDING = "hold_archive_pending"
    HOLD_PRUNE_PENDING = "hold_prune_pending"
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
class ArchiveJournalEntry:
    kind: ArchiveJournalEntryKind
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
    accepted_archive_entry_digest: bytes
    accepted_prune_proposal_digest: bytes
    contradiction_journaled: bool
    prune_memory_journaled: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(ARCHIVE_JOURNAL_DOMAIN + b":entry:" + bencode({
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
            b"archive_entry": self.accepted_archive_entry_digest,
            b"prune_proposal": self.accepted_prune_proposal_digest,
            b"contradiction": 1 if self.contradiction_journaled else 0,
            b"prune_memory": 1 if self.prune_memory_journaled else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ArchiveJournalReport:
    decision_kind: ArchiveJournalDecisionKind
    accept: bool
    watch: bool
    archive_journaled: bool
    contradiction_preserved: bool
    prune_memory_preserved: bool
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
    for attr in ("report_digest", "accepted_entry_digest", "accepted_proposal_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _entry_boundary(entry: ArchiveJournalEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_archive_journal_entry(*, kind: ArchiveJournalEntryKind, sequence: int, repair_settlement_report: Any, closure_archive_report: Any, repair_prune_report: Any, restart_generation: int = 1, previous_digest: bytes = ZERO_DIGEST, contradiction_journaled: bool | None = None, prune_memory_journaled: bool | None = None, family_id: str = "archive-journal-family-a", path_family_id: str = "archive-journal-path-a", hard_negative_count: int = 0) -> ArchiveJournalEntry:
    contradiction = bool(getattr(closure_archive_report, "contradiction_archived", False)) and bool(getattr(repair_prune_report, "contradiction_preserved", False)) if contradiction_journaled is None else bool(contradiction_journaled)
    prune_memory = bool(getattr(repair_prune_report, "soft_prune_allowed", False)) if prune_memory_journaled is None else bool(prune_memory_journaled)
    return ArchiveJournalEntry(
        kind=ArchiveJournalEntryKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        restart_generation=restart_generation,
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
        accepted_archive_entry_digest=getattr(closure_archive_report, "accepted_entry_digest", ZERO_DIGEST),
        accepted_prune_proposal_digest=getattr(repair_prune_report, "accepted_proposal_digest", ZERO_DIGEST),
        contradiction_journaled=contradiction,
        prune_memory_journaled=prune_memory,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: ArchiveJournalDecisionKind, accept: bool, watch: bool, journaled: bool, contradiction: bool, prune_memory: bool, reason: str, *, repair_settlement_report: Any, closure_archive_report: Any, repair_prune_report: Any, entries: tuple[ArchiveJournalEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> ArchiveJournalReport:
    digests = tuple(e.entry_digest for e in entries)
    families = {e.family_id for e in entries}
    paths = {e.path_family_id for e in entries}
    hard = sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in (repair_settlement_report, closure_archive_report, repair_prune_report)) + sum(e.hard_negative_count for e in entries)
    generation = max((e.restart_generation for e in entries), default=0)
    report_digest = sha256(ARCHIVE_JOURNAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"journaled": 1 if journaled else 0,
        b"contradiction": 1 if contradiction else 0,
        b"prune_memory": 1 if prune_memory else 0,
        b"generation": generation,
        b"settlement": _digest(repair_settlement_report),
        b"archive": _digest(closure_archive_report),
        b"prune": _digest(repair_prune_report),
        b"entries": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return ArchiveJournalReport(kind, accept, watch, journaled, contradiction, prune_memory, reason, generation, SideEffectAction(getattr(repair_settlement_report, "action")), getattr(repair_settlement_report, "profile_id"), getattr(repair_settlement_report, "service_name"), getattr(repair_settlement_report, "scope_digest"), getattr(repair_settlement_report, "request_digest"), getattr(repair_settlement_report, "payload_digest"), getattr(repair_settlement_report, "idempotency_key"), getattr(repair_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(repair_settlement_report), _digest(closure_archive_report), _digest(repair_prune_report), accepted_entry_digest, digests, len(families), len(paths), hard, report_digest)


def assess_archive_journal(*, repair_settlement_report: Any, closure_archive_report: Any, repair_prune_report: Any, entries: Iterable[ArchiveJournalEntry] = (), previous_digest: bytes = ZERO_DIGEST, seen_entry_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> ArchiveJournalReport:
    entry_tuple = tuple(entries)
    if bool(getattr(repair_settlement_report, "quarantined", False)) or not bool(getattr(repair_settlement_report, "settlement_ready", False)):
        return _report(ArchiveJournalDecisionKind.HOLD_ARCHIVE_PENDING, False, True, False, False, False, "repair settlement not ready", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if bool(getattr(closure_archive_report, "quarantined", False)) or not bool(getattr(closure_archive_report, "archived", False)):
        return _report(ArchiveJournalDecisionKind.HOLD_ARCHIVE_PENDING, False, True, False, False, False, "closure archive not ready", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if bool(getattr(repair_prune_report, "quarantined", False)) or not bool(getattr(repair_prune_report, "soft_prune_allowed", False)):
        return _report(ArchiveJournalDecisionKind.HOLD_PRUNE_PENDING, False, True, False, False, False, "repair prune not ready", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if any(_boundary(c) != _boundary(repair_settlement_report) for c in (closure_archive_report, repair_prune_report)):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "component boundary drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if int(getattr(repair_settlement_report, "hard_negative_count", 0) or 0) or int(getattr(closure_archive_report, "hard_negative_count", 0) or 0) or int(getattr(repair_prune_report, "hard_negative_count", 0) or 0):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "component hard-negative pressure", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if not bool(getattr(closure_archive_report, "contradiction_archived", False)) or not bool(getattr(repair_prune_report, "contradiction_preserved", False)):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, False, "component contradiction memory missing", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if not entry_tuple:
        return _report(ArchiveJournalDecisionKind.HOLD_PRUNE_PENDING, False, True, False, False, False, "archive journal entries pending", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    digests = [e.entry_digest for e in entry_tuple]
    seen = set(seen_entry_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "archive journal replay", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if any(e.sequence <= 0 or e.restart_generation <= 0 for e in entry_tuple):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "non-positive sequence/generation", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for entry in entry_tuple:
        by_seq.setdefault(entry.sequence, set()).add(entry.entry_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence archive-journal fork", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    ordered = sorted(entry_tuple, key=lambda e: e.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(ArchiveJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous-link mismatch", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.entry_digest:
            return _report(ArchiveJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "archive-journal chain mismatch", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if any(_entry_boundary(e) != _boundary(repair_settlement_report) for e in entry_tuple):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "entry boundary drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if any(e.repair_settlement_digest != _digest(repair_settlement_report) or e.closure_archive_digest != _digest(closure_archive_report) or e.repair_prune_digest != _digest(repair_prune_report) for e in entry_tuple):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "entry component digest drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if any(not e.contradiction_journaled or not e.prune_memory_journaled for e in entry_tuple):
        return _report(ArchiveJournalDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, False, "entry dropped contradiction/prune memory", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if len({e.family_id for e in entry_tuple}) < min_family_count:
        return _report(ArchiveJournalDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low archive journal family diversity", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    if len({e.path_family_id for e in entry_tuple}) < min_path_family_count:
        return _report(ArchiveJournalDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low archive journal path diversity", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple)
    accepted = ordered[-1]
    return _report(ArchiveJournalDecisionKind.ACCEPT_ARCHIVE_JOURNALED, True, False, True, True, True, "archive/prune closure journaled", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, repair_prune_report=repair_prune_report, entries=entry_tuple, accepted_entry_digest=accepted.entry_digest)
