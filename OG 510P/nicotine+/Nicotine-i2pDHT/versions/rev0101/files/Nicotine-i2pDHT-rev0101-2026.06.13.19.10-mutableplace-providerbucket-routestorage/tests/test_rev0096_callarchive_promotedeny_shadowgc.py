from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativearchivefold import audit_native_archive_fold
from i2p_dht_lab.nativecallarchive import (
    NativeCallArchiveDecisionKind,
    NativeCallArchiveEntry,
    assess_native_call_archive,
)
from i2p_dht_lab.nativepromotiondeny import (
    NativePromotionDenyCapsule,
    NativePromotionDenyDecisionKind,
    assess_native_promotion_deny,
)
from i2p_dht_lab.nativeshadowgc import (
    NativeShadowGCDecisionKind,
    NativeShadowGCProposal,
    assess_native_shadow_gc,
)

ROOT = Path(__file__).resolve().parents[1]
ART = sha256(b"rev0096-artifact")
SRC = sha256(b"rev0096-source")
FB = sha256(b"rev0096-fallback")
ORACLE = sha256(b"rev0096-python-oracle")
CALL = sha256(b"rev0096-call-vector")
PY_RESULT = sha256(b"rev0096-python-result")
NATIVE_RESULT = PY_RESULT
ADMISSION = sha256(b"rev0096-admission")
SETTLEMENT = sha256(b"rev0096-settlement")
FAULT_SEAL = sha256(b"rev0096-fault-seal")


@dataclass(frozen=True)
class FakeCallLedger:
    accepted: bool = True
    python_route_ledgered: bool = True
    native_call_permission: bool = False
    native_result_authoritative: bool = False
    tombstone_memory: bool = True
    fault_memory: bool = True
    admission_digest: bytes = ADMISSION
    settlement_digest: bytes = SETTLEMENT
    fault_seal_digest: bytes = FAULT_SEAL
    report_digest: bytes = sha256(b"rev0096-call-ledger")


def _archive_entry(ledger: FakeCallLedger | None = None, **kw):
    ledger = ledger or FakeCallLedger()
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0096-native-archive",
        sequence=1,
        previous_digest=b"",
        call_ledger_digest=ledger.report_digest,
        admission_digest=ADMISSION,
        settlement_digest=SETTLEMENT,
        fault_seal_digest=FAULT_SEAL,
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
        archive_call_ledger_memory=True,
        archive_admission_memory=True,
        archive_settlement_memory=True,
        archive_fault_seal_memory=True,
        archive_python_oracle_memory=True,
        archive_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeCallArchiveEntry(**data)


def _archive(ledger: FakeCallLedger | None = None, entry: NativeCallArchiveEntry | None = None):
    ledger = ledger or FakeCallLedger()
    ent = entry or _archive_entry(ledger)
    return assess_native_call_archive(ledger, ent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), ent


