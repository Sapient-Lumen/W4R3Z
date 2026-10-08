from __future__ import annotations

from i2p_dht_lab.adaptivealpha import AdaptiveLookupDecisionKind
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.interestledger import (
    InterestBudgetPolicy,
    InterestDecisionKind,
    InterestEvent,
    InterestEventKind,
    InterestLedger,
    events_from_liveness_report,
)
from i2p_dht_lab.livenessbudget import LivenessBudgetDecision, LivenessBudgetDecisionKind, LivenessBudgetReport, LivenessSpend
from i2p_dht_lab.siblingcast import SiblingAckKind, SiblingAckPolicy, SiblingCandidate, SiblingCastPolicy, SiblingStoreAck
from i2p_dht_lab.storemesh import (
    StoreLedgerDecisionKind,
    StoreMeshDecisionKind,
    StoreMeshPolicy,
    StoreReceiptLedger,
    StoreRecordKind,
    StoreWorkItem,
    assess_store_round,
    plan_store_mesh,
)
from i2p_dht_lab.tombstonecache import TombstoneCache, TombstoneKind, TombstoneRecord


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def target(name: bytes) -> bytes:
    return sha256(b"rev0019 target " + name)


def candidate(n: int, family: str, key: bytes, *, refusal_until: int = 0, garden: bool = False) -> SiblingCandidate:
    node_id = bytes([n % 256]) + sha256(key + bytes([n % 256]))[1:]
    return SiblingCandidate(node_id=node_id, family_id=family, garden=garden, latency_ms=80 + n, capacity_score=100 - n, refusal_until=refusal_until)


def ack(node: SiblingCandidate, kind: SiblingAckKind, digest: bytes, *, rank: int, at: int = 10_010) -> SiblingStoreAck:
    return SiblingStoreAck(node.node_id, node.family_id, kind, digest, replica_rank=rank, observed_at=at, rtt_ms=90 + rank)


def work_item(kind: StoreRecordKind = StoreRecordKind.MUTABLE_HEAD, *, key: bytes | None = None, digest: bytes | None = None) -> StoreWorkItem:
    key = key or target(b"store")
    digest = digest or sha256(b"rev0019 record digest")
    return StoreWorkItem(target=key, record_digest=digest, kind=kind, namespace="heads", issued_at=10_000, expires_at=20_000, priority=80)


def candidates(key: bytes) -> tuple[SiblingCandidate, ...]:
    return tuple(candidate(i, family, key, garden=(i % 2 == 0)) for i, family in enumerate(("east", "west", "north", "south", "garden", "mirror"), start=1))


def policy() -> StoreMeshPolicy:
    return StoreMeshPolicy(
        sibling_policy=SiblingCastPolicy(desired_siblings=5, min_siblings=4, min_families=3, max_per_family=2, reserve_count=1),
        ack_policy=SiblingAckPolicy(min_store_acks=4, min_store_families=3, timeout_limit=2),
        refusal_hold_count=3,
        refusal_backoff_seconds=900,
        cumulative_min_store_acks=5,
        cumulative_min_families=3,
    )


def test_store_mesh_blocks_non_tombstone_when_live_tombstone_exists() -> None:
    now = 10_100
    key = target(b"tombstone-block")
    digest = sha256(b"blocked record")
    tombstone = TombstoneRecord.create(
        keypair=kp(1),
        target_commitment=key,
        kind=TombstoneKind.MUTABLE_DELETED,
        issuer_family="owner",
        sequence=1,
        issued_at=10_000,
        expires_at=20_000,
        subject_digest=digest,
    )
    cache = TombstoneCache()
    assert cache.add(tombstone, now=now)
    tomb_report = cache.analyze(target_commitment=key, now=now)
    plan = plan_store_mesh(candidates(key), item=work_item(key=key, digest=digest), now=now, tombstone_report=tomb_report, policy=policy())
    assert plan.decision.kind is StoreMeshDecisionKind.PLAN_BLOCKED_BY_TOMBSTONE
    assert plan.sibling_plan is None


