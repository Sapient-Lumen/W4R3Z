"""rev0092 native load re-entry request.

rev0091 deliberately stopped at a route-to-load-gate marker.  This module is
one seam later: it prepares a *request* to revisit the native load gate, but it
still does not load a library and still does not dispatch a native call.

The purpose is to catch the bypass class where re-entry/preflight memory is
mistaken for fresh native-load permission.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativereentryjournal import NativeReentryJournalReport

NATIVE_LOAD_REENTRY_DOMAIN = DOMAIN + b":native-load-reentry-v1:"


class NativeLoadReentryDecisionKind(str, Enum):
    ACCEPT_LOAD_GATE_REQUEST_ONLY = "accept_load_gate_request_only"
    HOLD_REENTRY_JOURNAL_NOT_READY = "hold_reentry_journal_not_ready"
    HOLD_RELAUNCH_GATE_NOT_READY = "hold_relaunch_gate_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT = "quarantine_load_or_dispatch_attempt"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeLoadReentryRequest:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    reentry_journal_digest: bytes
    relaunch_gate_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    loader_id: str
    route_to_load_gate_only: bool
    native_load_attempted: bool
    native_dispatch_attempted: bool
    python_fallback_active: bool
    preserve_reentry_memory: bool
    preserve_relaunch_memory: bool
    preserve_oracle_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def request_digest(self) -> bytes:
        return sha256(NATIVE_LOAD_REENTRY_DOMAIN + b":request:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"reentry": self.reentry_journal_digest,
            b"relaunch": self.relaunch_gate_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"loader": self.loader_id,
            b"route_only": 1 if self.route_to_load_gate_only else 0,
            b"load_attempted": 1 if self.native_load_attempted else 0,
            b"dispatch_attempted": 1 if self.native_dispatch_attempted else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"preserve_reentry": 1 if self.preserve_reentry_memory else 0,
            b"preserve_relaunch": 1 if self.preserve_relaunch_memory else 0,
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
class NativeLoadReentryReport:
    decision_kind: NativeLoadReentryDecisionKind
    accepted: bool
    load_gate_request_ready: bool
    route_to_load_gate_only: bool
    native_load_allowed: bool
    native_dispatch_allowed: bool
    fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    request_digest: bytes
    reentry_journal_digest: bytes
    relaunch_gate_digest: bytes
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
        return sha256(NATIVE_LOAD_REENTRY_DOMAIN + b":report:" + bencode({
            b"decision": NativeLoadReentryDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"ready": 1 if self.load_gate_request_ready else 0,
            b"route_only": 1 if self.route_to_load_gate_only else 0,
            b"load_allowed": 1 if self.native_load_allowed else 0,
            b"dispatch_allowed": 1 if self.native_dispatch_allowed else 0,
            b"fallback": 1 if self.fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"request_digest": self.request_digest,
            b"reentry": self.reentry_journal_digest,
            b"relaunch": self.relaunch_gate_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"loader": self.loader_id,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def assess_native_load_reentry(
    reentry: NativeReentryJournalReport,
    relaunch_gate: Any,
    request: NativeLoadReentryRequest,
    *,
    previous: NativeLoadReentryRequest | None = None,
    prior_request_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeLoadReentryReport:
    families = set(observed_families or (request.family_id,))
    path_families = set(observed_path_families or (request.path_family_id,))
    tombstone_memory = bool(reentry.tombstone_memory and request.preserve_tombstone_memory)
    fault_memory = bool(reentry.fault_memory and request.preserve_quarantine_memory and request.preserve_crash_memory)

    def report(kind: NativeLoadReentryDecisionKind, accepted: bool, ready: bool, route: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeLoadReentryReport:
        return NativeLoadReentryReport(kind, accepted, ready, route, False, False, fallback, quarantine, watch, obligations, request.request_digest, reentry.report_digest, _get(relaunch_gate, "report_digest", b""), request.artifact_digest, request.source_digest, request.fallback_digest, request.python_oracle_digest, request.loader_id, tombstone_memory, fault_memory, len(families), len(path_families))

    if request.request_digest in prior_request_digests:
        return report(NativeLoadReentryDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, True, False, ("native-load-reentry-replay",))
    if previous is not None:
        if request.sequence < previous.sequence:
            return report(NativeLoadReentryDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, True, False, ("native-load-reentry-rollback",))
        if request.sequence == previous.sequence and request.request_digest != previous.request_digest:
            return report(NativeLoadReentryDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, True, False, ("native-load-reentry-same-sequence-fork",))
        if request.sequence > previous.sequence and request.previous_digest != previous.request_digest:
            return report(NativeLoadReentryDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, True, False, ("native-load-reentry-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeLoadReentryDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, True, False, ("native-load-reentry-low-diversity",))
    if not all((request.component, request.profile, request.operation, request.request_id, request.loader_id)):
        return report(NativeLoadReentryDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, True, True, False, ("native-load-reentry-missing-boundary",))
    if request.native_load_attempted or request.native_dispatch_attempted or not request.route_to_load_gate_only:
        return report(NativeLoadReentryDecisionKind.QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT, False, False, False, True, True, False, ("reentry-may-request-load-gate-only",))
    if not request.python_fallback_active:
        return report(NativeLoadReentryDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, True, False, ("python-fallback-must-remain-active",))
    if not all((request.preserve_reentry_memory, request.preserve_relaunch_memory, request.preserve_oracle_memory, request.preserve_fallback_memory, request.preserve_tombstone_memory, request.preserve_quarantine_memory, request.preserve_crash_memory)):
        return report(NativeLoadReentryDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, True, False, ("native-load-reentry-memory-drop",))
    if not reentry.accepted or not reentry.journaled or not reentry.route_to_load_gate_only:
        return report(NativeLoadReentryDecisionKind.HOLD_REENTRY_JOURNAL_NOT_READY, False, False, False, True, reentry.quarantine, True, ("reentry-journal-not-ready",))
    if not _get(relaunch_gate, "accepted", False) or not _get(relaunch_gate, "relaunch_plan_ready", False):
        return report(NativeLoadReentryDecisionKind.HOLD_RELAUNCH_GATE_NOT_READY, False, False, False, True, bool(_get(relaunch_gate, "quarantine", False)), True, ("relaunch-gate-not-ready",))
    if request.reentry_journal_digest != reentry.report_digest or request.relaunch_gate_digest != _get(relaunch_gate, "report_digest", b""):
        return report(NativeLoadReentryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-load-reentry-component-digest-drift",))
    if request.artifact_digest != reentry.artifact_digest or request.source_digest != reentry.source_digest or request.fallback_digest != reentry.fallback_digest or request.python_oracle_digest != reentry.python_oracle_digest:
        return report(NativeLoadReentryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-load-reentry-reentry-digest-drift",))
    if request.artifact_digest != _get(relaunch_gate, "artifact_digest", request.artifact_digest) or request.source_digest != _get(relaunch_gate, "source_digest", request.source_digest) or request.fallback_digest != _get(relaunch_gate, "fallback_digest", request.fallback_digest) or request.python_oracle_digest != _get(relaunch_gate, "python_oracle_digest", request.python_oracle_digest):
        return report(NativeLoadReentryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-load-reentry-relaunch-digest-drift",))
    return report(NativeLoadReentryDecisionKind.ACCEPT_LOAD_GATE_REQUEST_ONLY, True, True, True, True, False, False, ("route-to-load-gate-only", "native-load-still-forbidden-here", "dispatch-still-forbidden"))
