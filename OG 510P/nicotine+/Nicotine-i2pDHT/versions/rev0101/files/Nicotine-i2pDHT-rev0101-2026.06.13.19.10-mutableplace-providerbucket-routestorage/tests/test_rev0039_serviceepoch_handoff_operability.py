from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.servicecontinuity import ServiceContinuitySignal
from i2p_dht_lab.serviceepochledger import (
    ServiceEpochLedgerDecisionKind,
    ServiceEpochLedgerPolicy,
    ServiceEpochObservation,
    ServiceEpochOutcome,
    assess_service_epoch_ledger,
)
from i2p_dht_lab.servicehandoffledger import (
    ServiceHandoffDecisionKind,
    ServiceHandoffWitness,
    assess_service_handoff,
)
from i2p_dht_lab.serviceoperabilityfold import audit_serviceoperability_fold


def d(label: str) -> bytes:
    return sha256(("rev0039:" + label).encode("utf-8"))


CATALOG = d("catalog")
SCOPE = d("scope")
REQUEST = d("request")
SUCCESSOR = d("successor")
WITHDRAWAL = d("withdrawal")
ROUTE = d("route")
NOW = 1_000


def obs(epoch: int, outcome: ServiceEpochOutcome = ServiceEpochOutcome.COMPLETED, *, family: str = "fam-a", catalog: bytes = CATALOG, scope: bytes = SCOPE, request: bytes = REQUEST, branch_count: int = 6, expires: int = 2_000, report: bytes | None = None) -> ServiceEpochObservation:
    return ServiceEpochObservation(
        epoch=epoch,
        observed_at=900 + epoch,
        expires_at=expires,
        service_name="head_watch",
        catalog_digest=catalog,
        scope_digest=scope,
        request_digest=request,
        report_digest=report or d(f"obs:{epoch}:{outcome.value}:{family}"),
        outcome=outcome,
        branch_count=branch_count,
        family_id=family,
    )


def stable_epoch_report():
    return assess_service_epoch_ledger(
        (obs(10, family="fam-a"), obs(11, family="fam-b"), obs(12, family="fam-c")),
        now=NOW,
        expected_service_name="head_watch",
        expected_catalog_digest=CATALOG,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
    )


def test_service_epoch_ledger_accepts_stable_multi_epoch_service() -> None:
    report = stable_epoch_report()
    assert report.decision_kind is ServiceEpochLedgerDecisionKind.ACCEPT_STABLE_SERVICE
    assert report.accept
    assert report.completed_epochs == 3
    assert report.families == ("fam-a", "fam-b", "fam-c")


def test_service_epoch_ledger_detects_replay_rollback_fork_and_gap() -> None:
    first = obs(10, family="fam-a")
    report = assess_service_epoch_ledger((first, obs(11, family="fam-b"), obs(12, family="fam-c")), now=NOW, previously_seen_reports=(first.report_digest,))
    assert report.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_REPLAY

    rollback = assess_service_epoch_ledger((obs(5), obs(6), obs(7)), now=NOW, previous_highest_epoch=12)
    assert rollback.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_EPOCH_ROLLBACK

    fork = assess_service_epoch_ledger((obs(10, report=d("fork-a")), obs(10, report=d("fork-b")), obs(11, family="fam-b")), now=NOW)
    assert fork.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_EPOCH_FORK

    gap = assess_service_epoch_ledger((obs(10), obs(13, family="fam-b"), obs(14, family="fam-c")), now=NOW)
    assert gap.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_GAP


def test_service_epoch_ledger_blocks_withdrawal_drift_expiry_and_weak_branch() -> None:
    withdrawal = assess_service_epoch_ledger((obs(10), obs(11, ServiceEpochOutcome.ACTIVE_WITHDRAWAL, family="fam-b"), obs(12, family="fam-c")), now=NOW)
    assert withdrawal.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_ACTIVE_WITHDRAWAL

    drift = assess_service_epoch_ledger((obs(10), obs(11, family="fam-b", catalog=d("other-catalog")), obs(12, family="fam-c")), now=NOW, expected_catalog_digest=CATALOG)
    assert drift.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_CATALOG_DRIFT

    expired = assess_service_epoch_ledger((obs(10, expires=995), obs(11, family="fam-b"), obs(12, family="fam-c")), now=NOW)
    assert expired.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE

    weak = assess_service_epoch_ledger((obs(10), obs(11, family="fam-b", branch_count=2), obs(12, family="fam-c")), now=NOW)
    assert weak.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_BRANCH_REPORT


