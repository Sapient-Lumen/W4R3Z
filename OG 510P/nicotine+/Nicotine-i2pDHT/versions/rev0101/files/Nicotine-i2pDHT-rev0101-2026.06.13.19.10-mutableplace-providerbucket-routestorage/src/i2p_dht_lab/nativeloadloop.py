"""rev0093 native load-loop boundary.

rev0092 could request that the existing native load gate be reconsidered, but it
kept both native load and native dispatch forbidden.  This module is one seam
later: it models the *loopback* from re-entry/revalidation/call-hold evidence
back toward the load gate while preserving the fact that Python is still the
only executor.

The danger class is subtle: a component can be individually true (load re-entry
accepted, revalidation accepted, call held) and still be unsafe to treat as a
fresh native-load attempt if one of those memories drifted, was dropped, or was
replayed at another request boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecallhold import NativeCallHoldReport
from .nativeloadreentry import NativeLoadReentryReport
from .revalidationseal import RevalidationSealReport

NATIVE_LOAD_LOOP_DOMAIN = DOMAIN + b":native-load-loop-v1:"


class NativeLoadLoopDecisionKind(str, Enum):
    ACCEPT_LOOPBACK_HELD_ON_PYTHON = "accept_loopback_held_on_python"
    HOLD_REENTRY_NOT_READY = "hold_reentry_not_ready"
    HOLD_REVALIDATION_NOT_READY = "hold_revalidation_not_ready"
    HOLD_CALL_HOLD_NOT_READY = "hold_call_hold_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT = "quarantine_load_or_dispatch_attempt"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeLoadLoopCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_reentry_digest: bytes
    revalidation_seal_digest: bytes
    call_hold_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    loopback_to_load_gate: bool
    native_load_attempted: bool
    native_dispatch_attempted: bool
    python_fallback_active: bool
    preserve_load_reentry_memory: bool
    preserve_revalidation_memory: bool
    preserve_call_hold_memory: bool
    preserve_python_oracle_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(NATIVE_LOAD_LOOP_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load_reentry": self.load_reentry_digest,
            b"revalidation": self.revalidation_seal_digest,
            b"call_hold": self.call_hold_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"loopback": 1 if self.loopback_to_load_gate else 0,
            b"load_attempted": 1 if self.native_load_attempted else 0,
            b"dispatch_attempted": 1 if self.native_dispatch_attempted else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"preserve_reentry": 1 if self.preserve_load_reentry_memory else 0,
            b"preserve_revalidation": 1 if self.preserve_revalidation_memory else 0,
            b"preserve_call_hold": 1 if self.preserve_call_hold_memory else 0,
            b"preserve_oracle": 1 if self.preserve_python_oracle_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeLoadLoopReport:
    decision_kind: NativeLoadLoopDecisionKind
    accepted: bool
    loopback_ready: bool
    native_load_allowed: bool
    native_dispatch_allowed: bool
    python_fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    load_reentry_digest: bytes
    revalidation_seal_digest: bytes
    call_hold_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_LOAD_LOOP_DOMAIN + b":report:" + bencode({
            b"decision": NativeLoadLoopDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"loopback_ready": 1 if self.loopback_ready else 0,
            b"native_load_allowed": 1 if self.native_load_allowed else 0,
            b"native_dispatch_allowed": 1 if self.native_dispatch_allowed else 0,
            b"fallback": 1 if self.python_fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"load_reentry": self.load_reentry_digest,
            b"revalidation": self.revalidation_seal_digest,
            b"call_hold": self.call_hold_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_load_loop(
    load_reentry: NativeLoadReentryReport,
    revalidation: RevalidationSealReport,
    call_hold: NativeCallHoldReport,
    capsule: NativeLoadLoopCapsule,
    *,
    previous: NativeLoadLoopCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeLoadLoopReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(load_reentry.tombstone_memory and revalidation.tombstone_memory and call_hold.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(load_reentry.fault_memory and revalidation.fault_memory and call_hold.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeLoadLoopDecisionKind, accepted: bool, ready: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeLoadLoopReport:
        return NativeLoadLoopReport(kind, accepted, ready, False, False, fallback, quarantine, watch, obligations, capsule.capsule_digest, load_reentry.report_digest, revalidation.report_digest, call_hold.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, capsule.call_vector_digest, tombstone_memory, fault_memory, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeLoadLoopDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("native-load-loop-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeLoadLoopDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("native-load-loop-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeLoadLoopDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, True, False, ("native-load-loop-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeLoadLoopDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, True, False, ("native-load-loop-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeLoadLoopDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, True, False, ("native-load-loop-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id, capsule.call_vector_digest)):
        return report(NativeLoadLoopDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, True, False, ("native-load-loop-missing-boundary",))
    if capsule.native_load_attempted or capsule.native_dispatch_attempted or not capsule.loopback_to_load_gate:
        return report(NativeLoadLoopDecisionKind.QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT, False, False, True, True, False, ("loopback-is-not-load-or-dispatch",))
    if not capsule.python_fallback_active:
        return report(NativeLoadLoopDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, False, ("python-fallback-must-remain-active",))
    if not all((capsule.preserve_load_reentry_memory, capsule.preserve_revalidation_memory, capsule.preserve_call_hold_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, capsule.preserve_tombstone_memory, capsule.preserve_quarantine_memory, capsule.preserve_crash_memory)):
        return report(NativeLoadLoopDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, False, ("native-load-loop-memory-drop",))
    if not load_reentry.accepted or not load_reentry.load_gate_request_ready:
        return report(NativeLoadLoopDecisionKind.HOLD_REENTRY_NOT_READY, False, False, True, load_reentry.quarantine, True, ("load-reentry-not-ready",))
    if not revalidation.accepted or not revalidation.revalidated:
        return report(NativeLoadLoopDecisionKind.HOLD_REVALIDATION_NOT_READY, False, False, True, revalidation.quarantine, True, ("revalidation-not-ready",))
    if not call_hold.accepted or not call_hold.call_held or call_hold.native_call_executed or not call_hold.python_fallback_executed:
        return report(NativeLoadLoopDecisionKind.HOLD_CALL_HOLD_NOT_READY, False, False, True, call_hold.quarantine, True, ("call-hold-not-ready",))
    if capsule.load_reentry_digest != load_reentry.report_digest or capsule.revalidation_seal_digest != revalidation.report_digest or capsule.call_hold_digest != call_hold.report_digest:
        return report(NativeLoadLoopDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-load-loop-component-digest-drift",))
    if capsule.artifact_digest != load_reentry.artifact_digest or capsule.artifact_digest != revalidation.artifact_digest or capsule.artifact_digest != call_hold.artifact_digest or capsule.source_digest != load_reentry.source_digest or capsule.source_digest != revalidation.source_digest or capsule.source_digest != call_hold.source_digest or capsule.fallback_digest != load_reentry.fallback_digest or capsule.fallback_digest != revalidation.fallback_digest or capsule.fallback_digest != call_hold.fallback_digest or capsule.python_oracle_digest != load_reentry.python_oracle_digest or capsule.python_oracle_digest != revalidation.python_oracle_digest or capsule.python_oracle_digest != call_hold.python_oracle_digest or capsule.call_vector_digest != call_hold.call_vector_digest:
        return report(NativeLoadLoopDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-load-loop-artifact-source-fallback-oracle-or-vector-drift",))
    return report(NativeLoadLoopDecisionKind.ACCEPT_LOOPBACK_HELD_ON_PYTHON, True, True, True, False, False, ("loopback-to-load-gate-recorded", "native-load-still-forbidden", "native-dispatch-still-forbidden", "python-fallback-active"))
