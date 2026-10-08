from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.readrepair import (
    ReadRepairDecisionKind,
    ReadRepairPolicy,
    ReplicaObservation,
    ReplicaObservationKind,
    plan_read_repair,
)
from i2p_dht_lab.storagelease import (
    StorageLeaseDecisionKind,
    StorageLeaseMemory,
    StorageLeasePolicy,
    StorageLeaseReceipt,
    StorageLeaseReceiptKind,
    assess_storage_lease_quorum,
    storage_tombstone_target,
)
from i2p_dht_lab.storeflight import (
    CustodyReceipt,
    StoreCandidate,
    StoreClass,
    StoreFlightDecisionKind,
    StoreFlightPolicy,
    StoreFlightSummaryKind,
    StoreRecordKind,
    StoreSlot,
    plan_store_flight,
)
from i2p_dht_lab.tombstonecache import TombstoneCache, TombstoneKind, TombstoneRecord


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "rev0019") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def candidate(n: int, family: str, *, kind: StoreRecordKind = StoreRecordKind.PROVIDER_RECORD, size: int = 1024, priority: int = 0, proof_ok: bool = True, issued_at: int = 10_000, expires_at: int = 20_000, tombstone_target: bytes = b"") -> StoreCandidate:
    return StoreCandidate(
        key=sha256(b"candidate-key" + bytes([n % 256])),
        record_digest=sha256(b"candidate-digest" + bytes([n % 256])),
        kind=kind,
        namespace="rev0019",
        source_family=family,
        size_bytes=size,
        issued_at=issued_at,
        expires_at=expires_at,
        priority=priority,
        proof_ok=proof_ok,
        tombstone_target=tombstone_target,
    )


def lease(n: int, family: str, target: bytes, digest: bytes, *, seq: int = 1, kind: StorageLeaseReceiptKind = StorageLeaseReceiptKind.GRANTED, issued_at: int = 10_000, expires: int = 30_000, renew_after: int = 15_000) -> StorageLeaseReceipt:
    return StorageLeaseReceipt.create(
        keypair=kp(n),
        storage_node_id=ident(n, "lease").node_id,
        family_id=family,
        target=target,
        record_digest=digest,
        record_kind=StoreRecordKind.MUTABLE_HEAD,
        store_class=StoreClass.GARDEN_LEASE,
        lease_sequence=seq,
        kind=kind,
        issued_at=issued_at,
        lease_expires_at=expires,
        renewal_after=renew_after,
    )


def replica(n: int, family: str, target: bytes, digest: bytes, *, kind: ReplicaObservationKind, observed_digest: bytes | None = None, expires: int = 20_000) -> ReplicaObservation:
    return ReplicaObservation(
        node_id=ident(n, "replica").node_id,
        family_id=family,
        target=target,
        expected_digest=digest,
        kind=kind,
        observed_digest=digest if observed_digest is None and kind is ReplicaObservationKind.EXACT else (observed_digest or b""),
        observed_at=10_500,
        lease_expires_at=expires,
        store_class=StoreClass.CANONICAL,
    )


def test_storeflight_accepts_records_and_issues_verifiable_custody_receipts() -> None:
    garden_key = kp(200)
    garden_id = ident(200, "garden").node_id
    candidates = (
        candidate(1, "east", kind=StoreRecordKind.TOMBSTONE, priority=100),
        candidate(2, "west", kind=StoreRecordKind.MUTABLE_HEAD, priority=90),
        candidate(3, "north", kind=StoreRecordKind.PROVIDER_RECORD),
    )
    report = plan_store_flight(candidates, garden_keypair=garden_key, garden_node_id=garden_id, now=10_100, policy=StoreFlightPolicy(max_records=8, max_bytes=50_000, control_plane_reserve_records=0, control_plane_reserve_bytes=0))
    assert report.summary.kind is StoreFlightSummaryKind.STORED_ALL
    assert len(report.accepted) == 3
    assert all(action.receipt and action.receipt.verify(garden_key.public_key_bytes) for action in report.accepted)
    assert isinstance(report.accepted[0].receipt, CustodyReceipt)


