from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativecallhold import (
    NativeCallHoldCapsule,
    NativeCallHoldDecisionKind,
    assess_native_call_hold,
)
from i2p_dht_lab.nativeloadreentry import (
    NativeLoadReentryDecisionKind,
    NativeLoadReentryRequest,
    assess_native_load_reentry,
)
from i2p_dht_lab.nativeloadreentryfold import audit_native_load_reentry_fold
from i2p_dht_lab.revalidationseal import (
    RevalidationSealCapsule,
    RevalidationSealDecisionKind,
    assess_revalidation_seal,
)

ROOT = Path(__file__).resolve().parents[1]
ART = sha256(b"artifact")
SRC = sha256(b"source")
FB = sha256(b"fallback")
ORACLE = sha256(b"python-oracle")
LANES = tuple(sha256(f"lane-{idx}".encode()) for idx in range(8))
CALL = sha256(b"call-vector")


@dataclass(frozen=True)
class FakeReentry:
    accepted: bool = True
    journaled: bool = True
    route_to_load_gate_only: bool = True
    quarantine: bool = False
    tombstone_memory: bool = True
    fault_memory: bool = True
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    report_digest: bytes = sha256(b"reentry-report")


@dataclass(frozen=True)
class FakeRelaunch:
    accepted: bool = True
    relaunch_plan_ready: bool = True
    quarantine: bool = False
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    report_digest: bytes = sha256(b"relaunch-report")


def _load_request(reentry=FakeReentry(), relaunch=FakeRelaunch(), **kw):
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0092-native",
        sequence=1, previous_digest=b"", reentry_journal_digest=reentry.report_digest,
        relaunch_gate_digest=relaunch.report_digest, artifact_digest=ART, source_digest=SRC, fallback_digest=FB,
        python_oracle_digest=ORACLE, loader_id="ctypes-local-xor-v1", route_to_load_gate_only=True,
        native_load_attempted=False, native_dispatch_attempted=False, python_fallback_active=True,
        preserve_reentry_memory=True, preserve_relaunch_memory=True, preserve_oracle_memory=True,
        preserve_fallback_memory=True, preserve_tombstone_memory=True, preserve_quarantine_memory=True,
        preserve_crash_memory=True, family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return NativeLoadReentryRequest(**data)


def _load_reentry(reentry=FakeReentry(), relaunch=FakeRelaunch(), request=None):
    req = request or _load_request(reentry, relaunch)
    return assess_native_load_reentry(reentry, relaunch, req, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), req


def _seal_capsule(load_report, **kw):
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0092-native",
        sequence=1, previous_digest=b"", load_reentry_digest=load_report.report_digest, artifact_digest=ART,
        source_digest=SRC, fallback_digest=FB, python_oracle_digest=ORACLE, parity_digest=LANES[0],
        abi_digest=LANES[1], fallback_seal_digest=LANES[2], runtime_stamp_digest=LANES[3],
        selection_digest=LANES[4], provenance_digest=LANES[5], corpus_digest=LANES[6], budget_digest=LANES[7],
        issued_at=100, expires_at=200, observed_at=150, prior_lanes_fresh=True,
        preserve_load_reentry_memory=True, preserve_fallback_memory=True, preserve_tombstone_memory=True,
        preserve_quarantine_memory=True, preserve_crash_memory=True, family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return RevalidationSealCapsule(**data)


def _seal(load_report=None, capsule=None):
    if load_report is None:
        load_report, _ = _load_reentry()
    cap = capsule or _seal_capsule(load_report)
    return assess_revalidation_seal(load_report, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), now=150), cap


def _call_capsule(load_report, seal_report, **kw):
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0092-native",
        sequence=1, previous_digest=b"", load_reentry_digest=load_report.report_digest,
        revalidation_seal_digest=seal_report.report_digest, artifact_digest=ART, source_digest=SRC,
        fallback_digest=FB, python_oracle_digest=ORACLE, call_vector_digest=CALL, native_call_requested=True,
        native_call_executed=False, python_fallback_executed=True, preserve_load_reentry_memory=True,
        preserve_revalidation_memory=True, preserve_python_oracle_memory=True, preserve_fallback_memory=True,
        preserve_tombstone_memory=True, preserve_quarantine_memory=True, preserve_crash_memory=True,
        family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return NativeCallHoldCapsule(**data)


