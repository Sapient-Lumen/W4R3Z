from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.contactlease import (
    ContactLease,
    ContactLeaseBook,
    ContactLeasePurpose,
    ContactLeaseVerdictKind,
    ContactPortfolioDecisionKind,
    ContactPortfolioPolicy,
    assess_contact_portfolio,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.regionledger import RegionLedger, RegionLedgerPolicy, RegionTombstone
from i2p_dht_lab.siblingcast import (
    SiblingAckDecisionKind,
    SiblingAckKind,
    SiblingAckPolicy,
    SiblingCandidate,
    SiblingCastDecisionKind,
    SiblingCastPolicy,
    SiblingCastPurpose,
    SiblingStoreAck,
    analyze_sibling_store_acks,
    plan_sibling_cast,
)
from i2p_dht_lab.sweep import AdvertKind, Advertisement, SweepPolicy
from i2p_dht_lab.sweepaudit import SweepAuditDecisionKind, SweepAuditPolicy, audit_region_sweep
from i2p_dht_lab.surfaceledger import SurfaceLedgerEntry, audit_surface_ledger


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "lease") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def lease(
    n: int,
    family: str,
    *,
    sequence: int = 1,
    issued_at: int = 10_000,
    ttl: int = 1_000,
    purposes: tuple[ContactLeasePurpose, ...] = (ContactLeasePurpose.ROUTE,),
) -> ContactLease:
    return ContactLease.create(
        identity=ident(n),
        keypair=kp(n),
        family_id=family,
        purposes=purposes,
        sequence=sequence,
        issued_at=issued_at,
        ttl=ttl,
    )


def sibling(n: int, family: str, target: bytes, *, writable: bool = True, garden: bool = False, latency: int = 100, capacity: int = 10, refusal_until: int = 0) -> SiblingCandidate:
    node_id = bytes([n % 256]) + sha256(target + bytes([n % 256]))[1:]
    return SiblingCandidate(node_id=node_id, family_id=family, writable=writable, garden=garden, latency_ms=latency + n, capacity_score=capacity, refusal_until=refusal_until)


def ack(candidate: SiblingCandidate, kind: SiblingAckKind, digest: bytes, *, rank: int = 0, at: int = 10_000) -> SiblingStoreAck:
    return SiblingStoreAck(candidate.node_id, candidate.family_id, kind, digest, rank, at, rtt_ms=100 + rank)


def advert(n: int, *, kind: AdvertKind = AdvertKind.PROVIDER, namespace: str = "blocks", weight: int = 1, region: int | None = None) -> Advertisement:
    base = sha256(b"rev0018 sweep advert" + bytes([n % 256]))
    if region is not None:
        # Region prefix works with tests that use region_prefix_bits=3.
        key_int = (region << (256 - 3)) | (int.from_bytes(base, "big") & ((1 << (256 - 3)) - 1))
        key = key_int.to_bytes(32, "big")
    else:
        key = bytes([n % 256]) + base[1:]
    return Advertisement(key=key, kind=kind, namespace=namespace, weight=weight, last_published_at=0)


def test_contact_portfolio_accepts_fresh_diverse_entrances() -> None:
    now = 10_100
    leases = (
        lease(1, "east", purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE)),
        lease(2, "west", purposes=(ContactLeasePurpose.ROUTE,)),
        lease(3, "north", purposes=(ContactLeasePurpose.WITNESS,)),
        lease(4, "south", purposes=(ContactLeasePurpose.GARDEN_SERVICE,)),
    )
    report = assess_contact_portfolio(leases, now=now, target=sha256(b"contact target"), policy=ContactPortfolioPolicy(min_leases=4, min_families=3, max_per_family=2, min_seed_gates=1, min_route_contacts=2))
    assert report.decision.kind is ContactPortfolioDecisionKind.ACCEPT_DIVERSE_ENTRANCES
    assert report.seed_gate_count == 1
    assert report.route_count == 2
    assert len(report.family_counts) >= 3