def test_storeflight_refuses_bulk_that_would_consume_control_plane_reserve() -> None:
    garden_key = kp(201)
    garden_id = ident(201, "garden").node_id
    bulk = tuple(candidate(i, "bulk", kind=StoreRecordKind.SLOPPY_CACHE, size=20_000) for i in range(10, 13))
    existing_control = (StoreSlot(candidate(9, "owner", kind=StoreRecordKind.TOMBSTONE, size=35_000, priority=100), stored_at=9_000, custody_until=20_000),)
    report = plan_store_flight(bulk, garden_keypair=garden_key, garden_node_id=garden_id, now=10_100, existing_slots=existing_control, policy=StoreFlightPolicy(max_records=8, max_bytes=70_000, control_plane_reserve_bytes=40_000, max_per_source_family=10, max_bulk_per_source_family=10))
    assert report.summary.kind is StoreFlightSummaryKind.NO_ACCEPTED_RECORDS
    assert report.refused
    assert all(action.kind is StoreFlightDecisionKind.REFUSE_OVER_BUDGET for action in report.refused)


def test_storeflight_evicts_low_priority_sloppy_cache_for_tombstone() -> None:
    garden_key = kp(202)
    garden_id = ident(202, "garden").node_id
    existing = [StoreSlot(candidate(i, f"family-{i}", kind=StoreRecordKind.SLOPPY_CACHE, size=10_000), stored_at=9_000, custody_until=20_000) for i in range(20, 24)]
    tomb = candidate(30, "owner", kind=StoreRecordKind.TOMBSTONE, size=8_000, priority=100)
    report = plan_store_flight((tomb,), garden_keypair=garden_key, garden_node_id=garden_id, now=10_100, existing_slots=existing, policy=StoreFlightPolicy(max_records=4, max_bytes=40_000, max_candidate_size=20_000))
    assert report.accepted[0].kind is StoreFlightDecisionKind.ACCEPT_WITH_EVICTION
    assert report.evicted_slots
    assert report.summary.kind is StoreFlightSummaryKind.CONTROL_PLANE_PROTECTED


def test_storeflight_quarantines_failed_proof_and_tombstoned_digest() -> None:
    garden_key = kp(203)
    garden_id = ident(203, "garden").node_id
    bad = candidate(40, "east", proof_ok=False)
    dead = candidate(41, "west")
    report = plan_store_flight((bad, dead), garden_keypair=garden_key, garden_node_id=garden_id, now=10_100, tombstoned_digests=(dead.record_digest,))
    assert report.summary.kind is StoreFlightSummaryKind.NO_ACCEPTED_RECORDS
    assert {action.kind for action in report.quarantined} == {StoreFlightDecisionKind.QUARANTINE_BAD_PROOF, StoreFlightDecisionKind.QUARANTINE_TOMBSTONED}


def test_storage_leasequorum_accepts_live_diverse_leases() -> None:
    target = sha256(b"lease target")
    digest = sha256(b"lease digest")
    receipts = tuple(lease(i, family, target, digest) for i, family in enumerate(("east", "west", "north", "south"), start=1))
    report = assess_storage_lease_quorum(target=target, record_digest=digest, receipts=receipts, now=10_500, policy=StorageLeasePolicy(min_live_leases=4, min_families=3))
    assert report.decision.kind is StorageLeaseDecisionKind.LIVE_DIVERSE_LEASES
    assert report.decision.accept
    assert len(report.family_counts) >= 3


def test_storage_leasequorum_marks_near_horizon_as_renew_soon() -> None:
    target = sha256(b"lease renew target")
    digest = sha256(b"lease renew digest")
    receipts = tuple(lease(i, family, target, digest, expires=14_000) for i, family in enumerate(("east", "west", "north", "south"), start=10))
    report = assess_storage_lease_quorum(target=target, record_digest=digest, receipts=receipts, now=10_500, policy=StorageLeasePolicy(min_live_leases=4, min_families=3, min_remaining_seconds=1_000, renew_within_seconds=4_000))
    assert report.decision.kind is StorageLeaseDecisionKind.LIVE_BUT_RENEW_SOON
    assert report.needs_renewal


def test_storage_leasequorum_quarantines_same_sequence_fork() -> None:
    target = sha256(b"lease fork target")
    digest = sha256(b"lease fork digest")
    base = lease(70, "east", target, digest, seq=3, expires=30_000)
    fork_unsigned = replace(base, lease_expires_at=40_000, note="forked same sequence", signature=b"")
    fork = replace(fork_unsigned, signature=kp(70).sign(fork_unsigned.unsigned_payload()))
    others = tuple(lease(i, family, target, digest, seq=3) for i, family in enumerate(("west", "north", "south"), start=71))
    report = assess_storage_lease_quorum(target=target, record_digest=digest, receipts=(base, fork) + others, now=10_500, memory=StorageLeaseMemory())
    assert report.decision.kind is StorageLeaseDecisionKind.QUARANTINE_LEASE_FORK
    assert report.fork_pressure


