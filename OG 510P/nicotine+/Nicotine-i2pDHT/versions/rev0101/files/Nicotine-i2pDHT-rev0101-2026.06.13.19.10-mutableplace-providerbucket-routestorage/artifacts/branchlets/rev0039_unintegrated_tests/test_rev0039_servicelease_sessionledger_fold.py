from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.servicecatalog import GardenServiceClass
from i2p_dht_lab.servicecontinuity import ServiceContinuityDecisionKind, ServiceContinuityPolicy, ServiceContinuitySignal, assess_service_continuity
from i2p_dht_lab.servicelease import ServiceLeaseCapsule, ServiceLeaseDecisionKind, ServiceLeasePolicy, assess_service_lease
from i2p_dht_lab.sessionledger import ServiceSessionObservation, SessionLedgerDecisionKind, SessionLedgerPolicy, assess_session_ledger
from i2p_dht_lab.sessionfold import audit_session_fold


def d(label: str) -> bytes:
    return sha256(("rev0039:" + label).encode("utf-8"))


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def node(n: int) -> bytes:
    return NodeIdentity.create(destination=f"rev0039-{n}.b32.i2p", keypair=kp(n)).node_id


def sig(branch: str, *, catalog: bytes | None = None, scope: bytes | None = None, request: bytes | None = None, accept: bool = True, refused: bool = False, withdrawal: bool = False) -> ServiceContinuitySignal:
    return ServiceContinuitySignal(
        branch=branch,
        report_digest=d("signal:" + branch + (":refused" if refused else "") + (":withdrawal" if withdrawal else "")),
        accept=accept,
        catalog_digest=catalog or d("catalog"),
        scope_digest=scope or d("scope"),
        request_digest=request or d("request"),
        service_name=GardenServiceClass.HEAD_WATCH.value,
        refused_usefully=refused,
        active_withdrawal=withdrawal,
    )


CONTINUITY_POLICY = ServiceContinuityPolicy(required_branches=("catalog_wire", "announcement", "ingress", "ticket", "receipt", "use_gate"), min_distinct_branches=6)
LEASE_POLICY = ServiceLeasePolicy(max_units=12, max_streams=3, max_raw_key_budget=2)


