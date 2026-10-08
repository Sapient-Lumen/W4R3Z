from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.adaptivealpha import AdaptiveLookupDecision, AdaptiveLookupDecisionKind, AdaptiveLookupKnobs, AdaptiveLookupReport
from i2p_dht_lab.budgetreceipt import BudgetReceiptBook, BudgetReceiptVerdictKind, GardenBudgetAction, GardenBudgetReceipt, action_for_audit
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.leaseroute import LeaseRouteBook, LeaseRouteDecisionKind, LeaseRoutePolicy, assess_leased_route_gossip
from i2p_dht_lab.livenessbudget import LivenessBudgetDecision, LivenessBudgetDecisionKind, LivenessBudgetReport, LivenessSpend
from i2p_dht_lab.proofhandshake import ProviderProofVerdict, ProviderProofVerdictKind
from i2p_dht_lab.regionledger import RegionLedger, RegionLedgerPolicy, RegionTombstone
from i2p_dht_lab.roundledger import RoundEvidence, RoundLedgerDecisionKind, assess_repeated_rounds
from i2p_dht_lab.routegossip import RouteContact, RouteGossipBatch, RouteGossipPolicy
from i2p_dht_lab.siblingcast import (
    SiblingAckKind,
    SiblingAckPolicy,
    SiblingCandidate,
    SiblingCastPolicy,
    SiblingCastPurpose,
    SiblingStoreAck,
    analyze_sibling_store_acks,
    plan_sibling_cast,
)
from i2p_dht_lab.storemesh import StoreMeshDecisionKind, StoreMeshPolicy, StoreMeshRound, StoreRecordKind, assess_store_mesh
from i2p_dht_lab.sweep import AdvertKind, Advertisement, SweepPolicy
from i2p_dht_lab.sweepaudit import SweepAuditDecisionKind, SweepAuditPolicy, audit_region_sweep
from i2p_dht_lab.surfaceledger import audit_surface_ledger, rev0019_entries
from i2p_dht_lab.witnesscache import WitnessCacheDecision, WitnessCacheDecisionKind, WitnessCacheSummary


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "rev0019") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def lease(n: int, family: str, *, sequence: int = 1, issued_at: int = 10_000, ttl: int = 1_000, purposes: tuple[ContactLeasePurpose, ...] = (ContactLeasePurpose.ROUTE,)) -> ContactLease:
    return ContactLease.create(identity=ident(n, "lease19"), keypair=kp(n), family_id=family, purposes=purposes, sequence=sequence, issued_at=issued_at, ttl=ttl)


def route_contact_from_lease(item: ContactLease, *, introduced_by: str, at: int, success: int = 1, failure: int = 0) -> RouteContact:
    return RouteContact(
        node_id=item.node_id,
        destination_hint=item.destination,
        family_id=item.family_id,
        introduced_by=introduced_by,
        first_seen_at=at - 10,
        last_seen_at=at,
        success_count=success,
        failure_count=failure,
    )


def gossip_batch(issuer_n: int, target: bytes, contacts: tuple[RouteContact, ...], *, family: str = "garden", at: int = 10_050) -> RouteGossipBatch:
    return RouteGossipBatch(issuer_node_id=ident(issuer_n, "garden19").node_id, issuer_family=family, target=target, issued_at=at, contacts=contacts)


def sibling(n: int, family: str, target: bytes) -> SiblingCandidate:
    node_id = target[:-1] + bytes([(target[-1] ^ n) & 0xFF])
    return SiblingCandidate(node_id=node_id, family_id=family, writable=True, garden=n % 2 == 0, latency_ms=100 + n, capacity_score=max(1, 20 - n))


def ack(candidate: SiblingCandidate, kind: SiblingAckKind, digest: bytes, *, rank: int = 0, at: int = 20_000) -> SiblingStoreAck:
    return SiblingStoreAck(candidate.node_id, candidate.family_id, kind, digest, rank, at, rtt_ms=80 + rank)


