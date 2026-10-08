from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.gardenrefusal import (
    GardenAdmissionPolicy,
    GardenRefusalReason,
    GardenWorkKind,
    GardenWorkRequest,
    admit_garden_work,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.providerpoison import (
    ProviderPoisonDecisionKind,
    ProviderPoisonPolicy,
    ProviderProbeKind,
    ProviderProbeReceipt,
    analyze_provider_poisoning,
    make_provider_probe_plan,
)
from i2p_dht_lab.records import ProviderRecord


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def provider_record(n: int, *, content_key: bytes = b"content-A", seq: int = 1, expires_at: int = 20_000) -> tuple[ProviderRecord, DhtKeypair, NodeIdentity]:
    keypair = kp(n)
    ident = NodeIdentity.create(destination=f"provider-{n}.b32.i2p", keypair=keypair)
    record = ProviderRecord(
        namespace="rev0011.provider",
        content_key=content_key,
        provider_node_id=ident.node_id,
        provider_public_key=ident.public_key,
        sequence=seq,
        expires_at=expires_at,
        hints={"transport": "i2p-stream", "role": "provider"},
    ).signed(keypair)
    return record, keypair, ident


def receipt(record: ProviderRecord, keypair: DhtKeypair, kind: ProviderProbeKind, *, nonce: bytes = b"challenge", at: int = 10_100) -> ProviderProbeReceipt:
    return ProviderProbeReceipt.create(
        keypair=keypair,
        provider_node_id=record.provider_node_id,
        content_key=record.content_key,
        challenge_nonce=nonce,
        kind=kind,
        issued_at=at,
        block_digest=b"digest" if kind is ProviderProbeKind.CAN_SERVE else b"",
        note=kind.value,
    )


def test_provider_poisoning_treats_signed_false_providers_as_harder_than_silence() -> None:
    r1, k1, _ = provider_record(1)
    r2, k2, _ = provider_record(2)
    r3, k3, _ = provider_record(3)
    report = analyze_provider_poisoning(
        (r1, r2, r3),
        content_key=b"content-A",
        receipts=(
            receipt(r1, k1, ProviderProbeKind.CANNOT_SERVE),
            receipt(r2, k2, ProviderProbeKind.WRONG_CONTENT),
            receipt(r3, k3, ProviderProbeKind.CAN_SERVE),
        ),
        families={r1.provider_node_id: "captured-a", r2.provider_node_id: "captured-b", r3.provider_node_id: "honest-west"},
        now=10_200,
        expected_challenge_nonce=b"challenge",
        policy=ProviderPoisonPolicy(min_true_providers=1, min_true_families=1, false_provider_limit=0),
    )

    assert report.decision.kind is ProviderPoisonDecisionKind.CONTINUE_FALSE_PROVIDER_PRESSURE
    assert report.false_provider_count == 2
    assert report.true_provider_count == 1
    assert report.needs_more_paths
    assert report.poison_families == frozenset({"captured-a", "captured-b"})


def test_provider_poisoning_requires_true_provider_family_diversity_even_with_many_receipts() -> None:
    records = [provider_record(n) for n in (4, 5, 6)]
    report = analyze_provider_poisoning(
        tuple(record for record, _key, _ident in records),
        content_key=b"content-A",
        receipts=tuple(receipt(record, key, ProviderProbeKind.CAN_SERVE) for record, key, _ident in records),
        families={record.provider_node_id: "same-garden-family" for record, _key, _ident in records},
        now=10_200,
        expected_challenge_nonce=b"challenge",
        policy=ProviderPoisonPolicy(min_true_providers=2, min_true_families=2),
    )

    assert report.decision.kind is ProviderPoisonDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY
    assert report.true_provider_count == 3
    assert report.true_families == frozenset({"same-garden-family"})


def test_provider_poisoning_accepts_diverse_true_providers_and_treats_graceful_refusal_as_nonpoison() -> None:
    r1, k1, _ = provider_record(7)
    r2, k2, _ = provider_record(8)
    r3, k3, _ = provider_record(9)
    report = analyze_provider_poisoning(
        (r1, r2, r3),
        content_key=b"content-A",
        receipts=(
            receipt(r1, k1, ProviderProbeKind.CAN_SERVE),
            receipt(r2, k2, ProviderProbeKind.REFUSED_GRACEFULLY),
            receipt(r3, k3, ProviderProbeKind.CAN_SERVE),
        ),
        families={r1.provider_node_id: "garden-east", r2.provider_node_id: "buddy-north", r3.provider_node_id: "direct-west"},
        now=10_200,
        expected_challenge_nonce=b"challenge",
        policy=ProviderPoisonPolicy(min_true_providers=2, min_true_families=2),
    )

    assert report.decision.kind is ProviderPoisonDecisionKind.ACCEPT_TRUE_PROVIDERS
    assert report.decision.accept
    assert report.false_provider_count == 0
    assert any(observation.graceful_refusal for observation in report.observations)


def test_provider_poisoning_detects_invalid_or_wrong_challenge_probe_receipts() -> None:
    r1, k1, _ = provider_record(10)
    r2, _k2, _ = provider_record(11)
    bad_sig = replace(r2, signature=b"x" * 64)
    wrong_challenge = receipt(r1, k1, ProviderProbeKind.CAN_SERVE, nonce=b"wrong")
    report = analyze_provider_poisoning(
        (r1, bad_sig),
        content_key=b"content-A",
        receipts=(wrong_challenge,),
        now=10_200,
        expected_challenge_nonce=b"challenge",
        policy=ProviderPoisonPolicy(min_true_providers=1, min_true_families=1, invalid_receipt_limit=0),
    )

    assert report.decision.kind is ProviderPoisonDecisionKind.CONTINUE_INVALID_PROOF_PRESSURE
    assert report.valid_record_count == 1
    assert report.invalid_probe_count == 1


def test_provider_probe_plan_filters_wrong_key_and_orders_by_sequence() -> None:
    old, _k_old, _ = provider_record(12, seq=1)
    new, _k_new, _ = provider_record(13, seq=5)
    wrong, _k_wrong, _ = provider_record(14, content_key=b"other")
    plan = make_provider_probe_plan((old, wrong, new), content_key=b"content-A", nonce=b"n", issued_at=10_000, now=10_001)

    assert plan.providers_to_probe[0].sequence == 5
    assert plan.providers_to_probe[1].sequence == 1
    assert plan.skipped_invalid == (wrong,)
    assert plan.challenge.verify_time(now=10_001)


def work_request(n: int, family: str, *, kind: GardenWorkKind = GardenWorkKind.REGION_REPROVIDE, provider_cost: int = 100, watch_cost: int = 0, streams: int = 1, bonus: int = 0, issued_at: int = 30_000) -> GardenWorkRequest:
    return GardenWorkRequest(
        requester_node_id=bytes([n]) * 32,
        family_id=family,
        kind=kind,
        target=b"target" * 6 + bytes([n, n]),
        issued_at=issued_at + n,
        stream_cost=streams,
        provider_record_cost=provider_cost,
        mutable_watch_cost=watch_cost,
        priority_bonus=bonus,
    )


def test_garden_refusal_preserves_capacity_for_diverse_families_under_flood() -> None:
    garden = kp(40)
    ident = NodeIdentity.create(destination="garden-40.b32.i2p", keypair=garden)
    policy = GardenAdmissionPolicy(max_streams=4, max_provider_records=400, max_mutable_watches=0, max_accepts_per_family=1, retry_base_seconds=300)
    flood = [work_request(i, "captured", provider_cost=100, bonus=5) for i in range(1, 5)]
    diverse = [work_request(10, "buddy", provider_cost=100), work_request(11, "garden-west", provider_cost=100), work_request(12, "direct", provider_cost=100)]

    batch = admit_garden_work(flood + diverse, garden_keypair=garden, garden_node_id=ident.node_id, now=30_100, policy=policy)

    assert len(batch.accepted) == 4
    assert len(batch.refused) == 3
    assert batch.accepted_families == frozenset({"captured", "buddy", "garden-west", "direct"})
    assert sum(1 for decision in batch.refused if decision.reason is GardenRefusalReason.PER_FAMILY_QUOTA) == 3
    assert all(decision.receipt is not None and decision.receipt.verify(now=30_101, expected_garden_public_key=garden.public_key_bytes) for decision in batch.refused)


def test_garden_refusal_prioritizes_witness_and_head_work_over_bulk_provider_floods() -> None:
    garden = kp(41)
    ident = NodeIdentity.create(destination="garden-41.b32.i2p", keypair=garden)
    policy = GardenAdmissionPolicy(max_streams=2, max_provider_records=100, max_mutable_watches=1, max_accepts_per_family=2)
    bulk = work_request(20, "bulk", kind=GardenWorkKind.BULK_PROVIDER, provider_cost=100, streams=1)
    witness = work_request(21, "sentinel", kind=GardenWorkKind.WITNESS_QUERY, provider_cost=0, streams=1)
    head_watch = work_request(22, "watcher", kind=GardenWorkKind.HEAD_WATCH, provider_cost=0, watch_cost=1, streams=1)

    batch = admit_garden_work((bulk, witness, head_watch), garden_keypair=garden, garden_node_id=ident.node_id, now=30_100, policy=policy)

    accepted_kinds = {decision.request.kind for decision in batch.accepted}
    assert accepted_kinds == {GardenWorkKind.WITNESS_QUERY, GardenWorkKind.HEAD_WATCH}
    assert any(decision.reason is GardenRefusalReason.OVER_STREAM_BUDGET for decision in batch.refused)


def test_garden_refusal_budget_exhaustion_turns_later_refusals_into_explicit_drops() -> None:
    garden = kp(42)
    ident = NodeIdentity.create(destination="garden-42.b32.i2p", keypair=garden)
    policy = GardenAdmissionPolicy(max_streams=0, max_provider_records=0, max_mutable_watches=0, max_refusals_per_window=1)
    requests = [work_request(30 + i, f"family-{i}", provider_cost=1, streams=1) for i in range(3)]

    batch = admit_garden_work(requests, garden_keypair=garden, garden_node_id=ident.node_id, now=30_100, policy=policy)

    assert len(batch.refused) == 1
    assert len(batch.dropped) == 2
    assert all(decision.reason is GardenRefusalReason.REFUSAL_BUDGET_EXHAUSTED for decision in batch.dropped)


def test_garden_refusal_expired_or_invalid_requests_are_dropped_not_dressed_as_graceful() -> None:
    garden = kp(43)
    ident = NodeIdentity.create(destination="garden-43.b32.i2p", keypair=garden)
    expired = work_request(50, "old", issued_at=10_000)
    invalid = replace(work_request(51, "bad"), stream_cost=-1)

    batch = admit_garden_work((expired, invalid), garden_keypair=garden, garden_node_id=ident.node_id, now=31_000)

    assert len(batch.accepted) == 0
    assert len(batch.refused) == 0
    assert {decision.reason for decision in batch.dropped} == {GardenRefusalReason.EXPIRED_REQUEST, GardenRefusalReason.INVALID_REQUEST}
