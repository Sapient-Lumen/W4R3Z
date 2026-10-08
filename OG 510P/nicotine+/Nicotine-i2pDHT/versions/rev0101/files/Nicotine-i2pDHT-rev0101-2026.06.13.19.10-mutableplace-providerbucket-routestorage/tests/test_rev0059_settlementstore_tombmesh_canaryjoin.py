from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.canaryjoin import CanaryJoinDecisionKind, assess_canary_join
from i2p_dht_lab.finalityledger import FinalityLedgerDecisionKind, FinalityMarkerKind
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.pruneguard import PruneGuardDecisionKind
from i2p_dht_lab.retryescrow import RetryEscrowDecisionKind
from i2p_dht_lab.settlementlane import SettlementDecisionKind, SettlementKind
from i2p_dht_lab.settlementstore import SettlementStoreDecisionKind, assess_settlement_store
from i2p_dht_lab.settlementstorefold import audit_settlementstore_fold
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectPhase
from i2p_dht_lab.tombrepairjoin import TombRepairJoinDecisionKind, assess_tomb_repair_join
from i2p_dht_lab.tombstonerepair import TombstoneRepairDecisionKind

PROFILE = "rev0059-profile"
SERVICE = "rev0059-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0059:scope")
REQUEST = sha256(DOMAIN + b":rev0059:request")
PAYLOAD = sha256(DOMAIN + b":rev0059:payload")
IDEM = sha256(DOMAIN + b":rev0059:idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0059-test:" + label.encode())