def test_contact_lease_book_rejects_stale_rollback_after_advance() -> None:
    now = 10_100
    book = ContactLeaseBook()
    old = lease(11, "east", sequence=1)
    new = lease(11, "east", sequence=2, issued_at=10_010)
    assert book.observe(new, now=now).kind is ContactLeaseVerdictKind.ACCEPT_FIRST
    verdict = book.observe(old, now=now)
    assert verdict.kind is ContactLeaseVerdictKind.REJECT_STALE_ROLLBACK
    assert verdict.risky


def test_contact_portfolio_quarantines_same_sequence_fork_pressure() -> None:
    now = 10_100
    first = lease(21, "east", sequence=5, purposes=(ContactLeasePurpose.ROUTE,))
    fork = ContactLease.create(
        identity=ident(21),
        keypair=kp(21),
        family_id="west",
        purposes=(ContactLeasePurpose.SEED_GATE,),
        sequence=5,
        issued_at=10_000,
        ttl=1_000,
        note="same sequence divergent lease",
    )
    report = assess_contact_portfolio((first, fork), now=now, policy=ContactPortfolioPolicy(min_leases=1, min_families=1, min_seed_gates=0, min_route_contacts=0))
    assert report.decision.kind is ContactPortfolioDecisionKind.QUARANTINE_FORK_PRESSURE
    assert report.fork_pressure


def test_contact_lease_book_rejects_expired_but_signed_lease() -> None:
    book = ContactLeaseBook()
    expired = lease(22, "east", issued_at=1_000, ttl=10)
    verdict = book.observe(expired, now=2_000)
    assert verdict.kind is ContactLeaseVerdictKind.REJECT_EXPIRED
    assert verdict.risky


def test_sibling_cast_buys_family_diversity_and_reserves() -> None:
    target = sha256(b"sibling target")
    candidates = (
        sibling(1, "captured", target, capacity=99),
        sibling(2, "captured", target, capacity=98),
        sibling(3, "captured", target, capacity=97),
        sibling(4, "east", target, garden=True, capacity=50),
        sibling(5, "west", target, garden=True, capacity=50),
        sibling(6, "north", target, capacity=50),
        sibling(7, "south", target, garden=True, capacity=50),
    )
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.STORE_MUTABLE_HEAD, now=10_000, policy=SiblingCastPolicy(desired_siblings=5, min_siblings=4, min_families=3, max_per_family=2, reserve_count=2))
    assert plan.decision.kind is SiblingCastDecisionKind.PLAN_READY_WITH_RESERVES
    assert sum(1 for item in plan.primary if item.family_id == "captured") <= 2
    assert len(plan.family_counts) >= 3
    assert len(plan.reserves) == 2


def test_sibling_store_ack_accepts_exact_digest_with_family_diversity() -> None:
    target = sha256(b"sibling ack target")
    digest = sha256(b"record digest")
    candidates = tuple(sibling(i, family, target) for i, family in enumerate(("east", "west", "north", "south", "garden"), start=1))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.STORE_IMMUTABLE, now=10_000, policy=SiblingCastPolicy(desired_siblings=5, min_siblings=4, min_families=3, reserve_count=0))
    report = analyze_sibling_store_acks(plan, record_digest=digest, acks=(ack(item, SiblingAckKind.STORED, digest, rank=rank) for rank, item in enumerate(plan.primary)), policy=SiblingAckPolicy(min_store_acks=4, min_store_families=3))
    assert report.decision.kind is SiblingAckDecisionKind.STORED_DIVERSE
    assert report.stored_count >= 4
    assert len(report.stored_families) >= 3


def test_sibling_store_ack_quarantines_wrong_digest() -> None:
    target = sha256(b"sibling wrong digest target")
    digest = sha256(b"good digest")
    candidates = tuple(sibling(i, family, target) for i, family in enumerate(("east", "west", "north", "south"), start=10))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.STORE_IMMUTABLE, now=10_000, policy=SiblingCastPolicy(desired_siblings=4, min_siblings=4, min_families=3, reserve_count=0))
    bad_ack = ack(plan.primary[0], SiblingAckKind.WRONG_DIGEST, sha256(b"bad digest"), rank=0)
    good_acks = tuple(ack(item, SiblingAckKind.STORED, digest, rank=rank + 1) for rank, item in enumerate(plan.primary[1:]))
    report = analyze_sibling_store_acks(plan, record_digest=digest, acks=(bad_ack,) + good_acks)
    assert report.decision.kind is SiblingAckDecisionKind.QUARANTINE_CONTRADICTION