def test_store_mesh_accepts_exact_digest_family_diverse_ack_round() -> None:
    now = 10_100
    key = target(b"ack-round")
    item = work_item(key=key)
    plan = plan_store_mesh(candidates(key), item=item, now=now, policy=policy())
    assert plan.decision.kind is StoreMeshDecisionKind.PLAN_READY
    assert plan.sibling_plan is not None
    acks = tuple(ack(node, SiblingAckKind.STORED, item.record_digest, rank=rank) for rank, node in enumerate(plan.sibling_plan.primary[:4]))
    report = assess_store_round(plan, acks=acks, now=now, policy=policy())
    assert report.decision.kind is StoreMeshDecisionKind.STORED_DIVERSE
    assert report.accepted
    assert len(report.stored_families) >= 3


def test_store_mesh_holds_under_useful_refusal_pressure_before_retrying() -> None:
    now = 10_100
    key = target(b"refusal-round")
    item = work_item(kind=StoreRecordKind.PROVIDER_RECORD, key=key)
    plan = plan_store_mesh(candidates(key), item=item, now=now, policy=policy())
    assert plan.sibling_plan is not None
    refusal_acks = tuple(ack(node, SiblingAckKind.REFUSED, item.record_digest, rank=rank) for rank, node in enumerate(plan.sibling_plan.primary[:3]))
    report = assess_store_round(plan, acks=refusal_acks, now=now, policy=policy())
    assert report.decision.kind is StoreMeshDecisionKind.HOLD_USEFUL_REFUSAL
    assert report.decision.retry_after_seconds == 900
    assert not report.accepted


def test_store_receipt_ledger_accepts_cumulative_diverse_store_evidence() -> None:
    now = 10_100
    key = target(b"cumulative")
    item = work_item(kind=StoreRecordKind.IMMUTABLE, key=key)
    plan = plan_store_mesh(candidates(key), item=item, now=now, policy=policy())
    assert plan.sibling_plan is not None
    first = assess_store_round(plan, acks=(ack(plan.sibling_plan.primary[0], SiblingAckKind.STORED, item.record_digest, rank=0), ack(plan.sibling_plan.primary[1], SiblingAckKind.STORED, item.record_digest, rank=1)), now=now, policy=policy())
    second = assess_store_round(plan, acks=tuple(ack(node, SiblingAckKind.STORED, item.record_digest, rank=rank + 2) for rank, node in enumerate(plan.sibling_plan.primary[2:5])), now=now + 10, policy=policy())
    ledger = StoreReceiptLedger()
    ledger.observe(first)
    ledger.observe(second)
    summary = ledger.summarize(record_digest=item.record_digest, now=now + 20, policy=policy())
    assert summary.decision.kind is StoreLedgerDecisionKind.STORED_CUMULATIVE
    assert summary.stored_node_count >= 5
    assert len(summary.stored_families) >= 3


def test_store_receipt_ledger_quarantines_cross_round_node_contradiction() -> None:
    now = 10_100
    key = target(b"cumulative-bad")
    item = work_item(kind=StoreRecordKind.IMMUTABLE, key=key)
    plan = plan_store_mesh(candidates(key), item=item, now=now, policy=policy())
    assert plan.sibling_plan is not None
    node = plan.sibling_plan.primary[0]
    first = assess_store_round(plan, acks=(ack(node, SiblingAckKind.STORED, item.record_digest, rank=0),), now=now, policy=policy())
    second = assess_store_round(plan, acks=(ack(node, SiblingAckKind.STORED, sha256(b"different digest"), rank=1),), now=now + 10, policy=policy())
    ledger = StoreReceiptLedger()
    ledger.observe(first)
    ledger.observe(second)
    summary = ledger.summarize(record_digest=item.record_digest, now=now + 20, policy=policy())
    assert summary.decision.kind is StoreLedgerDecisionKind.QUARANTINE_CUMULATIVE_CONTRADICTION
    assert node.node_id in summary.contradiction_node_ids


def event(key: bytes, family: str, kind: InterestEventKind, *, at: int = 1000, points: int = 10, raw: bool = False, decoy: bool = False, round_seed: bytes = b"r") -> InterestEvent:
    return InterestEvent(key, family, kind, at, points, raw_content_key_exposed=raw, decoy=decoy, round_id=sha256(round_seed + family.encode() + kind.value.encode()))