def accepted_ack_report(target: bytes, digest: bytes, *, purpose: SiblingCastPurpose = SiblingCastPurpose.STORE_MUTABLE_HEAD):
    candidates = tuple(sibling(n, fam, target) for n, fam in enumerate(("east", "west", "north", "south", "garden"), start=1))
    plan = plan_sibling_cast(candidates, target=target, purpose=purpose, now=20_000, policy=SiblingCastPolicy(desired_siblings=5, min_siblings=4, min_families=3, reserve_count=0))
    return analyze_sibling_store_acks(plan, record_digest=digest, acks=tuple(ack(item, SiblingAckKind.STORED, digest, rank=i) for i, item in enumerate(plan.primary[:4])), policy=SiblingAckPolicy(min_store_acks=4, min_store_families=3))


def weak_ack_report(target: bytes, digest: bytes):
    candidates = tuple(sibling(n, fam, target) for n, fam in enumerate(("east", "west", "north", "south"), start=10))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.STORE_MUTABLE_HEAD, now=20_000, policy=SiblingCastPolicy(desired_siblings=4, min_siblings=4, min_families=3, reserve_count=0))
    return analyze_sibling_store_acks(plan, record_digest=digest, acks=(ack(plan.primary[0], SiblingAckKind.STORED, digest),), policy=SiblingAckPolicy(min_store_acks=4, min_store_families=3))


def advert(n: int, *, region: int = 0, weight: int = 1) -> Advertisement:
    base = sha256(b"rev0019 sweep advert" + bytes([n % 256]))
    key_int = (region << (256 - 3)) | (int.from_bytes(base, "big") & ((1 << (256 - 3)) - 1))
    return Advertisement(key=key_int.to_bytes(32, "big"), kind=AdvertKind.PROVIDER, namespace="blocks", weight=weight, last_published_at=0)


def sweep_audit(*, overweight: bool = False, tombstone_late: bool = False):
    now = 30_000
    ledger = RegionLedger()
    if overweight:
        ledger.ingest(tuple(advert(i, region=1, weight=10) for i in range(1, 5)), source_family="east", now=now)
        ledger.ingest(tuple(advert(i, region=2, weight=10) for i in range(20, 24)), source_family="west", now=now)
        report = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=3, max_batch_weight=20), max_batches=8, large_batch_threshold=99))
        return audit_region_sweep(report, policy=SweepAuditPolicy(max_total_weight=12, max_batch_weight=20, min_source_families=1, max_single_family_share_percent=100))
    first = advert(1, region=1, weight=1)
    second = advert(2, region=2, weight=1)
    ledger.ingest((first,), source_family="east", now=now)
    ledger.ingest((second,), source_family="west", now=now)
    if tombstone_late:
        ledger.add_tombstone(RegionTombstone(key=second.key, kind=second.kind, namespace=second.namespace, issuer_family="owner", issued_at=now - 1, expires_at=now + 1_000))
    report = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=3, max_batch_weight=8), max_batches=8, large_batch_threshold=99))
    return audit_region_sweep(report, policy=SweepAuditPolicy(max_total_weight=64, max_batch_weight=8, min_source_families=2, require_tombstones_first=True))


def liveness(kind: LivenessBudgetDecisionKind = LivenessBudgetDecisionKind.PROCEED_BOUNDED) -> LivenessBudgetReport:
    decision = LivenessBudgetDecision(kind, kind is LivenessBudgetDecisionKind.PROCEED_BOUNDED, "test liveness")
    return LivenessBudgetReport(
        AdaptiveLookupDecisionKind.ACCEPT_READY,
        LivenessSpend(lookup_queries=2, real_probe_count=2, decoy_probe_count=1, raw_key_exposures=0, metadata_points=42, real_probe_families=frozenset({"east", "west"}), probe_families=frozenset({"east", "west", "decoy"})),
        decision,
        sha256(b"liveness" + kind.value.encode()),
    )


