from dataclasses import replace

from i2p_dht_lab.budgetreceipt import (
    BudgetReceiptBook,
    BudgetReceiptVerdictKind,
    GardenBudgetAction,
    GardenBudgetReceipt,
    action_for_audit,
)
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.leasequorum import (
    LeaseObservation,
    LeaseQuorumDecisionKind,
    LeaseQuorumPolicy,
    LeaseSourceKind,
    assess_lease_quorum,
)
from i2p_dht_lab.storeflight import (
    CustodyReceipt,
    StoreCandidate,
    StoreFlightDecisionKind,
    StoreFlightPolicy,
    StoreFlightSummaryKind,
    StoreRecordKind,
    StoreSlot,
    plan_store_flight,
)
from i2p_dht_lab.surfaceledger import audit_surface_ledger, rev0019_entries
from i2p_dht_lab.sweepaudit import SweepAuditDecision, SweepAuditDecisionKind, SweepAuditReport


def keypair(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def node(n: int) -> tuple[DhtKeypair, NodeIdentity]:
    kp = keypair(n)
    return kp, NodeIdentity.create(destination=f"garden-{n}.b32.i2p", keypair=kp)


def digest(label: str) -> bytes:
    return sha256(label.encode())


def candidate(label: str, kind: StoreRecordKind, family: str, *, now: int = 1000, size: int = 1000, priority: int = 0, proof_ok: bool = True) -> StoreCandidate:
    return StoreCandidate(
        key=digest("key:" + label),
        record_digest=digest("record:" + label),
        kind=kind,
        namespace="rev0019",
        source_family=family,
        size_bytes=size,
        issued_at=now - 10,
        expires_at=now + 3600,
        priority=priority,
        proof_ok=proof_ok,
    )


def lease(n: int, family: str, purposes: tuple[ContactLeasePurpose, ...], *, seq: int = 1, note: str = "") -> ContactLease:
    kp, ident = node(n)
    return ContactLease.create(
        identity=ident,
        keypair=kp,
        family_id=family,
        purposes=purposes,
        sequence=seq,
        issued_at=1000,
        ttl=3600,
        note=note,
    )


def observation(n: int, *, node_family: str, source_family: str, path_family: str, source_kind: LeaseSourceKind = LeaseSourceKind.GARDEN_SEED, purposes: tuple[ContactLeasePurpose, ...] = (ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE)) -> LeaseObservation:
    return LeaseObservation(
        lease(n, node_family, purposes),
        source_kind=source_kind,
        source_family=source_family,
        path_family=path_family,
        observed_at=1100,
    )


def test_storeflight_protects_tombstones_and_mutable_heads_under_bulk_flood() -> None:
    garden_kp, garden = node(200)
    existing = [
        StoreSlot(candidate(f"sloppy-{idx}", StoreRecordKind.SLOPPY_CACHE, "bulk-A", now=1000, size=800), stored_at=900, custody_until=2000)
        for idx in range(4)
    ]
    incoming = [
        candidate("provider-big", StoreRecordKind.PROVIDER_RECORD, "bulk-A", now=1000, size=1200),
        candidate("mutable-head", StoreRecordKind.MUTABLE_HEAD, "writer-A", now=1000, size=400, priority=50),
        candidate("tombstone", StoreRecordKind.TOMBSTONE, "sentinel-A", now=1000, size=300, priority=100),
    ]
    report = plan_store_flight(
        incoming,
        garden_keypair=garden_kp,
        garden_node_id=garden.node_id,
        now=1000,
        existing_slots=existing,
        policy=StoreFlightPolicy(max_records=5, max_bytes=3400, max_candidate_size=2000, control_plane_reserve_records=2, control_plane_reserve_bytes=500),
    )
    accepted_kinds = {action.candidate.kind for action in report.accepted}
    assert StoreRecordKind.TOMBSTONE in accepted_kinds
    assert StoreRecordKind.MUTABLE_HEAD in accepted_kinds
    assert any(action.kind is StoreFlightDecisionKind.ACCEPT_WITH_EVICTION for action in report.accepted)
    assert report.evicted_slots
    assert all(slot.candidate.kind is StoreRecordKind.SLOPPY_CACHE for slot in report.evicted_slots)
    assert report.final_bytes <= 3400
    assert report.summary.kind in {StoreFlightSummaryKind.CONTROL_PLANE_PROTECTED, StoreFlightSummaryKind.STORED_WITH_REFUSALS}
    for action in report.accepted:
        assert action.receipt is not None
        assert action.receipt.verify(garden_kp.public_key_bytes)


def test_storeflight_refuses_family_bulk_and_quarantines_bad_or_tombstoned_records() -> None:
    garden_kp, garden = node(201)
    bad = candidate("bad-proof", StoreRecordKind.PROVIDER_RECORD, "bulk-B", proof_ok=False)
    tombstoned = candidate("dead", StoreRecordKind.MUTABLE_HEAD, "writer-B")
    bulk = [candidate(f"bulk-{idx}", StoreRecordKind.PROVIDER_RECORD, "bulk-B", size=100) for idx in range(4)]
    report = plan_store_flight(
        [*bulk, bad, tombstoned],
        garden_keypair=garden_kp,
        garden_node_id=garden.node_id,
        now=1000,
        tombstoned_digests={tombstoned.record_digest},
        policy=StoreFlightPolicy(max_records=10, max_bytes=10_000, max_bulk_per_source_family=2),
    )
    assert sum(1 for action in report.accepted if action.candidate.kind is StoreRecordKind.PROVIDER_RECORD) == 2
    assert any(action.kind is StoreFlightDecisionKind.REFUSE_FAMILY_CAP for action in report.refused)
    assert any(action.kind is StoreFlightDecisionKind.QUARANTINE_BAD_PROOF for action in report.quarantined)
    assert any(action.kind is StoreFlightDecisionKind.QUARANTINE_TOMBSTONED for action in report.quarantined)
    assert report.summary.kind is StoreFlightSummaryKind.QUARANTINE_PRESSURE


def test_custody_receipt_signature_and_tamper_detection() -> None:
    garden_kp, garden = node(202)
    cand = candidate("receipt", StoreRecordKind.CONTACT_LEASE, "seed-A")
    receipt = CustodyReceipt.create(garden_keypair=garden_kp, garden_node_id=garden.node_id, candidate=cand, accepted_at=1000, custody_until=1600)
    assert receipt.verify(garden_kp.public_key_bytes)
    tampered = replace(receipt, size_bytes=receipt.size_bytes + 1)
    assert not tampered.verify(garden_kp.public_key_bytes)


def test_lease_quorum_accepts_diverse_fresh_entrance_portfolio() -> None:
    observations = [
        observation(1, node_family="nA", source_family="sA", path_family="pA"),
        observation(2, node_family="nB", source_family="sB", path_family="pB", purposes=(ContactLeasePurpose.ROUTE,)),
        observation(3, node_family="nC", source_family="sC", path_family="pA", purposes=(ContactLeasePurpose.SEED_GATE,)),
        observation(4, node_family="nD", source_family="sD", path_family="pC", source_kind=LeaseSourceKind.ROUTE_GOSSIP, purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.WITNESS)),
        observation(5, node_family="nE", source_family="sE", path_family="pB", source_kind=LeaseSourceKind.CACHE, purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE)),
    ]
    report = assess_lease_quorum(observations, now=1100, policy=LeaseQuorumPolicy(min_valid_leases=5, min_node_families=3, min_source_families=3, min_path_families=2))
    assert report.decision.kind is LeaseQuorumDecisionKind.ACCEPT_LEASE_QUORUM
    assert report.decision.accept
    assert len(report.selected_observations) == 5
    assert report.purpose_counts[ContactLeasePurpose.ROUTE.value] >= 2
    assert report.purpose_counts[ContactLeasePurpose.SEED_GATE.value] >= 1