def report(label: str, **kw):
    base = dict(
        report_digest=d(label),
        accept=True,
        watch=False,
        quarantined=False,
        action=ACTION,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        family_count=2,
        path_family_count=2,
        hard_negative_count=0,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def terminal_components():
    finality = report(
        "finality-terminal",
        decision_kind=FinalityLedgerDecisionKind.ACCEPT_TERMINAL_COMMIT,
        marker_kind=FinalityMarkerKind.TERMINAL_COMMIT,
        terminal=True,
        final_phase=SideEffectPhase.COMMIT,
        retry_required=False,
        dead_letter_required=False,
        accepted_marker_digest=d("accepted-finality"),
    )
    settlement = report(
        "settlement-terminal",
        decision_kind=SettlementDecisionKind.ACCEPT_TERMINAL_SETTLEMENT,
        settlement_kind=SettlementKind.COMMIT_SETTLED,
        final_phase=SideEffectPhase.COMMIT,
        retry_required=False,
        dead_letter_required=False,
    )
    attestation = report("attestation", role_digests=())
    prune = report("prune", decision_kind=PruneGuardDecisionKind.ACCEPT_TERMINAL_SOFT_PRUNE)
    tomb = report(
        "tombrepair-zero",
        decision_kind=TombstoneRepairDecisionKind.ACCEPT_NO_LIVE_TOMBSTONES,
        carried_tombstone_count=0,
        live_tombstone_count=0,
        resurrection_count=0,
    )
    return finality, settlement, attestation, prune, tomb


def retry_components():
    finality = report(
        "finality-retry",
        decision_kind=FinalityLedgerDecisionKind.ACCEPT_RETRY_PENDING,
        marker_kind=FinalityMarkerKind.RETRY_PENDING,
        terminal=False,
        watch=True,
        final_phase=None,
        retry_required=True,
        dead_letter_required=True,
        accepted_marker_digest=d("accepted-retry-finality"),
    )
    settlement = report(
        "settlement-retry",
        decision_kind=SettlementDecisionKind.ACCEPT_RETRY_HOLD,
        settlement_kind=SettlementKind.RETRY_HELD,
        watch=True,
        final_phase=None,
        retry_required=True,
        dead_letter_required=True,
    )
    attestation = report("attestation-retry")
    prune = report("prune-retry", decision_kind=PruneGuardDecisionKind.ACCEPT_PENDING_HOLD, watch=True)
    retry = report("retry-escrow", decision_kind=RetryEscrowDecisionKind.ACCEPT_RETRY_ESCROW, watch=True, accepted_ticket_digest=d("ticket"), carried_dead_letter_digest=d("dead"))
    tomb = report(
        "tombrepair-retry",
        decision_kind=TombstoneRepairDecisionKind.ACCEPT_REPAIR_COVERAGE,
        carried_tombstone_count=2,
        live_tombstone_count=2,
        resurrection_count=0,
        watch=False,
    )
    return finality, settlement, attestation, prune, retry, tomb


def test_settlement_store_accepts_terminal_branch_join() -> None:
    finality, settlement, attestation, prune, tomb = terminal_components()
    store = assess_settlement_store(finality_report=finality, settlement_report=settlement, attestation_pack_report=attestation, prune_guard_report=prune, tombstone_repair_report=tomb)
    assert store.decision_kind is SettlementStoreDecisionKind.ACCEPT_TERMINAL_STORE
    assert store.accept and store.terminal and not store.watch
    assert store.finality_digest == finality.report_digest
    assert store.settlement_digest == settlement.report_digest


def test_settlement_store_rejects_finality_settlement_semantic_drift() -> None:
    finality, _, attestation, prune, tomb = terminal_components()
    _, retry_settlement, _, _, retry, _ = retry_components()
    drift = assess_settlement_store(finality_report=finality, settlement_report=retry_settlement, attestation_pack_report=attestation, prune_guard_report=prune, tombstone_repair_report=tomb, retry_escrow_report=retry)
    assert drift.decision_kind is SettlementStoreDecisionKind.QUARANTINE_FINALITY_SETTLEMENT_DRIFT


def test_settlement_store_keeps_retry_watch_with_escrow_and_rejects_missing_escrow() -> None:
    finality, settlement, attestation, prune, retry, tomb = retry_components()
    missing = assess_settlement_store(finality_report=finality, settlement_report=settlement, attestation_pack_report=attestation, prune_guard_report=prune, tombstone_repair_report=tomb)
    assert missing.decision_kind is SettlementStoreDecisionKind.QUARANTINE_RETRY_WITHOUT_ESCROW
    store = assess_settlement_store(finality_report=finality, settlement_report=settlement, attestation_pack_report=attestation, prune_guard_report=prune, tombstone_repair_report=tomb, retry_escrow_report=retry)
    assert store.decision_kind is SettlementStoreDecisionKind.ACCEPT_RETRY_HELD_STORE
    assert store.accept and store.watch and not store.terminal


def test_tomb_repair_join_holds_missing_and_rejects_resurrection() -> None:
    finality, settlement, attestation, prune, retry, tomb = retry_components()
    store = assess_settlement_store(finality_report=finality, settlement_report=settlement, attestation_pack_report=attestation, prune_guard_report=prune, tombstone_repair_report=tomb, retry_escrow_report=retry)
    missing = assess_tomb_repair_join(settlement_store_report=store, tombstone_repair_report=None, prune_guard_report=prune, expected_live_tombstone_count=2)
    assert missing.decision_kind is TombRepairJoinDecisionKind.HOLD_MISSING_REPAIR

    bad_tomb = report("bad-tomb", decision_kind=TombstoneRepairDecisionKind.QUARANTINE_RESURRECTION_PRESSURE, carried_tombstone_count=2, live_tombstone_count=2, resurrection_count=1)
    bad = assess_tomb_repair_join(settlement_store_report=store, tombstone_repair_report=bad_tomb, prune_guard_report=prune, expected_live_tombstone_count=2)
    assert bad.decision_kind is TombRepairJoinDecisionKind.QUARANTINE_RESURRECTION_PRESSURE

    good = assess_tomb_repair_join(settlement_store_report=store, tombstone_repair_report=tomb, prune_guard_report=prune, expected_live_tombstone_count=2)
    assert good.decision_kind is TombRepairJoinDecisionKind.ACCEPT_REPAIR_CARRIED


def test_canary_join_requires_tomb_join_and_retry_escrow_for_watchful_store() -> None:
    finality, settlement, attestation, prune, retry, tomb = retry_components()
    store = assess_settlement_store(finality_report=finality, settlement_report=settlement, attestation_pack_report=attestation, prune_guard_report=prune, tombstone_repair_report=tomb, retry_escrow_report=retry)
    sam = report("sam-canary", watch=False)
    router = report("router-canary", watch=False)
    without_tomb = assess_canary_join(settlement_store_report=store, tomb_repair_join_report=None, sam_canary_report=sam, router_canary_report=router, retry_escrow_report=retry)
    assert without_tomb.decision_kind is CanaryJoinDecisionKind.QUARANTINE_CANARY_WITHOUT_TOMB_JOIN

    tomb_join = assess_tomb_repair_join(settlement_store_report=store, tombstone_repair_report=tomb, prune_guard_report=prune, expected_live_tombstone_count=2)
    accepted = assess_canary_join(settlement_store_report=store, tomb_repair_join_report=tomb_join, sam_canary_report=sam, router_canary_report=router, retry_escrow_report=retry)
    assert accepted.decision_kind is CanaryJoinDecisionKind.ACCEPT_RETRY_CANARY_READY
    assert accepted.accept and accepted.watch


def test_canary_join_rejects_terminal_with_retry_escrow() -> None:
    finality, settlement, attestation, prune, tomb = terminal_components()
    store = assess_settlement_store(finality_report=finality, settlement_report=settlement, attestation_pack_report=attestation, prune_guard_report=prune, tombstone_repair_report=tomb)
    tomb_join = assess_tomb_repair_join(settlement_store_report=store, tombstone_repair_report=tomb, prune_guard_report=prune, expected_live_tombstone_count=0)
    sam = report("sam-canary-terminal")
    router = report("router-canary-terminal")
    retry = report("unexpected-retry-escrow", decision_kind=RetryEscrowDecisionKind.ACCEPT_RETRY_ESCROW, watch=True)
    bad = assess_canary_join(settlement_store_report=store, tomb_repair_join_report=tomb_join, sam_canary_report=sam, router_canary_report=router, retry_escrow_report=retry)
    assert bad.decision_kind is CanaryJoinDecisionKind.QUARANTINE_TERMINAL_HAS_RETRY_ESCROW


def test_settlementstorefold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_settlementstore_fold(root, revision="rev0059", artifact_stem=root.name)
    assert report.status == "pass", report.findings
