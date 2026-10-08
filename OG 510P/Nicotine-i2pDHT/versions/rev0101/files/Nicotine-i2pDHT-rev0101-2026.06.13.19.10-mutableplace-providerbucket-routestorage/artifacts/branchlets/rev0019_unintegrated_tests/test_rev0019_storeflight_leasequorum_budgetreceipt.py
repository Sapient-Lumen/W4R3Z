from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.adaptivealpha import AdaptiveAlphaPolicy, recommend_adaptive_lookup
from i2p_dht_lab.budgetreceipt import GardenBudgetAction, issue_budget_receipt
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose, ContactPortfolioPolicy, assess_contact_portfolio
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.leaseroute import LeaseRouteDecisionKind, LeaseRoutePolicy, assess_lease_route
from i2p_dht_lab.livenessbudget import LivenessBudgetPolicy, assess_liveness_budget
from i2p_dht_lab.lookuptranscript import LookupEvent, LookupEventKind, LookupKind, LookupTranscript
from i2p_dht_lab.pressureledger import PressureLedgerDecisionKind, PressureRound, summarize_pressure_rounds
from i2p_dht_lab.privateprovider import ProviderCandidate, PrivateProbeBudget, plan_private_provider_probes
from i2p_dht_lab.regionledger import RegionLedger, RegionLedgerPolicy, RegionTombstone
from i2p_dht_lab.routegossip import RouteContact, RouteGossipBatch, RouteGossipBook, RouteGossipPolicy
from i2p_dht_lab.siblingbroadcast import SiblingBroadcastPolicy, SiblingReceiptKind, SiblingStoreReceipt, assess_sibling_broadcast
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
from i2p_dht_lab.storeflight import StoreFlightDecisionKind, StoreFlightPolicy, assess_store_flight
from i2p_dht_lab.surfaceledger import audit_surface_ledger
from i2p_dht_lab.sweep import AdvertKind, Advertisement, SweepPolicy
from i2p_dht_lab.sweepaudit import SweepAuditDecisionKind, SweepAuditPolicy, audit_region_sweep
from i2p_dht_lab.tombstonecache import TombstoneCache, TombstoneCachePolicy, TombstoneKind, TombstoneRecord
from i2p_dht_lab.witnesscache import WitnessCachePolicy


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "rev0019") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def lease(n: int, family: str, *, now: int = 10_000, purposes: tuple[ContactLeasePurpose, ...] = (ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE), sequence: int = 1) -> ContactLease:
    return ContactLease.create(identity=ident(n, "lease19"), keypair=kp(n), family_id=family, purposes=purposes, sequence=sequence, issued_at=now - 100, ttl=10_000)


def contact_from_lease(item: ContactLease, *, family: str | None = None, introduced_by: str = "garden-a", now: int = 10_000, failures: int = 0) -> RouteContact:
    return RouteContact(
        node_id=item.node_id,
        destination_hint=item.destination,
        family_id=family or item.family_id,
        introduced_by=introduced_by,
        first_seen_at=now - 100,
        last_seen_at=now - 10,
        success_count=1,
        failure_count=failures,
        stale_after_seconds=3_600,
    )


def gossip_for_contacts(contacts: tuple[RouteContact, ...], *, target: bytes, now: int, issuer_family: str = "garden-a"):
    book = RouteGossipBook()
    stale = RouteContact(
        node_id=sha256(b"old stale contact"),
        destination_hint="stale.b32.i2p",
        family_id="stale",
        introduced_by="old-garden",
        first_seen_at=now - 10_000,
        last_seen_at=now - 9_000,
        success_count=1,
        stale_after_seconds=1,
    )
    book.remember(stale)
    batch = RouteGossipBatch(issuer_node_id=ident(250, "issuer").node_id, issuer_family=issuer_family, target=target, issued_at=now, contacts=contacts)
    return book.ingest_gossip((batch,), now=now, policy=RouteGossipPolicy(min_repair_contacts=4, min_repair_families=3, max_per_family=2, max_issuer_fraction=1.0, repair_limit=6))


def sibling(n: int, family: str, target: bytes, *, garden: bool = False, writable: bool = True) -> SiblingCandidate:
    node_id = sha256(target + b":sibling:" + bytes([n % 256]))
    return SiblingCandidate(node_id=node_id, family_id=family, writable=writable, garden=garden, latency_ms=100 + n, capacity_score=20 - (n % 10))


