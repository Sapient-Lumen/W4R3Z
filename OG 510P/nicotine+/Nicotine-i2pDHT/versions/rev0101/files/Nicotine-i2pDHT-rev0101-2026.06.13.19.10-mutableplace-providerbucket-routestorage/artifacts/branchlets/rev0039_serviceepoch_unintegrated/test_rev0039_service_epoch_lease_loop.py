from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.continuityjournal import (
    ContinuityJournalDecisionKind,
    ContinuityJournalEntry,
    ZERO_DIGEST as JOURNAL_ZERO,
    assess_continuity_journal_entry,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.probeloop import (
    ProbeLoopDecisionKind,
    ProbeLoopObservation,
    ProbeLoopObservationKind,
    ProbeLoopPolicy,
    assess_probe_loop,
)
from i2p_dht_lab.servicecatalog import GardenServiceClass
from i2p_dht_lab.servicecontinuity import ServiceContinuityDecisionKind, ServiceContinuityReport
from i2p_dht_lab.serviceepochfold import audit_serviceepoch_fold
from i2p_dht_lab.serviceepochledger import (
    ServiceEpochLedgerDecisionKind,
    ServiceEpochLedgerPolicy,
    ServiceEpochObservation,
    ServiceEpochOutcome,
    assess_service_epoch_ledger,
)
from i2p_dht_lab.servicelease import (
    ServiceLeaseCapsule,
    ServiceLeaseDecisionKind,
    ServiceLeasePolicy,
    assess_service_lease,
)
from i2p_dht_lab.sessionledger import (
    ServiceSessionObservation,
    SessionLedgerDecisionKind,
    SessionLedgerPolicy,
    assess_session_ledger,
)
from i2p_dht_lab.successionrepair import (
    SuccessionRepairDecisionKind,
    SuccessionRepairPolicy,
    SuccessionRepairSignal,
    SuccessionRepairSignalKind,
    ZERO_DIGEST as SUCCESSION_ZERO,
    assess_succession_repair,
)


def d(label: str) -> bytes:
    return sha256(("rev0039:" + label).encode("utf-8"))


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0039-{n}.b32.i2p", keypair=kp(n))


def continuity(*, accept: bool = True, catalog: bytes | None = None, scope: bytes | None = None, request: bytes | None = None) -> ServiceContinuityReport:
    kind = ServiceContinuityDecisionKind.ACCEPT_SERVICE_CONTINUITY if accept else ServiceContinuityDecisionKind.HOLD_MISSING_REQUIRED_BRANCH
    digest = d("continuity:" + ("ok" if accept else "hold") + ":" + (catalog or d("catalog")).hex()[:8])
    return ServiceContinuityReport(
        decision_kind=kind,
        accept=accept,
        reason="rev0039 continuity fixture",
        branches=("catalog_wire", "announcement", "ingress", "ticket", "receipt", "use_gate"),
        catalog_digest=catalog or d("catalog"),
        scope_digest=scope or d("scope"),
        request_digest=request or d("request"),
        accepted_signal_digests=(d("sig-a"), d("sig-b")),
        pressure_digests=(),
        report_digest=digest,
    )


def make_lease(sequence: int = 1, *, previous: ServiceLeaseCapsule | None = None, cont: ServiceContinuityReport | None = None, units: int = 10, caller: bytes | None = None) -> ServiceLeaseCapsule:
    cont = cont or continuity()
    return ServiceLeaseCapsule.create(
        keypair=kp(1),
        issuer_node_id=ident(1).node_id,
        sequence=sequence,
        issued_at=1_000 + sequence,
        expires_at=2_000 + sequence,
        continuity=cont,
        service=GardenServiceClass.HEAD_WATCH,
        caller_node_id=caller or ident(2).node_id,
        object_digest=d("object"),
        granted_units=units,
        granted_streams=2,
        raw_key_budget=1,
        previous_lease_digest=previous.lease_digest if previous is not None else JOURNAL_ZERO,
    )


def test_service_lease_accepts_and_blocks_renewal_drift() -> None:
    cont = continuity()
    lease = make_lease(cont=cont)
    policy = ServiceLeasePolicy(max_units=20, max_streams=3, max_raw_key_budget=2)
    report = assess_service_lease(lease, continuity=cont, policy=policy, now=1_050, expected_caller_node_id=ident(2).node_id, expected_object_digest=d("object"), expected_service=GardenServiceClass.HEAD_WATCH)
    assert report.decision_kind is ServiceLeaseDecisionKind.ACCEPT_SERVICE_LEASE
    assert report.accept

    renewed = make_lease(sequence=2, previous=lease, cont=cont)
    renewed_report = assess_service_lease(renewed, continuity=cont, policy=policy, now=1_060, previous_lease=lease)
    assert renewed_report.decision_kind is ServiceLeaseDecisionKind.ACCEPT_RENEWED_SERVICE_LEASE

    bad_renewal = replace(renewed, previous_lease_digest=d("not-prev"), signature=kp(1).sign(replace(renewed, previous_lease_digest=d("not-prev"), signature=b"").unsigned_payload()))
    assert assess_service_lease(bad_renewal, continuity=cont, policy=policy, now=1_060, previous_lease=lease).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_PREVIOUS_LINK

    overclaim = make_lease(cont=cont, units=99)
    assert assess_service_lease(overclaim, continuity=cont, policy=policy, now=1_050).decision_kind is ServiceLeaseDecisionKind.QUARANTINE_BUDGET_OVERCLAIM


def test_session_ledger_accepts_repeated_windows_and_blocks_bad_memory() -> None:
    cont = continuity()
    lease = make_lease(cont=cont)
    lease_report = assess_service_lease(lease, continuity=cont, policy=ServiceLeasePolicy(max_units=20, max_streams=3, max_raw_key_budget=2), now=1_050)
    obs = (
        ServiceSessionObservation.from_lease_report(lease_report, window_id=1, event_digest=d("event-1"), completed_units=4, source_family="fam-a", path_family="path-a"),
        ServiceSessionObservation.from_lease_report(lease_report, window_id=2, event_digest=d("event-2"), completed_units=5, source_family="fam-b", path_family="path-b"),
    )
    report = assess_session_ledger(obs, policy=SessionLedgerPolicy(min_windows=2, max_completed_units=20), lease_report=lease_report)
    assert report.decision_kind is SessionLedgerDecisionKind.ACCEPT_SESSION_ADVANCE

    replay = assess_session_ledger(obs, policy=SessionLedgerPolicy(min_windows=2), lease_report=lease_report, previously_seen_events=(d("event-1"),))
    assert replay.decision_kind is SessionLedgerDecisionKind.QUARANTINE_REPLAY

    overspend = tuple(replace(item, completed_units=80) for item in obs)
    assert assess_session_ledger(overspend, policy=SessionLedgerPolicy(min_windows=2, max_completed_units=20), lease_report=lease_report).decision_kind is SessionLedgerDecisionKind.QUARANTINE_QUOTA_OVERSPEND


def test_continuity_journal_preserves_hard_negatives_and_links() -> None:
    cont = continuity()
    hard = d("hard-withdrawal")
    first = ContinuityJournalEntry.create(keypair=kp(3), sequence=1, prev_entry_digest=JOURNAL_ZERO, continuity_report_digest=cont.report_digest, scope_digest=cont.scope_digest or d("scope"), request_digest=cont.request_digest or d("request"), hard_negative_digests=(hard,), issued_at=1_000)
    first_report = assess_continuity_journal_entry(first, continuity_report=cont, now=1_010, known_hard_negatives=(hard,))
    assert first_report.decision_kind is ContinuityJournalDecisionKind.ACCEPT_ADVANCING_ENTRY

    second = ContinuityJournalEntry.create(keypair=kp(3), sequence=2, prev_entry_digest=first.entry_digest, continuity_report_digest=cont.report_digest, scope_digest=cont.scope_digest or d("scope"), request_digest=cont.request_digest or d("request"), hard_negative_digests=(hard,), issued_at=1_020)
    assert assess_continuity_journal_entry(second, continuity_report=cont, now=1_030, previous=first, known_hard_negatives=(hard,)).decision_kind is ContinuityJournalDecisionKind.ACCEPT_ADVANCING_ENTRY

    dropped_hard = ContinuityJournalEntry.create(keypair=kp(3), sequence=2, prev_entry_digest=first.entry_digest, continuity_report_digest=cont.report_digest, scope_digest=cont.scope_digest or d("scope"), request_digest=cont.request_digest or d("request"), hard_negative_digests=(), issued_at=1_020)
    assert assess_continuity_journal_entry(dropped_hard, continuity_report=cont, now=1_030, previous=first, known_hard_negatives=(hard,)).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_DROPPED_HARD_NEGATIVE

    wrong_prev = ContinuityJournalEntry.create(keypair=kp(3), sequence=2, prev_entry_digest=d("wrong-prev"), continuity_report_digest=cont.report_digest, scope_digest=cont.scope_digest or d("scope"), request_digest=cont.request_digest or d("request"), hard_negative_digests=(hard,), issued_at=1_020)
    assert assess_continuity_journal_entry(wrong_prev, continuity_report=cont, now=1_030, previous=first, known_hard_negatives=(hard,)).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_PREV_MISMATCH


def probe(kind: ProbeLoopObservationKind, label: str, *, fam: str = "fam-a", path: str = "path-a", raw: int = 0, decoys: int = 0) -> ProbeLoopObservation:
    return ProbeLoopObservation(
        receipt_digest=d("probe-receipt:" + label),
        plan_digest=d("probe-plan"),
        service_name="head_watch",
        kind=kind,
        source_family=fam,
        path_family=path,
        raw_key_exposures=raw,
        decoy_count=decoys,
    )


def test_probe_loop_accepts_diverse_health_and_blocks_metadata_or_lies() -> None:
    policy = ProbeLoopPolicy(min_healthy=2, min_source_families=2, min_path_families=2, max_raw_key_exposures=1, min_decoy_count=1, max_family_share=0.75)
    healthy = (probe(ProbeLoopObservationKind.HEALTHY, "a", fam="fam-a", path="path-a", raw=1, decoys=1), probe(ProbeLoopObservationKind.HEALTHY, "b", fam="fam-b", path="path-b"), probe(ProbeLoopObservationKind.USEFUL_REFUSAL, "c", fam="fam-c", path="path-c"))
    report = assess_probe_loop(healthy, policy=policy)
    assert report.decision_kind is ProbeLoopDecisionKind.ACCEPT_PROBE_LOOP_HEALTH

    no_decoy = (probe(ProbeLoopObservationKind.HEALTHY, "a", fam="fam-a", path="path-a", raw=1, decoys=0), probe(ProbeLoopObservationKind.HEALTHY, "b", fam="fam-b", path="path-b"))
    assert assess_probe_loop(no_decoy, policy=policy).decision_kind is ProbeLoopDecisionKind.QUARANTINE_DECOY_SHORTFALL

    false = healthy + (probe(ProbeLoopObservationKind.FALSE_SERVICE, "false", fam="fam-d", path="path-d"),)
    assert assess_probe_loop(false, policy=policy).decision_kind is ProbeLoopDecisionKind.QUARANTINE_FALSE_SERVICE

    mono = (probe(ProbeLoopObservationKind.HEALTHY, "a", fam="fam-a", path="path-a"), probe(ProbeLoopObservationKind.HEALTHY, "b", fam="fam-a", path="path-a"), probe(ProbeLoopObservationKind.HEALTHY, "c", fam="fam-a", path="path-a"))
    assert assess_probe_loop(mono, policy=policy).decision_kind is ProbeLoopDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def epoch_obs(epoch: int, outcome: ServiceEpochOutcome, *, family: str, report_label: str | None = None, branch_count: int = 6, catalog: bytes | None = None, scope: bytes | None = None, request: bytes | None = None) -> ServiceEpochObservation:
    return ServiceEpochObservation(
        epoch=epoch,
        observed_at=1_000 + epoch,
        expires_at=2_000 + epoch,
        service_name="head_watch",
        catalog_digest=catalog or d("catalog"),
        scope_digest=scope or d("scope"),
        request_digest=request or d("request"),
        report_digest=d(report_label or f"epoch-report-{epoch}"),
        outcome=outcome,
        branch_count=branch_count,
        family_id=family,
    )


def test_service_epoch_ledger_detects_stability_forks_and_refusal_loops() -> None:
    policy = ServiceEpochLedgerPolicy(min_epochs=3, min_completed_epochs=2, min_distinct_families=2, min_branch_count=4)
    obs = (epoch_obs(1, ServiceEpochOutcome.COMPLETED, family="fam-a"), epoch_obs(2, ServiceEpochOutcome.USEFUL_REFUSAL, family="fam-b"), epoch_obs(3, ServiceEpochOutcome.COMPLETED, family="fam-c"))
    report = assess_service_epoch_ledger(obs, policy=policy, now=1_100, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request"))
    assert report.decision_kind is ServiceEpochLedgerDecisionKind.ACCEPT_STABLE_SERVICE

    fork = obs + (epoch_obs(2, ServiceEpochOutcome.COMPLETED, family="fam-d", report_label="epoch-report-2-fork"),)
    assert assess_service_epoch_ledger(fork, policy=policy, now=1_100).decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_EPOCH_FORK

    refusals = (epoch_obs(1, ServiceEpochOutcome.USEFUL_REFUSAL, family="fam-a"), epoch_obs(2, ServiceEpochOutcome.USEFUL_REFUSAL, family="fam-b"), epoch_obs(3, ServiceEpochOutcome.USEFUL_REFUSAL, family="fam-c"))
    assert assess_service_epoch_ledger(refusals, policy=policy, now=1_100).decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP

    weak = (epoch_obs(1, ServiceEpochOutcome.COMPLETED, family="fam-a", branch_count=2), epoch_obs(2, ServiceEpochOutcome.COMPLETED, family="fam-b"), epoch_obs(3, ServiceEpochOutcome.COMPLETED, family="fam-c"))
    assert assess_service_epoch_ledger(weak, policy=policy, now=1_100).decision_kind is ServiceEpochLedgerDecisionKind.QUARANTINE_BRANCH_REPORT


def repair_signal(kind: SuccessionRepairSignalKind, *, successor: bytes = SUCCESSION_ZERO, catalog: bytes | None = None, scope: bytes | None = None, request: bytes | None = None, accept: bool = True, tombstone: bool = False, label: str | None = None) -> SuccessionRepairSignal:
    return SuccessionRepairSignal(
        kind=kind,
        report_digest=d(label or "repair:" + kind.value),
        accept=accept,
        catalog_digest=catalog or d("catalog"),
        scope_digest=scope or d("scope"),
        request_digest=request or d("request"),
        successor_catalog_digest=successor,
        active_tombstone=tombstone,
    )


def test_succession_repair_requires_journal_probe_and_successor_when_withdrawing() -> None:
    successor = d("successor-catalog")
    policy = SuccessionRepairPolicy(require_probe_health=True, require_journal=True)
    signals = (
        repair_signal(SuccessionRepairSignalKind.SUCCESSOR_CATALOG, successor=successor),
        repair_signal(SuccessionRepairSignalKind.WITHDRAWAL, successor=successor),
        repair_signal(SuccessionRepairSignalKind.CONTINUITY_JOURNAL),
        repair_signal(SuccessionRepairSignalKind.PROBE_LOOP),
    )
    report = assess_succession_repair(signals, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request"))
    assert report.decision_kind is SuccessionRepairDecisionKind.ACCEPT_SUCCESSOR_REPAIR
    assert report.successor_catalog_digest == successor

    missing_successor = (repair_signal(SuccessionRepairSignalKind.WITHDRAWAL, successor=successor), repair_signal(SuccessionRepairSignalKind.CONTINUITY_JOURNAL), repair_signal(SuccessionRepairSignalKind.PROBE_LOOP))
    assert assess_succession_repair(missing_successor, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.QUARANTINE_WITHDRAWAL_WITHOUT_SUCCESSOR

    tombstone = signals + (repair_signal(SuccessionRepairSignalKind.TOMBSTONE, tombstone=True, label="repair:tombstone"),)
    assert assess_succession_repair(tombstone, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.QUARANTINE_ACTIVE_TOMBSTONE

    no_probe = signals[:3]
    assert assess_succession_repair(no_probe, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.HOLD_MISSING_PROBE_HEALTH


def test_serviceepochfold_audits_current_revision() -> None:
    report = audit_serviceepoch_fold(".", revision="rev0039", artifact_stem="Nicotine-i2pDHT-rev0039-2026.06.04.06.15-serviceops-healthdrain-journalfold")
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.predecessor_status == "pass"
