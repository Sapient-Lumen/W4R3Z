"""rev0063 egress journal compaction for ACK/retry contradictions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

EGRESS_JOURNAL_DOMAIN = DOMAIN + b":egress-journal-v1:"


class EgressJournalEntryKind(str, Enum):
    LATE_ACK = "late_ack"
    RETRY_SETTLEMENT = "retry_settlement"
    WITHDRAW_REPAIR = "withdraw_repair"
    CONTRADICTION = "contradiction"
    COMPACTION_SUMMARY = "compaction_summary"


class EgressJournalDecisionKind(str, Enum):
    ACCEPT_JOURNAL_COMPACTED = "accept_journal_compacted"
    ACCEPT_JOURNAL_RETAINS_CONTRADICTION = "accept_journal_retains_contradiction"
    HOLD_RETRY_OR_WITHDRAW_PENDING = "hold_retry_or_withdraw_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_DROPPED_CONTRADICTION = "quarantine_dropped_contradiction"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class EgressJournalEntry:
    kind: EgressJournalEntryKind
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
    late_ack_digest: bytes
    retry_settlement_digest: bytes
    withdraw_repair_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(EGRESS_JOURNAL_DOMAIN + b":entry:" + bencode({
            b"kind": self.kind.value, b"seq": self.sequence, b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value, b"profile": self.profile_id, b"service": self.service_name,
            b"scope": self.scope_digest, b"request": self.request_digest, b"payload": self.payload_digest,
            b"idem": self.idempotency_key, b"retry_idem": self.retry_idempotency_key,
            b"late_ack": self.late_ack_digest, b"retry_settlement": self.retry_settlement_digest,
            b"withdraw": self.withdraw_repair_digest, b"family": self.family_id, b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class EgressJournalReport:
    decision_kind: EgressJournalDecisionKind
    accept: bool
    watch: bool
    compacted: bool
    contradiction_retained: bool
    pending_repair: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    late_ack_digest: bytes
    retry_settlement_digest: bytes
    withdraw_repair_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _entry_boundary(entry: EgressJournalEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def _base_report(*reports: Any | None) -> Any:
    for report in reports:
        if report is not None:
            return report
    raise ValueError("at least one component report is required")


def make_egress_journal_entry(*, kind: EgressJournalEntryKind, sequence: int, base_report: Any, late_ack_report: Any | None = None, retry_settlement_report: Any | None = None, withdraw_repair_report: Any | None = None, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> EgressJournalEntry:
    return EgressJournalEntry(kind, sequence, previous_digest, SideEffectAction(getattr(base_report, "action")), getattr(base_report, "profile_id"), getattr(base_report, "service_name"), getattr(base_report, "scope_digest"), getattr(base_report, "request_digest"), getattr(base_report, "payload_digest"), getattr(base_report, "idempotency_key"), getattr(base_report, "retry_idempotency_key", ZERO_DIGEST), _digest(late_ack_report), _digest(retry_settlement_report), _digest(withdraw_repair_report), family_id, path_family_id, hard_negative_count)


def _report(kind: EgressJournalDecisionKind, accept: bool, watch: bool, compacted: bool, contradiction: bool, pending: bool, reason: str, *, late_ack_report: Any | None, retry_settlement_report: Any | None, withdraw_repair_report: Any | None, entries: tuple[EgressJournalEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> EgressJournalReport:
    base = _base_report(retry_settlement_report, late_ack_report, withdraw_repair_report)
    digests = tuple(entry.entry_digest for entry in entries)
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    hard = sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in (late_ack_report, retry_settlement_report, withdraw_repair_report) if component is not None) + sum(entry.hard_negative_count for entry in entries)
    report_digest = sha256(EGRESS_JOURNAL_DOMAIN + b":report:" + bencode({b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0, b"compacted": 1 if compacted else 0, b"contradiction": 1 if contradiction else 0, b"pending": 1 if pending else 0, b"late_ack": _digest(late_ack_report), b"retry_settlement": _digest(retry_settlement_report), b"withdraw": _digest(withdraw_repair_report), b"entries": list(digests), b"families": len(families), b"paths": len(paths), b"hard": hard}))
    return EgressJournalReport(kind, accept, watch, compacted, contradiction, pending, reason, SideEffectAction(getattr(base, "action")), getattr(base, "profile_id"), getattr(base, "service_name"), getattr(base, "scope_digest"), getattr(base, "request_digest"), getattr(base, "payload_digest"), getattr(base, "idempotency_key"), getattr(base, "retry_idempotency_key", ZERO_DIGEST), _digest(late_ack_report), _digest(retry_settlement_report), _digest(withdraw_repair_report), accepted_entry_digest, digests, len(families), len(paths), hard, report_digest)


def assess_egress_journal(*, late_ack_report: Any | None = None, retry_settlement_report: Any | None = None, withdraw_repair_report: Any | None = None, entries: Iterable[EgressJournalEntry] = (), previous_digest: bytes = ZERO_DIGEST, seen_entry_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> EgressJournalReport:
    entry_tuple = tuple(entries)
    components = tuple(c for c in (late_ack_report, retry_settlement_report, withdraw_repair_report) if c is not None)
    if not components:
        raise ValueError("egress journal needs at least one component report")
    if any(bool(getattr(c, "quarantined", False)) for c in components):
        return _report(EgressJournalDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "component quarantined", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    if any(_boundary(c) != _boundary(components[0]) for c in components):
        return _report(EgressJournalDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "component boundary drift", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    if not entry_tuple:
        return _report(EgressJournalDecisionKind.HOLD_RETRY_OR_WITHDRAW_PENDING, False, True, False, False, True, "journal entry pending", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    digests = [entry.entry_digest for entry in entry_tuple]
    if any(d in set(seen_entry_digests) for d in digests) or len(set(digests)) != len(digests):
        return _report(EgressJournalDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "journal replay", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for entry in entry_tuple:
        by_seq.setdefault(entry.sequence, set()).add(entry.entry_digest)
    if any(len(v) > 1 for v in by_seq.values()):
        return _report(EgressJournalDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence journal fork", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    ordered = sorted(entry_tuple, key=lambda entry: entry.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(EgressJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous-link mismatch", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    if any(_entry_boundary(entry) != _boundary(components[0]) for entry in entry_tuple):
        return _report(EgressJournalDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "entry boundary drift", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    if any(entry.late_ack_digest != _digest(late_ack_report) or entry.retry_settlement_digest != _digest(retry_settlement_report) or entry.withdraw_repair_digest != _digest(withdraw_repair_report) for entry in entry_tuple):
        return _report(EgressJournalDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "entry component digest drift", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    if sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in components) + sum(entry.hard_negative_count for entry in entry_tuple):
        return _report(EgressJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "hard negative pressure", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    if len({entry.family_id for entry in entry_tuple}) < min_family_count:
        return _report(EgressJournalDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, True, "low journal family diversity", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    if len({entry.path_family_id for entry in entry_tuple}) < min_path_family_count:
        return _report(EgressJournalDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, True, "low journal path diversity", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    late_present = bool(getattr(late_ack_report, "late_ack_present", False)) if late_ack_report is not None else False
    retry_terminal = bool(getattr(retry_settlement_report, "retry_terminal", False)) if retry_settlement_report is not None else False
    contradiction_required = late_present and retry_terminal
    contradiction_retained = any(entry.kind is EgressJournalEntryKind.CONTRADICTION for entry in entry_tuple)
    if contradiction_required and not contradiction_retained:
        return _report(EgressJournalDecisionKind.QUARANTINE_DROPPED_CONTRADICTION, False, False, False, False, False, "late ACK/retry-delivered contradiction was compacted away", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    pending = bool(getattr(retry_settlement_report, "retry_pending", False)) if retry_settlement_report is not None else False
    if pending:
        return _report(EgressJournalDecisionKind.HOLD_RETRY_OR_WITHDRAW_PENDING, False, True, False, contradiction_retained, True, "retry or withdraw still pending", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple)
    if contradiction_retained:
        return _report(EgressJournalDecisionKind.ACCEPT_JOURNAL_RETAINS_CONTRADICTION, True, False, True, True, False, "journal compaction retained contradiction evidence", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple, accepted_entry_digest=entry_tuple[-1].entry_digest)
    return _report(EgressJournalDecisionKind.ACCEPT_JOURNAL_COMPACTED, True, False, True, False, False, "journal compacted without dropping required contradictions", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, withdraw_repair_report=withdraw_repair_report, entries=entry_tuple, accepted_entry_digest=entry_tuple[-1].entry_digest)
