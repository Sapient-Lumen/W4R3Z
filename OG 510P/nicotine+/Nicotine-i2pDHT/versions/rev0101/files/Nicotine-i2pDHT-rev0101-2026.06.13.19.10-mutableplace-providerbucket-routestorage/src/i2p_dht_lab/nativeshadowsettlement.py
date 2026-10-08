"""rev0095 native shadow-settlement boundary.

rev0094 allowed a native result to be observed only in shadow mode and then
compared against the Python oracle.  This module makes the next seam explicit:
a matching shadow result may be *settled as evidence*, but it still does not
become native authority or native dispatch permission.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_SHADOW_SETTLEMENT_DOMAIN = DOMAIN + b":native-shadow-settlement-v1:"


class NativeShadowSettlementDecisionKind(str, Enum):
    ACCEPT_SHADOW_SETTLED_EVIDENCE = "accept_shadow_settled_evidence"
    HOLD_SHADOW_OR_DIFF_NOT_READY = "hold_shadow_or_diff_not_ready"
    HOLD_FAULT_SEAL_NOT_READY = "hold_fault_seal_not_ready"
    QUARANTINE_RESULT_MISMATCH_OR_FAULT = "quarantine_result_mismatch_or_fault"
    QUARANTINE_NATIVE_AUTHORITY_ATTEMPT = "quarantine_native_authority_attempt"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeShadowSettlementCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    shadow_call_digest: bytes
    result_diff_digest: bytes
    fault_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    native_fault_digest: bytes
    result_match: bool
    fault_sealed: bool
    match_sealed: bool
    keep_python_fallback: bool
    native_authority_denied: bool
    native_authority_claimed: bool
    shadow_settlement_only: bool
    preserve_shadow_memory: bool
    preserve_result_diff_memory: bool
    preserve_fault_seal_memory: bool
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
        return sha256(NATIVE_SHADOW_SETTLEMENT_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"shadow": self.shadow_call_digest,
            b"diff": self.result_diff_digest,
            b"fault_seal": self.fault_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"native_fault": self.native_fault_digest,
            b"result_match": 1 if self.result_match else 0,
            b"fault_sealed": 1 if self.fault_sealed else 0,
            b"match_sealed": 1 if self.match_sealed else 0,
            b"keep_fallback": 1 if self.keep_python_fallback else 0,
            b"deny_native_authority": 1 if self.native_authority_denied else 0,
            b"native_authority_claimed": 1 if self.native_authority_claimed else 0,
            b"settlement_only": 1 if self.shadow_settlement_only else 0,
            b"preserve_shadow": 1 if self.preserve_shadow_memory else 0,
            b"preserve_diff": 1 if self.preserve_result_diff_memory else 0,
            b"preserve_fault_seal": 1 if self.preserve_fault_seal_memory else 0,
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
class NativeShadowSettlementReport:
    decision_kind: NativeShadowSettlementDecisionKind
    accepted: bool
    shadow_settled: bool
    native_call_permission: bool
    native_result_authoritative: bool
    python_fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    shadow_call_digest: bytes
    result_diff_digest: bytes
    fault_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    native_fault_digest: bytes
    result_match: bool
    fault_sealed: bool
    match_sealed: bool
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_SHADOW_SETTLEMENT_DOMAIN + b":report:" + bencode({
            b"decision": NativeShadowSettlementDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"settled": 1 if self.shadow_settled else 0,
            b"native_call_permission": 1 if self.native_call_permission else 0,
            b"native_authority": 1 if self.native_result_authoritative else 0,
            b"fallback": 1 if self.python_fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"shadow": self.shadow_call_digest,
            b"diff": self.result_diff_digest,
            b"fault_seal": self.fault_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"native_fault": self.native_fault_digest,
            b"match": 1 if self.result_match else 0,
            b"fault_sealed": 1 if self.fault_sealed else 0,
            b"match_sealed": 1 if self.match_sealed else 0,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def _digest(obj: Any, name: str) -> bytes:
    return getattr(obj, name)


def assess_native_shadow_settlement(
    shadow_call: Any,
    result_diff: Any,
    fault_seal: Any,
    capsule: NativeShadowSettlementCapsule,
    *,
    previous: NativeShadowSettlementCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeShadowSettlementReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(
        getattr(shadow_call, "tombstone_memory", False)
        and getattr(result_diff, "tombstone_memory", False)
        and getattr(fault_seal, "tombstone_memory", False)
        and capsule.preserve_tombstone_memory
    )
    fault_memory = bool(
        getattr(shadow_call, "fault_memory", False)
        and getattr(result_diff, "fault_memory", False)
        and getattr(fault_seal, "fault_memory", False)
        and capsule.preserve_quarantine_memory
        and capsule.preserve_crash_memory
    )

    def report(kind: NativeShadowSettlementDecisionKind, accepted: bool, settled: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeShadowSettlementReport:
        return NativeShadowSettlementReport(
            kind, accepted, settled, False, False, capsule.keep_python_fallback, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.shadow_call_digest, capsule.result_diff_digest, capsule.fault_seal_digest,
            capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest,
            capsule.call_vector_digest, capsule.python_result_digest, capsule.native_result_digest,
            capsule.native_fault_digest, capsule.result_match, capsule.fault_sealed, capsule.match_sealed,
            tombstone_memory, fault_memory or capsule.fault_sealed, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeShadowSettlementDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-shadow-settlement-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeShadowSettlementDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-shadow-settlement-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeShadowSettlementDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-shadow-settlement-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeShadowSettlementDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-shadow-settlement-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeShadowSettlementDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-shadow-settlement-low-diversity",))
    if capsule.shadow_call_digest != _digest(shadow_call, "report_digest") or capsule.result_diff_digest != _digest(result_diff, "report_digest") or capsule.fault_seal_digest != _digest(fault_seal, "report_digest"):
        return report(NativeShadowSettlementDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-shadow-settlement-component-digest-drift",))
    if capsule.artifact_digest != getattr(result_diff, "artifact_digest", capsule.artifact_digest) or capsule.source_digest != getattr(result_diff, "source_digest", capsule.source_digest):
        return report(NativeShadowSettlementDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-shadow-settlement-artifact-drift",))
    if not (getattr(shadow_call, "accepted", False) and getattr(shadow_call, "shadow_observation", False) and getattr(result_diff, "accepted", False)):
        return report(NativeShadowSettlementDecisionKind.HOLD_SHADOW_OR_DIFF_NOT_READY, False, False, False, True, ("shadow-or-diff-not-ready",))
    if not getattr(fault_seal, "accepted", False):
        return report(NativeShadowSettlementDecisionKind.HOLD_FAULT_SEAL_NOT_READY, False, False, False, True, ("fault-seal-not-ready",))
    if not capsule.result_match or getattr(result_diff, "mismatch_fault", False) or (capsule.fault_sealed and not capsule.match_sealed):
        return report(NativeShadowSettlementDecisionKind.QUARANTINE_RESULT_MISMATCH_OR_FAULT, False, False, True, False, ("native-shadow-settlement-mismatch-or-fault",))
    if capsule.native_authority_claimed or not capsule.native_authority_denied or not capsule.shadow_settlement_only:
        return report(NativeShadowSettlementDecisionKind.QUARANTINE_NATIVE_AUTHORITY_ATTEMPT, False, False, True, False, ("native-shadow-settlement-must-deny-native-authority",))
    if not all((capsule.keep_python_fallback, capsule.preserve_shadow_memory, capsule.preserve_result_diff_memory, capsule.preserve_fault_seal_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, tombstone_memory)):
        return report(NativeShadowSettlementDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-shadow-settlement-memory-drop",))
    return report(NativeShadowSettlementDecisionKind.ACCEPT_SHADOW_SETTLED_EVIDENCE, True, True, False, False, ("native-shadow-settled-as-evidence-only", "python-remains-authoritative"))
