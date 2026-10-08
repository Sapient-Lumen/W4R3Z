from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.faultseal import (
    NativeFaultSealCapsule,
    NativeFaultSealDecisionKind,
    assess_native_fault_seal,
)
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativeshadowcall import (
    NativeShadowCallCapsule,
    NativeShadowCallDecisionKind,
    assess_native_shadow_call,
)
from i2p_dht_lab.nativeshadowfold import audit_native_shadow_fold
from i2p_dht_lab.resultdiff import (
    NativeResultDiffCapsule,
    NativeResultDiffDecisionKind,
    assess_native_result_diff,
)

ROOT = Path(__file__).resolve().parents[1]
ART = sha256(b"rev0094-artifact")
SRC = sha256(b"rev0094-source")
FB = sha256(b"rev0094-fallback")
ORACLE = sha256(b"rev0094-python-oracle")
CALL = sha256(b"rev0094-call-vector")
PY_RESULT = sha256(b"rev0094-python-result")
NATIVE_RESULT = PY_RESULT
BAD_NATIVE_RESULT = sha256(b"rev0094-bad-native-result")
FAULT = sha256(b"rev0094-native-fault")


@dataclass(frozen=True)
class FakeDispatchFence:
    accepted: bool = True
    dispatch_fenced: bool = True
    quarantine: bool = False
    tombstone_memory: bool = True
    fault_memory: bool = True
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    call_vector_digest: bytes = CALL
    python_result_digest: bytes = PY_RESULT
    report_digest: bytes = sha256(b"rev0094-dispatch-fence")


def _shadow_capsule(dispatch=None, **kw):
    dispatch = dispatch or FakeDispatchFence()
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0094-native-shadow",
        sequence=1,
        previous_digest=b"",
        dispatch_fence_digest=dispatch.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        python_result_digest=PY_RESULT,
        native_result_digest=NATIVE_RESULT,
        native_fault_digest=b"",
        shadow_mode=True,
        native_result_observed=True,
        native_result_selected=False,
        native_authority_claimed=False,
        python_fallback_active=True,
        preserve_dispatch_fence_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeShadowCallCapsule(**data)


def _shadow(dispatch=None, capsule=None):
    dispatch = dispatch or FakeDispatchFence()
    cap = capsule or _shadow_capsule(dispatch)
    return assess_native_shadow_call(dispatch, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap, dispatch


def _diff_capsule(shadow, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0094-native-shadow",
        sequence=1,
        previous_digest=b"",
        shadow_call_digest=shadow.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        python_result_digest=PY_RESULT,
        native_result_digest=NATIVE_RESULT,
        native_fault_digest=b"",
        native_result_present=True,
        results_match=True,
        python_result_authoritative=True,
        preserve_shadow_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeResultDiffCapsule(**data)


def _diff(shadow=None, capsule=None):
    if shadow is None:
        shadow, _, _ = _shadow()
    cap = capsule or _diff_capsule(shadow)
    return assess_native_result_diff(shadow, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap, shadow


def _seal_capsule(dispatch, shadow, diff, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0094-native-shadow",
        sequence=1,
        previous_digest=b"",
        dispatch_fence_digest=dispatch.report_digest,
        shadow_call_digest=shadow.report_digest,
        result_diff_digest=diff.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        python_result_digest=PY_RESULT,
        native_result_digest=diff.native_result_digest,
        native_fault_digest=diff.native_fault_digest,
        result_match=diff.result_match,
        mismatch_fault=diff.mismatch_fault,
        keep_python_fallback=True,
        native_authority_denied=True,
        preserve_dispatch_fence_memory=True,
        preserve_shadow_memory=True,
        preserve_result_diff_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeFaultSealCapsule(**data)


def _seal(diff=None, shadow=None, dispatch=None, capsule=None):
    if diff is None:
        diff, _, shadow = _diff(shadow)
    dispatch = dispatch or FakeDispatchFence()
    cap = capsule or _seal_capsule(dispatch, shadow, diff)
    return assess_native_fault_seal(dispatch, shadow, diff, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def test_shadow_call_accepts_shadow_observation_without_native_authority():
    report, _, _ = _shadow()
    assert report.decision_kind == NativeShadowCallDecisionKind.ACCEPT_SHADOW_OBSERVATION
    assert report.accepted
    assert report.shadow_observation
    assert not report.native_result_authoritative
    assert report.python_fallback_active


def test_shadow_call_quarantines_native_authority_claim():
    dispatch = FakeDispatchFence()
    cap = _shadow_capsule(dispatch, native_result_selected=True, native_authority_claimed=True)
    report, _, _ = _shadow(dispatch, cap)
    assert report.decision_kind == NativeShadowCallDecisionKind.QUARANTINE_NATIVE_AUTHORITY_ATTEMPT
    assert report.quarantine


def test_result_diff_accepts_matching_shadow_result_as_evidence_only():
    report, _, _ = _diff()
    assert report.decision_kind == NativeResultDiffDecisionKind.ACCEPT_MATCH_AS_SHADOW_EVIDENCE
    assert report.accepted
    assert report.result_match
    assert report.python_result_authoritative


def test_result_diff_mismatch_quarantines_and_sets_fault_pressure():
    shadow, _, _ = _shadow(capsule=_shadow_capsule(native_result_digest=BAD_NATIVE_RESULT))
    cap = _diff_capsule(shadow, native_result_digest=BAD_NATIVE_RESULT, native_fault_digest=FAULT, results_match=False)
    report, _, _ = _diff(shadow, cap)
    assert report.decision_kind == NativeResultDiffDecisionKind.QUARANTINE_RESULT_MISMATCH
    assert report.quarantine
    assert report.mismatch_fault
    assert report.fault_memory


def test_fault_seal_can_seal_native_mismatch_to_python_fallback():
    dispatch = FakeDispatchFence()
    shadow, _, _ = _shadow(dispatch, _shadow_capsule(dispatch, native_result_digest=BAD_NATIVE_RESULT, native_fault_digest=FAULT))
    diff_cap = _diff_capsule(shadow, native_result_digest=BAD_NATIVE_RESULT, native_fault_digest=FAULT, results_match=False)
    diff, _, _ = _diff(shadow, diff_cap)
    seal_cap = _seal_capsule(dispatch, shadow, diff)
    report, _ = _seal(diff, shadow, dispatch, seal_cap)
    assert report.decision_kind == NativeFaultSealDecisionKind.ACCEPT_FAULT_SEALED_TO_FALLBACK
    assert report.accepted
    assert report.fault_sealed
    assert report.keep_python_fallback
    assert report.native_authority_denied


def test_fault_seal_rejects_digest_drift_and_memory_drop():
    dispatch = FakeDispatchFence()
    shadow, _, _ = _shadow(dispatch)
    diff, _, _ = _diff(shadow)
    drift = _seal_capsule(dispatch, shadow, diff, shadow_call_digest=sha256(b"wrong-shadow"))
    report, _ = _seal(diff, shadow, dispatch, drift)
    assert report.decision_kind == NativeFaultSealDecisionKind.QUARANTINE_DIGEST_DRIFT
    drop = _seal_capsule(dispatch, shadow, diff, keep_python_fallback=False)
    report, _ = _seal(diff, shadow, dispatch, drop)
    assert report.decision_kind == NativeFaultSealDecisionKind.QUARANTINE_MEMORY_DROP


def test_native_shadow_fold_audit_passes_current_surface():
    report = audit_native_shadow_fold(ROOT, revision="rev0094")
    assert report.status == "pass", report.findings
