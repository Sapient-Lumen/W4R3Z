from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.servicecatalog import GardenServiceClass
from i2p_dht_lab.servicecontinuity import ServiceContinuityPolicy, ServiceContinuitySignal, assess_service_continuity
from i2p_dht_lab.servicelease import ServiceLeaseCapsule, ServiceLeaseDecisionKind, ServiceLeasePolicy, assess_service_lease
from i2p_dht_lab.sessionledger import ServiceSessionObservation, SessionLedgerDecisionKind, SessionLedgerPolicy, assess_session_ledger
from i2p_dht_lab.serviceepochfold import audit_serviceepoch_fold


def d(label: str) -> bytes:
    return sha256(("rev0039-serviceepoch:" + label).encode())


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def sig(branch: str):
    return ServiceContinuitySignal(
        branch=branch,
        report_digest=d("report:" + branch),
        accept=True,
        catalog_digest=d("catalog"),
        scope_digest=d("scope"),
        request_digest=d("request"),
        service_name="head_watch",
    )


def continuity():
    policy = ServiceContinuityPolicy(required_branches=("catalog", "ticket", "receipt"), min_distinct_branches=3)
    return assess_service_continuity((sig("catalog"), sig("ticket"), sig("receipt")), policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request"))


def lease(sequence: int = 0, previous: bytes = b"\x00" * 32, units: int = 10):
    cont = continuity()
    return ServiceLeaseCapsule.create(
        keypair=kp(9),
        issuer_node_id=d("issuer"),
        sequence=sequence,
        issued_at=100,
        expires_at=500,
        continuity=cont,
        service=GardenServiceClass.HEAD_WATCH,
        caller_node_id=d("caller"),
        object_digest=d("object"),
        granted_units=units,
        granted_streams=2,
        raw_key_budget=1,
        previous_lease_digest=previous,
    )


def test_service_lease_accepts_renewal_and_rejects_drift() -> None:
    cont = continuity()
    first = lease()
    policy = ServiceLeasePolicy(max_units=20, max_streams=4, max_raw_key_budget=2)
    first_report = assess_service_lease(first, continuity=cont, policy=policy, now=150, expected_caller_node_id=d("caller"), expected_object_digest=d("object"), expected_service=GardenServiceClass.HEAD_WATCH)
    assert first_report.decision_kind is ServiceLeaseDecisionKind.ACCEPT_SERVICE_LEASE

    renewed = lease(sequence=1, previous=first.lease_digest)
    assert assess_service_lease(renewed, continuity=cont, policy=policy, now=150, previous_lease=first).decision_kind is ServiceLeaseDecisionKind.ACCEPT_RENEWED_SERVICE_LEASE

    bad = replace(renewed, previous_lease_digest=d("wrong-prev"), signature=b"")
    bad = replace(bad, signature=kp(9).sign(bad.unsigned_payload()))
    assert assess_service_lease(bad, continuity=cont, policy=policy, now=150, previous_lease=first).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_PREVIOUS_LINK

    over = lease(units=99)
    assert assess_service_lease(over, continuity=cont, policy=policy, now=150).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_BUDGET_OVERCLAIM


def test_session_ledger_blocks_replay_overspend_and_accepts_diverse_windows() -> None:
    cont = continuity()
    report = assess_service_lease(lease(), continuity=cont, policy=ServiceLeasePolicy(max_units=20, max_streams=4, max_raw_key_budget=2), now=150)
    obs1 = ServiceSessionObservation.from_lease_report(report, window_id=1, event_digest=d("event:1"), completed_units=3, source_family="src-a", path_family="path-a")
    obs2 = ServiceSessionObservation.from_lease_report(report, window_id=2, event_digest=d("event:2"), completed_units=4, source_family="src-b", path_family="path-b")
    policy = SessionLedgerPolicy(min_windows=2, min_source_families=2, min_path_families=2, max_completed_units=10)
    assert assess_session_ledger((obs1, obs2), policy=policy, lease_report=report).decision_kind is SessionLedgerDecisionKind.ACCEPT_SESSION_ADVANCE
    assert assess_session_ledger((obs1, obs2), policy=policy, lease_report=report, previously_seen_events=(d("event:1"),)).decision_kind is SessionLedgerDecisionKind.QUARANTINE_REPLAY
    overspend = replace(obs2, completed_units=99)
    assert assess_session_ledger((obs1, overspend), policy=policy, lease_report=report).decision_kind is SessionLedgerDecisionKind.QUARANTINE_QUOTA_OVERSPEND


def test_serviceepochfold_audits_current_revision() -> None:
    stem = "Nicotine-i2pDHT-rev0039-2026.06.04.06.15-continuityjournal-probeloop-successionrepair"
    report = audit_serviceepoch_fold(".", revision="rev0039", artifact_stem=stem)
    assert report.status == "pass"
