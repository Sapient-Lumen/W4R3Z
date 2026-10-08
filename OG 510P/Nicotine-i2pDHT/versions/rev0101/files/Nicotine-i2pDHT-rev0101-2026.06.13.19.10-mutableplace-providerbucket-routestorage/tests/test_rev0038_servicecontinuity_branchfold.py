from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.servicecatalog import GardenServiceClass
from i2p_dht_lab.servicecontinuity import (
    ServiceContinuityDecisionKind,
    ServiceContinuityPolicy,
    ServiceContinuitySignal,
    assess_service_continuity,
)
from i2p_dht_lab.servicecontinuityfold import audit_servicecontinuity_fold
from i2p_dht_lab.servicereceipt import ServiceReceiptDecisionKind, ServiceReceiptReport
from i2p_dht_lab.servicewithdrawal import ServiceWithdrawalDecisionKind, ServiceWithdrawalReport


def d(label: str) -> bytes:
    return sha256(("rev0038:" + label).encode("utf-8"))


def sig(branch: str, *, accept: bool = True, quarantined: bool = False, catalog: bytes | None = None, scope: bytes | None = None, request: bytes | None = None, withdrawal: bool = False, refused: bool = False, watch: bool = False) -> ServiceContinuitySignal:
    return ServiceContinuitySignal(
        branch=branch,
        report_digest=d("report:" + branch + (":q" if quarantined else "") + (":w" if withdrawal else "") + (":r" if refused else "")),
        accept=accept,
        quarantined=quarantined,
        catalog_digest=catalog or d("catalog"),
        scope_digest=scope or d("scope"),
        request_digest=request or d("request"),
        service_name="head_watch",
        active_withdrawal=withdrawal,
        refused_usefully=refused,
        watch_only=watch,
    )


POLICY = ServiceContinuityPolicy(
    required_branches=("catalog_wire", "announcement", "ingress", "ticket", "receipt", "use_gate"),
    min_distinct_branches=6,
)


def accepted_signals() -> tuple[ServiceContinuitySignal, ...]:
    return (
        sig("catalog_wire"),
        sig("announcement"),
        sig("ingress"),
        sig("ticket"),
        sig("receipt"),
        sig("use_gate"),
        sig("handoff"),
        sig("service_probe", watch=True),
        sig("relay", watch=True),
    )


def test_service_continuity_accepts_folded_branchlets_at_one_boundary() -> None:
    report = assess_service_continuity(
        accepted_signals(),
        policy=POLICY,
        expected_catalog_digest=d("catalog"),
        expected_scope_digest=d("scope"),
        expected_request_digest=d("request"),
    )
    assert report.decision_kind is ServiceContinuityDecisionKind.ACCEPT_SERVICE_CONTINUITY
    assert report.accept
    assert "catalog_wire" in report.branches
    assert "handoff" in report.branches
    assert report.catalog_digest == d("catalog")


def test_service_continuity_blocks_withdrawal_replay_quarantine_and_missing_branch() -> None:
    with_withdrawal = accepted_signals() + (sig("withdrawal", withdrawal=True),)
    assert assess_service_continuity(with_withdrawal, policy=POLICY).decision_kind is ServiceContinuityDecisionKind.QUARANTINE_ACTIVE_WITHDRAWAL

    replay = assess_service_continuity(accepted_signals(), policy=POLICY, previously_seen_reports=(d("report:ticket"),))
    assert replay.decision_kind is ServiceContinuityDecisionKind.QUARANTINE_REPLAY

    quarantined = tuple(replace(item, quarantined=True) if item.branch == "ingress" else item for item in accepted_signals())
    assert assess_service_continuity(quarantined, policy=POLICY).decision_kind is ServiceContinuityDecisionKind.QUARANTINE_BRANCH_REPORT

    missing = tuple(item for item in accepted_signals() if item.branch != "receipt")
    assert assess_service_continuity(missing, policy=POLICY).decision_kind is ServiceContinuityDecisionKind.HOLD_MISSING_REQUIRED_BRANCH


