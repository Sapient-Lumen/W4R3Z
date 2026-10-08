"""rev0094 native fault-seal memory.

Result-diff mismatch or native shadow faults must survive restart as sticky local
memory.  This module seals the result-diff report together with the shadow-call
and dispatch-fence evidence that produced it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .dispatchfence import NativeDispatchFenceReport
from .ids import DOMAIN, sha256
from .nativeshadowcall import NativeShadowCallReport
from .resultdiff import NativeResultDiffReport

NATIVE_FAULT_SEAL_DOMAIN = DOMAIN + b":native-fault-seal-v1:"


class NativeFaultSealDecisionKind(str, Enum):
    ACCEPT_MATCH_SEALED_AS_NON_AUTHORITY = "accept_match_sealed_as_non_authority"
    ACCEPT_FAULT_SEALED_TO_FALLBACK = "accept_fault_sealed_to_fallback"
    HOLD_DIFF_WATCH = "hold_diff_watch"
    QUARANTINE_COMPONENT_NOT_READY = "quarantine_component_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeFaultSealCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    dispatch_fence_digest: bytes
    shadow_call_digest: bytes
    result_diff_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    native_fault_digest: bytes
    result_match: bool
    mismatch_fault: bool
    keep_python_fallback: bool
    native_authority_denied: bool
    preserve_dispatch_fence_memory: bool
    preserve_shadow_memory: bool
    preserve_result_diff_memory: bool
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
        return sha256(NATIVE_FAULT_SEAL_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"dispatch_fence": self.dispatch_fence_digest,
            b"shadow": self.shadow_call_digest,
            b"diff": self.result_diff_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"native_fault": self.native_fault_digest,
            b"match": 1 if self.result_match else 0,
            b"mismatch_fault": 1 if self.mismatch_fault else 0,
            b"keep_fallback": 1 if self.keep_python_fallback else 0,
            b"deny_native_authority": 1 if self.native_authority_denied else 0,
            b"preserve_fence": 1 if self.preserve_dispatch_fence_memory else 0,
            b"preserve_shadow": 1 if self.preserve_shadow_memory else 0,
            b"preserve_diff": 1 if self.preserve_result_diff_memory else 0,
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
class NativeFaultSealReport:
    decision_kind: NativeFaultSealDecisionKind
    accepted: bool
    fault_sealed: bool
    match_sealed: bool
    keep_python_fallback: bool
    native_authority_denied: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    dispatch_fence_digest: bytes
    shadow_call_digest: bytes
    result_diff_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    native_fault_digest: bytes
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_FAULT_SEAL_DOMAIN + b":report:" + bencode({
            b"decision": NativeFaultSealDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"fault_sealed": 1 if self.fault_sealed else 0,
            b"match_sealed": 1 if self.match_sealed else 0,
            b"keep_fallback": 1 if self.keep_python_fallback else 0,
            b"deny_native_authority": 1 if self.native_authority_denied else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"dispatch_fence": self.dispatch_fence_digest,
            b"shadow": self.shadow_call_digest,
            b"diff": self.result_diff_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"native_fault": self.native_fault_digest,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_fault_seal(
    dispatch_fence: NativeDispatchFenceReport,
    shadow_call: NativeShadowCallReport,
    result_diff: NativeResultDiffReport,
    capsule: NativeFaultSealCapsule,
    *,
    previous: NativeFaultSealCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeFaultSealReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(dispatch_fence.tombstone_memory and shadow_call.tombstone_memory and result_diff.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(dispatch_fence.fault_memory and shadow_call.fault_memory and result_diff.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeFaultSealDecisionKind, accepted: bool, fault_sealed: bool, match_sealed: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeFaultSealReport:
        return NativeFaultSealReport(kind, accepted, fault_sealed, match_sealed, capsule.keep_python_fallback, capsule.native_authority_denied, quarantine, watch, obligations, capsule.capsule_digest, dispatch_fence.report_digest, shadow_call.report_digest, result_diff.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, capsule.call_vector_digest, capsule.python_result_digest, capsule.native_result_digest, capsule.native_fault_digest, tombstone_memory, fault_memory or fault_sealed, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeFaultSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, False, ("native-fault-seal-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeFaultSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, False, ("native-fault-seal-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeFaultSealDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, False, ("native-fault-seal-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeFaultSealDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, False, ("native-fault-seal-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeFaultSealDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, False, ("native-fault-seal-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id, capsule.call_vector_digest, capsule.python_result_digest)):
        return report(NativeFaultSealDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, True, False, ("native-fault-seal-missing-boundary",))
    if not dispatch_fence.accepted or not shadow_call.accepted or not result_diff.accepted:
        if result_diff.mismatch_fault:
            # A mismatch report is allowed to be sealed even though the diff report is not accepted.
            pass
        else:
            return report(NativeFaultSealDecisionKind.QUARANTINE_COMPONENT_NOT_READY, False, False, False, True, True, ("native-fault-seal-component-not-ready",))
    if not capsule.keep_python_fallback or not capsule.native_authority_denied:
        return report(NativeFaultSealDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, False, ("fault-seal-must-keep-python-and-deny-native-authority",))
    if not all((capsule.preserve_dispatch_fence_memory, capsule.preserve_shadow_memory, capsule.preserve_result_diff_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, capsule.preserve_tombstone_memory, capsule.preserve_quarantine_memory, capsule.preserve_crash_memory)):
        return report(NativeFaultSealDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, False, ("native-fault-seal-memory-drop",))
    if capsule.dispatch_fence_digest != dispatch_fence.report_digest or capsule.shadow_call_digest != shadow_call.report_digest or capsule.result_diff_digest != result_diff.report_digest:
        return report(NativeFaultSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, False, ("native-fault-seal-component-digest-drift",))
    if capsule.artifact_digest != dispatch_fence.artifact_digest or capsule.artifact_digest != shadow_call.artifact_digest or capsule.artifact_digest != result_diff.artifact_digest or capsule.source_digest != dispatch_fence.source_digest or capsule.source_digest != shadow_call.source_digest or capsule.source_digest != result_diff.source_digest or capsule.fallback_digest != dispatch_fence.fallback_digest or capsule.fallback_digest != shadow_call.fallback_digest or capsule.fallback_digest != result_diff.fallback_digest or capsule.python_oracle_digest != dispatch_fence.python_oracle_digest or capsule.python_oracle_digest != shadow_call.python_oracle_digest or capsule.python_oracle_digest != result_diff.python_oracle_digest or capsule.call_vector_digest != dispatch_fence.call_vector_digest or capsule.call_vector_digest != shadow_call.call_vector_digest or capsule.call_vector_digest != result_diff.call_vector_digest or capsule.python_result_digest != dispatch_fence.python_result_digest or capsule.python_result_digest != shadow_call.python_result_digest or capsule.python_result_digest != result_diff.python_result_digest or capsule.native_result_digest != shadow_call.native_result_digest or capsule.native_result_digest != result_diff.native_result_digest:
        return report(NativeFaultSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, False, ("native-fault-seal-artifact-source-fallback-oracle-vector-result-drift",))
    if result_diff.watch:
        return report(NativeFaultSealDecisionKind.HOLD_DIFF_WATCH, True, False, False, False, True, ("result-diff-watch-carried", "keep-python-fallback"))
    if result_diff.mismatch_fault or capsule.mismatch_fault:
        return report(NativeFaultSealDecisionKind.ACCEPT_FAULT_SEALED_TO_FALLBACK, True, True, False, False, False, ("native-fault-sealed", "keep-python-fallback", "quarantine-native-artifact"))
    return report(NativeFaultSealDecisionKind.ACCEPT_MATCH_SEALED_AS_NON_AUTHORITY, True, False, True, False, False, ("native-match-sealed-as-shadow-only", "python-remains-authority"))