def test_lease_quorum_rejects_source_capture_even_with_node_diversity() -> None:
    observations = [
        observation(10 + idx, node_family=f"n{idx}", source_family="captured-seed", path_family="same-path")
        for idx in range(6)
    ]
    report = assess_lease_quorum(observations, now=1100, policy=LeaseQuorumPolicy(min_valid_leases=4, min_node_families=3, min_source_families=3, min_path_families=2, max_per_source_family=6))
    assert report.decision.kind in {LeaseQuorumDecisionKind.CONTINUE_LOW_SOURCE_DIVERSITY, LeaseQuorumDecisionKind.QUARANTINE_SOURCE_CAPTURE}
    assert report.needs_more_sources


def test_lease_quorum_quarantines_same_sequence_fork() -> None:
    first = lease(30, "fork-family", (ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE), seq=7, note="first")
    second = lease(30, "fork-family", (ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE), seq=7, note="second")
    observations = [
        LeaseObservation(first, LeaseSourceKind.GARDEN_SEED, "sA", "pA", 1100),
        LeaseObservation(second, LeaseSourceKind.ROUTE_GOSSIP, "sB", "pB", 1100),
        observation(31, node_family="nB", source_family="sC", path_family="pC"),
        observation(32, node_family="nC", source_family="sD", path_family="pD"),
        observation(33, node_family="nD", source_family="sE", path_family="pE"),
    ]
    report = assess_lease_quorum(observations, now=1100, policy=LeaseQuorumPolicy(min_valid_leases=3, min_node_families=2, min_source_families=2))
    assert report.fork_pressure
    assert report.decision.kind is LeaseQuorumDecisionKind.QUARANTINE_FORK_PRESSURE


