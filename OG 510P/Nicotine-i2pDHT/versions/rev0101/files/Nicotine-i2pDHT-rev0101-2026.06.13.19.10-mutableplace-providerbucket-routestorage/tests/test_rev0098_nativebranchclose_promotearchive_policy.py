from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativearchivereplay import NativeArchiveReplayReport, NativeArchiveReplayDecisionKind
from i2p_dht_lab.nativebranchclose import (
    NativeBranchCloseCapsule,
    NativeBranchCloseDecisionKind,
    assess_native_branch_close,
)
from i2p_dht_lab.nativebranchclosefold import audit_native_branch_close_fold
from i2p_dht_lab.nativefoldspine import audit_native_fold_spine
from i2p_dht_lab.nativepromotearchive import (
    NativePromoteArchiveDecisionKind,
    NativePromoteArchiveEntry,
    assess_native_promote_archive,
)
from i2p_dht_lab.nativepromotionpolicy import (
    NativePromotionPolicyCapsule,
    NativePromotionPolicyDecisionKind,
    assess_native_promotion_policy,
)

ROOT = Path(__file__).resolve().parents[1]
ART = sha256(b"rev0098-artifact")
SRC = sha256(b"rev0098-source")
FB = sha256(b"rev0098-fallback")
ORACLE = sha256(b"rev0098-oracle")
REVIEW = sha256(b"rev0098-review")
REPLAY = sha256(b"rev0098-replay")
CALL_ARCHIVE = sha256(b"rev0098-call-archive")
DENIAL = sha256(b"rev0098-promotion-denial")
SHADOW_GC = sha256(b"rev0098-shadow-gc")
REASON = sha256(b"rev0098-review-reason")
ARCHIVE_REASON = sha256(b"rev0098-archive-reason")
POLICY_REASON = sha256(b"rev0098-policy-reason")


@dataclass(frozen=True)
class FakeArchiveReplay:
    accepted: bool = True
    replay_archived: bool = True
    native_permission: bool = False
    report_digest: bytes = REPLAY


@dataclass(frozen=True)
class FakePromotionReview:
    accepted: bool = True
    review_held: bool = True
    promotion_denied: bool = True
    python_fallback_active: bool = True
    native_call_permission: bool = False
    native_result_authority: bool = False
    report_digest: bytes = REVIEW