def store_ack(candidate: SiblingCandidate, kind: SiblingAckKind, digest: bytes, *, rank: int, at: int = 10_000) -> SiblingStoreAck:
    return SiblingStoreAck(candidate.node_id, candidate.family_id, kind, digest, rank, at, rtt_ms=50 + rank)


def broadcast_receipt(n: int, family: str, target: bytes, digest: bytes, *, rank: int, kind: SiblingReceiptKind = SiblingReceiptKind.ACCEPTED, now: int = 10_000) -> SiblingStoreReceipt:
    return SiblingStoreReceipt.create(
        keypair=kp(n),
        storage_node_id=ident(n, "broadcast19").node_id,
        family_id=family,
        target=target,
        record_digest=digest,
        sibling_rank=rank,
        kind=kind,
        issued_at=now - 1,
        ttl=10_000,
        retry_after=now + 300 if kind is SiblingReceiptKind.USEFUL_REFUSAL else 0,
    )


def advert(n: int, *, region: int = 0, weight: int = 1, kind: AdvertKind = AdvertKind.PROVIDER) -> Advertisement:
    base = sha256(b"rev0019 advert" + bytes([n % 256]))
    key_int = (region << (256 - 3)) | (int.from_bytes(base, "big") & ((1 << (256 - 3)) - 1))
    return Advertisement(key=key_int.to_bytes(32, "big"), kind=kind, namespace="blocks", weight=weight, last_published_at=0)


def provider_candidate(n: int, family: str) -> ProviderCandidate:
    return ProviderCandidate(provider_node_id=ident(300 + n, "provider19").node_id, family_id=family, distance_rank=n, latency_ms=100 + n, reliability_score=10, supports_commitment_probe=True)


def lookup_event(seq: int, family: str, kind: LookupEventKind, at: int) -> LookupEvent:
    return LookupEvent(sequence=seq, path_id=f"p{seq}", family_id=family, node_id=ident(400 + seq, "lookup19").node_id, kind=kind, sent_at_ms=0, completed_at_ms=at, payload_digest=sha256(b"lookup event" + bytes([seq % 256])))


def clean_liveness(now: int = 10_000):
    tx = LookupTranscript(
        lookup_id=sha256(b"rev0019 clean lookup"),
        kind=LookupKind.FIND_PROVIDER,
        target=sha256(b"rev0019 provider target"),
        events=(
            lookup_event(1, "east", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 100),
            lookup_event(2, "west", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 400),
            lookup_event(3, "north", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 700),
        ),
    )
    adaptive = recommend_adaptive_lookup((tx,), policy=AdaptiveAlphaPolicy(fast_window_ms=20))
    plan = plan_private_provider_probes(
        (provider_candidate(1, "east"), provider_candidate(2, "west"), provider_candidate(3, "north")),
        namespace="blocks",
        content_key=sha256(b"rev0019 block"),
        nonce=sha256(b"rev0019 nonce"),
        issued_at=now,
        budget=PrivateProbeBudget(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, max_content_key_exposures=1),
    )
    return assess_liveness_budget(adaptive_report=adaptive, probe_plan=plan, policy=LivenessBudgetPolicy(max_lookup_queries=100, max_metadata_points=1_000, min_decoy_ratio_ppm=200_000))


def test_lease_route_accepts_stale_evict_then_fresh_leased_repair() -> None:
    now = 10_000
    target = sha256(b"lease route target")
    leases = (
        lease(1, "east", now=now),
        lease(2, "west", now=now),
        lease(3, "north", now=now),
        lease(4, "south", now=now),
    )
    portfolio = assess_contact_portfolio(leases, now=now, target=target, policy=ContactPortfolioPolicy(min_leases=4, min_families=3, min_seed_gates=1, min_route_contacts=4))
    gossip = gossip_for_contacts(tuple(contact_from_lease(item, introduced_by=f"garden-{idx}", now=now) for idx, item in enumerate(leases)), target=target, now=now)
    report = assess_lease_route(portfolio=portfolio, gossip=gossip, now=now, policy=LeaseRoutePolicy(min_leased_contacts=4, min_lease_families=3, max_unleased_fraction_percent=0))
    assert report.decision.kind is LeaseRouteDecisionKind.EVICT_STALE_THEN_REPAIR
    assert report.decision.accept
    assert report.leased_family_count >= 3
    assert report.stale_evictions