def test_storage_leasequorum_blocks_live_tombstone() -> None:
    target = sha256(b"lease tomb target")
    digest = sha256(b"lease tomb digest")
    cache = TombstoneCache()
    tomb = TombstoneRecord.create(
        keypair=kp(90),
        target_commitment=storage_tombstone_target(target, digest),
        kind=TombstoneKind.MUTABLE_DELETED,
        issuer_family="owner",
        sequence=1,
        issued_at=10_000,
        expires_at=20_000,
        reason="deleted head",
    )
    assert cache.add(tomb, now=10_500)
    receipts = tuple(lease(i, family, target, digest) for i, family in enumerate(("east", "west", "north", "south"), start=91))
    report = assess_storage_lease_quorum(target=target, record_digest=digest, receipts=receipts, now=10_500, tombstone_cache=cache)
    assert report.decision.kind is StorageLeaseDecisionKind.BLOCKED_BY_TOMBSTONE


def test_readrepair_accepts_healthy_diverse_replicas() -> None:
    target = sha256(b"read target")
    digest = sha256(b"read digest")
    observations = tuple(replica(i, family, target, digest, kind=ReplicaObservationKind.EXACT) for i, family in enumerate(("east", "west", "north", "south"), start=1))
    report = plan_read_repair(target=target, expected_digest=digest, observations=observations, now=11_000, policy=ReadRepairPolicy(min_exact=4, min_exact_families=3))
    assert report.decision.kind is ReadRepairDecisionKind.HEALTHY_DIVERSE_REPLICAS
    assert report.decision.accept


def test_readrepair_schedules_family_capped_repairs_for_missing_and_stale() -> None:
    target = sha256(b"repair target")
    digest = sha256(b"repair digest")
    observations = (
        replica(1, "east", target, digest, kind=ReplicaObservationKind.EXACT),
        replica(2, "east", target, digest, kind=ReplicaObservationKind.STALE),
        replica(3, "west", target, digest, kind=ReplicaObservationKind.MISSING),
        replica(4, "west", target, digest, kind=ReplicaObservationKind.TIMEOUT),
        replica(5, "north", target, digest, kind=ReplicaObservationKind.MISSING),
    )
    report = plan_read_repair(target=target, expected_digest=digest, observations=observations, now=11_000, policy=ReadRepairPolicy(min_exact=4, max_repair_actions=3))
    assert report.decision.kind is ReadRepairDecisionKind.REPAIR_MISSING_OR_STALE
    assert len(report.repair_actions) == 3
    assert len({action.family_id for action in report.repair_actions}) == 3


def test_readrepair_quarantines_wrong_digest() -> None:
    target = sha256(b"wrong read target")
    digest = sha256(b"wrong read digest")
    observations = (
        replica(1, "east", target, digest, kind=ReplicaObservationKind.EXACT),
        replica(2, "west", target, digest, kind=ReplicaObservationKind.WRONG_DIGEST, observed_digest=sha256(b"evil")),
    )
    report = plan_read_repair(target=target, expected_digest=digest, observations=observations, now=11_000)
    assert report.decision.kind is ReadRepairDecisionKind.QUARANTINE_WRONG_DIGEST


def test_readrepair_blocks_resurrection_against_tombstone() -> None:
    target = sha256(b"resurrection target")
    digest = sha256(b"resurrection digest")
    tomb_target = sha256(b"custom tomb target")
    cache = TombstoneCache()
    tomb = TombstoneRecord.create(
        keypair=kp(100),
        target_commitment=tomb_target,
        kind=TombstoneKind.PROVIDER_WITHDRAWN,
        issuer_family="owner",
        sequence=1,
        issued_at=10_000,
        expires_at=20_000,
    )
    assert cache.add(tomb, now=11_000)
    observations = tuple(replica(i, family, target, digest, kind=ReplicaObservationKind.EXACT) for i, family in enumerate(("east", "west", "north", "south"), start=101))
    report = plan_read_repair(target=target, expected_digest=digest, observations=observations, now=11_000, tombstone_cache=cache, tombstone_target=tomb_target)
    assert report.decision.kind is ReadRepairDecisionKind.QUARANTINE_RESURRECTION_PRESSURE
