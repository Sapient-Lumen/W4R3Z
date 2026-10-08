"""rev0090 relaunch gate.

A native handoff candidate cannot dispatch.  It must revalidate prior native
lanes through fresh digests before it can become a no-network relaunch plan.
The output is still not a load or send; it is a candidate plan with Python
fallback locked on.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativehandoff import NativeHandoffReport

RELAUNCH_GATE_DOMAIN = DOMAIN + b":native-relaunch-gate-v1:"


class NativeRelaunchGateDecisionKind(str, Enum):
    ACCEPT_NO_NETWORK_RELAUNCH_PLAN = "accept_no_network_relaunch_plan"
    HOLD_HANDOFF_NOT_CANDIDATE = "hold_handoff_not_candidate"
    HOLD_PRIOR_NATIVE_REVALIDATION_REQUIRED = "hold_prior_native_revalidation_required"
    HOLD_FALLBACK_ONLY_PROFILE = "hold_fallback_only_profile"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT = "quarantine_dispatch_or_load_attempt"
    QUARANTINE_PYTHON_FALLBACK_MISSING = "quarantine_python_fallback_missing"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeRelaunchGatePlan:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    handoff_digest: bytes
    parity_digest: bytes
    abi_digest: bytes
    fallback_seal_digest: bytes
    runtime_stamp_digest: bytes
    selection_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    prior_native_lanes_revalidated: bool
    fallback_only_profile: bool
    python_fallback_available: bool
    no_network: bool
    load_attempted: bool
    dispatch_attempted: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def plan_digest(self) -> bytes:
        return sha256(RELAUNCH_GATE_DOMAIN + b":plan:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"handoff": self.handoff_digest,
            b"parity": self.parity_digest,
            b"abi": self.abi_digest,
            b"fallback_seal": self.fallback_seal_digest,
            b"runtime": self.runtime_stamp_digest,
            b"selection": self.selection_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"prior_revalidated": 1 if self.prior_native_lanes_revalidated else 0,
            b"fallback_only_profile": 1 if self.fallback_only_profile else 0,
            b"fallback_available": 1 if self.python_fallback_available else 0,
            b"no_network": 1 if self.no_network else 0,
            b"load_attempted": 1 if self.load_attempted else 0,
            b"dispatch_attempted": 1 if self.dispatch_attempted else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeRelaunchGateReport:
    decision_kind: NativeRelaunchGateDecisionKind
    accepted: bool
    relaunch_plan_ready: bool
    native_load_allowed: bool
    dispatch_allowed: bool
    fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    plan_digest: bytes
    handoff_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    revalidated_digest_count: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(RELAUNCH_GATE_DOMAIN + b":report:" + bencode({
            b"decision": NativeRelaunchGateDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"ready": 1 if self.relaunch_plan_ready else 0,
            b"load_allowed": 1 if self.native_load_allowed else 0,
            b"dispatch_allowed": 1 if self.dispatch_allowed else 0,
            b"fallback": 1 if self.fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"plan": self.plan_digest,
            b"handoff": self.handoff_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"revalidated_count": self.revalidated_digest_count,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_relaunch_gate(
    handoff: NativeHandoffReport,
    plan: NativeRelaunchGatePlan,
    *,
    previous: NativeRelaunchGatePlan | None = None,
    prior_plan_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
    required_revalidation_digests: int = 5,
) -> NativeRelaunchGateReport:
    families = set(observed_families or (plan.family_id,))
    path_families = set(observed_path_families or (plan.path_family_id,))
    prior_digests = (plan.parity_digest, plan.abi_digest, plan.fallback_seal_digest, plan.runtime_stamp_digest, plan.selection_digest)
    revalidated_count = sum(1 for digest in prior_digests if bool(digest))

    def report(kind: NativeRelaunchGateDecisionKind, accepted: bool, ready: bool, load_allowed: bool, dispatch_allowed: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeRelaunchGateReport:
        return NativeRelaunchGateReport(kind, accepted, ready, load_allowed, dispatch_allowed, fallback, quarantine, watch, obligations, plan.plan_digest, handoff.report_digest, plan.artifact_digest, plan.source_digest, plan.fallback_digest, plan.python_oracle_digest, revalidated_count, len(families), len(path_families))

    if plan.plan_digest in prior_plan_digests:
        return report(NativeRelaunchGateDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, False, True, True, False, ("native-relaunch-gate-replay",))
    if previous is not None:
        if plan.sequence < previous.sequence:
            return report(NativeRelaunchGateDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, False, True, True, False, ("native-relaunch-gate-rollback",))
        if plan.sequence == previous.sequence and plan.plan_digest != previous.plan_digest:
            return report(NativeRelaunchGateDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, False, True, True, False, ("native-relaunch-gate-same-sequence-fork",))
        if plan.sequence > previous.sequence and plan.previous_digest != previous.plan_digest:
            return report(NativeRelaunchGateDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, False, True, True, False, ("native-relaunch-gate-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeRelaunchGateDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, False, True, True, False, ("native-relaunch-gate-low-diversity",))
    if not all((plan.component, plan.profile, plan.operation, plan.request_id)):
        return report(NativeRelaunchGateDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, False, True, True, False, ("native-relaunch-gate-missing-boundary",))
    if plan.handoff_digest != handoff.report_digest or plan.artifact_digest != handoff.artifact_digest or plan.source_digest != handoff.source_digest or plan.fallback_digest != handoff.fallback_digest or plan.python_oracle_digest != handoff.python_oracle_digest:
        return report(NativeRelaunchGateDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, True, True, False, ("native-relaunch-gate-component-digest-drift",))
    if plan.load_attempted or plan.dispatch_attempted or not plan.no_network:
        return report(NativeRelaunchGateDecisionKind.QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT, False, False, False, False, True, True, False, ("relaunch-gate-is-no-network-and-no-dispatch",))
    if not plan.python_fallback_available or not handoff.fallback_active:
        return report(NativeRelaunchGateDecisionKind.QUARANTINE_PYTHON_FALLBACK_MISSING, False, False, False, False, True, True, False, ("python-fallback-required-for-relaunch-plan",))
    if not handoff.accepted or not handoff.relaunch_candidate or handoff.quarantine:
        return report(NativeRelaunchGateDecisionKind.HOLD_HANDOFF_NOT_CANDIDATE, True, False, False, False, True, False, True, ("handoff-not-candidate", "fallback-active"))
    if plan.fallback_only_profile:
        return report(NativeRelaunchGateDecisionKind.HOLD_FALLBACK_ONLY_PROFILE, True, False, False, False, True, False, True, ("profile-forces-python-fallback",))
    if not plan.prior_native_lanes_revalidated or revalidated_count < required_revalidation_digests:
        return report(NativeRelaunchGateDecisionKind.HOLD_PRIOR_NATIVE_REVALIDATION_REQUIRED, True, False, False, False, True, False, True, ("prior-native-lanes-must-revalidate",))
    return report(NativeRelaunchGateDecisionKind.ACCEPT_NO_NETWORK_RELAUNCH_PLAN, True, True, False, False, True, False, False, ("no-network-relaunch-plan", "load-and-dispatch-still-forbidden"))
