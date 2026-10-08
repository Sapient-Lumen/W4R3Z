from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativearchivereplay import (
    NativeArchiveReplayDecisionKind,
    NativeArchiveReplayEntry,
    assess_native_archive_replay,
)
from i2p_dht_lab.nativearchivereplayfold import audit_native_archive_replay_fold
from i2p_dht_lab.nativefoldspine import audit_native_fold_spine
from i2p_dht_lab.nativepromotereview import (
    NativePromotionReviewCapsule,
    NativePromotionReviewDecisionKind,
    assess_native_promotion_review,
)

ROOT = Path(__file__).resolve().parents[1]
ART = sha256(b"rev0097-artifact")
SRC = sha256(b"rev0097-source")
FB = sha256(b"rev0097-fallback")
ORACLE = sha256(b"rev0097-oracle")
CALL = sha256(b"rev0097-call")
PY_RESULT = sha256(b"rev0097-python-result")
NATIVE_RESULT = PY_RESULT
LEDGER = sha256(b"rev0097-call-ledger")
ARCHIVE = sha256(b"rev0097-call-archive")
DENIAL = sha256(b"rev0097-promotion-denial")
SHADOW_GC = sha256(b"rev0097-shadow-gc")
REASON = sha256(b"rev0097-human-review-reason")


@dataclass(frozen=True)
class FakeCallArchive:
    accepted: bool = True
    python_route_archived: bool = True
    native_call_permission: bool = False
    native_result_authoritative: bool = False
    report_digest: bytes = ARCHIVE


@dataclass(frozen=True)
class FakePromotionDenial:
    accepted: bool = True
    promotion_denied: bool = True
    python_fallback_active: bool = True
    native_call_permission: bool = False
    report_digest: bytes = DENIAL


@dataclass(frozen=True)
class FakeShadowGC:
    accepted: bool = True
    soft_compacted: bool = True
    native_promotion_still_denied: bool = True
    python_route_preserved: bool = True
    report_digest: bytes = SHADOW_GC


def _entry(**kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0097-native-archive-replay",
        sequence=1,
        previous_digest=b"",
        restart_generation=7,
        call_archive_digest=ARCHIVE,
        promotion_denial_digest=DENIAL,
        shadow_gc_digest=SHADOW_GC,
        call_ledger_digest=LEDGER,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        python_result_digest=PY_RESULT,
        native_result_digest=NATIVE_RESULT,
        route="python_fallback",
        native_shadow_observed=True,
        native_call_executed=False,
        native_result_selected=False,
        native_promotion_denied=True,
        native_call_permission=False,
        native_result_authoritative=False,
        preserve_call_archive_memory=True,
        preserve_promotion_denial_memory=True,
        preserve_shadow_gc_memory=True,
        preserve_call_ledger_memory=True,
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
    return NativeArchiveReplayEntry(**data)


def _replay(entry=None, archive=None, denial=None, gc=None):
    entry = entry or _entry()
    return assess_native_archive_replay(
        archive or FakeCallArchive(),
        denial or FakePromotionDenial(),
        gc or FakeShadowGC(),
        entry,
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    ), entry


def _review_capsule(replay, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0097-native-archive-replay",
        sequence=1,
        previous_digest=b"",
        archive_replay_digest=replay.report_digest,
        call_archive_digest=ARCHIVE,
        promotion_denial_digest=DENIAL,
        shadow_gc_digest=SHADOW_GC,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        review_requested=True,
        review_reason_digest=REASON,
        repeated_shadow_match_count=17,
        require_human_review=True,
        keep_python_fallback=True,
        deny_native_promotion_now=True,
        native_call_permission_requested=False,
        native_result_authority_requested=False,
        operator_override_requested=False,
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
    return NativePromotionReviewCapsule(**data)


def _review(replay=None, capsule=None):
    replay = replay or _replay()[0]
    capsule = capsule or _review_capsule(replay)
    return assess_native_promotion_review(
        replay,
        capsule,
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    ), capsule


def test_archive_replay_preserves_python_route_and_denies_native_permission():
    report, _ = _replay()
    assert report.decision_kind == NativeArchiveReplayDecisionKind.ACCEPT_REPLAY_ARCHIVED
    assert report.accepted
    assert report.replay_archived
    assert report.python_route_preserved
    assert report.promotion_denied
    assert not report.native_permission


def test_archive_replay_quarantines_native_permission_attempt():
    entry = _entry(native_call_executed=True, native_call_permission=True)
    report, _ = _replay(entry=entry)
    assert report.decision_kind == NativeArchiveReplayDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT
    assert report.quarantine


def test_archive_replay_detects_digest_drift_and_previous_link_pressure():
    drift = _entry(call_archive_digest=sha256(b"wrong-archive"))
    report, _ = _replay(entry=drift)
    assert report.decision_kind == NativeArchiveReplayDecisionKind.QUARANTINE_DIGEST_DRIFT
    first = _entry()
    second = replace(first, sequence=2, previous_digest=sha256(b"wrong-prev"))
    report = assess_native_archive_replay(
        FakeCallArchive(), FakePromotionDenial(), FakeShadowGC(), second,
        previous=first,
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == NativeArchiveReplayDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH


def test_promotion_review_holds_and_keeps_python_fallback():
    report, _ = _review()
    assert report.decision_kind == NativePromotionReviewDecisionKind.ACCEPT_REVIEW_HELD
    assert report.accepted
    assert report.review_held
    assert report.promotion_denied
    assert report.python_fallback_active
    assert not report.native_call_permission


def test_promotion_review_quarantines_native_permission_and_memory_drop():
    replay = _replay()[0]
    capsule = _review_capsule(replay, native_call_permission_requested=True)
    report, _ = _review(replay, capsule)
    assert report.decision_kind == NativePromotionReviewDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT
    capsule = _review_capsule(replay, preserve_shadow_gc_memory=False)
    report, _ = _review(replay, capsule)
    assert report.decision_kind == NativePromotionReviewDecisionKind.QUARANTINE_MEMORY_DROP


def test_native_fold_spine_is_compact_and_current():
    report = audit_native_fold_spine(ROOT, revision="rev0097")
    assert report.status == "pass", report.findings
    assert report.checked_count >= 17


def test_native_archive_replay_fold_current_path_passes():
    report = audit_native_archive_replay_fold(ROOT, revision="rev0097")
    assert report.status == "pass", report.findings
