"""rev0099 substrate re-entry gate after closing the native branch.

rev0098 closed the current GCC/native branch as shadow-only.  This module joins
that close-out with a Python-owned DHT record-plane oracle before the cube is
allowed to treat itself as back on the substrate-DHT design path.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

SUBSTRATE_REENTRY_DOMAIN = DOMAIN + b":substrate-reentry-v1:"


class SubstrateReentryDecisionKind(str, Enum):
    ACCEPT_RETURN_TO_DHT_SUBSTRATE = "accept_return_to_dht_substrate"
    HOLD_COMPONENT_NOT_READY = "hold_component_not_ready"
    QUARANTINE_NATIVE_PERMISSION_LEAK = "quarantine_native_permission_leak"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class SubstrateReentryCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    native_branch_close_digest: bytes
    record_plane_oracle_digest: bytes
    native_fold_spine_digest: bytes
    substrate_scope: str
    branch_state: str
    python_protocol_truth: bool
    native_branch_closed_shadow_only: bool
    native_permissions_closed: bool
    return_to_record_plane: bool
    return_to_mutable_plane: bool
    return_to_provider_plane: bool
    return_to_routing_plane: bool
    require_new_native_branch_for_promotion: bool
    preserve_native_branch_close_memory: bool
    preserve_native_fold_spine_memory: bool
    preserve_record_plane_oracle_memory: bool
    preserve_mutable_head_memory: bool
    preserve_provider_false_memory: bool
    preserve_witness_memory: bool
    preserve_tombstone_memory: bool
    preserve_garden_refusal_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(SUBSTRATE_REENTRY_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"branch_close": self.native_branch_close_digest,
            b"record_oracle": self.record_plane_oracle_digest,
            b"spine": self.native_fold_spine_digest,
            b"scope": self.substrate_scope,
            b"branch_state": self.branch_state,
            b"python_truth": 1 if self.python_protocol_truth else 0,
            b"shadow_only": 1 if self.native_branch_closed_shadow_only else 0,
            b"native_permissions_closed": 1 if self.native_permissions_closed else 0,
            b"record_plane": 1 if self.return_to_record_plane else 0,
            b"mutable_plane": 1 if self.return_to_mutable_plane else 0,
            b"provider_plane": 1 if self.return_to_provider_plane else 0,
            b"routing_plane": 1 if self.return_to_routing_plane else 0,
            b"new_native_branch": 1 if self.require_new_native_branch_for_promotion else 0,
            b"preserve_branch": 1 if self.preserve_native_branch_close_memory else 0,
            b"preserve_spine": 1 if self.preserve_native_fold_spine_memory else 0,
            b"preserve_record": 1 if self.preserve_record_plane_oracle_memory else 0,
            b"preserve_mutable": 1 if self.preserve_mutable_head_memory else 0,
            b"preserve_provider_false": 1 if self.preserve_provider_false_memory else 0,
            b"preserve_witness": 1 if self.preserve_witness_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_refusal": 1 if self.preserve_garden_refusal_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class SubstrateReentryReport:
    decision_kind: SubstrateReentryDecisionKind
    accepted: bool
    substrate_reentered: bool
    python_protocol_truth: bool
    native_permission_leak: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    native_branch_close_digest: bytes
    record_plane_oracle_digest: bytes
    native_fold_spine_digest: bytes
    substrate_scope: str
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(SUBSTRATE_REENTRY_DOMAIN + b":report:" + bencode({
            b"decision": self.decision_kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"reentered": 1 if self.substrate_reentered else 0,
            b"python_truth": 1 if self.python_protocol_truth else 0,
            b"native_leak": 1 if self.native_permission_leak else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"branch_close": self.native_branch_close_digest,
            b"record_oracle": self.record_plane_oracle_digest,
            b"spine": self.native_fold_spine_digest,
            b"scope": self.substrate_scope,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_substrate_reentry(
    native_branch_close: object,
    record_plane_oracle: object,
    native_fold_spine: object,
    capsule: SubstrateReentryCapsule,
    *,
    previous: SubstrateReentryCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> SubstrateReentryReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: SubstrateReentryDecisionKind, accepted: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> SubstrateReentryReport:
        leak = not capsule.native_permissions_closed or not capsule.native_branch_closed_shadow_only
        return SubstrateReentryReport(
            kind, accepted, accepted and capsule.substrate_scope == "generic-i2p-dht-substrate", accepted and capsule.python_protocol_truth,
            leak, quarantine, watch, obligations, capsule.capsule_digest, capsule.native_branch_close_digest,
            capsule.record_plane_oracle_digest, capsule.native_fold_spine_digest, capsule.substrate_scope, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(SubstrateReentryDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("substrate-reentry-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(SubstrateReentryDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("substrate-reentry-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(SubstrateReentryDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, False, ("substrate-reentry-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(SubstrateReentryDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, False, ("substrate-reentry-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(SubstrateReentryDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, False, ("substrate-reentry-low-diversity",))
    if not getattr(native_branch_close, "accepted", False) or not getattr(native_branch_close, "branch_closed", False):
        return report(SubstrateReentryDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("native-branch-close-not-ready",))
    if getattr(native_branch_close, "native_permission", True):
        return report(SubstrateReentryDecisionKind.QUARANTINE_NATIVE_PERMISSION_LEAK, False, True, False, ("native-branch-close-permission-leak",))
    if not getattr(record_plane_oracle, "accepted", False) or not getattr(record_plane_oracle, "python_record_truth", False):
        return report(SubstrateReentryDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("record-plane-oracle-not-ready",))
    if getattr(record_plane_oracle, "native_record_permission", True):
        return report(SubstrateReentryDecisionKind.QUARANTINE_NATIVE_PERMISSION_LEAK, False, True, False, ("record-plane-native-permission-leak",))
    if getattr(native_fold_spine, "status", "fail") != "pass":
        return report(SubstrateReentryDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("native-fold-spine-not-ready",))
    if capsule.native_branch_close_digest != getattr(native_branch_close, "report_digest", b"") or capsule.record_plane_oracle_digest != getattr(record_plane_oracle, "report_digest", b"") or capsule.native_fold_spine_digest != getattr(native_fold_spine, "report_digest", b""):
        return report(SubstrateReentryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, ("substrate-reentry-component-digest-drift",))
    if capsule.substrate_scope != "generic-i2p-dht-substrate" or capsule.branch_state != "native-shadow-branch-closed":
        return report(SubstrateReentryDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, ("substrate-reentry-boundary-drift",))
    if not all((
        capsule.python_protocol_truth,
        capsule.native_branch_closed_shadow_only,
        capsule.native_permissions_closed,
        capsule.return_to_record_plane,
        capsule.return_to_mutable_plane,
        capsule.return_to_provider_plane,
        capsule.return_to_routing_plane,
        capsule.require_new_native_branch_for_promotion,
    )):
        return report(SubstrateReentryDecisionKind.QUARANTINE_NATIVE_PERMISSION_LEAK, False, True, False, ("substrate-reentry-permission-or-plane-drop",))
    if not all((
        capsule.preserve_native_branch_close_memory,
        capsule.preserve_native_fold_spine_memory,
        capsule.preserve_record_plane_oracle_memory,
        capsule.preserve_mutable_head_memory,
        capsule.preserve_provider_false_memory,
        capsule.preserve_witness_memory,
        capsule.preserve_tombstone_memory,
        capsule.preserve_garden_refusal_memory,
    )):
        return report(SubstrateReentryDecisionKind.QUARANTINE_MEMORY_DROP, False, True, False, ("substrate-reentry-memory-drop",))
    return report(SubstrateReentryDecisionKind.ACCEPT_RETURN_TO_DHT_SUBSTRATE, True, False, False, ("resume-generic-dht-substrate-design", "native-branch-remains-closed"))
