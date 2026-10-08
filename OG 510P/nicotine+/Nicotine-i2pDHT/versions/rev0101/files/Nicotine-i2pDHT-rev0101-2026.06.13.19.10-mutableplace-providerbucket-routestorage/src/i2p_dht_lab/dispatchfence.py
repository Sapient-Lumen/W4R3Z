"""rev0093 native dispatch fence.

This is the last seam of rev0093: even after loopback and call-canary evidence,
the native call remains fenced.  The report may say that evidence is ready for a
future dispatch decision, but it never says that dispatch happened or is allowed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecallcanary import NativeCallCanaryReport
from .nativecallhold import NativeCallHoldReport
from .nativeloadloop import NativeLoadLoopReport
from .revalidationseal import RevalidationSealReport

NATIVE_DISPATCH_FENCE_DOMAIN = DOMAIN + b":native-dispatch-fence-v1:"


class NativeDispatchFenceDecisionKind(str, Enum):
    ACCEPT_DISPATCH_FENCED_ON_PYTHON = "accept_dispatch_fenced_on_python"
    HOLD_LOOPBACK_NOT_READY = "hold_loopback_not_ready"
    HOLD_CANARY_NOT_READY = "hold_canary_not_ready"
    HOLD_REVALIDATION_NOT_READY = "hold_revalidation_not_ready"
    HOLD_CALL_HOLD_NOT_READY = "hold_call_hold_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT = "quarantine_dispatch_or_load_attempt"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeDispatchFenceCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_loop_digest: bytes
    call_canary_digest: bytes
    revalidation_seal_digest: bytes
    call_hold_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_load_attempted: bool
    native_dispatch_attempted: bool
    native_call_executed: bool
    python_fallback_active: bool
    preserve_load_loop_memory: bool
    preserve_canary_memory: bool
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
        return sha256(NATIVE_DISPATCH_FENCE_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load_loop": self.load_loop_digest,
            b"call_canary": self.call_canary_digest,
            b"revalidation": self.revalidation_seal_digest,
            b"call_hold": self.call_hold_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"load_attempted": 1 if self.native_load_attempted else 0,
            b"dispatch_attempted": 1 if self.native_dispatch_attempted else 0,
            b"native_call_executed": 1 if self.native_call_executed else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"preserve_loop": 1 if self.preserve_load_loop_memory else 0,
            b"preserve_canary": 1 if self.preserve_canary_memory else 0,
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
class NativeDispatchFenceReport:
    decision_kind: NativeDispatchFenceDecisionKind
    accepted: bool
    dispatch_fenced: bool
    native_load_allowed: bool
    native_dispatch_allowed: bool
    native_call_executed: bool
    python_fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    load_loop_digest: bytes
    call_canary_digest: bytes
    revalidation_seal_digest: bytes
    call_hold_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_DISPATCH_FENCE_DOMAIN + b":report:" + bencode({
            b"decision": NativeDispatchFenceDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"fenced": 1 if self.dispatch_fenced else 0,
            b"load_allowed": 1 if self.native_load_allowed else 0,
            b"dispatch_allowed": 1 if self.native_dispatch_allowed else 0,
            b"native_executed": 1 if self.native_call_executed else 0,
            b"fallback": 1 if self.python_fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"load_loop": self.load_loop_digest,
            b"call_canary": self.call_canary_digest,
            b"revalidation": self.revalidation_seal_digest,
            b"call_hold": self.call_hold_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_dispatch_fence(
    load_loop: NativeLoadLoopReport,
    call_canary: NativeCallCanaryReport,
    revalidation: RevalidationSealReport,
    call_hold: NativeCallHoldReport,
    capsule: NativeDispatchFenceCapsule,
    *,
    previous: NativeDispatchFenceCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeDispatchFenceReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(load_loop.tombstone_memory and call_canary.tombstone_memory and revalidation.tombstone_memory and call_hold.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(load_loop.fault_memory and call_canary.fault_memory and revalidation.fault_memory and call_hold.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeDispatchFenceDecisionKind, accepted: bool, fenced: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeDispatchFenceReport:
        return NativeDispatchFenceReport(kind, accepted, fenced, False, False, capsule.native_call_executed, fallback, quarantine, watch, obligations, capsule.capsule_digest, load_loop.report_digest, call_canary.report_digest, revalidation.report_digest, call_hold.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, capsule.call_vector_digest, capsule.python_result_digest, tombstone_memory, fault_memory, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeDispatchFenceDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("native-dispatch-fence-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeDispatchFenceDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("native-dispatch-fence-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeDispatchFenceDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, True, False, ("native-dispatch-fence-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeDispatchFenceDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, True, False, ("native-dispatch-fence-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeDispatchFenceDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, True, False, ("native-dispatch-fence-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id, capsule.call_vector_digest, capsule.python_result_digest)):
        return report(NativeDispatchFenceDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, True, False, ("native-dispatch-fence-missing-boundary",))
    if capsule.native_load_attempted or capsule.native_dispatch_attempted or capsule.native_call_executed:
        return report(NativeDispatchFenceDecisionKind.QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT, False, False, capsule.python_fallback_active, True, False, ("dispatch-fence-observed-native-side-effect",))
    if not capsule.python_fallback_active:
        return report(NativeDispatchFenceDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, False, ("python-fallback-must-remain-active",))
    if not all((capsule.preserve_load_loop_memory, capsule.preserve_canary_memory, capsule.preserve_revalidation_memory, capsule.preserve_call_hold_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, capsule.preserve_tombstone_memory, capsule.preserve_quarantine_memory, capsule.preserve_crash_memory)):
        return report(NativeDispatchFenceDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, False, ("native-dispatch-fence-memory-drop",))
    if not load_loop.accepted or not load_loop.loopback_ready:
        return report(NativeDispatchFenceDecisionKind.HOLD_LOOPBACK_NOT_READY, False, False, True, load_loop.quarantine, True, ("load-loop-not-ready",))
    if not call_canary.accepted or not call_canary.canary_ready:
        return report(NativeDispatchFenceDecisionKind.HOLD_CANARY_NOT_READY, False, False, True, call_canary.quarantine, True, ("call-canary-not-ready",))
    if not revalidation.accepted or not revalidation.revalidated:
        return report(NativeDispatchFenceDecisionKind.HOLD_REVALIDATION_NOT_READY, False, False, True, revalidation.quarantine, True, ("revalidation-not-ready",))
    if not call_hold.accepted or not call_hold.call_held:
        return report(NativeDispatchFenceDecisionKind.HOLD_CALL_HOLD_NOT_READY, False, False, True, call_hold.quarantine, True, ("call-hold-not-ready",))
    if capsule.load_loop_digest != load_loop.report_digest or capsule.call_canary_digest != call_canary.report_digest or capsule.revalidation_seal_digest != revalidation.report_digest or capsule.call_hold_digest != call_hold.report_digest:
        return report(NativeDispatchFenceDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-dispatch-fence-component-digest-drift",))
    if capsule.artifact_digest != load_loop.artifact_digest or capsule.artifact_digest != call_canary.artifact_digest or capsule.artifact_digest != revalidation.artifact_digest or capsule.artifact_digest != call_hold.artifact_digest or capsule.source_digest != load_loop.source_digest or capsule.source_digest != call_canary.source_digest or capsule.source_digest != revalidation.source_digest or capsule.source_digest != call_hold.source_digest or capsule.fallback_digest != load_loop.fallback_digest or capsule.fallback_digest != call_canary.fallback_digest or capsule.fallback_digest != revalidation.fallback_digest or capsule.fallback_digest != call_hold.fallback_digest or capsule.python_oracle_digest != load_loop.python_oracle_digest or capsule.python_oracle_digest != call_canary.python_oracle_digest or capsule.python_oracle_digest != revalidation.python_oracle_digest or capsule.python_oracle_digest != call_hold.python_oracle_digest or capsule.call_vector_digest != load_loop.call_vector_digest or capsule.call_vector_digest != call_canary.call_vector_digest or capsule.call_vector_digest != call_hold.call_vector_digest or capsule.python_result_digest != call_canary.python_result_digest:
        return report(NativeDispatchFenceDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-dispatch-fence-artifact-source-fallback-oracle-vector-or-result-drift",))
    return report(NativeDispatchFenceDecisionKind.ACCEPT_DISPATCH_FENCED_ON_PYTHON, True, True, True, False, False, ("dispatch-fenced", "native-load-still-forbidden", "native-call-still-forbidden", "python-oracle-result-carried"))