def witness(kind: WitnessCacheDecisionKind = WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE) -> WitnessCacheSummary:
    return WitnessCacheSummary(
        target_commitment=sha256(b"target commitment"),
        now=40_000,
        valid_cached_count=2,
        expired_count=0,
        counted_count=2,
        family_weights={"east": 100, "west": 100} if kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE else {},
        claim_weights={"provider_true": 200} if kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE else {},
        contradictions=(),
        decision=WitnessCacheDecision(kind, kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE, "test witness"),
        transcript_digest=sha256(b"witness" + kind.value.encode()),
    )


def proof(kind: ProviderProofVerdictKind) -> ProviderProofVerdict:
    return ProviderProofVerdict(kind, kind in {ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER, ProviderProofVerdictKind.ACCEPT_USEFUL_REFUSAL}, sha256(b"proof" + kind.value.encode()), "test proof")


def test_leased_route_gossip_commits_only_fresh_route_leased_contacts() -> None:
    now = 10_100
    target = sha256(b"lease route target")
    leases = (
        lease(1, "east"),
        lease(2, "west"),
        lease(3, "north"),
        lease(4, "south"),
    )
    contacts = tuple(route_contact_from_lease(item, introduced_by=f"intro-{idx}", at=10_050) for idx, item in enumerate(leases))
    book = LeaseRouteBook.empty()
    report = assess_leased_route_gossip(
        book,
        (gossip_batch(50, target, contacts),),
        leases,
        now=now,
        route_policy=RouteGossipPolicy(min_repair_contacts=4, min_repair_families=3, max_per_family=2, repair_limit=4),
        lease_policy=LeaseRoutePolicy(min_leased_selected=4, min_lease_families=3),
    )
    assert report.decision.kind is LeaseRouteDecisionKind.ACCEPT_LEASED_REPAIR
    assert len(book.route_book.contacts) == 4
    assert len(report.lease_family_counts) >= 3


def test_leased_route_gossip_quarantines_unleased_selected_contacts() -> None:
    now = 10_100
    target = sha256(b"lease route unleased")
    good = (lease(11, "east"), lease(12, "west"), lease(13, "north"))
    missing = lease(14, "south")
    contacts = tuple(route_contact_from_lease(item, introduced_by=f"intro-{idx}", at=10_050) for idx, item in enumerate(good + (missing,)))
    report = assess_leased_route_gossip(
        LeaseRouteBook.empty(),
        (gossip_batch(51, target, contacts),),
        good,
        now=now,
        route_policy=RouteGossipPolicy(min_repair_contacts=4, min_repair_families=3, max_per_family=2, repair_limit=4),
        lease_policy=LeaseRoutePolicy(min_leased_selected=4, min_lease_families=3, max_unleased_selected=0),
    )
    assert report.decision.kind is LeaseRouteDecisionKind.QUARANTINE_UNLEASED_SELECTION
    assert len(report.unleased_selected) == 1


def test_leased_route_gossip_accepts_stale_eviction_only_with_leased_repair() -> None:
    now = 10_100
    target = sha256(b"lease route stale")
    book = LeaseRouteBook.empty()
    stale = RouteContact(node_id=sha256(b"old node"), destination_hint="old.b32.i2p", family_id="old", introduced_by="old-seed", first_seen_at=0, last_seen_at=0, success_count=1, stale_after_seconds=10)
    book.route_book.remember(stale)
    leases = tuple(lease(21 + idx, family) for idx, family in enumerate(("east", "west", "north", "south")))
    contacts = tuple(route_contact_from_lease(item, introduced_by=f"intro-{idx}", at=10_095) for idx, item in enumerate(leases))
    report = assess_leased_route_gossip(
        book,
        (gossip_batch(52, target, contacts),),
        leases,
        now=now,
        route_policy=RouteGossipPolicy(min_repair_contacts=4, min_repair_families=3, max_per_family=2, stale_after_seconds=100, repair_limit=4),
        lease_policy=LeaseRoutePolicy(min_leased_selected=4, min_lease_families=3),
    )
    assert report.decision.kind is LeaseRouteDecisionKind.ACCEPT_EVICT_STALE_THEN_REPAIR
    assert stale.node_id not in book.route_book.contacts
    assert len(book.route_book.contacts) == 4