def _deny_capsule(archive, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0096-native-archive",
        sequence=1,
        previous_digest=b"",
        call_archive_digest=archive.report_digest,
        call_ledger_digest=archive.call_ledger_digest,
        admission_digest=ADMISSION,
        settlement_digest=SETTLEMENT,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        repeated_shadow_match_count=9,
        promotion_requested=True,
        deny_promotion=True,
        native_call_permission_requested=False,
        native_result_authority_requested=False,
        operator_override_requested=False,
        keep_python_fallback=True,
        require_future_human_audit=True,
        preserve_call_archive_memory=True,
        preserve_call_ledger_memory=True,
        preserve_admission_memory=True,
        preserve_settlement_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativePromotionDenyCapsule(**data)


def _denial(archive=None, capsule=None):
    archive = archive or _archive()[0]
    cap = capsule or _deny_capsule(archive)
    return assess_native_promotion_deny(archive, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def _gc_proposal(archive, denial, **kw):
    data = dict(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0096-native-archive",
        sequence=1,
        previous_digest=b"",
        call_archive_digest=archive.report_digest,
        promotion_denial_digest=denial.report_digest,
        call_ledger_digest=archive.call_ledger_digest,
        admission_digest=ADMISSION,
        settlement_digest=SETTLEMENT,
        artifact_digest=ART,
        source_digest=SRC,
        fallback_digest=FB,
        python_oracle_digest=ORACLE,
        call_vector_digest=CALL,
        soft_shadow_vectors_before=128,
        soft_shadow_vectors_after=8,
        preserve_summary_marker=True,
        preserve_call_archive_memory=True,
        preserve_promotion_denial_memory=True,
        preserve_call_ledger_memory=True,
        preserve_python_route_memory=True,
        preserve_python_oracle_memory=True,
        preserve_fallback_memory=True,
        preserve_tombstone_memory=True,
        preserve_quarantine_memory=True,
        preserve_crash_memory=True,
        drop_required_memory=False,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return NativeShadowGCProposal(**data)


def _gc(archive=None, denial=None, proposal=None):
    archive = archive or _archive()[0]
    denial = denial or _denial(archive)[0]
    prop = proposal or _gc_proposal(archive, denial)
    return assess_native_shadow_gc(archive, denial, prop, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), prop


def test_archive_accepts_python_route_and_no_native_authority():
    report, _ = _archive()
    assert report.decision_kind == NativeCallArchiveDecisionKind.ACCEPT_CALL_ARCHIVED
    assert report.accepted
    assert report.call_archived
    assert report.python_route_archived
    assert not report.native_call_permission
    assert not report.native_result_authoritative


def test_archive_quarantines_native_result_selection():
    entry = _archive_entry(native_result_selected=True)
    report, _ = _archive(entry=entry)
    assert report.decision_kind == NativeCallArchiveDecisionKind.QUARANTINE_NATIVE_ROUTE_OR_AUTHORITY
    assert report.quarantine


def test_promotion_denial_accepts_repeated_match_as_denied_evidence():
    archive, _ = _archive()
    denial, _ = _denial(archive)
    assert denial.decision_kind == NativePromotionDenyDecisionKind.ACCEPT_PROMOTION_DENIED
    assert denial.accepted
    assert denial.promotion_denied
    assert not denial.native_call_permission
    assert denial.python_fallback_active


def test_promotion_denial_quarantines_operator_override_or_native_permission():
    archive, _ = _archive()
    capsule = _deny_capsule(archive, native_call_permission_requested=True, operator_override_requested=True)
    denial, _ = _denial(archive, capsule)
    assert denial.decision_kind == NativePromotionDenyDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT
    assert denial.quarantine


def test_shadow_gc_compacts_soft_vectors_but_keeps_denial_and_python_route():
    archive, _ = _archive()
    denial, _ = _denial(archive)
    gc, _ = _gc(archive, denial)
    assert gc.decision_kind == NativeShadowGCDecisionKind.ACCEPT_SOFT_SHADOW_COMPACTION
    assert gc.accepted
    assert gc.soft_compacted
    assert gc.python_route_preserved
    assert gc.native_promotion_still_denied
    assert gc.soft_shadow_vectors_after < gc.soft_shadow_vectors_before


def test_shadow_gc_quarantines_required_memory_drop():
    archive, _ = _archive()
    denial, _ = _denial(archive)
    proposal = _gc_proposal(archive, denial, preserve_promotion_denial_memory=False)
    gc, _ = _gc(archive, denial, proposal)
    assert gc.decision_kind == NativeShadowGCDecisionKind.QUARANTINE_REQUIRED_MEMORY_DROP
    assert gc.quarantine


def test_replay_and_previous_link_pressure_on_gc():
    archive, _ = _archive()
    denial, _ = _denial(archive)
    first = _gc_proposal(archive, denial)
    second = replace(first, sequence=2, previous_digest=sha256(b"wrong-prev"))
    gc = assess_native_shadow_gc(archive, denial, second, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert gc.decision_kind == NativeShadowGCDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH


def test_native_archive_fold_current_path_passes():
    report = audit_native_archive_fold(ROOT, revision="rev0096")
    assert report.status == "pass", report.findings
