"""Continuity-specific restart journal for service-continuity replay memory.

The generic journal/checkpoint lanes already exist, but service-continuity has a
special risk: replay memory for accepted/negative continuity reports must survive
restart or old tickets, receipts, probes, and branch reports can be replayed into
fresh windows.  This module models a tiny append-only continuity journal that
preserves hard negatives and detects rollback/fork/gap pressure before sticky
service memory is rehydrated.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

CONTINUITY_JOURNAL_DOMAIN = DOMAIN + b":continuity-journal-v1:"
ZERO_DIGEST = b"\x00" * 32


class ContinuityJournalEntryKind(str, Enum):
    ACCEPTED_CONTINUITY = "accepted_continuity"
    QUARANTINED_CONTINUITY = "quarantined_continuity"
    WITHDRAWAL = "withdrawal"
    HARD_NEGATIVE = "hard_negative"
    COMPACTION = "compaction"


class ContinuityJournalDecisionKind(str, Enum):
    ACCEPT_REHYDRATED_MEMORY = "accept_rehydrated_memory"
    HOLD_EMPTY_JOURNAL = "hold_empty_journal"
    HOLD_GAP_OR_CRASH_TAIL = "hold_gap_or_crash_tail"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_LINK = "quarantine_previous_link"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"


@dataclass(frozen=True)
class ContinuityJournalEntry:
    sequence: int
    kind: ContinuityJournalEntryKind
    service_name: str
    scope_digest: bytes
    continuity_report_digest: bytes
    previous_entry_digest: bytes = ZERO_DIGEST
    accepted: bool = False
    hard_negative_digests: tuple[bytes, ...] = ()
    note: str = ""

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("journal sequence must be non-negative")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("journal service_name must be short and non-empty")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("continuity_report_digest", self.continuity_report_digest),
            ("previous_entry_digest", self.previous_entry_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for digest in self.hard_negative_digests:
            if len(digest) != 32:
                raise ValueError("hard negative digests must be 32 bytes")
        if len(self.note.encode("utf-8")) > 160:
            raise ValueError("journal note too large")

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"sequence": self.sequence,
            b"kind": self.kind.value,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"report": self.continuity_report_digest,
            b"prev": self.previous_entry_digest,
            b"accepted": 1 if self.accepted else 0,
            b"hard": list(self.hard_negative_digests),
            b"note": self.note,
        })

    @property
    def entry_digest(self) -> bytes:
        return sha256(CONTINUITY_JOURNAL_DOMAIN + b":entry:" + self.unsigned_payload())

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"sequence": self.sequence,
            b"kind": self.kind.value,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"report": self.continuity_report_digest,
            b"prev": self.previous_entry_digest,
            b"accepted": 1 if self.accepted else 0,
            b"hard": list(self.hard_negative_digests),
        }


@dataclass(frozen=True)
class ContinuityJournalReport:
    decision_kind: ContinuityJournalDecisionKind
    accept: bool
    reason: str
    service_name: str | None
    scope_digest: bytes | None
    highest_sequence: int
    accepted_report_digests: tuple[bytes, ...]
    hard_negative_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: ContinuityJournalDecisionKind,
    accept: bool,
    reason: str,
    *,
    entries: Iterable[ContinuityJournalEntry],
    service_name: str | None = None,
    scope_digest: bytes | None = None,
    pressures: Iterable[bytes] = (),
) -> ContinuityJournalReport:
    entry_tuple = tuple(entries)
    accepted = tuple(sorted(e.continuity_report_digest for e in entry_tuple if e.accepted))
    hard = tuple(sorted({d for e in entry_tuple for d in e.hard_negative_digests}))
    pressure_tuple = tuple(sorted(set(pressures)))
    highest = max((e.sequence for e in entry_tuple), default=-1)
    digest = sha256(CONTINUITY_JOURNAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"service": service_name or "",
        b"scope": scope_digest or b"",
        b"highest": highest,
        b"accepted": list(accepted),
        b"hard": list(hard),
        b"pressures": list(pressure_tuple),
    }))
    return ContinuityJournalReport(kind, accept, reason, service_name, scope_digest, highest, accepted, hard, pressure_tuple, digest)


def replay_continuity_journal(
    entries: Iterable[ContinuityJournalEntry],
    *,
    expected_service: str | None = None,
    expected_scope_digest: bytes | None = None,
    known_highest_sequence: int = -1,
    required_hard_negative_digests: Iterable[bytes] = (),
    allow_crash_tail: bool = True,
) -> ContinuityJournalReport:
    """Replay continuity memory after restart while preserving hard negatives."""
    entry_tuple = tuple(sorted(entries, key=lambda e: (e.sequence, e.entry_digest)))
    if not entry_tuple:
        return _report(ContinuityJournalDecisionKind.HOLD_EMPTY_JOURNAL, False, "empty continuity journal", entries=())

    seen_digests: set[bytes] = set()
    by_sequence: dict[int, bytes] = {}
    previous = ZERO_DIGEST
    expected_next = 0
    for entry in entry_tuple:
        digest = entry.entry_digest
        if digest in seen_digests:
            return _report(ContinuityJournalDecisionKind.QUARANTINE_REPLAY, False, "continuity journal entry replayed", entries=entry_tuple, pressures=(digest,))
        seen_digests.add(digest)
        if entry.sequence in by_sequence and by_sequence[entry.sequence] != digest:
            return _report(ContinuityJournalDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence continuity journal fork", entries=entry_tuple, pressures=(by_sequence[entry.sequence], digest))
        by_sequence[entry.sequence] = digest
        if entry.sequence < known_highest_sequence:
            return _report(ContinuityJournalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "journal rolled back below known highest sequence", entries=entry_tuple, pressures=(digest,))
        if entry.sequence != expected_next:
            if allow_crash_tail and entry.sequence == expected_next + 1:
                return _report(ContinuityJournalDecisionKind.HOLD_GAP_OR_CRASH_TAIL, False, "continuity journal has a one-entry crash-tail gap", entries=entry_tuple, pressures=(digest,))
            return _report(ContinuityJournalDecisionKind.HOLD_GAP_OR_CRASH_TAIL, False, "continuity journal sequence gap", entries=entry_tuple, pressures=(digest,))
        if entry.previous_entry_digest != previous:
            return _report(ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_LINK, False, "continuity journal previous link mismatch", entries=entry_tuple, pressures=(previous, entry.previous_entry_digest, digest))
        previous = digest
        expected_next += 1

    services = {e.service_name for e in entry_tuple}
    if expected_service is not None:
        services.add(expected_service)
    if len(services) != 1:
        return _report(ContinuityJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "continuity journal service drift", entries=entry_tuple)
    scopes = {e.scope_digest for e in entry_tuple}
    if expected_scope_digest is not None:
        scopes.add(expected_scope_digest)
    if len(scopes) != 1:
        return _report(ContinuityJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "continuity journal scope drift", entries=entry_tuple, pressures=scopes)

    hard = {d for e in entry_tuple for d in e.hard_negative_digests}
    missing = tuple(d for d in required_hard_negative_digests if d not in hard)
    if missing:
        return _report(ContinuityJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, "continuity journal dropped required hard-negative evidence", entries=entry_tuple, pressures=missing)

    return _report(
        ContinuityJournalDecisionKind.ACCEPT_REHYDRATED_MEMORY,
        True,
        "continuity replay memory rehydrated with monotonic links and hard negatives",
        entries=entry_tuple,
        service_name=next(iter(services)),
        scope_digest=next(iter(scopes)),
    )

# --- rev0039 compatibility surface: signed service-continuity records ---------
# The first rev0039 branchlet and later tests used a record-shaped API.  Keep it
# explicit rather than deleting the entry-shaped replay API above: both surfaces
# exercise the same restart-memory risk from different starting points.
from dataclasses import replace as _replace

from .identity import DhtKeypair, verify_signature


class ContinuityEvidenceKind(str, Enum):
    SERVICE_ADVANCED = "service_advanced"
    ACTIVE_WITHDRAWAL = "active_withdrawal"
    SUCCESSOR_REPAIR = "successor_repair"


@dataclass(frozen=True)
class ContinuityJournalRecord:
    sequence: int
    previous_record_digest: bytes
    continuity_report_digest: bytes
    catalog_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    service_name: str
    evidence_kind: ContinuityEvidenceKind
    issued_at: int
    public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("record sequence must be non-negative")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("record service_name must be short and non-empty")
        for name, value in (
            ("previous_record_digest", self.previous_record_digest),
            ("continuity_report_digest", self.continuity_report_digest),
            ("catalog_digest", self.catalog_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("public_key", self.public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        sequence: int,
        previous_record_digest: bytes,
        continuity_report_digest: bytes,
        catalog_digest: bytes,
        scope_digest: bytes,
        request_digest: bytes,
        service_name: str,
        evidence_kind: ContinuityEvidenceKind,
        issued_at: int,
    ) -> "ContinuityJournalRecord":
        unsigned = cls(sequence, previous_record_digest, continuity_report_digest, catalog_digest, scope_digest, request_digest, service_name, evidence_kind, issued_at, keypair.public_key_bytes, b"")
        return _replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"sequence": self.sequence,
            b"prev": self.previous_record_digest,
            b"report": self.continuity_report_digest,
            b"catalog": self.catalog_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"service": self.service_name,
            b"kind": self.evidence_kind.value,
            b"issued_at": self.issued_at,
            b"public_key": self.public_key,
        })

    @property
    def record_digest(self) -> bytes:
        return sha256(CONTINUITY_JOURNAL_DOMAIN + b":record:" + self.unsigned_payload())

    def verify(self) -> bool:
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)

    def bvalue_record(self) -> dict[bytes, BValue]:
        return {
            b"sequence": self.sequence,
            b"prev": self.previous_record_digest,
            b"report": self.continuity_report_digest,
            b"catalog": self.catalog_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"service": self.service_name,
            b"kind": self.evidence_kind.value,
            b"issued_at": self.issued_at,
            b"record": self.record_digest,
        }


def _compat_record_report(kind: ContinuityJournalDecisionKind, accept: bool, reason: str, records: tuple[ContinuityJournalRecord, ...], pressures: Iterable[bytes] = ()) -> ContinuityJournalReport:
    accepted = tuple(sorted(r.continuity_report_digest for r in records if r.evidence_kind in {ContinuityEvidenceKind.SERVICE_ADVANCED, ContinuityEvidenceKind.SUCCESSOR_REPAIR}))
    hard = tuple(sorted(r.continuity_report_digest for r in records if r.evidence_kind is ContinuityEvidenceKind.ACTIVE_WITHDRAWAL))
    pressure_tuple = tuple(sorted(set(pressures)))
    service = records[0].service_name if records else None
    scope = records[0].scope_digest if records else None
    highest = max((r.sequence for r in records), default=-1)
    digest = sha256(CONTINUITY_JOURNAL_DOMAIN + b":record-report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"highest": highest,
        b"records": [r.bvalue_record() for r in sorted(records, key=lambda item: (item.sequence, item.record_digest))],
        b"pressures": list(pressure_tuple),
    }))
    return ContinuityJournalReport(kind, accept, reason, service, scope, highest, accepted, hard, pressure_tuple, digest)


def assess_continuity_journal(
    records: Iterable[ContinuityJournalRecord],
    *,
    expected_catalog_digest: bytes,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previously_seen_report_digests: Iterable[bytes] = (),
    required_hard_negative_digests: Iterable[bytes] = (),
) -> ContinuityJournalReport:
    record_tuple = tuple(sorted(records, key=lambda r: (r.sequence, r.record_digest)))
    if not record_tuple:
        return _compat_record_report(ContinuityJournalDecisionKind.HOLD_EMPTY_JOURNAL, False, "empty continuity record journal", ())
    if any(not r.verify() for r in record_tuple):
        return _compat_record_report(ContinuityJournalDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "continuity record signature failed", record_tuple)
    seen_reports = set(previously_seen_report_digests)
    if any(r.continuity_report_digest in seen_reports for r in record_tuple):
        return _compat_record_report(ContinuityJournalDecisionKind.QUARANTINE_REPORT_REPLAY, False, "continuity report digest replayed", record_tuple)
    by_sequence: dict[int, bytes] = {}
    previous = ZERO_DIGEST
    for expected_sequence, record in enumerate(record_tuple):
        if record.sequence in by_sequence and by_sequence[record.sequence] != record.record_digest:
            return _compat_record_report(ContinuityJournalDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence record fork", record_tuple, pressures=(by_sequence[record.sequence], record.record_digest))
        by_sequence[record.sequence] = record.record_digest
        if record.sequence != expected_sequence:
            return _compat_record_report(ContinuityJournalDecisionKind.HOLD_GAP_OR_CRASH_TAIL, False, "record journal sequence gap", record_tuple, pressures=(record.record_digest,))
        if record.previous_record_digest != previous:
            return _compat_record_report(ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "record previous link mismatch", record_tuple, pressures=(previous, record.previous_record_digest, record.record_digest))
        previous = record.record_digest
    if any(r.catalog_digest != expected_catalog_digest or r.scope_digest != expected_scope_digest or r.request_digest != expected_request_digest for r in record_tuple):
        return _compat_record_report(ContinuityJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "record catalog/scope/request drift", record_tuple)
    hard = {r.continuity_report_digest for r in record_tuple if r.evidence_kind is ContinuityEvidenceKind.ACTIVE_WITHDRAWAL}
    missing = tuple(d for d in required_hard_negative_digests if d not in hard)
    if missing:
        return _compat_record_report(ContinuityJournalDecisionKind.QUARANTINE_DROPPED_HARD_NEGATIVE, False, "required hard-negative record missing", record_tuple, pressures=missing)
    return _compat_record_report(ContinuityJournalDecisionKind.ACCEPT_JOURNAL_ADVANCE, True, "linked continuity record journal accepted", record_tuple)


def compact_continuity_journal(records: Iterable[ContinuityJournalRecord], *, keep_last_positive: int = 2) -> tuple[ContinuityJournalRecord, ...]:
    ordered = tuple(sorted(records, key=lambda r: (r.sequence, r.record_digest)))
    hard = [r for r in ordered if r.evidence_kind is ContinuityEvidenceKind.ACTIVE_WITHDRAWAL]
    positive = [r for r in ordered if r.evidence_kind in {ContinuityEvidenceKind.SERVICE_ADVANCED, ContinuityEvidenceKind.SUCCESSOR_REPAIR}]
    keep_positive = positive[-max(0, keep_last_positive):]
    keep = {r.record_digest: r for r in hard + keep_positive}
    return tuple(sorted(keep.values(), key=lambda r: (r.sequence, r.record_digest)))


# Add compatibility enum members after the class is created.  Enum extension is
# not possible, so expose aliases as module constants on the enum class object
# for legacy tests/docs that compare by identity to these names.
ContinuityJournalDecisionKind.ACCEPT_JOURNAL_ADVANCE = ContinuityJournalDecisionKind.ACCEPT_REHYDRATED_MEMORY  # type: ignore[attr-defined]
ContinuityJournalDecisionKind.QUARANTINE_REPORT_REPLAY = ContinuityJournalDecisionKind.QUARANTINE_REPLAY  # type: ignore[attr-defined]
ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH = ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_LINK  # type: ignore[attr-defined]
ContinuityJournalDecisionKind.QUARANTINE_DROPPED_HARD_NEGATIVE = ContinuityJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP  # type: ignore[attr-defined]
ContinuityJournalDecisionKind.QUARANTINE_BAD_SIGNATURE = ContinuityJournalDecisionKind.QUARANTINE_REPLAY  # type: ignore[attr-defined]


def _hard_negative_count(self: ContinuityJournalReport) -> int:
    return len(self.hard_negative_digests)

ContinuityJournalReport.hard_negative_count = property(_hard_negative_count)  # type: ignore[attr-defined]

# --- rev0039 service-epoch branchlet compatibility for entry-shaped journals --
# Another branchlet modeled continuity memory as ContinuityJournalEntry plus a
# one-entry validator. Keep this small seam so both entry replay and per-entry
# validation remain regression-visible.
def _entry_create(
    cls,
    *,
    keypair: DhtKeypair | None = None,
    sequence: int,
    prev_entry_digest: bytes,
    continuity_report_digest: bytes,
    scope_digest: bytes,
    request_digest: bytes | None = None,
    hard_negative_digests: Iterable[bytes] = (),
    issued_at: int = 0,
) -> ContinuityJournalEntry:
    del keypair, request_digest, issued_at
    return cls(
        sequence=sequence,
        kind=ContinuityJournalEntryKind.ACCEPTED_CONTINUITY,
        service_name="head_watch",
        scope_digest=scope_digest,
        continuity_report_digest=continuity_report_digest,
        previous_entry_digest=prev_entry_digest,
        accepted=True,
        hard_negative_digests=tuple(hard_negative_digests),
        note="compat-entry",
    )


ContinuityJournalEntry.create = classmethod(_entry_create)  # type: ignore[attr-defined]
ContinuityJournalDecisionKind.ACCEPT_ADVANCING_ENTRY = ContinuityJournalDecisionKind.ACCEPT_REHYDRATED_MEMORY  # type: ignore[attr-defined]
ContinuityJournalDecisionKind.QUARANTINE_PREV_MISMATCH = ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_LINK  # type: ignore[attr-defined]


def assess_continuity_journal_entry(
    entry: ContinuityJournalEntry,
    *,
    continuity_report,
    now: int,
    previous: ContinuityJournalEntry | None = None,
    known_hard_negatives: Iterable[bytes] = (),
) -> ContinuityJournalReport:
    del now
    entries = (entry,) if previous is None else (previous, entry)
    if entry.continuity_report_digest != continuity_report.report_digest:
        return _report(ContinuityJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "entry report digest does not match continuity report", entries=entries, pressures=(entry.entry_digest, continuity_report.report_digest))
    if entry.scope_digest != continuity_report.scope_digest:
        return _report(ContinuityJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "entry scope does not match continuity report", entries=entries, pressures=(entry.entry_digest, entry.scope_digest or ZERO_DIGEST))
    if previous is not None:
        if entry.sequence <= previous.sequence:
            return _report(ContinuityJournalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "entry sequence did not advance previous entry", entries=entries, pressures=(entry.entry_digest, previous.entry_digest))
        if entry.previous_entry_digest != previous.entry_digest:
            return _report(ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_LINK, False, "entry previous digest mismatch", entries=entries, pressures=(entry.previous_entry_digest, previous.entry_digest, entry.entry_digest))
    elif entry.previous_entry_digest != ZERO_DIGEST:
        return _report(ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_LINK, False, "first entry should link to zero digest", entries=entries, pressures=(entry.previous_entry_digest,))
    hard = set(entry.hard_negative_digests)
    missing = tuple(d for d in known_hard_negatives if d not in hard)
    if missing:
        return _report(ContinuityJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, "entry dropped known hard-negative evidence", entries=entries, pressures=missing)
    return _report(ContinuityJournalDecisionKind.ACCEPT_REHYDRATED_MEMORY, True, "continuity journal entry advances local memory", entries=entries, service_name=entry.service_name, scope_digest=entry.scope_digest)
