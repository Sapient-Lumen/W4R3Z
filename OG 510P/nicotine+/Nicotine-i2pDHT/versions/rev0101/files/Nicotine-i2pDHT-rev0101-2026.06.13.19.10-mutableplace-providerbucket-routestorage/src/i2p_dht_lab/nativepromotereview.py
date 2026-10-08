"""rev0097 native promotion-review hold.

This module intentionally does *not* promote native code.  It records that a
human/operator review may be requested after archive replay, but the only valid
outcome in this cube remains Python fallback with native promotion held.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_PROMOTION_REVIEW_DOMAIN = DOMAIN + b":native-promotion-review-v1:"


class NativePromotionReviewDecisionKind(str, Enum):
    ACCEPT_REVIEW_HELD = "accept_review_held"
    HOLD_REPLAY_NOT_READY = "hold_replay_not_ready"
    QUARANTINE_NATIVE_PERMISSION_ATTEMPT = "quarantine_native_permission_attempt"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativePromotionReviewCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    archive_replay_digest: bytes
    call_archive_digest: bytes
    promotion_denial_digest: bytes
    shadow_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    review_requested: bool
    review_reason_digest: bytes
    repeated_shadow_match_count: int
    require_human_review: bool
    keep_python_fallback: bool
    deny_native_promotion_now: bool
    native_call_permission_requested: bool
    native_result_authority_requested: bool
    operator_override_requested: bool
    preserve_archive_replay_memory: bool
    preserve_call_archive_memory: bool
    preserve_promotion_denial_memory: bool
    preserve_shadow_gc_memory: bool
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
        return sha256(NATIVE_PROMOTION_REVIEW_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"archive_replay": self.archive_replay_digest,
            b"call_archive": self.call_archive_digest,
            b"promotion_denial": self.promotion_denial_digest,
            b"shadow_gc": self.shadow_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"review_requested": 1 if self.review_requested else 0,
            b"reason": self.review_reason_digest,
            b"shadow_count": self.repeated_shadow_match_count,
            b"human_review": 1 if self.require_human_review else 0,
            b"fallback_active": 1 if self.keep_python_fallback else 0,
            b"deny_now": 1 if self.deny_native_promotion_now else 0,
            b"call_permission_requested": 1 if self.native_call_permission_requested else 0,
            b"authority_requested": 1 if self.native_result_authority_requested else 0,
            b"operator_override": 1 if self.operator_override_requested else 0,
            b"preserve_replay": 1 if self.preserve_archive_replay_memory else 0,
            b"preserve_archive": 1 if self.preserve_call_archive_memory else 0,
            b"preserve_denial": 1 if self.preserve_promotion_denial_memory else 0,
            b"preserve_gc": 1 if self.preserve_shadow_gc_memory else 0,
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
class NativePromotionReviewReport:
    decision_kind: NativePromotionReviewDecisionKind
    accepted: bool
    review_held: bool
    promotion_denied: bool
    python_fallback_active: bool
    native_call_permission: bool
    native_result_authority: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    archive_replay_digest: bytes
    call_archive_digest: bytes
    promotion_denial_digest: bytes
    shadow_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    review_reason_digest: bytes
    repeated_shadow_match_count: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTION_REVIEW_DOMAIN + b":report:" + bencode({
            b"decision": NativePromotionReviewDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"review_held": 1 if self.review_held else 0,
            b"promotion_denied": 1 if self.promotion_denied else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"native_call_permission": 1 if self.native_call_permission else 0,
            b"native_authority": 1 if self.native_result_authority else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"archive_replay": self.archive_replay_digest,
            b"call_archive": self.call_archive_digest,
            b"promotion_denial": self.promotion_denial_digest,
            b"shadow_gc": self.shadow_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"reason": self.review_reason_digest,
            b"shadow_count": self.repeated_shadow_match_count,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_promotion_review(
    archive_replay: Any,
    capsule: NativePromotionReviewCapsule,
    *,
    previous: NativePromotionReviewCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativePromotionReviewReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: NativePromotionReviewDecisionKind, accepted: bool, review_held: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativePromotionReviewReport:
        return NativePromotionReviewReport(
            kind, accepted, review_held, review_held and capsule.deny_native_promotion_now,
            review_held and capsule.keep_python_fallback, False, False, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.archive_replay_digest, capsule.call_archive_digest,
            capsule.promotion_denial_digest, capsule.shadow_gc_digest, capsule.artifact_digest,
            capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest,
            capsule.review_reason_digest, capsule.repeated_shadow_match_count,
            len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativePromotionReviewDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-promotion-review-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativePromotionReviewDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-promotion-review-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativePromotionReviewDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-promotion-review-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativePromotionReviewDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-promotion-review-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativePromotionReviewDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-promotion-review-low-diversity",))
    if capsule.archive_replay_digest != getattr(archive_replay, "report_digest", b""):
        return report(NativePromotionReviewDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-promotion-review-replay-digest-drift",))
    if not getattr(archive_replay, "accepted", False) or not getattr(archive_replay, "replay_archived", False):
        return report(NativePromotionReviewDecisionKind.HOLD_REPLAY_NOT_READY, False, False, False, True, ("native-promotion-review-replay-not-ready",))
    if capsule.native_call_permission_requested or capsule.native_result_authority_requested or capsule.operator_override_requested:
        return report(NativePromotionReviewDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-promotion-review-native-permission-attempt",))
    if not capsule.review_requested or not capsule.require_human_review or not capsule.keep_python_fallback or not capsule.deny_native_promotion_now:
        return report(NativePromotionReviewDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-promotion-review-not-held",))
    required_memory = (
        capsule.preserve_archive_replay_memory,
        capsule.preserve_call_archive_memory,
        capsule.preserve_promotion_denial_memory,
        capsule.preserve_shadow_gc_memory,
        capsule.preserve_python_route_memory,
        capsule.preserve_python_oracle_memory,
        capsule.preserve_fallback_memory,
        capsule.preserve_tombstone_memory,
        capsule.preserve_quarantine_memory,
        capsule.preserve_crash_memory,
    )
    if not all(required_memory):
        return report(NativePromotionReviewDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-promotion-review-required-memory-drop",))
    return report(NativePromotionReviewDecisionKind.ACCEPT_REVIEW_HELD, True, True, False, False, ("native-promotion-review-human-audit-required", "native-promotion-review-python-fallback-active"))
