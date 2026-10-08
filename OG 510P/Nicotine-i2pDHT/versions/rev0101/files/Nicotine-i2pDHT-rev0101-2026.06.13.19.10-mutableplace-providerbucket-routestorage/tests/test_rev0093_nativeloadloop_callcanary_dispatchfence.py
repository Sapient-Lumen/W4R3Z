from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.dispatchfence import (
    NativeDispatchFenceCapsule,
    NativeDispatchFenceDecisionKind,
    assess_native_dispatch_fence,
)
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativecallcanary import (
    NativeCallCanaryCapsule,
    NativeCallCanaryDecisionKind,
    assess_native_call_canary,
)
from i2p_dht_lab.nativecallhold import NativeCallHoldCapsule, assess_native_call_hold
from i2p_dht_lab.nativeloadloop import (
    NativeLoadLoopCapsule,
    NativeLoadLoopDecisionKind,
    assess_native_load_loop,
)
from i2p_dht_lab.nativeloadloopfold import audit_native_load_loop_fold
from i2p_dht_lab.nativeloadreentry import NativeLoadReentryRequest, assess_native_load_reentry
from i2p_dht_lab.revalidationseal import RevalidationSealCapsule, assess_revalidation_seal

ROOT = Path(__file__).resolve().parents[1]
ART = sha256(b"rev0093-artifact")
SRC = sha256(b"rev0093-source")
FB = sha256(b"rev0093-fallback")
ORACLE = sha256(b"rev0093-python-oracle")
CALL = sha256(b"rev0093-call-vector")
RESULT = sha256(b"python-result: xor-compare returns -1")
LANES = tuple(sha256(f"rev0093-lane-{idx}".encode()) for idx in range(8))


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
    report_digest: bytes = sha256(b"rev0093-reentry-journal")


@dataclass(frozen=True)
class FakeRelaunch:
    accepted: bool = True
    relaunch_plan_ready: bool = True
    quarantine: bool = False
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    report_digest: bytes = sha256(b"rev0093-relaunch-gate")


