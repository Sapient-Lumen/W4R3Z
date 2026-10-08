from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativeadmission import (
    NativeAdmissionCapsule,
    NativeAdmissionDecisionKind,
    assess_native_admission,
)
from i2p_dht_lab.nativecallledger import (
    NativeCallLedgerDecisionKind,
    NativeCallLedgerEntry,
    assess_native_call_ledger,
)
from i2p_dht_lab.nativesettlementfold import audit_native_settlement_fold
from i2p_dht_lab.nativeshadowsettlement import (
    NativeShadowSettlementCapsule,
    NativeShadowSettlementDecisionKind,
    assess_native_shadow_settlement,
)

ROOT = Path(__file__).resolve().parents[1]
ART = sha256(b"rev0095-artifact")
SRC = sha256(b"rev0095-source")
FB = sha256(b"rev0095-fallback")
ORACLE = sha256(b"rev0095-python-oracle")
CALL = sha256(b"rev0095-call-vector")
PY_RESULT = sha256(b"rev0095-python-result")
NATIVE_RESULT = PY_RESULT
FAULT = sha256(b"rev0095-fault")
BUDGET = sha256(b"rev0095-native-budget")
SANDBOX = sha256(b"rev0095-sandbox-stub")


@dataclass(frozen=True)
class FakeShadow:
    accepted: bool = True
    shadow_observation: bool = True
    tombstone_memory: bool = True
    fault_memory: bool = True
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    call_vector_digest: bytes = CALL
    python_result_digest: bytes = PY_RESULT
    native_result_digest: bytes = NATIVE_RESULT
    native_fault_digest: bytes = b""
    report_digest: bytes = sha256(b"rev0095-shadow-report")


@dataclass(frozen=True)
class FakeDiff:
    accepted: bool = True
    result_match: bool = True
    mismatch_fault: bool = False
    python_result_authoritative: bool = True
    tombstone_memory: bool = True
    fault_memory: bool = True
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    call_vector_digest: bytes = CALL
    python_result_digest: bytes = PY_RESULT
    native_result_digest: bytes = NATIVE_RESULT
    native_fault_digest: bytes = b""
    report_digest: bytes = sha256(b"rev0095-diff-report")


@dataclass(frozen=True)
class FakeSeal:
    accepted: bool = True
    fault_sealed: bool = False
    match_sealed: bool = True
    keep_python_fallback: bool = True
    native_authority_denied: bool = True
    tombstone_memory: bool = True
    fault_memory: bool = True
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    call_vector_digest: bytes = CALL
    python_result_digest: bytes = PY_RESULT
    native_result_digest: bytes = NATIVE_RESULT
    native_fault_digest: bytes = b""
    report_digest: bytes = sha256(b"rev0095-fault-seal-report")


def _settlement_capsule(shadow=None, diff=None, seal=None, **kw):
    shadow = shadow or FakeShadow()
    diff = diff or FakeDiff()
    seal = seal or FakeSeal()
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0095-shadow-settlement",
        sequence=1,
        previous_digest=b"",
        shadow_call_digest=shadow.report_digest,
        result_diff_digest=diff.report_digest,
        fault_seal_digest=seal.report_digest,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        python_result_digest=PY_RESULT,
        native_result_digest=NATIVE_RESULT,
        native_fault_digest=b"",
        result_match=True,
        fault_sealed=False,
        match_sealed=True,
        keep_python_fallback=True,
        native_authority_denied=True,
        native_authority_claimed=False,
        shadow_settlement_only=True,
        preserve_shadow_memory=True,
        preserve_result_diff_memory=True,
        preserve_fault_seal_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeShadowSettlementCapsule(**data)