def _call(load_report=None, seal_report=None, capsule=None):
    if load_report is None:
        load_report, _ = _load_reentry()
    if seal_report is None:
        seal_report, _ = _seal(load_report)
    cap = capsule or _call_capsule(load_report, seal_report)
    return assess_native_call_hold(load_report, seal_report, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def test_load_reentry_prepares_request_but_does_not_load() -> None:
    report, _ = _load_reentry()
    assert report.decision_kind is NativeLoadReentryDecisionKind.ACCEPT_LOAD_GATE_REQUEST_ONLY
    assert report.load_gate_request_ready and report.route_to_load_gate_only
    assert not report.native_load_allowed and not report.native_dispatch_allowed

    attempted, _ = _load_reentry(request=_load_request(native_load_attempted=True))
    assert attempted.decision_kind is NativeLoadReentryDecisionKind.QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT

    no_reentry, _ = _load_reentry(reentry=FakeReentry(accepted=False, journaled=False))
    assert no_reentry.decision_kind is NativeLoadReentryDecisionKind.HOLD_REENTRY_JOURNAL_NOT_READY

    no_relaunch, _ = _load_reentry(relaunch=FakeRelaunch(relaunch_plan_ready=False))
    assert no_relaunch.decision_kind is NativeLoadReentryDecisionKind.HOLD_RELAUNCH_GATE_NOT_READY

    drift, _ = _load_reentry(request=_load_request(artifact_digest=sha256(b"wrong-artifact")))
    assert drift.decision_kind is NativeLoadReentryDecisionKind.QUARANTINE_DIGEST_DRIFT

    drop, _ = _load_reentry(request=_load_request(preserve_crash_memory=False))
    assert drop.decision_kind is NativeLoadReentryDecisionKind.QUARANTINE_MEMORY_DROP


def test_revalidation_seal_refreshes_prior_lanes_without_allowing_load() -> None:
    load_report, _ = _load_reentry()
    report, _ = _seal(load_report)
    assert report.decision_kind is RevalidationSealDecisionKind.ACCEPT_REVALIDATION_SEAL
    assert report.revalidated and not report.native_load_allowed and not report.native_dispatch_allowed

    stale = _seal_capsule(load_report, observed_at=250)
    stale_report = assess_revalidation_seal(load_report, stale, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), now=250)
    assert stale_report.decision_kind is RevalidationSealDecisionKind.HOLD_STALE_OR_EXPIRED

    missing = _seal_capsule(load_report, budget_digest=b"")
    missing_report, _ = _seal(load_report, missing)
    assert missing_report.decision_kind is RevalidationSealDecisionKind.QUARANTINE_MISSING_REQUIRED_LANES

    drift = _seal_capsule(load_report, load_reentry_digest=sha256(b"wrong-load-reentry"))
    drift_report, _ = _seal(load_report, drift)
    assert drift_report.decision_kind is RevalidationSealDecisionKind.QUARANTINE_DIGEST_DRIFT

    drop = _seal_capsule(load_report, preserve_tombstone_memory=False)
    drop_report, _ = _seal(load_report, drop)
    assert drop_report.decision_kind is RevalidationSealDecisionKind.QUARANTINE_MEMORY_DROP


def test_native_call_hold_keeps_python_oracle_route() -> None:
    load_report, _ = _load_reentry()
    seal_report, _ = _seal(load_report)
    report, _ = _call(load_report, seal_report)
    assert report.decision_kind is NativeCallHoldDecisionKind.ACCEPT_CALL_HELD_ON_PYTHON_FALLBACK
    assert report.call_held and report.python_fallback_executed
    assert not report.native_call_allowed and not report.native_call_executed

    executed = _call_capsule(load_report, seal_report, native_call_executed=True)
    executed_report, _ = _call(load_report, seal_report, executed)
    assert executed_report.decision_kind is NativeCallHoldDecisionKind.QUARANTINE_NATIVE_CALL_EXECUTED

    no_python = _call_capsule(load_report, seal_report, python_fallback_executed=False)
    no_python_report, _ = _call(load_report, seal_report, no_python)
    assert no_python_report.decision_kind is NativeCallHoldDecisionKind.QUARANTINE_MEMORY_DROP

    bad_seal = replace(seal_report, accepted=False, revalidated=False)
    hold_report, _ = _call(load_report, bad_seal)
    assert hold_report.decision_kind is NativeCallHoldDecisionKind.HOLD_REVALIDATION_SEAL_NOT_READY

    drift = _call_capsule(load_report, seal_report, fallback_digest=sha256(b"wrong-fallback"))
    drift_report, _ = _call(load_report, seal_report, drift)
    assert drift_report.decision_kind is NativeCallHoldDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_reentry_seal_call_hold_detect_replay_forks_and_low_diversity() -> None:
    load_report, req = _load_reentry()
    replay = assess_native_load_reentry(FakeReentry(), FakeRelaunch(), req, prior_request_digests=(req.request_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert replay.decision_kind is NativeLoadReentryDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = assess_native_load_reentry(FakeReentry(), FakeRelaunch(), replace(req, note="fork"), previous=req, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert fork.decision_kind is NativeLoadReentryDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    low = assess_native_load_reentry(FakeReentry(), FakeRelaunch(), req, observed_families=("family-a",), observed_path_families=("path-a",))
    assert low.decision_kind is NativeLoadReentryDecisionKind.QUARANTINE_LOW_DIVERSITY

    seal_report, seal_cap = _seal(load_report)
    replay_seal = assess_revalidation_seal(load_report, seal_cap, prior_capsule_digests=(seal_cap.capsule_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), now=150)
    assert replay_seal.decision_kind is RevalidationSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    bad_link = replace(seal_cap, sequence=2, previous_digest=sha256(b"bad-prev"))
    link = assess_revalidation_seal(load_report, bad_link, previous=seal_cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), now=150)
    assert link.decision_kind is RevalidationSealDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH

    call_report, call_cap = _call(load_report, seal_report)
    replay_call = assess_native_call_hold(load_report, seal_report, call_cap, prior_capsule_digests=(call_cap.capsule_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert replay_call.decision_kind is NativeCallHoldDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    assert call_report.accepted


def test_native_load_reentry_fold_happy_path() -> None:
    report = audit_native_load_reentry_fold(ROOT, revision="rev0092")
    assert report.status == "pass", report.findings
    assert report.predecessor_status == "pass"
    assert report.native_spine_status == "pass"
