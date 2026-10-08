from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.storagelease import (
    STORAGE_LEASE_DOMAIN,
    StorageLeaseDecisionKind,
    StorageStorageLeaseMemory,
    StorageLeasePolicy,
    StorageStorageLeaseReceiptKind,
    StorageLeaseReceipt,
    assess_storage_lease_quorum,
)
from i2p_dht_lab.readrepair import (
    ReadRepairDecisionKind,
    ReadRepairPolicy,
    ReplicaObservation,
    ReplicaObservationKind,
    plan_read_repair,
)
from i2p_dht_lab.storeflight import (
    ReadBackKind,
    StoreAckKind,
    StoreChallenge,
    StoreClass,
    StoreFlightDecisionKind,
    StoreFlightPolicy,
    StoreReadBack,
    StoreReceipt,
    StoreRecordKind,
    analyze_store_flight,
)
from i2p_dht_lab.tombstonecache import TombstoneCache, TombstoneKind, TombstoneRecord


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "rev0019") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def challenge(*, issued_at: int = 10_000, nonce: bytes = b"challenge-a") -> StoreChallenge:
    return StoreChallenge(
        target=sha256(b"store target"),
        record_digest=sha256(b"record payload digest"),
        record_kind=StoreRecordKind.MUTABLE_HEAD,
        challenge_nonce=nonce,
        issued_at=issued_at,
        ttl=1_000,
    )


def receipt(n: int, family: str, ch: StoreChallenge, *, ack: StoreAckKind = StoreAckKind.STORED, issued_at: int = 10_010, lease_expires_at: int = 20_000, rank: int = 0) -> StoreReceipt:
    return StoreReceipt.create(
        keypair=kp(n),
        storage_node_id=ident(n, "store").node_id,
        family_id=family,
        challenge=ch,
        store_class=StoreClass.CANONICAL,
        ack_kind=ack,
        issued_at=issued_at,
        lease_expires_at=lease_expires_at,
        replica_rank=rank,
    )


def readback(n: int, family: str, ch: StoreChallenge, *, kind: ReadBackKind = ReadBackKind.EXACT, observed_digest: bytes | None = None) -> StoreReadBack:
    return StoreReadBack(
        storage_node_id=ident(n, "store").node_id,
        family_id=family,
        kind=kind,
        target=ch.target,
        expected_digest=ch.record_digest,
        observed_digest=ch.record_digest if observed_digest is None and kind is ReadBackKind.EXACT else (observed_digest or b""),
        observed_at=10_050,
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


def test_storeflight_accepts_diverse_receipts_and_read_after_write() -> None:
    ch = challenge()
    receipts = tuple(receipt(i, family, ch, rank=i) for i, family in enumerate(("east", "west", "north", "south"), start=1))
    reads = (readback(1, "east", ch), readback(2, "west", ch))
    report = analyze_store_flight(challenge=ch, receipts=receipts, readbacks=reads, now=10_100, policy=StoreFlightPolicy(min_store_acks=4, min_store_families=3, min_readbacks=2, min_readback_families=2))
    assert report.decision.kind is StoreFlightDecisionKind.STORED_WITH_PRESSURE
    assert report.decision.accept
    assert len(report.stored_families) >= 3
    assert len(report.readback_families) == 2


def test_storeflight_receipts_without_readback_are_not_final_by_default() -> None:
    ch = challenge()
    receipts = tuple(receipt(i, family, ch, rank=i) for i, family in enumerate(("east", "west", "north", "south"), start=10))
    report = analyze_store_flight(challenge=ch, receipts=receipts, now=10_100, policy=StoreFlightPolicy(min_readbacks=2, min_readback_families=2))
    assert report.decision.kind is StoreFlightDecisionKind.STORED_BUT_NEEDS_READBACK
    assert not report.decision.accept


def test_storeflight_detects_stale_challenge_replay() -> None:
    old = challenge(issued_at=9_000, nonce=b"old-nonce")
    new = challenge(issued_at=10_000, nonce=b"new-nonce")
    replayed = receipt(31, "east", old, issued_at=9_010, lease_expires_at=30_000)
    report = analyze_store_flight(challenge=new, receipts=(replayed,), now=10_100)
    assert report.decision.kind is StoreFlightDecisionKind.CONTINUE_REPLAY_PRESSURE
    assert report.replay_pressure == 1


def test_storeflight_quarantines_wrong_readback_digest() -> None:
    ch = challenge()
    receipts = tuple(receipt(i, family, ch, rank=i) for i, family in enumerate(("east", "west", "north", "south"), start=40))
    reads = (readback(40, "east", ch), readback(41, "west", ch, kind=ReadBackKind.WRONG_DIGEST, observed_digest=sha256(b"bad")))
    report = analyze_store_flight(challenge=ch, receipts=receipts, readbacks=reads, now=10_100)
    assert report.decision.kind is StoreFlightDecisionKind.QUARANTINE_CONTRADICTION


def test_leasequorum_accepts_live_diverse_leases() -> None:
    target = sha256(b"lease target")
    digest = sha256(b"lease digest")
    receipts = tuple(lease(i, family, target, digest) for i, family in enumerate(("east", "west", "north", "south"), start=1))
    report = assess_storage_lease_quorum(target=target, record_digest=digest, receipts=receipts, now=10_500, policy=StorageLeasePolicy(min_live_leases=4, min_families=3))
    assert report.decision.kind is StorageLeaseDecisionKind.LIVE_DIVERSE_LEASES
    assert report.decision.accept
    assert len(report.family_counts) >= 3


def test_leasequorum_marks_near_horizon_as_renew_soon() -> None:
    target = sha256(b"lease renew target")
    digest = sha256(b"lease renew digest")
    receipts = tuple(lease(i, family, target, digest, expires=14_000) for i, family in enumerate(("east", "west", "north", "south"), start=10))
    report = assess_storage_lease_quorum(target=target, record_digest=digest, receipts=receipts, now=10_500, policy=StorageLeasePolicy(min_live_leases=4, min_families=3, min_remaining_seconds=1_000, renew_within_seconds=4_000))
    assert report.decision.kind is StorageLeaseDecisionKind.LIVE_BUT_RENEW_SOON
    assert report.needs_renewal


def test_leasequorum_quarantines_same_sequence_fork() -> None:
    target = sha256(b"lease fork target")
    digest = sha256(b"lease fork digest")
    base = lease(70, "east", target, digest, seq=3, expires=30_000)
    fork_unsigned = replace(base, lease_expires_at=40_000, note="forked same sequence", signature=b"")
    fork = replace(fork_unsigned, signature=kp(70).sign(fork_unsigned.unsigned_payload()))
    others = tuple(lease(i, family, target, digest, seq=3) for i, family in enumerate(("west", "north", "south"), start=71))
    report = assess_storage_lease_quorum(target=target, record_digest=digest, receipts=(base, fork) + others, now=10_500, memory=StorageLeaseMemory())
    assert report.decision.kind is StorageLeaseDecisionKind.QUARANTINE_LEASE_FORK
    assert report.fork_pressure


def test_leasequorum_blocks_live_tombstone() -> None:
    target = sha256(b"lease tomb target")
    digest = sha256(b"lease tomb digest")
    tomb_target = sha256(STORAGE_LEASE_DOMAIN + b":tombstone-target:" + target + digest)
    cache = TombstoneCache()
    tomb = TombstoneRecord.create(
        keypair=kp(90),
        target_commitment=tomb_target,
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
