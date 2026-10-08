"""rev0094 native shadow-call boundary.

rev0093 deliberately fenced native dispatch even after a call canary carried a
Python-oracle result.  This module adds the next *safe* seam: a shadow-call
observation may carry a native result digest, but only as evidence.  It is not
selected, not authoritative, and not allowed to replace Python execution.

The risk class is that a successful shadow call looks like permission to route
future DHT work through C.  This module makes the opposite rule executable:
shadow execution is only an observation that must preserve Python fallback,
prior dispatch-fence evidence, and native fault memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .dispatchfence import NativeDispatchFenceReport
from .ids import DOMAIN, sha256

NATIVE_SHADOW_CALL_DOMAIN = DOMAIN + b":native-shadow-call-v1:"


class NativeShadowCallDecisionKind(str, Enum):
    ACCEPT_SHADOW_OBSERVATION = "accept_shadow_observation"
    HOLD_DISPATCH_FENCE_NOT_READY = "hold_dispatch_fence_not_ready"
    QUARANTINE_NATIVE_AUTHORITY_ATTEMPT = "quarantine_native_authority_attempt"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeShadowCallCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    dispatch_fence_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    native_fault_digest: bytes
    shadow_mode: bool
    native_result_observed: bool
    native_result_selected: bool
    native_authority_claimed: bool
    python_fallback_active: bool
    preserve_dispatch_fence_memory: bool
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
        return sha256(NATIVE_SHADOW_CALL_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"dispatch_fence": self.dispatch_fence_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"native_fault": self.native_fault_digest,
            b"shadow": 1 if self.shadow_mode else 0,
            b"native_observed": 1 if self.native_result_observed else 0,
            b"native_selected": 1 if self.native_result_selected else 0,
            b"native_authority": 1 if self.native_authority_claimed else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"preserve_fence": 1 if self.preserve_dispatch_fence_memory else 0,
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
class NativeShadowCallReport:
    decision_kind: NativeShadowCallDecisionKind
    accepted: bool
    shadow_observation: bool
    native_result_authoritative: bool
    python_fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    dispatch_fence_digest: bytes
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
        return sha256(NATIVE_SHADOW_CALL_DOMAIN + b":report:" + bencode({
            b"decision": NativeShadowCallDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"shadow": 1 if self.shadow_observation else 0,
            b"native_authority": 1 if self.native_result_authoritative else 0,
            b"fallback": 1 if self.python_fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"dispatch_fence": self.dispatch_fence_digest,
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


def assess_native_shadow_call(
    dispatch_fence: NativeDispatchFenceReport,
    capsule: NativeShadowCallCapsule,
    *,
    previous: NativeShadowCallCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeShadowCallReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(dispatch_fence.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(dispatch_fence.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeShadowCallDecisionKind, accepted: bool, shadow: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeShadowCallReport:
        return NativeShadowCallReport(kind, accepted, shadow, False, fallback, quarantine, watch, obligations, capsule.capsule_digest, dispatch_fence.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, capsule.call_vector_digest, capsule.python_result_digest, capsule.native_result_digest, capsule.native_fault_digest, tombstone_memory, fault_memory, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeShadowCallDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("native-shadow-call-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeShadowCallDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("native-shadow-call-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeShadowCallDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, True, False, ("native-shadow-call-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeShadowCallDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, True, False, ("native-shadow-call-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeShadowCallDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, True, False, ("native-shadow-call-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id, capsule.call_vector_digest, capsule.python_result_digest)):
        return report(NativeShadowCallDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, True, False, ("native-shadow-call-missing-boundary",))
    if not dispatch_fence.accepted or not dispatch_fence.dispatch_fenced:
        return report(NativeShadowCallDecisionKind.HOLD_DISPATCH_FENCE_NOT_READY, False, False, True, dispatch_fence.quarantine, True, ("dispatch-fence-not-ready",))
    if not capsule.shadow_mode or capsule.native_result_selected or capsule.native_authority_claimed:
        return report(NativeShadowCallDecisionKind.QUARANTINE_NATIVE_AUTHORITY_ATTEMPT, False, False, capsule.python_fallback_active, True, False, ("shadow-call-must-not-claim-native-authority",))
    if not capsule.python_fallback_active:
        return report(NativeShadowCallDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, False, ("python-fallback-must-remain-active",))
    if not all((capsule.preserve_dispatch_fence_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, capsule.preserve_tombstone_memory, capsule.preserve_quarantine_memory, capsule.preserve_crash_memory)):
        return report(NativeShadowCallDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, False, ("native-shadow-call-memory-drop",))
    if capsule.dispatch_fence_digest != dispatch_fence.report_digest:
        return report(NativeShadowCallDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-shadow-call-dispatch-fence-digest-drift",))
    if capsule.artifact_digest != dispatch_fence.artifact_digest or capsule.source_digest != dispatch_fence.source_digest or capsule.fallback_digest != dispatch_fence.fallback_digest or capsule.python_oracle_digest != dispatch_fence.python_oracle_digest or capsule.call_vector_digest != dispatch_fence.call_vector_digest or capsule.python_result_digest != dispatch_fence.python_result_digest:
        return report(NativeShadowCallDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-shadow-call-artifact-source-fallback-oracle-vector-or-result-drift",))
    if capsule.native_result_observed and not capsule.native_result_digest:
        return report(NativeShadowCallDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-shadow-call-missing-native-result-digest",))
    return report(NativeShadowCallDecisionKind.ACCEPT_SHADOW_OBSERVATION, True, True, True, False, False, ("native-result-is-shadow-only", "python-result-remains-authoritative", "dispatch-still-not-granted"))