def test_lease_route_quarantines_unleased_gossip_even_when_route_gossip_looked_diverse() -> None:
    now = 10_000
    target = sha256(b"unleased route target")
    leases = (lease(10, "east", now=now), lease(11, "west", now=now), lease(12, "north", now=now), lease(13, "south", now=now))
    portfolio = assess_contact_portfolio(leases[:2], now=now, target=target, policy=ContactPortfolioPolicy(min_leases=2, min_families=2, min_seed_gates=1, min_route_contacts=2))
    unleased_contacts = tuple(contact_from_lease(item, introduced_by=f"garden-{idx}", now=now) for idx, item in enumerate(leases))
    gossip = gossip_for_contacts(unleased_contacts, target=target, now=now)
    report = assess_lease_route(portfolio=portfolio, gossip=gossip, now=now, policy=LeaseRoutePolicy(min_leased_contacts=2, min_lease_families=2, max_unleased_fraction_percent=25))
    assert report.decision.kind is LeaseRouteDecisionKind.QUARANTINE_UNLEASED_GOSSIP
    assert report.unleased_fraction_percent > 25


def test_lease_route_blocks_same_sequence_lease_fork_before_repair() -> None:
    now = 10_000
    first = lease(20, "east", now=now, sequence=7)
    fork = ContactLease.create(identity=ident(20, "lease19"), keypair=kp(20), family_id="west", purposes=(ContactLeasePurpose.ROUTE,), sequence=7, issued_at=now - 100, ttl=10_000, note="fork")
    portfolio = assess_contact_portfolio((first, fork), now=now, policy=ContactPortfolioPolicy(min_leases=1, min_families=1, min_seed_gates=0, min_route_contacts=0))
    gossip = gossip_for_contacts((contact_from_lease(first, now=now),), target=sha256(b"fork target"), now=now)
    report = assess_lease_route(portfolio=portfolio, gossip=gossip, now=now, policy=LeaseRoutePolicy(min_leased_contacts=1, min_lease_families=1))
    assert report.decision.kind is LeaseRouteDecisionKind.QUARANTINE_LEASE_FORK


def test_store_flight_accepts_exact_digest_siblingcast_and_broadcast() -> None:
    now = 10_000
    target = sha256(b"storeflight target")
    digest = sha256(b"storeflight record")
    candidates = tuple(sibling(i, family, target, garden=i % 2 == 0) for i, family in enumerate(("east", "west", "north", "south", "garden"), start=1))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.STORE_MUTABLE_HEAD, now=now, policy=SiblingCastPolicy(desired_siblings=5, min_siblings=4, min_families=3, reserve_count=0))
    ack_report = analyze_sibling_store_acks(plan, record_digest=digest, acks=tuple(store_ack(item, SiblingAckKind.STORED, digest, rank=rank, at=now) for rank, item in enumerate(plan.primary)), policy=SiblingAckPolicy(min_store_acks=4, min_store_families=3))
    broadcast = assess_sibling_broadcast(tuple(broadcast_receipt(50 + i, family, target, digest, rank=i, now=now) for i, family in enumerate(("east", "west", "north", "south", "garden"))), target=target, record_digest=digest, now=now, policy=SiblingBroadcastPolicy(min_accept_receipts=4, min_accept_families=3))
    flight = assess_store_flight(ack_report=ack_report, record_digest=digest, purpose=SiblingCastPurpose.STORE_MUTABLE_HEAD, broadcast_report=broadcast)
    assert flight.decision.kind is StoreFlightDecisionKind.STORE_DIVERSE_WITH_BROADCAST
    assert flight.decision.accept
    assert flight.stored_count >= 4