def test_store_mesh_accepts_mutable_head_after_tombstone_repair_round() -> None:
    target = sha256(b"store mesh target")
    tomb_digest = sha256(b"tombstone record")
    head_digest = sha256(b"mutable head record")
    tomb_round = StoreMeshRound(StoreRecordKind.TOMBSTONE, tomb_digest, accepted_ack_report(target, tomb_digest, purpose=SiblingCastPurpose.TOMBSTONE_REPAIR), observed_at=20_010)
    head_round = StoreMeshRound(StoreRecordKind.MUTABLE_HEAD, head_digest, accepted_ack_report(target, head_digest), observed_at=20_020, linked_tombstone_digest=tomb_digest)
    report = assess_store_mesh((tomb_round, head_round), policy=StoreMeshPolicy(require_tombstone_before_mutable=True))
    assert report.decision.kind is StoreMeshDecisionKind.ACCEPT_MESH_STORED
    assert tomb_digest in report.accepted_tombstone_digests


def test_store_mesh_blocks_mutable_head_until_linked_tombstone_repaired() -> None:
    target = sha256(b"store mesh tombstone first")
    tomb_digest = sha256(b"needed tomb")
    head_digest = sha256(b"head before tomb")
    head_round = StoreMeshRound(StoreRecordKind.MUTABLE_HEAD, head_digest, accepted_ack_report(target, head_digest), observed_at=20_020, linked_tombstone_digest=tomb_digest)
    report = assess_store_mesh((head_round,), policy=StoreMeshPolicy(require_tombstone_before_mutable=True))
    assert report.decision.kind is StoreMeshDecisionKind.CONTINUE_TOMBSTONE_FIRST


def test_store_mesh_quarantines_live_tombstone_resurrection_pressure() -> None:
    target = sha256(b"store mesh resurrection")
    live_tomb = sha256(b"live tombstone")
    provider_digest = sha256(b"stale provider claim")
    provider_round = StoreMeshRound(StoreRecordKind.PROVIDER, provider_digest, accepted_ack_report(target, provider_digest, purpose=SiblingCastPurpose.PROVIDER_ANNOUNCE), observed_at=20_020)
    report = assess_store_mesh((provider_round,), live_tombstone_digests=(live_tomb,))
    assert report.decision.kind is StoreMeshDecisionKind.QUARANTINE_RESURRECTION_PRESSURE


def test_store_mesh_holds_under_useful_refusal_pressure() -> None:
    target = sha256(b"store mesh refusal")
    digest = sha256(b"refusal digest")
    candidates = tuple(sibling(n, fam, target) for n, fam in enumerate(("east", "west", "north", "south"), start=30))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.STORE_IMMUTABLE, now=20_000, policy=SiblingCastPolicy(desired_siblings=4, min_siblings=4, min_families=3, reserve_count=0))
    ack_report = analyze_sibling_store_acks(plan, record_digest=digest, acks=tuple(ack(item, SiblingAckKind.REFUSED, digest, rank=i) for i, item in enumerate(plan.primary)), policy=SiblingAckPolicy(min_store_acks=4, min_store_families=3))
    mesh = assess_store_mesh((StoreMeshRound(StoreRecordKind.IMMUTABLE, digest, ack_report, observed_at=20_030),), policy=StoreMeshPolicy(max_refusal_share_ppm=250_000))
    assert mesh.decision.kind is StoreMeshDecisionKind.HOLD_USEFUL_REFUSALS


