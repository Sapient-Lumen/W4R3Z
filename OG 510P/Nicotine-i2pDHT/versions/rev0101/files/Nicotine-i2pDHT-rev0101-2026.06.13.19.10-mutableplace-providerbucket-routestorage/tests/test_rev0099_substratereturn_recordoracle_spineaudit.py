from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativefoldspine import audit_native_fold_spine
from i2p_dht_lab.recordplaneoracle import (
    RecordPlaneOracleCapsule,
    RecordPlaneOracleDecisionKind,
    assess_record_plane_oracle,
)
from i2p_dht_lab.substratereentry import (
    SubstrateReentryCapsule,
    SubstrateReentryDecisionKind,
    assess_substrate_reentry,
)
from i2p_dht_lab.substratereturnfold import audit_substrate_return_fold

ROOT = Path(__file__).resolve().parents[1]
BRANCH = sha256(b"rev0099-native-branch-close")
POLICY = sha256(b"rev0099-native-shadow-policy")


@dataclass(frozen=True)
class FakeNativeBranchClose:
    accepted: bool = True
    branch_closed: bool = True
    shadow_only: bool = True
    python_fallback_authoritative: bool = True
    native_permission: bool = False
    report_digest: bytes = BRANCH


@dataclass(frozen=True)
class FakeNativePolicy:
    accepted: bool = True
    shadow_only: bool = True
    native_dispatch_permission: bool = False
    report_digest: bytes = POLICY


