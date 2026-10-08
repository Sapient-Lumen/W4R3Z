"""rev0093 native call canary.

The call canary records the Python-oracle result for the exact call vector that
rev0092 held.  It is a canary, not execution permission: the native leaf is not
called, and the Python fallback result is the only accepted result.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecallhold import NativeCallHoldReport
from .nativeloadloop import NativeLoadLoopReport

NATIVE_CALL_CANARY_DOMAIN = DOMAIN + b":native-call-canary-v1:"


class NativeCallCanaryDecisionKind(str, Enum):
    ACCEPT_CANARY_ON_PYTHON_RESULT = "accept_canary_on_python_result"
    HOLD_LOAD_LOOP_NOT_READY = "hold_load_loop_not_ready"
    HOLD_CALL_HOLD_NOT_READY = "hold_call_hold_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_NATIVE_RESULT_OR_EXECUTION = "quarantine_native_result_or_execution"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeCallCanaryCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_loop_digest: bytes
    call_hold_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    native_call_executed: bool
    python_fallback_executed: bool
    preserve_load_loop_memory: bool
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
        return sha256(NATIVE_CALL_CANARY_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load_loop": self.load_loop_digest,
            b"call_hold": self.call_hold_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"native_executed": 1 if self.native_call_executed else 0,
            b"python_executed": 1 if self.python_fallback_executed else 0,
            b"preserve_loop": 1 if self.preserve_load_loop_memory else 0,
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
class NativeCallCanaryReport:
    decision_kind: NativeCallCanaryDecisionKind
    accepted: bool
    canary_ready: bool
    native_call_allowed: bool
    native_call_executed: bool
    python_fallback_executed: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    load_loop_digest: bytes
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
        return sha256(NATIVE_CALL_CANARY_DOMAIN + b":report:" + bencode({
            b"decision": NativeCallCanaryDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"ready": 1 if self.canary_ready else 0,
            b"native_allowed": 1 if self.native_call_allowed else 0,
            b"native_executed": 1 if self.native_call_executed else 0,
            b"python_executed": 1 if self.python_fallback_executed else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"load_loop": self.load_loop_digest,
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


def assess_native_call_canary(
    load_loop: NativeLoadLoopReport,
    call_hold: NativeCallHoldReport,
    capsule: NativeCallCanaryCapsule,
    *,
    expected_python_result_digest: bytes,
    previous: NativeCallCanaryCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeCallCanaryReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(load_loop.tombstone_memory and call_hold.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(load_loop.fault_memory and call_hold.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeCallCanaryDecisionKind, accepted: bool, ready: bool, native_executed: bool, python_executed: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeCallCanaryReport:
        return NativeCallCanaryReport(kind, accepted, ready, False, native_executed, python_executed, quarantine, watch, obligations, capsule.capsule_digest, load_loop.report_digest, call_hold.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, capsule.call_vector_digest, capsule.python_result_digest, tombstone_memory, fault_memory, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeCallCanaryDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, capsule.python_fallback_executed, True, False, ("native-call-canary-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeCallCanaryDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, capsule.python_fallback_executed, True, False, ("native-call-canary-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeCallCanaryDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, capsule.python_fallback_executed, True, False, ("native-call-canary-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeCallCanaryDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, capsule.python_fallback_executed, True, False, ("native-call-canary-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeCallCanaryDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, capsule.python_fallback_executed, True, False, ("native-call-canary-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id, capsule.call_vector_digest, capsule.python_result_digest)):
        return report(NativeCallCanaryDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, capsule.python_fallback_executed, True, False, ("native-call-canary-missing-boundary",))
    if capsule.native_call_executed or capsule.native_result_digest:
        return report(NativeCallCanaryDecisionKind.QUARANTINE_NATIVE_RESULT_OR_EXECUTION, False, False, capsule.native_call_executed, capsule.python_fallback_executed, True, False, ("native-result-or-execution-not-allowed-in-canary",))
    if not capsule.python_fallback_executed:
        return report(NativeCallCanaryDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, False, True, False, ("python-fallback-result-required",))
    if not all((capsule.preserve_load_loop_memory, capsule.preserve_call_hold_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, capsule.preserve_tombstone_memory, capsule.preserve_quarantine_memory, capsule.preserve_crash_memory)):
        return report(NativeCallCanaryDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, capsule.python_fallback_executed, True, False, ("native-call-canary-memory-drop",))
    if not load_loop.accepted or not load_loop.loopback_ready:
        return report(NativeCallCanaryDecisionKind.HOLD_LOAD_LOOP_NOT_READY, False, False, False, capsule.python_fallback_executed, load_loop.quarantine, True, ("load-loop-not-ready",))
    if not call_hold.accepted or not call_hold.call_held or not call_hold.python_fallback_executed:
        return report(NativeCallCanaryDecisionKind.HOLD_CALL_HOLD_NOT_READY, False, False, False, capsule.python_fallback_executed, call_hold.quarantine, True, ("call-hold-not-ready",))
    if capsule.load_loop_digest != load_loop.report_digest or capsule.call_hold_digest != call_hold.report_digest:
        return report(NativeCallCanaryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-call-canary-component-digest-drift",))
    if capsule.artifact_digest != load_loop.artifact_digest or capsule.artifact_digest != call_hold.artifact_digest or capsule.source_digest != load_loop.source_digest or capsule.source_digest != call_hold.source_digest or capsule.fallback_digest != load_loop.fallback_digest or capsule.fallback_digest != call_hold.fallback_digest or capsule.python_oracle_digest != load_loop.python_oracle_digest or capsule.python_oracle_digest != call_hold.python_oracle_digest or capsule.call_vector_digest != load_loop.call_vector_digest or capsule.call_vector_digest != call_hold.call_vector_digest:
        return report(NativeCallCanaryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-call-canary-artifact-source-fallback-oracle-or-vector-drift",))
    if capsule.python_result_digest != expected_python_result_digest:
        return report(NativeCallCanaryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("python-oracle-result-digest-drift",))
    return report(NativeCallCanaryDecisionKind.ACCEPT_CANARY_ON_PYTHON_RESULT, True, True, False, True, False, False, ("python-result-recorded", "native-call-still-forbidden", "canary-is-not-dispatch-permission"))