def continuity_report(*, accepted: bool = True):
    signals = (sig("catalog_wire"), sig("announcement"), sig("ingress"), sig("ticket"), sig("receipt"), sig("use_gate"))
    if not accepted:
        signals = (sig("ticket", refused=True), sig("receipt", refused=True))
        return assess_service_continuity(signals, policy=ServiceContinuityPolicy(required_branches=("ticket", "receipt"), min_distinct_branches=2))
    report = assess_service_continuity(signals, policy=CONTINUITY_POLICY, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request"))
    assert report.decision_kind is ServiceContinuityDecisionKind.ACCEPT_SERVICE_CONTINUITY
    return report


def lease(sequence: int, *, previous: ServiceLeaseCapsule | None = None, object_digest: bytes | None = None, units: int = 5, streams: int = 1, raw: int = 0, issued_at: int = 1000, expires_at: int = 1300, keypair: DhtKeypair | None = None) -> ServiceLeaseCapsule:
    return ServiceLeaseCapsule.create(
        keypair=keypair or kp(7),
        issuer_node_id=node(7),
        sequence=sequence,
        issued_at=issued_at,
        expires_at=expires_at,
        continuity=continuity_report(),
        service=GardenServiceClass.HEAD_WATCH,
        caller_node_id=node(8),
        object_digest=object_digest or d("object"),
        granted_units=units,
        granted_streams=streams,
        raw_key_budget=raw,
        previous_lease_digest=previous.lease_digest if previous else b"\x00" * 32,
    )


def accepted_lease_report():
    item = lease(1)
    return assess_service_lease(item, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, expected_caller_node_id=node(8), expected_object_digest=d("object"), expected_service=GardenServiceClass.HEAD_WATCH)


def obs(report, window: int, *, completed: int = 1, refused: int = 0, source: str = "fam-a", path: str = "path-a", **kwargs) -> ServiceSessionObservation:
    return ServiceSessionObservation.from_lease_report(
        report,
        window_id=window,
        event_digest=d(f"event:{window}:{completed}:{refused}:{source}:{path}:{kwargs}"),
        completed_units=completed,
        refused_units=refused,
        source_family=source,
        path_family=path,
        **kwargs,
    )


def test_service_lease_accepts_initial_and_renewed_exact_boundary() -> None:
    first = lease(1)
    first_report = assess_service_lease(first, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, expected_caller_node_id=node(8), expected_object_digest=d("object"), expected_service=GardenServiceClass.HEAD_WATCH)
    assert first_report.decision_kind is ServiceLeaseDecisionKind.ACCEPT_SERVICE_LEASE
    assert first_report.accept

    renewed = lease(2, previous=first, issued_at=1120, expires_at=1500)
    renewed_report = assess_service_lease(renewed, continuity=continuity_report(), policy=LEASE_POLICY, now=1130, previous_lease=first)
    assert renewed_report.decision_kind is ServiceLeaseDecisionKind.ACCEPT_RENEWED_SERVICE_LEASE
    assert renewed_report.accept


def test_service_lease_rejects_continuity_signature_time_replay_budget_and_binding() -> None:
    item = lease(1)
    assert assess_service_lease(item, continuity=continuity_report(accepted=False), policy=LEASE_POLICY, now=1100).decision_kind is ServiceLeaseDecisionKind.HOLD_CONTINUITY_NOT_ACCEPTED

    bad_sig = replace(item, signature=b"\x00" * 64)
    assert assess_service_lease(bad_sig, continuity=continuity_report(), policy=LEASE_POLICY, now=1100).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_BAD_SIGNATURE

    expired = lease(1, issued_at=100, expires_at=200)
    assert assess_service_lease(expired, continuity=continuity_report(), policy=LEASE_POLICY, now=1100).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE

    assert assess_service_lease(item, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, previously_seen_leases=(item.lease_digest,)).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_REPLAY

    over = lease(1, units=99)
    assert assess_service_lease(over, continuity=continuity_report(), policy=LEASE_POLICY, now=1100).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_BUDGET_OVERCLAIM

    assert assess_service_lease(item, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, expected_caller_node_id=node(99)).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_CALLER_MISMATCH
    assert assess_service_lease(item, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, expected_object_digest=d("other-object")).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_BINDING_MISMATCH


def test_service_lease_rejects_rollback_fork_missing_previous_and_renewal_drift() -> None:
    first = lease(2)
    rollback = lease(1, previous=first)
    assert assess_service_lease(rollback, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, previous_lease=first).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK

    fork = lease(2, previous=first, units=first.granted_units + 1)
    assert assess_service_lease(fork, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, previous_lease=first).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_SEQUENCE_FORK

    missing_prev = lease(3)
    assert assess_service_lease(missing_prev, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, previous_lease=first).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_PREVIOUS_LINK

    drift = lease(3, previous=first, object_digest=d("other-object"))
    assert assess_service_lease(drift, continuity=continuity_report(), policy=LEASE_POLICY, now=1100, previous_lease=first).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_BINDING_MISMATCH


def test_session_ledger_accepts_diverse_completed_windows() -> None:
    report = accepted_lease_report()
    ledger = assess_session_ledger((obs(report, 1, completed=2, source="fam-a", path="path-a"), obs(report, 2, completed=1, source="fam-b", path="path-b")), policy=SessionLedgerPolicy(max_completed_units=5), lease_report=report)
    assert ledger.decision_kind is SessionLedgerDecisionKind.ACCEPT_SESSION_ADVANCE
    assert ledger.accept
    assert ledger.completed_units == 3


def test_session_ledger_rejects_replay_fork_binding_drift_withdrawal_and_quota() -> None:
    report = accepted_lease_report()
    one = obs(report, 1, completed=1, source="fam-a", path="path-a")
    two = obs(report, 2, completed=1, source="fam-b", path="path-b")
    assert assess_session_ledger((one, two), policy=SessionLedgerPolicy(), lease_report=report, previously_seen_events=(one.event_digest,)).decision_kind is SessionLedgerDecisionKind.QUARANTINE_REPLAY

    fork = replace(two, window_id=1, event_digest=d("forked-window"))
    assert assess_session_ledger((one, fork), policy=SessionLedgerPolicy(), lease_report=report).decision_kind is SessionLedgerDecisionKind.QUARANTINE_WINDOW_FORK

    drift = replace(two, scope_digest=d("other-scope"))
    assert assess_session_ledger((one, drift), policy=SessionLedgerPolicy(), lease_report=report).decision_kind is SessionLedgerDecisionKind.QUARANTINE_BINDING_DRIFT

    withdrawal = obs(report, 2, completed=0, refused=0, source="fam-b", path="path-b", active_withdrawal=True)
    assert assess_session_ledger((one, withdrawal), policy=SessionLedgerPolicy(), lease_report=report).decision_kind is SessionLedgerDecisionKind.QUARANTINE_ACTIVE_WITHDRAWAL

    over = obs(report, 2, completed=99, source="fam-b", path="path-b")
    assert assess_session_ledger((one, over), policy=SessionLedgerPolicy(max_completed_units=10), lease_report=report).decision_kind is SessionLedgerDecisionKind.QUARANTINE_QUOTA_OVERSPEND


def test_session_ledger_holds_refusal_loops_low_diversity_and_bad_lease() -> None:
    report = accepted_lease_report()
    refusal = (obs(report, 1, completed=0, refused=1, source="fam-a", path="path-a"), obs(report, 2, completed=0, refused=1, source="fam-b", path="path-b"))
    assert assess_session_ledger(refusal, policy=SessionLedgerPolicy(), lease_report=report).decision_kind is SessionLedgerDecisionKind.HOLD_REFUSAL_ONLY_LOOP

    low_diversity = (obs(report, 1, completed=1, source="fam-a", path="path-a"), obs(report, 2, completed=1, source="fam-a", path="path-a"))
    assert assess_session_ledger(low_diversity, policy=SessionLedgerPolicy(), lease_report=report).decision_kind is SessionLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY

    bad_report = replace(report, accept=False, decision_kind=ServiceLeaseDecisionKind.QUARANTINE_BAD_SIGNATURE)
    assert assess_session_ledger(low_diversity, policy=SessionLedgerPolicy(), lease_report=bad_report).decision_kind is SessionLedgerDecisionKind.QUARANTINE_LEASE_REPORT


def test_session_ledger_quarantines_negative_after_success_and_can_watch_negative_pressure() -> None:
    report = accepted_lease_report()
    negative_success = (obs(report, 1, completed=1, source="fam-a", path="path-a"), obs(report, 2, completed=1, source="fam-b", path="path-b", hard_negative=True))
    assert assess_session_ledger(negative_success, policy=SessionLedgerPolicy(), lease_report=report).decision_kind is SessionLedgerDecisionKind.QUARANTINE_NEGATIVE_AFTER_SUCCESS

    watch = (obs(report, 1, completed=1, source="fam-a", path="path-a"), obs(report, 2, completed=0, refused=0, source="fam-b", path="path-b", hard_negative=True))
    assert assess_session_ledger(watch, policy=SessionLedgerPolicy(), lease_report=report).decision_kind is SessionLedgerDecisionKind.ACCEPT_SESSION_ADVANCE_WITH_WATCH


def test_sessionfold_audits_current_revision() -> None:
    report = audit_session_fold(".", revision="rev0039", artifact_stem="Nicotine-i2pDHT-rev0039-2026.06.04.06.15-servicelease-sessionledger-fold")
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
