"""rev0098 native branch-close join.

This is not a production native promotion process.  It is a local close-out seam
for the current GCC/native exploration: archived review plus shadow-only policy
plus replay memory may be marked closed, and the closed state still routes to
Python fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_BRANCH_CLOSE_DOMAIN = DOMAIN + b":native-branch-close-v1:"


class NativeBranchCloseDecisionKind(str, Enum):
    ACCEPT_BRANCH_CLOSED_SHADOW_ONLY = "accept_branch_closed_shadow_only"
    HOLD_COMPONENT_NOT_READY = "hold_component_not_ready"
    QUARANTINE_NATIVE_PERMISSION_ATTEMPT = "quarantine_native_permission_attempt"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeBranchCloseCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    archive_replay_digest: bytes
    promotion_review_digest: bytes
    promote_archive_digest: bytes
    promotion_policy_digest: bytes
    native_fold_spine_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    branch_state: str
    python_fallback_authoritative: bool
    native_load_allowed: bool
    native_dispatch_allowed: bool
    native_result_authority_allowed: bool
    future_promotion_requires_new_branch: bool
    preserve_archive_replay_memory: bool
    preserve_promotion_review_memory: bool
    preserve_promote_archive_memory: bool
    preserve_policy_memory: bool
    preserve_fold_spine_memory: bool
    preserve_python_route_memory: bool
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
        return sha256(NATIVE_BRANCH_CLOSE_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"archive_replay": self.archive_replay_digest,
            b"review": self.promotion_review_digest,
            b"promote_archive": self.promote_archive_digest,
            b"policy": self.promotion_policy_digest,
            b"spine": self.native_fold_spine_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"state": self.branch_state,
            b"fallback_authoritative": 1 if self.python_fallback_authoritative else 0,
            b"native_load": 1 if self.native_load_allowed else 0,
            b"native_dispatch": 1 if self.native_dispatch_allowed else 0,
            b"native_authority": 1 if self.native_result_authority_allowed else 0,
            b"new_branch_required": 1 if self.future_promotion_requires_new_branch else 0,
            b"preserve_replay": 1 if self.preserve_archive_replay_memory else 0,
            b"preserve_review": 1 if self.preserve_promotion_review_memory else 0,
            b"preserve_archive": 1 if self.preserve_promote_archive_memory else 0,
            b"preserve_policy": 1 if self.preserve_policy_memory else 0,
            b"preserve_spine": 1 if self.preserve_fold_spine_memory else 0,
            b"preserve_route": 1 if self.preserve_python_route_memory else 0,
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
class NativeBranchCloseReport:
    decision_kind: NativeBranchCloseDecisionKind
    accepted: bool
    branch_closed: bool
    shadow_only: bool
    python_fallback_authoritative: bool
    native_permission: bool
    future_promotion_requires_new_branch: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    archive_replay_digest: bytes
    promotion_review_digest: bytes
    promote_archive_digest: bytes
    promotion_policy_digest: bytes
    native_fold_spine_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_BRANCH_CLOSE_DOMAIN + b":report:" + bencode({
            b"decision": NativeBranchCloseDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"closed": 1 if self.branch_closed else 0,
            b"shadow_only": 1 if self.shadow_only else 0,
            b"fallback_authoritative": 1 if self.python_fallback_authoritative else 0,
            b"native_permission": 1 if self.native_permission else 0,
            b"new_branch_required": 1 if self.future_promotion_requires_new_branch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"archive_replay": self.archive_replay_digest,
            b"review": self.promotion_review_digest,
            b"promote_archive": self.promote_archive_digest,
            b"policy": self.promotion_policy_digest,
            b"spine": self.native_fold_spine_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_branch_close(
    archive_replay: Any,
    promotion_review: Any,
    promote_archive: Any,
    promotion_policy: Any,
    native_fold_spine: Any,
    capsule: NativeBranchCloseCapsule,
    *,
    previous: NativeBranchCloseCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeBranchCloseReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: NativeBranchCloseDecisionKind, accepted: bool, closed: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeBranchCloseReport:
        return NativeBranchCloseReport(
            kind, accepted, closed, closed and capsule.branch_state == "shadow_only_closed",
            closed and capsule.python_fallback_authoritative, False,
            closed and capsule.future_promotion_requires_new_branch, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.archive_replay_digest, capsule.promotion_review_digest,
            capsule.promote_archive_digest, capsule.promotion_policy_digest, capsule.native_fold_spine_digest,
            capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest,
            len(families), len(path_families),
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeBranchCloseDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-branch-close-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeBranchCloseDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-branch-close-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeBranchCloseDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-branch-close-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeBranchCloseDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-branch-close-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeBranchCloseDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-branch-close-low-diversity",))
    expected = (
        (capsule.archive_replay_digest, getattr(archive_replay, "report_digest", b""), "archive-replay"),
        (capsule.promotion_review_digest, getattr(promotion_review, "report_digest", b""), "promotion-review"),
        (capsule.promote_archive_digest, getattr(promote_archive, "report_digest", b""), "promote-archive"),
        (capsule.promotion_policy_digest, getattr(promotion_policy, "report_digest", b""), "promotion-policy"),
        (capsule.native_fold_spine_digest, getattr(native_fold_spine, "report_digest", b""), "native-fold-spine"),
    )
    for left, right, label in expected:
        if left != right:
            return report(NativeBranchCloseDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, (f"native-branch-close-{label}-digest-drift",))
    readiness = (
        getattr(archive_replay, "accepted", False),
        getattr(promotion_review, "accepted", False),
        getattr(promote_archive, "accepted", False),
        getattr(promotion_policy, "accepted", False),
        getattr(native_fold_spine, "status", "") == "pass",
    )
    if not all(readiness):
        return report(NativeBranchCloseDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, False, True, ("native-branch-close-component-not-ready",))
    native_attempt = (
        capsule.native_load_allowed,
        capsule.native_dispatch_allowed,
        capsule.native_result_authority_allowed,
        getattr(archive_replay, "native_permission", False),
        getattr(promotion_review, "native_call_permission", False),
        getattr(promotion_review, "native_result_authority", False),
        getattr(promote_archive, "native_call_permission", False),
        getattr(promote_archive, "native_result_authority", False),
        getattr(promotion_policy, "native_load_permission", False),
        getattr(promotion_policy, "native_dispatch_permission", False),
        getattr(promotion_policy, "native_result_authority", False),
    )
    if any(native_attempt) or capsule.branch_state != "shadow_only_closed" or not capsule.python_fallback_authoritative or not capsule.future_promotion_requires_new_branch:
        return report(NativeBranchCloseDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-branch-close-native-permission-attempt",))
    required_memory = (
        capsule.preserve_archive_replay_memory,
        capsule.preserve_promotion_review_memory,
        capsule.preserve_promote_archive_memory,
        capsule.preserve_policy_memory,
        capsule.preserve_fold_spine_memory,
        capsule.preserve_python_route_memory,
        capsule.preserve_python_oracle_memory,
        capsule.preserve_fallback_memory,
        capsule.preserve_tombstone_memory,
        capsule.preserve_quarantine_memory,
        capsule.preserve_crash_memory,
    )
    if not all(required_memory):
        return report(NativeBranchCloseDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-branch-close-required-memory-drop",))
    return report(NativeBranchCloseDecisionKind.ACCEPT_BRANCH_CLOSED_SHADOW_ONLY, True, True, False, False, ("native-branch-close-shadow-only", "native-branch-close-python-fallback-authoritative", "native-branch-close-new-branch-required-for-promotion"))
