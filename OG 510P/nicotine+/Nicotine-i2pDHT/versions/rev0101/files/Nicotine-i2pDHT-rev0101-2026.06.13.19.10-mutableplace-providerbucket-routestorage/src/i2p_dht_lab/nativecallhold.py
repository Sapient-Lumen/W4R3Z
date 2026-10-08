"""rev0092 native call hold.

A fresh revalidation seal still does not authorize a native call.  This module
pins the first-call boundary as a held canary/fallback route: Python may execute
as the oracle, but the native leaf remains uncalled until a later load gate
explicitly permits it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeloadreentry import NativeLoadReentryReport
from .revalidationseal import RevalidationSealReport

NATIVE_CALL_HOLD_DOMAIN = DOMAIN + b":native-call-hold-v1:"


class NativeCallHoldDecisionKind(str, Enum):
    ACCEPT_CALL_HELD_ON_PYTHON_FALLBACK = "accept_call_held_on_python_fallback"
    HOLD_LOAD_REENTRY_NOT_READY = "hold_load_reentry_not_ready"
    HOLD_REVALIDATION_SEAL_NOT_READY = "hold_revalidation_seal_not_ready"
    QUARANTINE_NATIVE_CALL_EXECUTED = "quarantine_native_call_executed"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeCallHoldCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_reentry_digest: bytes
    revalidation_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    native_call_requested: bool
    native_call_executed: bool
    python_fallback_executed: bool
    preserve_load_reentry_memory: bool
    preserve_revalidation_memory: bool
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
        return sha256(NATIVE_CALL_HOLD_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load_reentry": self.load_reentry_digest,
            b"revalidation": self.revalidation_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"native_requested": 1 if self.native_call_requested else 0,
            b"native_executed": 1 if self.native_call_executed else 0,
            b"python_executed": 1 if self.python_fallback_executed else 0,
            b"preserve_reentry": 1 if self.preserve_load_reentry_memory else 0,
            b"preserve_revalidation": 1 if self.preserve_revalidation_memory else 0,
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
class NativeCallHoldReport:
    decision_kind: NativeCallHoldDecisionKind
    accepted: bool
    call_held: bool
    native_call_allowed: bool
    native_call_executed: bool
    python_fallback_executed: bool
    fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    load_reentry_digest: bytes
    revalidation_seal_digest: bytes
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
        return sha256(NATIVE_CALL_HOLD_DOMAIN + b":report:" + bencode({
            b"decision": NativeCallHoldDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"held": 1 if self.call_held else 0,
            b"native_allowed": 1 if self.native_call_allowed else 0,
            b"native_executed": 1 if self.native_call_executed else 0,
            b"python_executed": 1 if self.python_fallback_executed else 0,
            b"fallback": 1 if self.fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"load_reentry": self.load_reentry_digest,
            b"revalidation": self.revalidation_seal_digest,
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


def assess_native_call_hold(
    load_reentry: NativeLoadReentryReport,
    revalidation: RevalidationSealReport,
    capsule: NativeCallHoldCapsule,
    *,
    previous: NativeCallHoldCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeCallHoldReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(load_reentry.tombstone_memory and revalidation.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(load_reentry.fault_memory and revalidation.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeCallHoldDecisionKind, accepted: bool, held: bool, native_executed: bool, python_executed: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeCallHoldReport:
        return NativeCallHoldReport(kind, accepted, held, False, native_executed, python_executed, fallback, quarantine, watch, obligations, capsule.capsule_digest, load_reentry.report_digest, revalidation.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, capsule.call_vector_digest, tombstone_memory, fault_memory, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeCallHoldDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, True, True, False, ("native-call-hold-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeCallHoldDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, True, True, False, ("native-call-hold-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeCallHoldDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, True, True, False, ("native-call-hold-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeCallHoldDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, True, True, False, ("native-call-hold-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeCallHoldDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, True, True, False, ("native-call-hold-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id, capsule.call_vector_digest)):
        return report(NativeCallHoldDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, True, True, True, False, ("native-call-hold-missing-boundary",))
    if capsule.native_call_executed:
        return report(NativeCallHoldDecisionKind.QUARANTINE_NATIVE_CALL_EXECUTED, False, False, True, capsule.python_fallback_executed, True, True, False, ("native-call-executed-before-load-gate",))
    if not load_reentry.accepted or not load_reentry.load_gate_request_ready:
        return report(NativeCallHoldDecisionKind.HOLD_LOAD_REENTRY_NOT_READY, False, False, False, capsule.python_fallback_executed, True, load_reentry.quarantine, True, ("load-reentry-not-ready",))
    if not revalidation.accepted or not revalidation.revalidated:
        return report(NativeCallHoldDecisionKind.HOLD_REVALIDATION_SEAL_NOT_READY, False, False, False, capsule.python_fallback_executed, True, revalidation.quarantine, True, ("revalidation-seal-not-ready",))
    if capsule.load_reentry_digest != load_reentry.report_digest or capsule.revalidation_seal_digest != revalidation.report_digest:
        return report(NativeCallHoldDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, True, False, ("native-call-hold-component-digest-drift",))
    if capsule.artifact_digest != load_reentry.artifact_digest or capsule.artifact_digest != revalidation.artifact_digest or capsule.source_digest != load_reentry.source_digest or capsule.source_digest != revalidation.source_digest or capsule.fallback_digest != load_reentry.fallback_digest or capsule.fallback_digest != revalidation.fallback_digest or capsule.python_oracle_digest != load_reentry.python_oracle_digest or capsule.python_oracle_digest != revalidation.python_oracle_digest:
        return report(NativeCallHoldDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, True, False, ("native-call-hold-artifact-source-fallback-oracle-drift",))
    if not all((capsule.preserve_load_reentry_memory, capsule.preserve_revalidation_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, capsule.preserve_tombstone_memory, capsule.preserve_quarantine_memory, capsule.preserve_crash_memory)):
        return report(NativeCallHoldDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, True, True, False, ("native-call-hold-memory-drop",))
    if not capsule.python_fallback_executed:
        return report(NativeCallHoldDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, False, True, True, False, ("python-fallback-oracle-must-execute-while-call-held",))
    return report(NativeCallHoldDecisionKind.ACCEPT_CALL_HELD_ON_PYTHON_FALLBACK, True, True, False, True, True, False, False, ("native-call-held", "python-fallback-oracle-executed", "load-gate-must-decide-later"))