def test_store_flight_blocks_provider_resurrection_when_tombstone_cache_blocks_resurrection() -> None:
    now = 10_000
    target = sha256(b"withdrawn provider target")
    digest = sha256(b"withdrawn provider record")
    candidates = tuple(sibling(i, family, target) for i, family in enumerate(("east", "west", "north", "south"), start=20))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.PROVIDER_ANNOUNCE, now=now, policy=SiblingCastPolicy(desired_siblings=4, min_siblings=4, min_families=3, reserve_count=0))
    ack_report = analyze_sibling_store_acks(plan, record_digest=digest, acks=tuple(store_ack(item, SiblingAckKind.STORED, digest, rank=rank) for rank, item in enumerate(plan.primary)), policy=SiblingAckPolicy(min_store_acks=4, min_store_families=3))
    cache = TombstoneCache()
    tomb = TombstoneRecord.create(keypair=kp(90), target_commitment=target, kind=TombstoneKind.PROVIDER_WITHDRAWN, issuer_family="owner", sequence=9, issued_at=now - 100, expires_at=now + 10_000)
    assert cache.add(tomb, now=now)
    tomb_report = cache.analyze(target_commitment=target, now=now, witness_summary=None, policy=TombstoneCachePolicy(resurrection_claim_weight=0))
    flight = assess_store_flight(ack_report=ack_report, record_digest=digest, purpose=SiblingCastPurpose.PROVIDER_ANNOUNCE, tombstone_report=tomb_report)
    assert flight.decision.kind is StoreFlightDecisionKind.QUARANTINE_TOMBSTONE_CONFLICT
    assert not flight.decision.accept


def test_store_flight_treats_useful_refusal_as_backoff_not_store_success() -> None:
    now = 10_000
    target = sha256(b"refusal store target")
    digest = sha256(b"refusal record")
    candidates = tuple(sibling(i, family, target) for i, family in enumerate(("east", "west", "north", "south"), start=40))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.STORE_MUTABLE_HEAD, now=now, policy=SiblingCastPolicy(desired_siblings=4, min_siblings=4, min_families=3, reserve_count=0))
    ack_report = analyze_sibling_store_acks(plan, record_digest=digest, acks=tuple(store_ack(item, SiblingAckKind.TIMEOUT, digest, rank=rank) for rank, item in enumerate(plan.primary)), policy=SiblingAckPolicy(timeout_limit=10))
    refusals = tuple(broadcast_receipt(80 + i, family, target, digest, rank=i, kind=SiblingReceiptKind.USEFUL_REFUSAL, now=now) for i, family in enumerate(("east", "west", "north")))
    broadcast = assess_sibling_broadcast(refusals, target=target, record_digest=digest, now=now, policy=SiblingBroadcastPolicy(min_accept_receipts=4, min_accept_families=3, useful_refusal_pressure=2))
    flight = assess_store_flight(ack_report=ack_report, record_digest=digest, purpose=SiblingCastPurpose.STORE_MUTABLE_HEAD, broadcast_report=broadcast, policy=StoreFlightPolicy(useful_refusals_to_backoff=2))
    assert flight.decision.kind is StoreFlightDecisionKind.CONTINUE_RETRY_AFTER_REFUSALS
    assert not flight.decision.accept
    assert flight.decision.retry_after_seconds > now


def test_budget_receipt_signs_throttle_and_verifies() -> None:
    now = 20_000
    ledger = RegionLedger()
    ledger.ingest(tuple(advert(i, region=i % 2, weight=40) for i in range(1, 8)), source_family="east", now=now)
    ledger.ingest(tuple(advert(i, region=i % 2, weight=40) for i in range(8, 12)), source_family="west", now=now)
    sweep = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=3, max_batch_weight=100), large_batch_threshold=999))
    audit = audit_region_sweep(sweep, policy=SweepAuditPolicy(max_total_weight=120, max_batch_weight=100, min_source_families=2))
    assert audit.decision.kind is SweepAuditDecisionKind.THROTTLE_WEIGHT
    receipt = issue_budget_receipt(keypair=kp(200), garden_node_id=ident(200, "garden19").node_id, garden_family="garden-east", sweep_audit=audit, issued_at=now)
    assert receipt.action is GardenBudgetAction.THROTTLE_WEIGHT
    assert receipt.deferred_weight > 0
    assert receipt.retry_after_seconds > 0
    assert receipt.verify(now=now + 1)
    tampered = replace(receipt, deferred_weight=0)
    assert not tampered.verify(now=now + 1)


