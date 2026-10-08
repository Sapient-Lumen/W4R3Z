"""rev0098 native promotion policy boundary.

This module encodes local policy for the native/GCC branch: repeated matching
shadow results may remain observable, but the admitted policy for this cube is
shadow-only with Python fallback authoritative.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_PROMOTION_POLICY_DOMAIN = DOMAIN + b":native-promotion-policy-v1:"
FORBIDDEN_NATIVE_SURFACES = ("parser", "crypto", "transport", "persistence", "policy", "moderation", "mutable_truth", "native_dispatch", "native_result_authority")


class NativePromotionPolicyDecisionKind(str, Enum):
    ACCEPT_SHADOW_ONLY_POLICY = "accept_shadow_only_policy"
    HOLD_ARCHIVE_NOT_READY = "hold_archive_not_ready"
    QUARANTINE_NATIVE_PERMISSION_ATTEMPT = "quarantine_native_permission_attempt"
    QUARANTINE_FORBIDDEN_SURFACE = "quarantine_forbidden_surface"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativePromotionPolicyCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    promote_archive_digest: bytes
    promotion_review_digest: bytes
    policy_scope: str
    policy_mode: str
    allowed_shadow_observation: bool
    require_python_fallback: bool
    deny_native_load: bool
    deny_native_dispatch: bool
    deny_native_result_authority: bool
    deny_native_parser: bool
    deny_native_crypto: bool
    deny_native_transport: bool
    deny_native_persistence: bool
    deny_native_policy: bool
    preserve_promote_archive_memory: bool
    preserve_review_memory: bool
    preserve_python_route_memory: bool
    preserve_python_oracle_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    policy_reason_digest: bytes
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTION_POLICY_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"archive": self.promote_archive_digest,
            b"review": self.promotion_review_digest,
            b"scope": self.policy_scope,
            b"mode": self.policy_mode,
            b"shadow_observation": 1 if self.allowed_shadow_observation else 0,
            b"fallback_required": 1 if self.require_python_fallback else 0,
            b"deny_load": 1 if self.deny_native_load else 0,
            b"deny_dispatch": 1 if self.deny_native_dispatch else 0,
            b"deny_authority": 1 if self.deny_native_result_authority else 0,
            b"deny_parser": 1 if self.deny_native_parser else 0,
            b"deny_crypto": 1 if self.deny_native_crypto else 0,
            b"deny_transport": 1 if self.deny_native_transport else 0,
            b"deny_persistence": 1 if self.deny_native_persistence else 0,
            b"deny_policy": 1 if self.deny_native_policy else 0,
            b"preserve_archive": 1 if self.preserve_promote_archive_memory else 0,
            b"preserve_review": 1 if self.preserve_review_memory else 0,
            b"preserve_route": 1 if self.preserve_python_route_memory else 0,
            b"preserve_oracle": 1 if self.preserve_python_oracle_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"reason": self.policy_reason_digest,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativePromotionPolicyReport:
    decision_kind: NativePromotionPolicyDecisionKind
    accepted: bool
    shadow_only: bool
    python_fallback_required: bool
    native_load_permission: bool
    native_dispatch_permission: bool
    native_result_authority: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    promote_archive_digest: bytes
    promotion_review_digest: bytes
    policy_reason_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTION_POLICY_DOMAIN + b":report:" + bencode({
            b"decision": NativePromotionPolicyDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"shadow_only": 1 if self.shadow_only else 0,
            b"fallback_required": 1 if self.python_fallback_required else 0,
            b"native_load": 1 if self.native_load_permission else 0,
            b"native_dispatch": 1 if self.native_dispatch_permission else 0,
            b"native_authority": 1 if self.native_result_authority else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"archive": self.promote_archive_digest,
            b"review": self.promotion_review_digest,
            b"reason": self.policy_reason_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_promotion_policy(
    promote_archive: Any,
    capsule: NativePromotionPolicyCapsule,
    *,
    previous: NativePromotionPolicyCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativePromotionPolicyReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: NativePromotionPolicyDecisionKind, accepted: bool, shadow_only: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativePromotionPolicyReport:
        return NativePromotionPolicyReport(
            kind, accepted, shadow_only, shadow_only and capsule.require_python_fallback,
            False, False, False, quarantine, watch, obligations, capsule.capsule_digest,
            capsule.promote_archive_digest, capsule.promotion_review_digest,
            capsule.policy_reason_digest, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativePromotionPolicyDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-promotion-policy-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativePromotionPolicyDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-promotion-policy-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativePromotionPolicyDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-promotion-policy-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativePromotionPolicyDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-promotion-policy-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativePromotionPolicyDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-promotion-policy-low-diversity",))
    if capsule.promote_archive_digest != getattr(promote_archive, "report_digest", b""):
        return report(NativePromotionPolicyDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-promotion-policy-archive-digest-drift",))
    if not getattr(promote_archive, "accepted", False) or not getattr(promote_archive, "review_archived", False):
        return report(NativePromotionPolicyDecisionKind.HOLD_ARCHIVE_NOT_READY, False, False, False, True, ("native-promotion-policy-archive-not-ready",))
    if getattr(promote_archive, "native_call_permission", False) or getattr(promote_archive, "native_result_authority", False):
        return report(NativePromotionPolicyDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-promotion-policy-archive-native-permission",))
    if capsule.policy_mode != "shadow_only" or not capsule.allowed_shadow_observation or not capsule.require_python_fallback:
        return report(NativePromotionPolicyDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-promotion-policy-not-shadow-only",))
    deny_guards = (
        capsule.deny_native_load,
        capsule.deny_native_dispatch,
        capsule.deny_native_result_authority,
        capsule.deny_native_parser,
        capsule.deny_native_crypto,
        capsule.deny_native_transport,
        capsule.deny_native_persistence,
        capsule.deny_native_policy,
    )
    if not all(deny_guards):
        return report(NativePromotionPolicyDecisionKind.QUARANTINE_FORBIDDEN_SURFACE, False, False, True, False, ("native-promotion-policy-forbidden-surface-open",))
    required_memory = (
        capsule.preserve_promote_archive_memory,
        capsule.preserve_review_memory,
        capsule.preserve_python_route_memory,
        capsule.preserve_python_oracle_memory,
        capsule.preserve_fallback_memory,
        capsule.preserve_tombstone_memory,
        capsule.preserve_quarantine_memory,
        capsule.preserve_crash_memory,
    )
    if not all(required_memory):
        return report(NativePromotionPolicyDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-promotion-policy-required-memory-drop",))
    return report(NativePromotionPolicyDecisionKind.ACCEPT_SHADOW_ONLY_POLICY, True, True, False, False, ("native-promotion-policy-shadow-only", "native-promotion-policy-python-fallback-required"))