def _settlement(shadow=None, diff=None, seal=None, capsule=None):
    shadow = shadow or FakeShadow()
    diff = diff or FakeDiff()
    seal = seal or FakeSeal()
    cap = capsule or _settlement_capsule(shadow, diff, seal)
    return assess_native_shadow_settlement(shadow, diff, seal, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def _admission_capsule(settlement, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0095-shadow-settlement",
        sequence=1,
        previous_digest=b"",
        settlement_digest=settlement.report_digest,
        native_budget_digest=BUDGET,
        sandbox_stub_digest=SANDBOX,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        allowed_component=True,
        side_effect_free_leaf=True,
        parser_surface=False,
        crypto_surface=False,
        transport_surface=False,
        persistence_surface=False,
        policy_surface=False,
        native_call_permission_requested=False,
        native_result_selection_requested=False,
        python_fallback_active=True,
        shadow_slot_only=True,
        preserve_settlement_memory=True,
        preserve_budget_memory=True,
        preserve_sandbox_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeAdmissionCapsule(**data)


def _admission(settlement=None, capsule=None):
    if settlement is None:
        settlement, _ = _settlement()
    cap = capsule or _admission_capsule(settlement)
    return assess_native_admission(settlement, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def _ledger_entry(admission, settlement, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0095-shadow-settlement",
        sequence=1,
        previous_digest=b"",
        admission_digest=admission.report_digest,
        settlement_digest=settlement.report_digest,
        fault_seal_digest=FakeSeal().report_digest,
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
        python_result_authoritative=True,
        preserve_admission_memory=True,
        preserve_settlement_memory=True,
        preserve_fault_seal_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeCallLedgerEntry(**data)


def _ledger(admission=None, settlement=None, entry=None):
    if settlement is None:
        settlement, _ = _settlement()
    if admission is None:
        admission, _ = _admission(settlement)
    ent = entry or _ledger_entry(admission, settlement)
    return assess_native_call_ledger(admission, ent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), ent


def test_shadow_settlement_accepts_matching_result_as_evidence_only():
    report, _ = _settlement()
    assert report.decision_kind == NativeShadowSettlementDecisionKind.ACCEPT_SHADOW_SETTLED_EVIDENCE
    assert report.accepted
    assert report.shadow_settled
    assert not report.native_call_permission
    assert not report.native_result_authoritative


def test_shadow_settlement_quarantines_mismatch_and_authority_claims():
    bad_diff = FakeDiff(result_match=False, mismatch_fault=True, native_fault_digest=FAULT)
    bad_seal = FakeSeal(fault_sealed=True, match_sealed=False, native_fault_digest=FAULT)
    cap = _settlement_capsule(diff=bad_diff, seal=bad_seal, result_match=False, fault_sealed=True, match_sealed=False, native_fault_digest=FAULT)
    report, _ = _settlement(diff=bad_diff, seal=bad_seal, capsule=cap)
    assert report.decision_kind == NativeShadowSettlementDecisionKind.QUARANTINE_RESULT_MISMATCH_OR_FAULT
    authority = _settlement_capsule(native_authority_claimed=True, shadow_settlement_only=False)
    report, _ = _settlement(capsule=authority)
    assert report.decision_kind == NativeShadowSettlementDecisionKind.QUARANTINE_NATIVE_AUTHORITY_ATTEMPT


def test_admission_accepts_shadow_slot_but_not_native_permission():
    settlement, _ = _settlement()
    report, _ = _admission(settlement)
    assert report.decision_kind == NativeAdmissionDecisionKind.ACCEPT_SHADOW_ADMISSION_HELD
    assert report.accepted
    assert report.admitted_to_shadow_slot
    assert not report.native_call_permission
    assert not report.native_result_selection


def test_admission_rejects_parser_surface_and_call_permission():
    settlement, _ = _settlement()
    cap = _admission_capsule(settlement, parser_surface=True)
    report, _ = _admission(settlement, cap)
    assert report.decision_kind == NativeAdmissionDecisionKind.QUARANTINE_FORBIDDEN_SURFACE
    cap = _admission_capsule(settlement, native_call_permission_requested=True)
    report, _ = _admission(settlement, cap)
    assert report.decision_kind == NativeAdmissionDecisionKind.QUARANTINE_NATIVE_CALL_PERMISSION


def test_call_ledger_accepts_python_route_and_rejects_native_execution():
    settlement, _ = _settlement()
    admission, _ = _admission(settlement)
    report, _ = _ledger(admission, settlement)
    assert report.decision_kind == NativeCallLedgerDecisionKind.ACCEPT_LEDGERED_PYTHON_ROUTE
    assert report.accepted
    assert report.python_route_ledgered
    assert not report.native_call_permission
    assert not report.native_result_authoritative
    native_entry = _ledger_entry(admission, settlement, native_call_executed=True, native_result_selected=True, route="native")
    report, _ = _ledger(admission, settlement, native_entry)
    assert report.decision_kind == NativeCallLedgerDecisionKind.QUARANTINE_NATIVE_AUTHORITY


def test_call_ledger_previous_link_and_digest_drift_are_pinned():
    settlement, _ = _settlement()
    admission, _ = _admission(settlement)
    first = _ledger_entry(admission, settlement)
    second = replace(first, sequence=2, previous_digest=sha256(b"wrong-prev"))
    report = assess_native_call_ledger(admission, second, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert report.decision_kind == NativeCallLedgerDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    drift = _ledger_entry(admission, settlement, admission_digest=sha256(b"wrong-admission"))
    report, _ = _ledger(admission, settlement, drift)
    assert report.decision_kind == NativeCallLedgerDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_native_settlement_fold_audit_passes_current_surface():
    report = audit_native_settlement_fold(ROOT, revision="rev0095")
    assert report.status == "pass", report.findings
