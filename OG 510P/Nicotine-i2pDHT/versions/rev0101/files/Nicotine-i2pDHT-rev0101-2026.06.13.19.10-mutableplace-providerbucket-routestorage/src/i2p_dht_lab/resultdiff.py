"""rev0094 native result-diff boundary.

A native shadow result is useful only if it is compared against the Python oracle
and stored as evidence.  Equal results are still not authority.  Unequal results
become sticky native-fault pressure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeshadowcall import NativeShadowCallReport

NATIVE_RESULT_DIFF_DOMAIN = DOMAIN + b":native-result-diff-v1:"


class NativeResultDiffDecisionKind(str, Enum):
    ACCEPT_MATCH_AS_SHADOW_EVIDENCE = "accept_match_as_shadow_evidence"
    HOLD_NO_NATIVE_RESULT = "hold_no_native_result"
    WATCH_NO_NATIVE_RESULT_OBSERVED = "watch_no_native_result_observed"
    QUARANTINE_RESULT_MISMATCH = "quarantine_result_mismatch"
    QUARANTINE_SHADOW_NOT_READY = "quarantine_shadow_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeResultDiffCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    shadow_call_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    native_fault_digest: bytes
    native_result_present: bool
    results_match: bool
    python_result_authoritative: bool
    preserve_shadow_memory: bool
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
        return sha256(NATIVE_RESULT_DIFF_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"shadow": self.shadow_call_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"native_fault": self.native_fault_digest,
            b"native_present": 1 if self.native_result_present else 0,
            b"match": 1 if self.results_match else 0,
            b"python_authority": 1 if self.python_result_authoritative else 0,
            b"preserve_shadow": 1 if self.preserve_shadow_memory else 0,
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
class NativeResultDiffReport:
    decision_kind: NativeResultDiffDecisionKind
    accepted: bool
    result_match: bool
    mismatch_fault: bool
    python_result_authoritative: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    shadow_call_digest: bytes
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
        return sha256(NATIVE_RESULT_DIFF_DOMAIN + b":report:" + bencode({
            b"decision": NativeResultDiffDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"match": 1 if self.result_match else 0,
            b"mismatch_fault": 1 if self.mismatch_fault else 0,
            b"python_authority": 1 if self.python_result_authoritative else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"shadow": self.shadow_call_digest,
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


def assess_native_result_diff(
    shadow_call: NativeShadowCallReport,
    capsule: NativeResultDiffCapsule,
    *,
    previous: NativeResultDiffCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeResultDiffReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(shadow_call.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(shadow_call.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeResultDiffDecisionKind, accepted: bool, match: bool, mismatch_fault: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeResultDiffReport:
        return NativeResultDiffReport(kind, accepted, match, mismatch_fault, capsule.python_result_authoritative, quarantine, watch, obligations, capsule.capsule_digest, shadow_call.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, capsule.call_vector_digest, capsule.python_result_digest, capsule.native_result_digest, capsule.native_fault_digest, tombstone_memory, fault_memory or mismatch_fault, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeResultDiffDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, False, ("native-result-diff-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeResultDiffDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, False, ("native-result-diff-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeResultDiffDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, False, ("native-result-diff-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeResultDiffDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, False, ("native-result-diff-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeResultDiffDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, False, ("native-result-diff-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id, capsule.call_vector_digest, capsule.python_result_digest)):
        return report(NativeResultDiffDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, True, False, ("native-result-diff-missing-boundary",))
    if not shadow_call.accepted or not shadow_call.shadow_observation:
        return report(NativeResultDiffDecisionKind.QUARANTINE_SHADOW_NOT_READY, False, False, False, True, True, ("shadow-call-not-ready",))
    if not capsule.python_result_authoritative:
        return report(NativeResultDiffDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, False, ("python-result-must-remain-authoritative",))
    if not all((capsule.preserve_shadow_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, capsule.preserve_tombstone_memory, capsule.preserve_quarantine_memory, capsule.preserve_crash_memory)):
        return report(NativeResultDiffDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, False, ("native-result-diff-memory-drop",))
    if capsule.shadow_call_digest != shadow_call.report_digest:
        return report(NativeResultDiffDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, False, ("native-result-diff-shadow-digest-drift",))
    if capsule.artifact_digest != shadow_call.artifact_digest or capsule.source_digest != shadow_call.source_digest or capsule.fallback_digest != shadow_call.fallback_digest or capsule.python_oracle_digest != shadow_call.python_oracle_digest or capsule.call_vector_digest != shadow_call.call_vector_digest or capsule.python_result_digest != shadow_call.python_result_digest or capsule.native_result_digest != shadow_call.native_result_digest:
        return report(NativeResultDiffDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, False, ("native-result-diff-input-digest-drift",))
    if not capsule.native_result_present:
        return report(NativeResultDiffDecisionKind.WATCH_NO_NATIVE_RESULT_OBSERVED, True, False, False, False, True, ("no-native-result-observed", "remain-on-python"))
    if not capsule.native_result_digest:
        return report(NativeResultDiffDecisionKind.HOLD_NO_NATIVE_RESULT, False, False, False, False, True, ("native-result-digest-missing",))
    if not capsule.results_match or capsule.native_result_digest != capsule.python_result_digest:
        return report(NativeResultDiffDecisionKind.QUARANTINE_RESULT_MISMATCH, False, False, True, True, False, ("native-result-mismatch", "quarantine-native-artifact", "keep-python-fallback"))
    return report(NativeResultDiffDecisionKind.ACCEPT_MATCH_AS_SHADOW_EVIDENCE, True, True, False, False, False, ("native-match-is-shadow-evidence", "python-result-remains-authoritative"))