def _load_reentry():
    reentry = FakeReentry()
    relaunch = FakeRelaunch()
    request = NativeLoadReentryRequest(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0093-native",
        sequence=1,
        previous_digest=b"",
        reentry_journal_digest=reentry.report_digest,
        relaunch_gate_digest=relaunch.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        loader_id="ctypes-local-xor-v1",
        route_to_load_gate_only=True,
        native_load_attempted=False,
        native_dispatch_attempted=False,
        python_fallback_active=True,
        preserve_reentry_memory=True,
        preserve_relaunch_memory=True,
        preserve_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    return assess_native_load_reentry(reentry, relaunch, request, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def _revalidation(load_reentry=None):
    load_reentry = load_reentry or _load_reentry()
    cap = RevalidationSealCapsule(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0093-native",
        sequence=1,
        previous_digest=b"",
        load_reentry_digest=load_reentry.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        parity_digest=LANES[0],
        abi_digest=LANES[1],
        fallback_seal_digest=LANES[2],
        runtime_stamp_digest=LANES[3],
        selection_digest=LANES[4],
        provenance_digest=LANES[5],
        corpus_digest=LANES[6],
        budget_digest=LANES[7],
        issued_at=100,
        expires_at=200,
        observed_at=150,
        prior_lanes_fresh=True,
        preserve_load_reentry_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    return assess_revalidation_seal(load_reentry, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), now=150)


def _call_hold(load_reentry=None, revalidation=None):
    load_reentry = load_reentry or _load_reentry()
    revalidation = revalidation or _revalidation(load_reentry)
    cap = NativeCallHoldCapsule(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0093-native",
        sequence=1,
        previous_digest=b"",
        load_reentry_digest=load_reentry.report_digest,
        revalidation_seal_digest=revalidation.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        native_call_requested=True,
        native_call_executed=False,
        python_fallback_executed=True,
        preserve_load_reentry_memory=True,
        preserve_revalidation_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    return assess_native_call_hold(load_reentry, revalidation, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def _loop_capsule(load_reentry, revalidation, call_hold, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0093-native",
        sequence=1,
        previous_digest=b"",
        load_reentry_digest=load_reentry.report_digest,
        revalidation_seal_digest=revalidation.report_digest,
        call_hold_digest=call_hold.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        loopback_to_load_gate=True,
        native_load_attempted=False,
        native_dispatch_attempted=False,
        python_fallback_active=True,
        preserve_load_reentry_memory=True,
        preserve_revalidation_memory=True,
        preserve_call_hold_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeLoadLoopCapsule(**data)


def _loop(load_reentry=None, revalidation=None, call_hold=None, capsule=None):
    load_reentry = load_reentry or _load_reentry()
    revalidation = revalidation or _revalidation(load_reentry)
    call_hold = call_hold or _call_hold(load_reentry, revalidation)
    cap = capsule or _loop_capsule(load_reentry, revalidation, call_hold)
    return assess_native_load_loop(load_reentry, revalidation, call_hold, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap, load_reentry, revalidation, call_hold


def _canary_capsule(load_loop, call_hold, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0093-native",
        sequence=1,
        previous_digest=b"",
        load_loop_digest=load_loop.report_digest,
        call_hold_digest=call_hold.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        python_result_digest=RESULT,
        native_result_digest=b"",
        native_call_executed=False,
        python_fallback_executed=True,
        preserve_load_loop_memory=True,
        preserve_call_hold_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeCallCanaryCapsule(**data)


def _canary(load_loop=None, call_hold=None, capsule=None):
    if load_loop is None or call_hold is None:
        load_loop, _, _, _, call_hold = _loop()
    cap = capsule or _canary_capsule(load_loop, call_hold)
    return assess_native_call_canary(load_loop, call_hold, cap, expected_python_result_digest=RESULT, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap, load_loop, call_hold


def _fence_capsule(load_loop, canary, revalidation, call_hold, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0093-native",
        sequence=1,
        previous_digest=b"",
        load_loop_digest=load_loop.report_digest,
        call_canary_digest=canary.report_digest,
        revalidation_seal_digest=revalidation.report_digest,
        call_hold_digest=call_hold.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        python_result_digest=RESULT,
        native_load_attempted=False,
        native_dispatch_attempted=False,
        native_call_executed=False,
        python_fallback_active=True,
        preserve_load_loop_memory=True,
        preserve_canary_memory=True,
        preserve_revalidation_memory=True,
        preserve_call_hold_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeDispatchFenceCapsule(**data)


def _fence(load_loop=None, canary=None, revalidation=None, call_hold=None, capsule=None):
    if load_loop is None or revalidation is None or call_hold is None:
        load_loop, _, _, revalidation, call_hold = _loop()
    if canary is None:
        canary, _, _, _ = _canary(load_loop, call_hold)
    cap = capsule or _fence_capsule(load_loop, canary, revalidation, call_hold)
    return assess_native_dispatch_fence(load_loop, canary, revalidation, call_hold, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def test_load_loop_call_canary_and_dispatch_fence_happy_path() -> None:
    loop_report, _, _, _, call_hold = _loop()
    assert loop_report.decision_kind is NativeLoadLoopDecisionKind.ACCEPT_LOOPBACK_HELD_ON_PYTHON
    assert loop_report.loopback_ready and not loop_report.native_load_allowed and not loop_report.native_dispatch_allowed

    canary_report, _, _, _ = _canary(loop_report, call_hold)
    assert canary_report.decision_kind is NativeCallCanaryDecisionKind.ACCEPT_CANARY_ON_PYTHON_RESULT
    assert canary_report.canary_ready and canary_report.python_fallback_executed and not canary_report.native_call_allowed

    fence_report, _ = _fence(loop_report, canary_report)
    assert fence_report.decision_kind is NativeDispatchFenceDecisionKind.ACCEPT_DISPATCH_FENCED_ON_PYTHON
    assert fence_report.dispatch_fenced and fence_report.python_fallback_active
    assert not fence_report.native_load_allowed and not fence_report.native_dispatch_allowed and not fence_report.native_call_executed


def test_load_loop_rejects_bypass_memory_drop_and_digest_drift() -> None:
    good_loop, _, load_reentry, revalidation, call_hold = _loop()
    attempted = _loop_capsule(load_reentry, revalidation, call_hold, native_dispatch_attempted=True)
    report = assess_native_load_loop(load_reentry, revalidation, call_hold, attempted, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert report.decision_kind is NativeLoadLoopDecisionKind.QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT

    drop = _loop_capsule(load_reentry, revalidation, call_hold, preserve_call_hold_memory=False)
    drop_report = assess_native_load_loop(load_reentry, revalidation, call_hold, drop, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert drop_report.decision_kind is NativeLoadLoopDecisionKind.QUARANTINE_MEMORY_DROP

    drift = _loop_capsule(load_reentry, revalidation, call_hold, call_vector_digest=sha256(b"wrong-vector"))
    drift_report = assess_native_load_loop(load_reentry, revalidation, call_hold, drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert drift_report.decision_kind is NativeLoadLoopDecisionKind.QUARANTINE_DIGEST_DRIFT
    assert good_loop.accepted


def test_call_canary_rejects_native_result_wrong_python_result_and_low_diversity() -> None:
    loop_report, _, _, _, call_hold = _loop()
    native_result = _canary_capsule(loop_report, call_hold, native_result_digest=sha256(b"native-result"))
    report = assess_native_call_canary(loop_report, call_hold, native_result, expected_python_result_digest=RESULT, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert report.decision_kind is NativeCallCanaryDecisionKind.QUARANTINE_NATIVE_RESULT_OR_EXECUTION

    bad_python = _canary_capsule(loop_report, call_hold, python_result_digest=sha256(b"wrong-python-result"))
    bad_report = assess_native_call_canary(loop_report, call_hold, bad_python, expected_python_result_digest=RESULT, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert bad_report.decision_kind is NativeCallCanaryDecisionKind.QUARANTINE_DIGEST_DRIFT

    low = assess_native_call_canary(loop_report, call_hold, _canary_capsule(loop_report, call_hold), expected_python_result_digest=RESULT, observed_families=("family-a",), observed_path_families=("path-a",))
    assert low.decision_kind is NativeCallCanaryDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_dispatch_fence_rejects_native_side_effect_replay_and_previous_link_mismatch() -> None:
    loop_report, loop_capsule, _, revalidation, call_hold = _loop()
    canary_report, _, _, _ = _canary(loop_report, call_hold)
    attempted = _fence_capsule(loop_report, canary_report, revalidation, call_hold, native_load_attempted=True)
    attempted_report = assess_native_dispatch_fence(loop_report, canary_report, revalidation, call_hold, attempted, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert attempted_report.decision_kind is NativeDispatchFenceDecisionKind.QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT

    good_report, good_cap = _fence(loop_report, canary_report, revalidation, call_hold)
    replay = assess_native_dispatch_fence(loop_report, canary_report, revalidation, call_hold, good_cap, prior_capsule_digests=(good_cap.capsule_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert replay.decision_kind is NativeDispatchFenceDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK

    bad_link = replace(good_cap, sequence=2, previous_digest=loop_capsule.capsule_digest)
    link = assess_native_dispatch_fence(loop_report, canary_report, revalidation, call_hold, bad_link, previous=good_cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert link.decision_kind is NativeDispatchFenceDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    assert good_report.accepted


def test_native_load_loop_fold_happy_path() -> None:
    report = audit_native_load_loop_fold(ROOT, revision="rev0093")
    assert report.status == "pass", report.findings
    assert report.predecessor_status == "pass"
    assert report.native_spine_status == "pass"
