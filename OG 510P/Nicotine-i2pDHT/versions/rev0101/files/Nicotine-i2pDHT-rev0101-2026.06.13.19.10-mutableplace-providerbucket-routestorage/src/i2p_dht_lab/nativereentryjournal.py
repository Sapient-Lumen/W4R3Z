"""rev0091 native re-entry journal.

The preflight route back toward the load gate is restart memory, not a hidden
branch in control flow.  This journal stores the preflight/oracle boundary while
preserving fallback, tombstone, quarantine, and crash evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeoracleseal import NativeOracleSealReport
from .nativepreflight import NativePreflightReport

NATIVE_REENTRY_JOURNAL_DOMAIN = DOMAIN + b":native-reentry-journal-v1:"


class NativeReentryJournalDecisionKind(str, Enum):
    ACCEPT_REENTRY_JOURNAL = "accept_reentry_journal"
    HOLD_PREFLIGHT_NOT_READY = "hold_preflight_not_ready"
    HOLD_ORACLE_SEAL_NOT_READY = "hold_oracle_seal_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeReentryJournalEntry:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    preflight_digest: bytes
    oracle_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    loader_id: str
    route_to_load_gate_only: bool
    python_fallback_active: bool
    preserve_preflight_memory: bool
    preserve_oracle_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def entry_digest(self) -> bytes:
        return sha256(NATIVE_REENTRY_JOURNAL_DOMAIN + b":entry:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"preflight": self.preflight_digest,
            b"oracle_seal": self.oracle_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"loader_id": self.loader_id,
            b"route_only": 1 if self.route_to_load_gate_only else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"preserve_preflight": 1 if self.preserve_preflight_memory else 0,
            b"preserve_oracle": 1 if self.preserve_oracle_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeReentryJournalReport:
    decision_kind: NativeReentryJournalDecisionKind
    accepted: bool
    journaled: bool
    route_to_load_gate_only: bool
    fallback_active: bool
    native_load_forbidden: bool
    dispatch_forbidden: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    entry_digest: bytes
    preflight_digest: bytes
    oracle_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    loader_id: str
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_REENTRY_JOURNAL_DOMAIN + b":report:" + bencode({
            b"decision": NativeReentryJournalDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"journaled": 1 if self.journaled else 0,
            b"route_only": 1 if self.route_to_load_gate_only else 0,
            b"fallback_active": 1 if self.fallback_active else 0,
            b"load_forbidden": 1 if self.native_load_forbidden else 0,
            b"dispatch_forbidden": 1 if self.dispatch_forbidden else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"entry": self.entry_digest,
            b"preflight": self.preflight_digest,
            b"oracle_seal": self.oracle_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"loader_id": self.loader_id,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault_memory": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_reentry_journal(
    preflight: NativePreflightReport,
    oracle_seal: NativeOracleSealReport,
    entry: NativeReentryJournalEntry,
    *,
    previous: NativeReentryJournalEntry | None = None,
    prior_entry_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeReentryJournalReport:
    families = set(observed_families or (entry.family_id,))
    path_families = set(observed_path_families or (entry.path_family_id,))
    tombstone_memory = bool(preflight.tombstone_memory and oracle_seal.tombstone_memory and entry.preserve_tombstone_memory)
    fault_memory = bool(preflight.fault_memory and oracle_seal.fault_memory and entry.preserve_quarantine_memory and entry.preserve_crash_memory)

    def report(kind: NativeReentryJournalDecisionKind, accepted: bool, journaled: bool, route: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeReentryJournalReport:
        return NativeReentryJournalReport(kind, accepted, journaled, route, fallback, True, True, quarantine, watch, obligations, entry.entry_digest, preflight.report_digest, oracle_seal.report_digest, entry.artifact_digest, entry.source_digest, entry.fallback_digest, entry.python_oracle_digest, entry.loader_id, tombstone_memory, fault_memory, len(families), len(path_families))

    if entry.entry_digest in prior_entry_digests:
        return report(NativeReentryJournalDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, True, False, ("native-reentry-journal-replay",))
    if previous is not None:
        if entry.sequence < previous.sequence:
            return report(NativeReentryJournalDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, True, False, ("native-reentry-journal-rollback",))
        if entry.sequence == previous.sequence and entry.entry_digest != previous.entry_digest:
            return report(NativeReentryJournalDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, True, False, ("native-reentry-journal-same-sequence-fork",))
        if entry.sequence > previous.sequence and entry.previous_digest != previous.entry_digest:
            return report(NativeReentryJournalDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, True, False, ("native-reentry-journal-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeReentryJournalDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, True, False, ("native-reentry-journal-low-diversity",))
    if not all((entry.component, entry.profile, entry.operation, entry.request_id, entry.loader_id)):
        return report(NativeReentryJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, True, True, False, ("native-reentry-journal-missing-boundary",))
    if not preflight.accepted or not preflight.route_to_load_gate_only:
        return report(NativeReentryJournalDecisionKind.HOLD_PREFLIGHT_NOT_READY, False, False, False, True, preflight.quarantine, True, ("native-preflight-not-ready",))
    if not oracle_seal.accepted or not oracle_seal.python_oracle_sealed:
        return report(NativeReentryJournalDecisionKind.HOLD_ORACLE_SEAL_NOT_READY, False, False, False, True, oracle_seal.quarantine, True, ("native-oracle-seal-not-ready",))
    if entry.preflight_digest != preflight.report_digest or entry.oracle_seal_digest != oracle_seal.report_digest:
        return report(NativeReentryJournalDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-reentry-journal-component-digest-drift",))
    if entry.artifact_digest != preflight.artifact_digest or entry.artifact_digest != oracle_seal.artifact_digest or entry.source_digest != preflight.source_digest or entry.source_digest != oracle_seal.source_digest or entry.fallback_digest != preflight.fallback_digest or entry.fallback_digest != oracle_seal.fallback_digest or entry.python_oracle_digest != preflight.python_oracle_digest or entry.python_oracle_digest != oracle_seal.python_oracle_digest:
        return report(NativeReentryJournalDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-reentry-journal-artifact-source-fallback-oracle-drift",))
    if entry.loader_id != preflight.loader_id:
        return report(NativeReentryJournalDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-reentry-journal-loader-drift",))
    if not entry.route_to_load_gate_only or not entry.python_fallback_active or not entry.preserve_preflight_memory or not entry.preserve_oracle_memory or not entry.preserve_fallback_memory or not tombstone_memory or not fault_memory:
        return report(NativeReentryJournalDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, True, False, ("native-reentry-journal-memory-drop",))
    return report(NativeReentryJournalDecisionKind.ACCEPT_REENTRY_JOURNAL, True, True, True, True, False, preflight.watch or oracle_seal.watch, ("native-reentry-journaled", "route-to-load-gate-only", "python-fallback-remains-active"))