def test_service_continuity_blocks_catalog_scope_request_drift_and_duplicate_branch() -> None:
    catalog_drift = tuple(replace(item, catalog_digest=d("other-catalog")) if item.branch == "ticket" else item for item in accepted_signals())
    assert assess_service_continuity(catalog_drift, policy=POLICY).decision_kind is ServiceContinuityDecisionKind.QUARANTINE_CATALOG_DRIFT

    scope_drift = tuple(replace(item, scope_digest=d("other-scope")) if item.branch == "ingress" else item for item in accepted_signals())
    assert assess_service_continuity(scope_drift, policy=POLICY).decision_kind is ServiceContinuityDecisionKind.QUARANTINE_SCOPE_DRIFT

    request_drift = tuple(replace(item, request_digest=d("other-request")) if item.branch == "use_gate" else item for item in accepted_signals())
    assert assess_service_continuity(request_drift, policy=POLICY).decision_kind is ServiceContinuityDecisionKind.QUARANTINE_REQUEST_DRIFT

    duplicate = accepted_signals() + (sig("ticket", request=d("request-2")),)
    assert assess_service_continuity(duplicate, policy=POLICY).decision_kind is ServiceContinuityDecisionKind.QUARANTINE_DUPLICATE_BRANCH


def test_service_continuity_holds_refusal_only_or_watch_only_windows() -> None:
    refusal_policy = ServiceContinuityPolicy(required_branches=("ticket", "receipt"), min_distinct_branches=2)
    refusal_only = (sig("ticket", refused=True), sig("receipt", refused=True))
    assert assess_service_continuity(refusal_only, policy=refusal_policy).decision_kind is ServiceContinuityDecisionKind.HOLD_REFUSAL_ONLY_OR_WATCH_ONLY

    watch_only = (sig("ticket", watch=True), sig("receipt", watch=True))
    assert assess_service_continuity(watch_only, policy=refusal_policy).decision_kind is ServiceContinuityDecisionKind.HOLD_REFUSAL_ONLY_OR_WATCH_ONLY


def test_signal_from_report_normalizes_service_receipt_and_withdrawal_reports() -> None:
    receipt = ServiceReceiptReport(
        decision_kind=ServiceReceiptDecisionKind.ACCEPT_SERVICE_COMPLETION,
        accept=True,
        reason="done",
        receipt_digest=d("receipt"),
        ticket_digest=d("ticket"),
        service=GardenServiceClass.HEAD_WATCH,
        pressure_digests=(),
        report_digest=d("receipt-report"),
    )
    receipt_signal = ServiceContinuitySignal.from_report("receipt", receipt, catalog_digest=d("catalog"), scope_digest=d("scope"), request_digest=d("request"))
    assert receipt_signal.accept
    assert not receipt_signal.quarantined
    assert receipt_signal.service_name == "head_watch"

    withdrawal = ServiceWithdrawalReport(
        decision_kind=ServiceWithdrawalDecisionKind.ACCEPT_CATALOG_RETIRED,
        accept=True,
        reason="retired",
        catalog_digest=d("catalog"),
        notice_digest=d("notice"),
        affected_services=("head_watch",),
        pressure_digests=(),
        report_digest=d("withdraw-report"),
    )
    withdrawal_signal = ServiceContinuitySignal.from_report("withdrawal", withdrawal, scope_digest=d("scope"), request_digest=d("request"))
    assert withdrawal_signal.active_withdrawal
    assert withdrawal_signal.accept


def test_servicecontinuityfold_audits_current_revision() -> None:
    report = audit_servicecontinuity_fold(".", revision="rev0038", artifact_stem="Nicotine-i2pDHT-rev0038-2026.06.04.05.39-servicecontinuity-branchfold")
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.ticketfold_status == "pass"
    assert report.serviceguard_status == "pass"