def fake_sweep_audit(kind: SweepAuditDecisionKind) -> SweepAuditReport:
    return SweepAuditReport(
        source_report_digest=digest("region-ledger-source"),
        batch_count=4,
        total_weight=1500,
        max_batch_weight=800,
        source_family_counts={"A": 3, "B": 1},
        tombstone_batch_indexes=(1,),
        decision=SweepAuditDecision(kind, kind is SweepAuditDecisionKind.PLAN_HEALTHY, "fake audit for rev0019 budget receipt tests"),
        transcript_digest=digest("sweep-audit:" + kind.value),
    )


def test_budget_receipt_book_accepts_matching_audit_receipt_and_catches_forks() -> None:
    garden_kp, garden = node(220)
    audit = fake_sweep_audit(SweepAuditDecisionKind.THROTTLE_WEIGHT)
    receipt = GardenBudgetReceipt.create(
        garden_keypair=garden_kp,
        garden_node_id=garden.node_id,
        audit=audit,
        sequence=1,
        issued_at=1200,
        window_start=1000,
        window_end=1600,
        action=action_for_audit(audit),
        accepted_batch_count=1,
        deferred_batch_count=3,
        reason="provider bulk exceeded this garden window",
    )
    book = BudgetReceiptBook()
    verdict = book.observe(receipt, audit=audit)
    assert verdict.kind is BudgetReceiptVerdictKind.ACCEPT_RECEIPT
    assert receipt.verify()

    wrong_action = GardenBudgetReceipt.create(
        garden_keypair=garden_kp,
        garden_node_id=garden.node_id,
        audit=audit,
        sequence=2,
        issued_at=1300,
        window_start=1000,
        window_end=1600,
        action=GardenBudgetAction.ACCEPTED_PLAN,
        accepted_batch_count=4,
        deferred_batch_count=0,
        reason="lying about accepted overweight plan",
    )
    assert book.observe(wrong_action, audit=audit).kind is BudgetReceiptVerdictKind.REJECT_ACTION_MISMATCH

    fork_a = GardenBudgetReceipt.create(
        garden_keypair=garden_kp,
        garden_node_id=garden.node_id,
        audit=audit,
        sequence=3,
        issued_at=1400,
        window_start=1000,
        window_end=1600,
        action=action_for_audit(audit),
        accepted_batch_count=2,
        deferred_batch_count=2,
        reason="first story",
    )
    fork_b = GardenBudgetReceipt.create(
        garden_keypair=garden_kp,
        garden_node_id=garden.node_id,
        audit=audit,
        sequence=3,
        issued_at=1401,
        window_start=1000,
        window_end=1600,
        action=action_for_audit(audit),
        accepted_batch_count=1,
        deferred_batch_count=3,
        reason="second story",
    )
    assert book.observe(fork_a, audit=audit).kind is BudgetReceiptVerdictKind.ACCEPT_RECEIPT
    assert book.observe(fork_b, audit=audit).kind is BudgetReceiptVerdictKind.QUARANTINE_SAME_SEQ_FORK


def test_surface_ledger_includes_rev0019_active_surfaces() -> None:
    report = audit_surface_ledger(".", entries=rev0019_entries())
    assert report.ok
    modules = {entry.module for entry in report.entries}
    assert "src/i2p_dht_lab/storeflight.py" in modules
    assert "src/i2p_dht_lab/leasequorum.py" in modules
    assert "src/i2p_dht_lab/budgetreceipt.py" in modules