def test_service_epoch_ledger_refusal_loop_watch_and_partial_acceptance() -> None:
    refusals = assess_service_epoch_ledger(
        (obs(10, ServiceEpochOutcome.USEFUL_REFUSAL), obs(11, ServiceEpochOutcome.USEFUL_REFUSAL, family="fam-b"), obs(12, ServiceEpochOutcome.USEFUL_REFUSAL, family="fam-c")),
        now=NOW,
    )
    assert refusals.decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP

    watch_only = assess_service_epoch_ledger(
        (obs(10, ServiceEpochOutcome.WATCH_ONLY), obs(11, ServiceEpochOutcome.WATCH_ONLY, family="fam-b"), obs(12, ServiceEpochOutcome.WATCH_ONLY, family="fam-c")),
        now=NOW,
    )
    assert watch_only.decision_kind is ServiceEpochLedgerDecisionKind.HOLD_WATCH_ONLY

    partial = assess_service_epoch_ledger(
        (obs(10, family="fam-a"), obs(11, ServiceEpochOutcome.WATCH_ONLY, family="fam-b"), obs(12, ServiceEpochOutcome.USEFUL_REFUSAL, family="fam-c")),
        now=NOW,
        policy=ServiceEpochLedgerPolicy(min_epochs=3, min_completed_epochs=2, min_distinct_families=2),
    )
    assert partial.decision_kind is ServiceEpochLedgerDecisionKind.ACCEPT_WITH_WATCH
    assert partial.accept


def test_service_epoch_observation_from_continuity_signals_classifies_outcomes() -> None:
    signal = ServiceContinuitySignal(
        branch="ticket",
        report_digest=d("ticket-report"),
        accept=True,
        catalog_digest=CATALOG,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        service_name="head_watch",
    )
    made = ServiceEpochObservation.from_continuity_signals(
        epoch=1,
        observed_at=10,
        expires_at=50,
        service_name="head_watch",
        catalog_digest=CATALOG,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        signals=(signal,),
        family_id="fam-z",
    )
    assert made.outcome is ServiceEpochOutcome.COMPLETED
    assert made.branch_count == 1

    refused = ServiceEpochObservation.from_continuity_signals(
        epoch=2,
        observed_at=10,
        expires_at=50,
        service_name="head_watch",
        catalog_digest=CATALOG,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        signals=(replace(signal, report_digest=d("refused"), refused_usefully=True),),
        family_id="fam-z",
    )
    assert refused.outcome is ServiceEpochOutcome.USEFUL_REFUSAL


def wit(name: str, family: str, *, predecessor: bytes = CATALOG, successor: bytes = SUCCESSOR, withdrawal: bytes = WITHDRAWAL, route: bytes = ROUTE, fork: bytes | None = None, expires: int = 2_000) -> ServiceHandoffWitness:
    return ServiceHandoffWitness(
        witness_id=name,
        family_id=family,
        observed_at=950,
        expires_at=expires,
        predecessor_catalog_digest=predecessor,
        successor_catalog_digest=successor,
        withdrawal_notice_digest=withdrawal,
        route_report_digest=route,
        continuity_report_digest=d(f"continuity:{name}"),
        fork_evidence_digest=fork or (b"\x00" * 32),
    )


def good_witnesses():
    return (wit("w1", "fam-a"), wit("w2", "fam-b"), wit("w3", "fam-c"))


def test_service_handoff_accepts_stable_successor_with_diverse_witnesses() -> None:
    report = assess_service_handoff(
        good_witnesses(),
        now=NOW,
        predecessor_catalog_digest=CATALOG,
        successor_catalog_digest=SUCCESSOR,
        withdrawal_notice_digest=WITHDRAWAL,
        predecessor_retired=True,
        successor_epoch_report=stable_epoch_report(),
    )
    assert report.decision_kind is ServiceHandoffDecisionKind.ACCEPT_HANDOFF
    assert report.accept
    assert report.witness_families == ("fam-a", "fam-b", "fam-c")