def test_budget_receipt_prioritizes_tombstones_before_bulk_work() -> None:
    now = 20_000
    ledger = RegionLedger()
    a1 = advert(1, region=3, weight=1)
    a2 = advert(2, region=0, weight=1)
    ledger.ingest((a1,), source_family="east", now=now)
    ledger.ingest((a2,), source_family="west", now=now)
    # This tombstone lives in region 3; ordinary region 0 batch comes first, so the audit should reorder.
    ledger.add_tombstone(RegionTombstone(key=a1.key, kind=a1.kind, namespace=a1.namespace, issuer_family="owner", issued_at=now - 10, expires_at=now + 1_000))
    sweep = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=10_000, region_prefix_bits=3, max_batch_weight=8), large_batch_threshold=99))
    audit = audit_region_sweep(sweep, policy=SweepAuditPolicy(max_total_weight=100, max_batch_weight=10, min_source_families=2, require_tombstones_first=True))
    assert audit.decision.kind is SweepAuditDecisionKind.PRIORITIZE_TOMBSTONES
    receipt = issue_budget_receipt(keypair=kp(201), garden_node_id=ident(201, "garden19").node_id, garden_family="garden-west", sweep_audit=audit, issued_at=now)
    assert receipt.action is GardenBudgetAction.PRIORITIZE_TOMBSTONES
    assert receipt.accepted_weight >= 1
    assert receipt.verify(now=now + 1)


def test_pressure_ledger_preserves_repeated_round_quarantine() -> None:
    now = 30_000
    liveness = clean_liveness(now)
    # Reuse a deliberately quarantine-shaped lease route from unleased gossip.
    target = sha256(b"pressure ledger target")
    leases = (lease(30, "east", now=now), lease(31, "west", now=now))
    portfolio = assess_contact_portfolio(leases, now=now, target=target, policy=ContactPortfolioPolicy(min_leases=2, min_families=2, min_seed_gates=1, min_route_contacts=2))
    contacts = tuple(contact_from_lease(lease(30 + i, family, now=now), family=family, introduced_by=f"g{i}", now=now) for i, family in enumerate(("east", "west", "north", "south")))
    gossip = gossip_for_contacts(contacts, target=target, now=now)
    route = assess_lease_route(portfolio=portfolio, gossip=gossip, now=now, policy=LeaseRoutePolicy(min_leased_contacts=2, min_lease_families=2, max_unleased_fraction_percent=25))
    assert route.decision.kind is LeaseRouteDecisionKind.QUARANTINE_UNLEASED_GOSSIP
    round1 = PressureRound(round_id=sha256(b"round1"), observed_at=now, liveness=liveness, lease_route=route)
    round2 = PressureRound(round_id=sha256(b"round2"), observed_at=now + 10, lease_route=route)
    ledger = summarize_pressure_rounds((round1, round2))
    assert ledger.decision.kind is PressureLedgerDecisionKind.QUARANTINE_REPEATED_PRESSURE
    assert not ledger.decision.proceed
    assert ledger.signal_counts["quarantine"] == 2


def test_pressure_ledger_accepts_one_clean_store_progress_round() -> None:
    now = 40_000
    target = sha256(b"clean store ledger")
    digest = sha256(b"clean store record")
    candidates = tuple(sibling(i, family, target) for i, family in enumerate(("east", "west", "north", "south"), start=60))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.STORE_IMMUTABLE, now=now, policy=SiblingCastPolicy(desired_siblings=4, min_siblings=4, min_families=3, reserve_count=0))
    ack_report = analyze_sibling_store_acks(plan, record_digest=digest, acks=tuple(store_ack(item, SiblingAckKind.STORED, digest, rank=rank, at=now) for rank, item in enumerate(plan.primary)), policy=SiblingAckPolicy(min_store_acks=4, min_store_families=3))
    flight = assess_store_flight(ack_report=ack_report, record_digest=digest, purpose=SiblingCastPurpose.STORE_IMMUTABLE)
    ledger = summarize_pressure_rounds((PressureRound(round_id=sha256(b"clean round"), observed_at=now, liveness=clean_liveness(now), store_flight=flight),))
    assert ledger.decision.kind is PressureLedgerDecisionKind.ACCEPT_PROGRESSING
    assert ledger.decision.proceed


def test_surface_ledger_tracks_rev0019_active_surfaces() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_surface_ledger(root)
    assert report.ok
    modules = {entry.module for entry in report.entries}
    assert "src/i2p_dht_lab/leaseroute.py" in modules
    assert "src/i2p_dht_lab/storeflight.py" in modules
    assert "src/i2p_dht_lab/budgetreceipt.py" in modules
    assert "src/i2p_dht_lab/pressureledger.py" in modules