def test_interest_ledger_allows_diverse_budgeted_round_with_decoys() -> None:
    key = target(b"interest-ok")
    ledger = InterestLedger()
    ledger.ingest((
        event(key, "east", InterestEventKind.LOOKUP_QUERY, points=3),
        event(key, "west", InterestEventKind.LOOKUP_QUERY, points=3),
        event(key, "north", InterestEventKind.PROVIDER_PROBE_COMMITMENT, points=8),
        event(key, "south", InterestEventKind.DECOY_PROBE, points=5, decoy=True),
    ))
    report = ledger.assess(target_commitment=key, now=1100, policy=InterestBudgetPolicy(max_target_points=100, min_decoy_ratio_ppm=250_000, max_rounds_per_target=8))
    assert report.decision.kind is InterestDecisionKind.ALLOW_NEXT_ROUND
    assert report.decoy_ratio_ppm >= 250_000
    assert not report.blocks_next_round


def test_interest_ledger_blocks_raw_key_exposure() -> None:
    key = target(b"interest-raw")
    ledger = InterestLedger()
    ledger.ingest(tuple(event(key, f"family-{i}", InterestEventKind.PROVIDER_PROBE_RAW, points=35, raw=True, round_seed=bytes([i])) for i in range(3)))
    report = ledger.assess(target_commitment=key, now=1100, policy=InterestBudgetPolicy(max_raw_key_exposures=1, max_target_points=999, max_rounds_per_target=10, min_decoy_ratio_ppm=0))
    assert report.decision.kind is InterestDecisionKind.REDUCE_RAW_EXPOSURE
    assert report.raw_key_exposures == 3


def test_interest_ledger_rotates_when_one_family_sees_too_much_target_interest() -> None:
    key = target(b"interest-family")
    ledger = InterestLedger()
    ledger.ingest((
        event(key, "captured", InterestEventKind.LOOKUP_QUERY, points=30, round_seed=b"a"),
        event(key, "captured", InterestEventKind.PROVIDER_PROBE_COMMITMENT, points=30, round_seed=b"b"),
        event(key, "east", InterestEventKind.DECOY_PROBE, points=5, decoy=True, round_seed=b"c"),
    ))
    report = ledger.assess(target_commitment=key, now=1100, policy=InterestBudgetPolicy(max_family_fraction_ppm=600_000, max_target_points=999, max_rounds_per_target=10, min_decoy_ratio_ppm=0))
    assert report.decision.kind is InterestDecisionKind.ROTATE_FAMILIES
    assert report.max_family_fraction_ppm > 600_000


def test_interest_ledger_stops_repeated_rounds_even_when_points_are_small() -> None:
    key = target(b"interest-repeat")
    ledger = InterestLedger()
    ledger.ingest(tuple(event(key, "east", InterestEventKind.LOOKUP_QUERY, at=1000 + i, points=1, round_seed=bytes([i])) for i in range(5)))
    report = ledger.assess(target_commitment=key, now=1100, policy=InterestBudgetPolicy(max_rounds_per_target=3, max_target_points=999, max_family_fraction_ppm=1_000_000, min_decoy_ratio_ppm=0))
    assert report.decision.kind is InterestDecisionKind.STOP_TARGET_REPETITION
    assert report.target_round_count == 5


def test_events_from_liveness_report_create_budget_trace_for_repeated_round_ledger() -> None:
    key = target(b"interest-helper")
    spend = LivenessSpend(
        lookup_queries=4,
        real_probe_count=2,
        decoy_probe_count=2,
        raw_key_exposures=1,
        metadata_points=0,
        real_probe_families=frozenset({"east", "west"}),
        probe_families=frozenset({"east", "west", "cover"}),
    )
    report = LivenessBudgetReport(
        adaptive_decision_kind=AdaptiveLookupDecisionKind.WIDEN_FOR_PATH_DIVERSITY,
        spend=spend,
        decision=LivenessBudgetDecision(LivenessBudgetDecisionKind.PROCEED_BOUNDED, True, "fixture"),
        transcript_digest=sha256(b"fake liveness report"),
    )
    events = events_from_liveness_report(report, target_commitment=key, now=1200, query_families=("east", "west", "north"))
    ledger = InterestLedger()
    ledger.ingest(events)
    summary = ledger.assess(target_commitment=key, now=1200, policy=InterestBudgetPolicy(max_target_points=200, max_rounds_per_target=10, max_family_fraction_ppm=750_000, max_raw_key_exposures=2, min_decoy_ratio_ppm=250_000))
    assert len(events) == 8
    assert summary.raw_key_exposures == 1
    assert summary.decoy_ratio_ppm >= 250_000
    assert summary.decision.kind is InterestDecisionKind.ALLOW_NEXT_ROUND
