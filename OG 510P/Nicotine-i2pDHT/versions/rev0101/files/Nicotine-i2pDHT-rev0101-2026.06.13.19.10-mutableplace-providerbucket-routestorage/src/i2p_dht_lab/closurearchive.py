"""rev0067 closure archive lane.

Repair settlement is not enough after restart unless the exact settlement and the
negative/contradiction memory that justified it are archived as typed local
facts.  This module keeps that memory sticky without pretending to be global
truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

CLOSURE_ARCHIVE_DOMAIN = DOMAIN + b":closure-archive-v1:"


class ClosureArchiveEntryKind(str, Enum):
    SETTLEMENT_ARCHIVED = "settlement_archived"
    CONTRADICTION_ARCHIVED = "contradiction_archived"
    HARD_NEGATIVE_ARCHIVED = "hard_negative_archived"
    SOFT_NOTE = "soft_note"


class ClosureArchiveDecisionKind(str, Enum):
    ACCEPT_CLOSURE_ARCHIVED = "accept_closure_archived"
    HOLD_SETTLEMENT_PENDING = "hold_settlement_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_SETTLEMENT_NOT_READY = "quarantine_settlement_not_ready"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_NOT_ARCHIVED = "quarantine_contradiction_not_archived"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ClosureArchiveEntry:
    kind: ClosureArchiveEntryKind
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
    repair_settlement_digest: bytes
    duplicate_closure_digest: bytes
    remote_witness_ledger_digest: bytes
    conflict_cooldown_digest: bytes
    contradiction_digest: bytes
    contradiction_archived: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(CLOSURE_ARCHIVE_DOMAIN + b":entry:" + bencode({
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
            b"settlement": self.repair_settlement_digest,
            b"closure": self.duplicate_closure_digest,
            b"remote": self.remote_witness_ledger_digest,
            b"cooldown": self.conflict_cooldown_digest,
            b"contradiction": self.contradiction_digest,
            b"archived": 1 if self.contradiction_archived else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ClosureArchiveReport:
    decision_kind: ClosureArchiveDecisionKind
    accept: bool
    watch: bool
    archived: bool
    contradiction_archived: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    repair_settlement_digest: bytes
    duplicate_closure_digest: bytes
    remote_witness_ledger_digest: bytes
    conflict_cooldown_digest: bytes
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
    for attr in ("report_digest", "accepted_observation_digest", "accepted_entry_digest", "accepted_ack_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _entry_boundary(entry: ClosureArchiveEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_closure_archive_entry(*, kind: ClosureArchiveEntryKind, sequence: int, repair_settlement_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_archived: bool | None = None, contradiction_digest: bytes | None = None, family_id: str = "closure-archive-family-a", path_family_id: str = "closure-archive-path-a", hard_negative_count: int = 0) -> ClosureArchiveEntry:
    archived = bool(getattr(repair_settlement_report, "contradiction_preserved", False)) if contradiction_archived is None else bool(contradiction_archived)
    c_digest = contradiction_digest if contradiction_digest is not None else sha256(CLOSURE_ARCHIVE_DOMAIN + b":contradiction:" + getattr(repair_settlement_report, "remote_witness_ledger_digest", ZERO_DIGEST) + getattr(repair_settlement_report, "conflict_cooldown_digest", ZERO_DIGEST))
    return ClosureArchiveEntry(
        kind=ClosureArchiveEntryKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(repair_settlement_report, "action")),
        profile_id=getattr(repair_settlement_report, "profile_id"),
        service_name=getattr(repair_settlement_report, "service_name"),
        scope_digest=getattr(repair_settlement_report, "scope_digest"),
        request_digest=getattr(repair_settlement_report, "request_digest"),
        payload_digest=getattr(repair_settlement_report, "payload_digest"),
        idempotency_key=getattr(repair_settlement_report, "idempotency_key"),
        retry_idempotency_key=getattr(repair_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        repair_settlement_digest=_digest(repair_settlement_report),
        duplicate_closure_digest=getattr(repair_settlement_report, "duplicate_closure_digest", ZERO_DIGEST),
        remote_witness_ledger_digest=getattr(repair_settlement_report, "remote_witness_ledger_digest", ZERO_DIGEST),
        conflict_cooldown_digest=getattr(repair_settlement_report, "conflict_cooldown_digest", ZERO_DIGEST),
        contradiction_digest=c_digest,
        contradiction_archived=archived,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: ClosureArchiveDecisionKind, accept: bool, watch: bool, archived: bool, contradiction_archived: bool, reason: str, *, repair_settlement_report: Any, entries: tuple[ClosureArchiveEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> ClosureArchiveReport:
    digests = tuple(e.entry_digest for e in entries)
    families = {e.family_id for e in entries}
    paths = {e.path_family_id for e in entries}
    hard = int(getattr(repair_settlement_report, "hard_negative_count", 0) or 0) + sum(e.hard_negative_count for e in entries)
    report_digest = sha256(CLOSURE_ARCHIVE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"archived": 1 if archived else 0,
        b"contradiction": 1 if contradiction_archived else 0,
        b"settlement": _digest(repair_settlement_report),
        b"entries": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return ClosureArchiveReport(kind, accept, watch, archived, contradiction_archived, reason, SideEffectAction(getattr(repair_settlement_report, "action")), getattr(repair_settlement_report, "profile_id"), getattr(repair_settlement_report, "service_name"), getattr(repair_settlement_report, "scope_digest"), getattr(repair_settlement_report, "request_digest"), getattr(repair_settlement_report, "payload_digest"), getattr(repair_settlement_report, "idempotency_key"), getattr(repair_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(repair_settlement_report), getattr(repair_settlement_report, "duplicate_closure_digest", ZERO_DIGEST), getattr(repair_settlement_report, "remote_witness_ledger_digest", ZERO_DIGEST), getattr(repair_settlement_report, "conflict_cooldown_digest", ZERO_DIGEST), accepted_entry_digest, digests, len(families), len(paths), hard, report_digest)


def assess_closure_archive(*, repair_settlement_report: Any, entries: Iterable[ClosureArchiveEntry] = (), previous_digest: bytes = ZERO_DIGEST, seen_entry_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> ClosureArchiveReport:
    entry_tuple = tuple(entries)
    if bool(getattr(repair_settlement_report, "quarantined", False)) or not bool(getattr(repair_settlement_report, "settlement_ready", False)):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_SETTLEMENT_NOT_READY, False, False, False, False, "repair settlement not ready", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if int(getattr(repair_settlement_report, "hard_negative_count", 0) or 0):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, "settlement hard-negative pressure", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if not entry_tuple:
        return _report(ClosureArchiveDecisionKind.HOLD_SETTLEMENT_PENDING, False, True, False, False, "archive entries pending", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    digests = [e.entry_digest for e in entry_tuple]
    seen = set(seen_entry_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_REPLAY, False, False, False, False, "archive replay", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if any(e.sequence <= 0 for e in entry_tuple):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, "non-positive archive sequence", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for entry in entry_tuple:
        by_seq.setdefault(entry.sequence, set()).add(entry.entry_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, "same-sequence archive fork", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    ordered = sorted(entry_tuple, key=lambda e: e.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(ClosureArchiveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, "previous-link mismatch", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.entry_digest:
            return _report(ClosureArchiveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, "archive chain mismatch", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if any(_entry_boundary(e) != _boundary(repair_settlement_report) for e in entry_tuple):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, "archive boundary drift", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if any(e.repair_settlement_digest != _digest(repair_settlement_report) or e.duplicate_closure_digest != getattr(repair_settlement_report, "duplicate_closure_digest", ZERO_DIGEST) for e in entry_tuple):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, "archive digest drift", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if sum(e.hard_negative_count for e in entry_tuple):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, "archive hard-negative pressure", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if bool(getattr(repair_settlement_report, "contradiction_preserved", False)) and not any(e.contradiction_archived and e.kind in (ClosureArchiveEntryKind.CONTRADICTION_ARCHIVED, ClosureArchiveEntryKind.SETTLEMENT_ARCHIVED) for e in entry_tuple):
        return _report(ClosureArchiveDecisionKind.QUARANTINE_CONTRADICTION_NOT_ARCHIVED, False, False, False, False, "contradiction memory missing from archive", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if not any(e.kind is ClosureArchiveEntryKind.SETTLEMENT_ARCHIVED for e in entry_tuple):
        return _report(ClosureArchiveDecisionKind.HOLD_SETTLEMENT_PENDING, False, True, False, any(e.contradiction_archived for e in entry_tuple), "settlement archive entry missing", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if len({e.family_id for e in entry_tuple}) < min_family_count:
        return _report(ClosureArchiveDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, "low archive family diversity", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    if len({e.path_family_id for e in entry_tuple}) < min_path_family_count:
        return _report(ClosureArchiveDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, "low archive path diversity", repair_settlement_report=repair_settlement_report, entries=entry_tuple)
    return _report(ClosureArchiveDecisionKind.ACCEPT_CLOSURE_ARCHIVED, True, False, True, True, "closure settlement archived", repair_settlement_report=repair_settlement_report, entries=entry_tuple, accepted_entry_digest=ordered[-1].entry_digest)