def _oracle_capsule(**kw):
    data = dict(
        component="record-plane",
        profile="generic-i2p-dht",
        operation="record-truth-boundary",
        request_id="rev0099-substrate-return",
        sequence=1,
        previous_digest=b"",
        native_branch_close_digest=BRANCH,
        native_policy_digest=POLICY,
        record_namespace="dht.records",
        record_scope="generic-record-plane",
        policy_mode="python_record_truth",
        python_validators_own_records=True,
        python_mutable_heads_own_latest=True,
        python_provider_proofs_own_semantics=True,
        python_parser_owns_untrusted_bytes=True,
        python_crypto_owns_signatures=True,
        python_transport_owns_sessions=True,
        python_persistence_owns_finality=True,
        native_record_parser_allowed=False,
        native_record_validator_allowed=False,
        native_mutable_truth_allowed=False,
        native_provider_truth_allowed=False,
        native_transport_allowed=False,
        native_persistence_allowed=False,
        preserve_native_branch_close_memory=True,
        preserve_native_policy_memory=True,
        preserve_mutable_head_memory=True,
        preserve_provider_false_memory=True,
        preserve_tombstone_memory=True,
        preserve_witness_memory=True,
        preserve_garden_refusal_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return RecordPlaneOracleCapsule(**data)


def _oracle(capsule=None, branch=None, policy=None):
    return assess_record_plane_oracle(
        branch or FakeNativeBranchClose(),
        policy or FakeNativePolicy(),
        capsule or _oracle_capsule(),
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _substrate_capsule(oracle_report, spine_report, **kw):
    data = dict(
        component="substrate-return",
        profile="generic-i2p-dht",
        operation="return-to-dht-design",
        request_id="rev0099-substrate-return",
        sequence=1,
        previous_digest=b"",
        native_branch_close_digest=BRANCH,
        record_plane_oracle_digest=oracle_report.report_digest,
        native_fold_spine_digest=spine_report.report_digest,
        substrate_scope="generic-i2p-dht-substrate",
        branch_state="native-shadow-branch-closed",
        python_protocol_truth=True,
        native_branch_closed_shadow_only=True,
        native_permissions_closed=True,
        return_to_record_plane=True,
        return_to_mutable_plane=True,
        return_to_provider_plane=True,
        return_to_routing_plane=True,
        require_new_native_branch_for_promotion=True,
        preserve_native_branch_close_memory=True,
        preserve_native_fold_spine_memory=True,
        preserve_record_plane_oracle_memory=True,
        preserve_mutable_head_memory=True,
        preserve_provider_false_memory=True,
        preserve_witness_memory=True,
        preserve_tombstone_memory=True,
        preserve_garden_refusal_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return SubstrateReentryCapsule(**data)


def _substrate(capsule=None, oracle_report=None, spine_report=None, branch=None):
    oracle_report = oracle_report or _oracle()
    spine_report = spine_report or audit_native_fold_spine(ROOT, revision="rev0099")
    return assess_substrate_reentry(
        branch or FakeNativeBranchClose(),
        oracle_report,
        spine_report,
        capsule or _substrate_capsule(oracle_report, spine_report),
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )


def test_record_plane_oracle_accepts_python_owned_records_after_native_close():
    report = _oracle()
    assert report.decision_kind == RecordPlaneOracleDecisionKind.ACCEPT_PYTHON_RECORD_ORACLE
    assert report.accepted
    assert report.python_record_truth
    assert not report.native_record_permission


def test_record_plane_oracle_rejects_native_record_or_provider_truth_permission():
    report = _oracle(_oracle_capsule(native_record_validator_allowed=True))
    assert report.decision_kind == RecordPlaneOracleDecisionKind.QUARANTINE_FORBIDDEN_NATIVE_SURFACE
    report = _oracle(_oracle_capsule(native_provider_truth_allowed=True))
    assert report.decision_kind == RecordPlaneOracleDecisionKind.QUARANTINE_FORBIDDEN_NATIVE_SURFACE


def test_record_plane_oracle_detects_digest_drift_memory_drop_and_sequence_pressure():
    report = _oracle(_oracle_capsule(native_branch_close_digest=sha256(b"wrong-branch")))
    assert report.decision_kind == RecordPlaneOracleDecisionKind.QUARANTINE_DIGEST_DRIFT
    report = _oracle(_oracle_capsule(preserve_provider_false_memory=False))
    assert report.decision_kind == RecordPlaneOracleDecisionKind.QUARANTINE_MEMORY_DROP
    first = _oracle_capsule()
    second = replace(first, sequence=2, previous_digest=sha256(b"wrong-prev"))
    report = assess_record_plane_oracle(
        FakeNativeBranchClose(), FakeNativePolicy(), second, previous=first,
        observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == RecordPlaneOracleDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH


def test_substrate_reentry_accepts_return_to_dht_substrate_after_record_oracle_and_native_spine():
    report = _substrate()
    assert report.decision_kind == SubstrateReentryDecisionKind.ACCEPT_RETURN_TO_DHT_SUBSTRATE
    assert report.accepted
    assert report.substrate_reentered
    assert report.python_protocol_truth
    assert not report.native_permission_leak


def test_substrate_reentry_rejects_native_permission_leak_digest_drift_and_memory_drop():
    oracle = _oracle()
    spine = audit_native_fold_spine(ROOT, revision="rev0099")
    capsule = _substrate_capsule(oracle, spine, native_permissions_closed=False)
    report = _substrate(capsule, oracle, spine)
    assert report.decision_kind == SubstrateReentryDecisionKind.QUARANTINE_NATIVE_PERMISSION_LEAK
    capsule = _substrate_capsule(oracle, spine, record_plane_oracle_digest=sha256(b"wrong-oracle"))
    report = _substrate(capsule, oracle, spine)
    assert report.decision_kind == SubstrateReentryDecisionKind.QUARANTINE_DIGEST_DRIFT
    capsule = _substrate_capsule(oracle, spine, preserve_tombstone_memory=False)
    report = _substrate(capsule, oracle, spine)
    assert report.decision_kind == SubstrateReentryDecisionKind.QUARANTINE_MEMORY_DROP


def test_substrate_reentry_holds_if_record_oracle_or_native_close_not_ready():
    oracle = _oracle(policy=FakeNativePolicy(accepted=False, shadow_only=False))
    spine = audit_native_fold_spine(ROOT, revision="rev0099")
    capsule = _substrate_capsule(oracle, spine)
    report = _substrate(capsule, oracle, spine)
    assert report.decision_kind == SubstrateReentryDecisionKind.HOLD_COMPONENT_NOT_READY
    oracle = _oracle()
    capsule = _substrate_capsule(oracle, spine)
    report = _substrate(capsule, oracle, spine, branch=FakeNativeBranchClose(accepted=True, branch_closed=True, native_permission=True))
    assert report.decision_kind == SubstrateReentryDecisionKind.QUARANTINE_NATIVE_PERMISSION_LEAK


def test_substrate_reentry_detects_replay_fork_and_low_diversity():
    oracle = _oracle()
    spine = audit_native_fold_spine(ROOT, revision="rev0099")
    first = _substrate_capsule(oracle, spine)
    second = replace(first, note="same-sequence-different")
    report = assess_substrate_reentry(
        FakeNativeBranchClose(), oracle, spine, second, previous=first,
        observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == SubstrateReentryDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    report = assess_substrate_reentry(
        FakeNativeBranchClose(), oracle, spine, first,
        observed_families=("family-a",), observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == SubstrateReentryDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_native_spine_and_substrate_return_fold_current_path_pass():
    spine = audit_native_fold_spine(ROOT, revision="rev0099")
    assert spine.status == "pass", spine.findings
    assert spine.checked_count >= 19
    fold = audit_substrate_return_fold(ROOT, revision="rev0099")
    assert fold.status == "pass", fold.findings
