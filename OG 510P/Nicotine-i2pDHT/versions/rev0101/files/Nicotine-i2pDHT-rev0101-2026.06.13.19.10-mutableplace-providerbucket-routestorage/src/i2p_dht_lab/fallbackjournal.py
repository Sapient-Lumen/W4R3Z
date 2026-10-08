"""rev0086 fallback journal for native selection.

Fallback is not just an implementation detail.  If native selection routes to
Python because of quarantine, watch, operator policy, or missing readiness, that
choice becomes previous-linked restart memory so a later run cannot rediscover
native as fresh.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeselection import NativeSelectionReport

FALLBACK_JOURNAL_DOMAIN = DOMAIN + b":native-fallback-journal-v1:"


class FallbackJournalDecisionKind(str, Enum):
    ACCEPT_NATIVE_NO_FALLBACK_ENTRY = "accept_native_no_fallback_entry"
    RECORD_FALLBACK_ENTRY = "record_fallback_entry"
    HOLD_MISSING_FALLBACK_ENTRY = "hold_missing_fallback_entry"
    QUARANTINE_ENTRY_REPLAY_OR_ROLLBACK = "quarantine_entry_replay_or_rollback"
    QUARANTINE_ENTRY_FORK = "quarantine_entry_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_FALLBACK_DIGEST_MISSING = "quarantine_fallback_digest_missing"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class FallbackJournalEntry:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    selection_digest: bytes
    quarantine_digest: bytes
    corpus_digest: bytes
    fallback_digest: bytes
    reason: str
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def entry_digest(self) -> bytes:
        return sha256(FALLBACK_JOURNAL_DOMAIN + b":entry:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"selection": self.selection_digest,
            b"quarantine": self.quarantine_digest,
            b"corpus": self.corpus_digest,
            b"fallback": self.fallback_digest,
            b"reason": self.reason,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class FallbackJournalReport:
    decision_kind: FallbackJournalDecisionKind
    accepted: bool
    fallback_active: bool
    native_allowed: bool
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    entry_digest: bytes
    selection_digest: bytes
    quarantine_digest: bytes
    corpus_digest: bytes
    fallback_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(FALLBACK_JOURNAL_DOMAIN + b":report:" + bencode({
            b"decision": FallbackJournalDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"fallback_active": 1 if self.fallback_active else 0,
            b"native_allowed": 1 if self.native_allowed else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"entry": self.entry_digest,
            b"selection": self.selection_digest,
            b"quarantine_digest": self.quarantine_digest,
            b"corpus": self.corpus_digest,
            b"fallback": self.fallback_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_fallback_journal(
    selection: NativeSelectionReport,
    entry: FallbackJournalEntry | None = None,
    *,
    previous: FallbackJournalEntry | None = None,
    prior_entry_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> FallbackJournalReport:
    zero = b""
    families = set(observed_families or ((entry.family_id,) if entry else ()))
    path_families = set(observed_path_families or ((entry.path_family_id,) if entry else ()))

    def entry_digest() -> bytes:
        return entry.entry_digest if entry else zero

    def report(kind: FallbackJournalDecisionKind, accepted: bool, fallback: bool, native: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> FallbackJournalReport:
        return FallbackJournalReport(kind, accepted, fallback, native, watch, quarantine, obligations, entry_digest(), selection.report_digest, selection.quarantine_digest, selection.corpus_digest, selection.fallback_digest, len(families), len(path_families))

    if selection.accepted and selection.native_selected and not selection.fallback_selected and entry is None:
        return report(FallbackJournalDecisionKind.ACCEPT_NATIVE_NO_FALLBACK_ENTRY, True, False, True, False, False, ("native-selected-no-fallback-entry-needed", "fallback-still-available-from-selection"))
    if selection.accepted and selection.native_selected and not selection.quarantine and entry is None:
        return report(FallbackJournalDecisionKind.ACCEPT_NATIVE_NO_FALLBACK_ENTRY, True, False, True, False, False, ("native-selected-with-python-fallback-bound",))
    if entry is None:
        return report(FallbackJournalDecisionKind.HOLD_MISSING_FALLBACK_ENTRY, False, True, False, True, False, ("fallback-selection-needs-restart-journal-entry",))

    families = set(observed_families or (entry.family_id,))
    path_families = set(observed_path_families or (entry.path_family_id,))
    if entry.entry_digest in prior_entry_digests:
        return report(FallbackJournalDecisionKind.QUARANTINE_ENTRY_REPLAY_OR_ROLLBACK, False, True, False, False, True, ("fallback-entry-replay", "preserve-prior-entry"))
    if previous is not None:
        if entry.sequence < previous.sequence:
            return report(FallbackJournalDecisionKind.QUARANTINE_ENTRY_REPLAY_OR_ROLLBACK, False, True, False, False, True, ("fallback-entry-rollback",))
        if entry.sequence == previous.sequence and entry.entry_digest != previous.entry_digest:
            return report(FallbackJournalDecisionKind.QUARANTINE_ENTRY_FORK, False, True, False, False, True, ("fallback-entry-fork",))
        if entry.sequence > previous.sequence and entry.previous_digest != previous.entry_digest:
            return report(FallbackJournalDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, False, False, True, ("fallback-entry-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(FallbackJournalDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, False, False, True, ("fallback-entry-low-diversity",))
    if not entry.fallback_digest:
        return report(FallbackJournalDecisionKind.QUARANTINE_FALLBACK_DIGEST_MISSING, False, True, False, False, True, ("fallback-entry-needs-python-fallback-digest",))
    if entry.selection_digest != selection.report_digest or entry.quarantine_digest != selection.quarantine_digest or entry.corpus_digest != selection.corpus_digest or entry.fallback_digest != selection.fallback_digest:
        return report(FallbackJournalDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, True, ("fallback-entry-component-digest-drift",))
    if entry.component == "" or entry.profile == "" or entry.operation == "" or entry.request_id == "":
        return report(FallbackJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, False, False, True, ("fallback-entry-scope-missing",))
    if selection.native_selected and not selection.quarantine:
        return report(FallbackJournalDecisionKind.ACCEPT_NATIVE_NO_FALLBACK_ENTRY, True, False, True, False, False, ("fallback-entry-is-historical-not-active", "do-not-delete-without-retention"))
    return report(FallbackJournalDecisionKind.RECORD_FALLBACK_ENTRY, True, True, False, selection.watch, selection.quarantine, ("record-fallback-route", "preserve-native-quarantine-or-watch-memory", "python-oracle-remains-selected"))