def test_garden_budget_receipt_accepts_action_matching_sweep_audit() -> None:
    audit = sweep_audit(overweight=True)
    assert audit.decision.kind is SweepAuditDecisionKind.THROTTLE_WEIGHT
    receipt = GardenBudgetReceipt.create(
        garden_keypair=kp(90),
        garden_node_id=ident(90, "gardenbudget").node_id,
        audit=audit,
        sequence=1,
        issued_at=30_100,
        window_start=30_100,
        window_end=30_700,
        action=action_for_audit(audit),
        accepted_batch_count=0,
        deferred_batch_count=audit.batch_count,
        reason="over budget; spread across later windows",
    )
    verdict = BudgetReceiptBook().observe(receipt, audit=audit)
    assert verdict.kind is BudgetReceiptVerdictKind.ACCEPT_RECEIPT
    assert receipt.verify()


def test_garden_budget_receipt_rejects_action_mismatch() -> None:
    audit = sweep_audit(overweight=True)
    receipt = GardenBudgetReceipt.create(
        garden_keypair=kp(91),
        garden_node_id=ident(91, "gardenbudget").node_id,
        audit=audit,
        sequence=1,
        issued_at=30_100,
        window_start=30_100,
        window_end=30_700,
        action=GardenBudgetAction.ACCEPTED_PLAN,
        accepted_batch_count=audit.batch_count,
        deferred_batch_count=0,
    )
    verdict = BudgetReceiptBook().observe(receipt, audit=audit)
    assert verdict.kind is BudgetReceiptVerdictKind.REJECT_ACTION_MISMATCH


def test_garden_budget_receipt_detects_same_sequence_fork() -> None:
    audit = sweep_audit(overweight=True)
    book = BudgetReceiptBook()
    first = GardenBudgetReceipt.create(garden_keypair=kp(92), garden_node_id=ident(92, "gardenbudget").node_id, audit=audit, sequence=2, issued_at=30_100, window_start=30_100, window_end=30_700, action=action_for_audit(audit), accepted_batch_count=0, deferred_batch_count=audit.batch_count, reason="first")
    fork = GardenBudgetReceipt.create(garden_keypair=kp(92), garden_node_id=ident(92, "gardenbudget").node_id, audit=audit, sequence=2, issued_at=30_101, window_start=30_100, window_end=30_700, action=action_for_audit(audit), accepted_batch_count=0, deferred_batch_count=audit.batch_count, reason="different receipt same seq")
    assert book.observe(first, audit=audit).accept
    verdict = book.observe(fork, audit=audit)
    assert verdict.kind is BudgetReceiptVerdictKind.QUARANTINE_SAME_SEQ_FORK


def test_round_ledger_accepts_only_when_liveness_provider_and_witness_surfaces_align() -> None:
    round_one = RoundEvidence(sha256(b"round one"), liveness(), (proof(ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER),), witness(), observed_at=40_000)
    report = assess_repeated_rounds((round_one,))
    assert report.decision.kind is RoundLedgerDecisionKind.ACCEPT_ROUND_EVIDENCE
    assert report.true_provider_count == 1


def test_round_ledger_quarantines_false_provider_even_with_good_liveness_and_witness() -> None:
    round_one = RoundEvidence(sha256(b"round false"), liveness(), (proof(ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER), proof(ProviderProofVerdictKind.REJECT_FALSE_PROVIDER)), witness(), observed_at=40_000)
    report = assess_repeated_rounds((round_one,))
    assert report.decision.kind is RoundLedgerDecisionKind.QUARANTINE_FALSE_PROVIDER


def test_round_ledger_stops_when_metadata_budget_is_spent() -> None:
    round_one = RoundEvidence(sha256(b"round budget"), liveness(LivenessBudgetDecisionKind.STOP_NO_BUDGET), (proof(ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER),), witness(), observed_at=40_000)
    report = assess_repeated_rounds((round_one,))
    assert report.decision.kind is RoundLedgerDecisionKind.STOP_METADATA_BUDGET


def test_surface_ledger_rev0019_entries_are_pinned_to_files() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_surface_ledger(root, rev0019_entries())
    assert report.ok
    assert report.error_count == 0