def test_sibling_store_ack_continues_under_timeout_pressure() -> None:
    target = sha256(b"sibling timeout target")
    digest = sha256(b"timeout digest")
    candidates = tuple(sibling(i, f"family-{i}", target) for i in range(20, 25))
    plan = plan_sibling_cast(candidates, target=target, purpose=SiblingCastPurpose.PROVIDER_ANNOUNCE, now=10_000, policy=SiblingCastPolicy(desired_siblings=5, min_siblings=4, min_families=3, reserve_count=0))
    timeouts = tuple(ack(item, SiblingAckKind.TIMEOUT, digest, rank=rank) for rank, item in enumerate(plan.primary))
    report = analyze_sibling_store_acks(plan, record_digest=digest, acks=timeouts, policy=SiblingAckPolicy(timeout_limit=2))
    assert report.decision.kind is SiblingAckDecisionKind.CONTINUE_TIMEOUT_PRESSURE
    assert report.timeout_count > 2


def test_sweep_audit_accepts_tombstone_first_diverse_budget() -> None:
    now = 20_000
    ledger = RegionLedger()
    a1 = advert(1, region=1, weight=2)
    a2 = advert(2, region=2, weight=2)
    a3 = advert(3, region=2, weight=2)
    ledger.ingest((a1, a2), source_family="east", now=now)
    ledger.ingest((a3,), source_family="west", now=now)
    ledger.add_tombstone(RegionTombstone(key=a1.key, kind=a1.kind, namespace=a1.namespace, issuer_family="owner", issued_at=now - 100, expires_at=now + 10_000))
    report = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=3, max_batch_weight=8), max_batches=8, large_batch_threshold=99))
    audit = audit_region_sweep(report, policy=SweepAuditPolicy(max_total_weight=64, max_batch_weight=8, min_source_families=2, require_tombstones_first=True))
    assert audit.decision.kind is SweepAuditDecisionKind.PLAN_HEALTHY
    assert audit.tombstone_batch_indexes[0] == 0


def test_sweep_audit_throttles_overweight_batch() -> None:
    now = 20_000
    ledger = RegionLedger()
    ledger.ingest((advert(30, region=1, weight=20), advert(31, region=1, weight=20)), source_family="east", now=now)
    ledger.ingest((advert(32, region=1, weight=20),), source_family="west", now=now)
    report = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=3, max_batch_weight=128), large_batch_threshold=99))
    audit = audit_region_sweep(report, policy=SweepAuditPolicy(max_total_weight=100, max_batch_weight=32, min_source_families=2))
    assert audit.decision.kind is SweepAuditDecisionKind.THROTTLE_WEIGHT


def test_sweep_audit_quarantines_source_family_monoculture() -> None:
    now = 20_000
    ledger = RegionLedger()
    ledger.ingest(tuple(advert(i, region=i % 3, weight=1) for i in range(40, 46)), source_family="captured", now=now)
    report = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=3, max_batch_weight=8), large_batch_threshold=99))
    audit = audit_region_sweep(report, policy=SweepAuditPolicy(max_total_weight=100, max_batch_weight=16, min_source_families=2, max_single_family_share_percent=70))
    assert audit.decision.kind is SweepAuditDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def test_surface_ledger_accepts_current_active_surface() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_surface_ledger(root)
    assert report.ok
    assert report.error_count == 0
    assert len(report.digest) == 32


def test_surface_ledger_reports_missing_active_surface(tmp_path: Path) -> None:
    entries = (SurfaceLedgerEntry("src/missing.py", "tests/missing.py", "docs/missing.md", "deliberate missing fixture"),)
    report = audit_surface_ledger(tmp_path, entries=entries)
    assert not report.ok
    assert report.error_count == 3
    assert {finding.code for finding in report.findings} == {"missing_module", "missing_test", "missing_doc"}