def test_service_handoff_blocks_one_family_replay_digest_mismatch_and_fork() -> None:
    mono = assess_service_handoff(
        (wit("w1", "fam-a"), wit("w2", "fam-a"), wit("w3", "fam-a")),
        now=NOW,
        predecessor_catalog_digest=CATALOG,
        successor_catalog_digest=SUCCESSOR,
        withdrawal_notice_digest=WITHDRAWAL,
        predecessor_retired=True,
        successor_epoch_report=stable_epoch_report(),
    )
    assert mono.decision_kind is ServiceHandoffDecisionKind.QUARANTINE_ONE_FAMILY

    replay_witness = wit("w1", "fam-a")
    replay = assess_service_handoff(
        (replay_witness, wit("w2", "fam-b"), wit("w3", "fam-c")),
        now=NOW,
        predecessor_catalog_digest=CATALOG,
        successor_catalog_digest=SUCCESSOR,
        withdrawal_notice_digest=WITHDRAWAL,
        predecessor_retired=True,
        successor_epoch_report=stable_epoch_report(),
        previously_seen_witnesses=(replay_witness.witness_digest,),
    )
    assert replay.decision_kind is ServiceHandoffDecisionKind.QUARANTINE_REPLAY

    mismatch = assess_service_handoff(
        (wit("w1", "fam-a"), wit("w2", "fam-b", successor=d("evil-successor")), wit("w3", "fam-c")),
        now=NOW,
        predecessor_catalog_digest=CATALOG,
        successor_catalog_digest=SUCCESSOR,
        withdrawal_notice_digest=WITHDRAWAL,
        predecessor_retired=True,
        successor_epoch_report=stable_epoch_report(),
    )
    assert mismatch.decision_kind is ServiceHandoffDecisionKind.QUARANTINE_DIGEST_MISMATCH

    fork = assess_service_handoff(
        (wit("w1", "fam-a"), wit("w2", "fam-b", fork=d("fork")), wit("w3", "fam-c")),
        now=NOW,
        predecessor_catalog_digest=CATALOG,
        successor_catalog_digest=SUCCESSOR,
        withdrawal_notice_digest=WITHDRAWAL,
        predecessor_retired=True,
        successor_epoch_report=stable_epoch_report(),
    )
    assert fork.decision_kind is ServiceHandoffDecisionKind.QUARANTINE_WITNESS_FORK


def test_service_handoff_requires_retirement_route_and_successor_stability() -> None:
    not_retired = assess_service_handoff(
        good_witnesses(),
        now=NOW,
        predecessor_catalog_digest=CATALOG,
        successor_catalog_digest=SUCCESSOR,
        withdrawal_notice_digest=WITHDRAWAL,
        predecessor_retired=False,
        successor_epoch_report=stable_epoch_report(),
    )
    assert not_retired.decision_kind is ServiceHandoffDecisionKind.QUARANTINE_PREDECESSOR_NOT_RETIRED

    no_route = assess_service_handoff(
        (wit("w1", "fam-a", route=b"\x00" * 32), wit("w2", "fam-b", route=b"\x00" * 32), wit("w3", "fam-c", route=b"\x00" * 32)),
        now=NOW,
        predecessor_catalog_digest=CATALOG,
        successor_catalog_digest=SUCCESSOR,
        withdrawal_notice_digest=WITHDRAWAL,
        predecessor_retired=True,
        successor_epoch_report=stable_epoch_report(),
    )
    assert no_route.decision_kind is ServiceHandoffDecisionKind.HOLD_MISSING_PROOF

    unstable_successor = assess_service_epoch_ledger((obs(10), obs(11, family="fam-b")), now=NOW)
    unstable = assess_service_handoff(
        good_witnesses(),
        now=NOW,
        predecessor_catalog_digest=CATALOG,
        successor_catalog_digest=SUCCESSOR,
        withdrawal_notice_digest=WITHDRAWAL,
        predecessor_retired=True,
        successor_epoch_report=unstable_successor,
    )
    assert unstable.decision_kind is ServiceHandoffDecisionKind.HOLD_MISSING_PROOF


def test_serviceoperabilityfold_audits_current_revision() -> None:
    report = audit_serviceoperability_fold(".", revision="rev0039", artifact_stem="Nicotine-i2pDHT-rev0039-2026.06.04.06.15-continuityjournal-probeloop-successionrepair")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
    assert report.surface_ledger_status == "pass"
    assert report.error_count == 0