def _promote_archive_entry(**kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0098-native-branch-close",
        sequence=1,
        previous_digest=b"",
        restart_generation=11,
        promotion_review_digest=REVIEW,
        archive_replay_digest=REPLAY,
        call_archive_digest=CALL_ARCHIVE,
        promotion_denial_digest=DENIAL,
        shadow_gc_digest=SHADOW_GC,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        review_reason_digest=REASON,
        archive_reason_digest=ARCHIVE_REASON,
        repeated_shadow_match_count=23,
        human_review_recorded=True,
        native_promotion_denied=True,
        python_fallback_active=True,
        native_call_permission=False,
        native_result_authority=False,
        preserve_review_memory=True,
        preserve_archive_replay_memory=True,
        preserve_call_archive_memory=True,
        preserve_promotion_denial_memory=True,
        preserve_shadow_gc_memory=True,
        preserve_python_route_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativePromoteArchiveEntry(**data)


def _archive(entry=None, review=None):
    return assess_native_promote_archive(
        review or FakePromotionReview(),
        entry or _promote_archive_entry(),
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _policy_capsule(archive_report, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0098-native-branch-close",
        sequence=1,
        previous_digest=b"",
        promote_archive_digest=archive_report.report_digest,
        promotion_review_digest=REVIEW,
        policy_scope="native-shadow-xor-distance-only",
        policy_mode="shadow_only",
        allowed_shadow_observation=True,
        require_python_fallback=True,
        deny_native_load=True,
        deny_native_dispatch=True,
        deny_native_result_authority=True,
        deny_native_parser=True,
        deny_native_crypto=True,
        deny_native_transport=True,
        deny_native_persistence=True,
        deny_native_policy=True,
        preserve_promote_archive_memory=True,
        preserve_review_memory=True,
        preserve_python_route_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        policy_reason_digest=POLICY_REASON,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativePromotionPolicyCapsule(**data)


def _policy(archive_report=None, capsule=None):
    archive_report = archive_report or _archive()
    capsule = capsule or _policy_capsule(archive_report)
    return assess_native_promotion_policy(
        archive_report,
        capsule,
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    ), capsule, archive_report


def _branch_capsule(archive_report, policy_report, spine_report, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0098-native-branch-close",
        sequence=1,
        previous_digest=b"",
        archive_replay_digest=REPLAY,
        promotion_review_digest=REVIEW,
        promote_archive_digest=archive_report.report_digest,
        promotion_policy_digest=policy_report.report_digest,
        native_fold_spine_digest=spine_report.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        branch_state="shadow_only_closed",
        python_fallback_authoritative=True,
        native_load_allowed=False,
        native_dispatch_allowed=False,
        native_result_authority_allowed=False,
        future_promotion_requires_new_branch=True,
        preserve_archive_replay_memory=True,
        preserve_promotion_review_memory=True,
        preserve_promote_archive_memory=True,
        preserve_policy_memory=True,
        preserve_fold_spine_memory=True,
        preserve_python_route_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeBranchCloseCapsule(**data)


def _branch(capsule=None):
    policy_report, _, archive_report = _policy()
    spine = audit_native_fold_spine(ROOT, revision="rev0098")
    capsule = capsule or _branch_capsule(archive_report, policy_report, spine)
    return assess_native_branch_close(
        FakeArchiveReplay(),
        FakePromotionReview(),
        archive_report,
        policy_report,
        spine,
        capsule,
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    ), capsule


def test_promote_archive_accepts_held_review_without_native_permission():
    report = _archive()
    assert report.decision_kind == NativePromoteArchiveDecisionKind.ACCEPT_REVIEW_ARCHIVED
    assert report.accepted
    assert report.review_archived
    assert report.promotion_denied
    assert report.python_fallback_active
    assert not report.native_call_permission
    assert not report.native_result_authority


def test_promote_archive_quarantines_permission_attempt_and_memory_drop():
    report = _archive(_promote_archive_entry(native_call_permission=True))
    assert report.decision_kind == NativePromoteArchiveDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT
    report = _archive(_promote_archive_entry(preserve_quarantine_memory=False))
    assert report.decision_kind == NativePromoteArchiveDecisionKind.QUARANTINE_MEMORY_DROP


def test_promote_archive_detects_previous_link_pressure():
    first = _promote_archive_entry()
    second = replace(first, sequence=2, previous_digest=sha256(b"wrong-prev"))
    report = assess_native_promote_archive(
        FakePromotionReview(), second, previous=first,
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == NativePromoteArchiveDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH


def test_policy_accepts_shadow_only_and_rejects_forbidden_surface():
    report, _, _ = _policy()
    assert report.decision_kind == NativePromotionPolicyDecisionKind.ACCEPT_SHADOW_ONLY_POLICY
    assert report.accepted and report.shadow_only and report.python_fallback_required
    assert not report.native_dispatch_permission
    archive = _archive()
    capsule = _policy_capsule(archive, deny_native_dispatch=False)
    report, _, _ = _policy(archive, capsule)
    assert report.decision_kind == NativePromotionPolicyDecisionKind.QUARANTINE_FORBIDDEN_SURFACE


def test_branch_close_accepts_shadow_only_closure():
    report, _ = _branch()
    assert report.decision_kind == NativeBranchCloseDecisionKind.ACCEPT_BRANCH_CLOSED_SHADOW_ONLY
    assert report.accepted
    assert report.branch_closed
    assert report.shadow_only
    assert report.python_fallback_authoritative
    assert report.future_promotion_requires_new_branch
    assert not report.native_permission


def test_branch_close_quarantines_digest_drift_permission_and_memory_drop():
    policy_report, _, archive_report = _policy()
    spine = audit_native_fold_spine(ROOT, revision="rev0098")
    drift_capsule = _branch_capsule(archive_report, policy_report, spine, promote_archive_digest=sha256(b"wrong-archive"))
    report = assess_native_branch_close(FakeArchiveReplay(), FakePromotionReview(), archive_report, policy_report, spine, drift_capsule, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert report.decision_kind == NativeBranchCloseDecisionKind.QUARANTINE_DIGEST_DRIFT
    permission_capsule = _branch_capsule(archive_report, policy_report, spine, native_dispatch_allowed=True)
    report = assess_native_branch_close(FakeArchiveReplay(), FakePromotionReview(), archive_report, policy_report, spine, permission_capsule, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert report.decision_kind == NativeBranchCloseDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT
    memory_capsule = _branch_capsule(archive_report, policy_report, spine, preserve_crash_memory=False)
    report = assess_native_branch_close(FakeArchiveReplay(), FakePromotionReview(), archive_report, policy_report, spine, memory_capsule, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert report.decision_kind == NativeBranchCloseDecisionKind.QUARANTINE_MEMORY_DROP


def test_native_spine_and_branch_close_fold_current_path_pass():
    spine = audit_native_fold_spine(ROOT, revision="rev0098")
    assert spine.status == "pass", spine.findings
    assert spine.checked_count >= 18
    fold = audit_native_branch_close_fold(ROOT, revision="rev0098")
    assert fold.status == "pass", fold.findings
