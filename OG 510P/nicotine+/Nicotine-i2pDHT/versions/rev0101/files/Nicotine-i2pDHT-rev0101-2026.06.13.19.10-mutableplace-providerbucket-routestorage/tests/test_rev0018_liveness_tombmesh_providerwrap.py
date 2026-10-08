from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.adaptivealpha import AdaptiveAlphaPolicy, recommend_adaptive_lookup
from i2p_dht_lab.gardenrefusal import GardenAdmissionPolicy
from i2p_dht_lab.gardenscheduler import GardenSchedulePolicy
from i2p_dht_lab.headlog import HeadEvent
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.livenessbudget import LivenessBudgetDecisionKind, LivenessBudgetPolicy, assess_liveness_budget
from i2p_dht_lab.lookuptranscript import LookupEvent, LookupEventKind, LookupKind, LookupTranscript
from i2p_dht_lab.privateprovider import ProviderCandidate, PrivateProbeBudget, plan_private_provider_probes
from i2p_dht_lab.provider_poison import ProviderNodeMemory, ProviderProbeOutcome, ProviderProbeReceipt
from i2p_dht_lab.provider_refactor import plan_provider_surface_migration
from i2p_dht_lab.providerwrap import observe_provider_receipt, provider_wrapper_readiness
from i2p_dht_lab.probewitness import WitnessClaimKind, WitnessReceipt
from i2p_dht_lab.regionledger import RegionLedger, RegionLedgerPolicy, RegionTombstone
from i2p_dht_lab.regionreceipt import RegionReceiptDecisionKind, bridge_region_ledger_to_garden_schedule
from i2p_dht_lab.sweep import AdvertKind, Advertisement, SweepPolicy
from i2p_dht_lab.tombmesh import TombMeshDecisionKind, TombMeshPolicy, analyze_tombstone_mesh
from i2p_dht_lab.tombstonecache import TombstoneCache, TombstoneCachePolicy, TombstoneKind, TombstoneRecord
from i2p_dht_lab.witnesscache import WitnessCachePolicy, WitnessEvidenceCache


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "rev0018") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def event(seq: int, family: str, path: str, kind: LookupEventKind, completed_at: int) -> LookupEvent:
    return LookupEvent(
        sequence=seq,
        path_id=path,
        family_id=family,
        node_id=ident(40 + seq, "adaptive").node_id,
        kind=kind,
        sent_at_ms=0,
        completed_at_ms=completed_at,
        payload_digest=sha256(b"rev0018 event" + bytes([seq % 256])),
    )


def transcript(name: bytes, events: tuple[LookupEvent, ...]) -> LookupTranscript:
    return LookupTranscript(lookup_id=sha256(b"lookup:" + name), kind=LookupKind.FIND_PROVIDER, target=sha256(b"target:" + name), events=events)


def candidate(n: int, family: str, *, commitment: bool = True) -> ProviderCandidate:
    return ProviderCandidate(provider_node_id=ident(100 + n, "candidate").node_id, family_id=family, distance_rank=n, latency_ms=100 + n, reliability_score=10, supports_commitment_probe=commitment)


def test_liveness_budget_reduces_metadata_when_fast_window_is_captured() -> None:
    tx = transcript(b"fast-capture", (
        event(1, "captured", "p1", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 90),
        event(2, "captured", "p2", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 95),
        event(3, "captured", "p3", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 100),
        event(4, "east", "p4", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 850),
        event(5, "west", "p5", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 900),
    ))
    adaptive = recommend_adaptive_lookup((tx,), policy=AdaptiveAlphaPolicy(base_alpha=3, max_alpha=8, fast_window_ms=20))
    plan = plan_private_provider_probes(
        (candidate(1, "captured", commitment=False), candidate(2, "captured", commitment=False), candidate(3, "east"), candidate(4, "west")),
        namespace="blocks",
        content_key=sha256(b"wanted block"),
        nonce=sha256(b"probe nonce"),
        issued_at=10_000,
        budget=PrivateProbeBudget(max_real_probes=3, max_decoy_probes=1, min_families=2, max_per_family=2, max_content_key_exposures=2),
    )

    report = assess_liveness_budget(adaptive_report=adaptive, probe_plan=plan, policy=LivenessBudgetPolicy(max_metadata_points=1_000, max_lookup_queries=100, max_raw_key_exposures=2))

    assert report.decision.kind is LivenessBudgetDecisionKind.QUARANTINE_FAST_CAPTURE
    assert not report.decision.proceed
    assert report.needs_more_network
    assert report.spend.real_probe_count >= 2


def test_liveness_budget_proceeds_when_probe_shape_is_diverse_and_bounded() -> None:
    tx = transcript(b"clean", (
        event(1, "east", "p1", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 100),
        event(2, "west", "p2", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 500),
        event(3, "north", "p3", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 900),
    ))
    adaptive = recommend_adaptive_lookup((tx,), policy=AdaptiveAlphaPolicy(fast_window_ms=25))
    plan = plan_private_provider_probes(
        (candidate(1, "east"), candidate(2, "west"), candidate(3, "north"), candidate(4, "south")),
        namespace="blocks",
        content_key=sha256(b"bounded block"),
        nonce=sha256(b"bounded nonce"),
        issued_at=20_000,
        budget=PrivateProbeBudget(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, max_content_key_exposures=1),
    )

    report = assess_liveness_budget(adaptive_report=adaptive, probe_plan=plan, policy=LivenessBudgetPolicy(max_lookup_queries=100, max_metadata_points=1_000, min_decoy_ratio_ppm=200_000))

    assert report.decision.kind is LivenessBudgetDecisionKind.PROCEED_BOUNDED
    assert report.decision.proceed
    assert report.spend.raw_key_exposures == 0
    assert report.spend.decoy_ratio_ppm >= 200_000


def witness(n: int, family: str, target: bytes, claim: WitnessClaimKind, *, issued_at: int) -> WitnessReceipt:
    return WitnessReceipt.create(
        keypair=kp(n),
        witness_node_id=ident(n, "witness").node_id,
        witness_family=family,
        subject_node_id=ident(200 + n, "subject").node_id,
        target_commitment=target,
        claim=claim,
        evidence_digest=sha256(b"rev0018 witness" + bytes([n % 256]) + claim.value.encode()),
        issued_at=issued_at,
        ttl=100_000,
    )


def witness_summary(target: bytes, claims: tuple[tuple[int, str, WitnessClaimKind], ...], *, now: int):
    cache = WitnessEvidenceCache()
    cache.ingest(tuple(witness(n, family, target, claim, issued_at=now - 10) for n, family, claim in claims), observed_at=now, now=now)
    return cache.summarize(target_commitment=target, now=now + 1, policy=WitnessCachePolicy(min_total_weight=100, min_families=1, max_per_family=3, max_age_seconds=100_000))


def test_tombstone_mesh_blocks_resurrection_when_live_tombstone_conflicts_with_alive_cache() -> None:
    target = sha256(b"rev0018 withdrawn provider")
    now = 30_000
    cache = TombstoneCache()
    tomb = TombstoneRecord.create(keypair=kp(88), target_commitment=target, kind=TombstoneKind.PROVIDER_WITHDRAWN, issuer_family="owner", sequence=7, issued_at=now - 100, expires_at=now + 5_000, reason="withdrawn")
    assert cache.add(tomb, now=now)
    summary = witness_summary(target, ((1, "east", WitnessClaimKind.PROVIDER_TRUE), (2, "west", WitnessClaimKind.MUTABLE_LATEST)), now=now)
    tomb_report = cache.analyze(target_commitment=target, now=now + 10, witness_summary=summary, policy=TombstoneCachePolicy(resurrection_claim_weight=100))

    mesh = analyze_tombstone_mesh(tombstone_report=tomb_report, witness_summary=summary, policy=TombMeshPolicy(min_witness_families=2, min_resurrection_weight=100))

    assert mesh.decision.kind is TombMeshDecisionKind.BLOCK_RESURRECTION_MESH
    assert mesh.blocks_resurrection
    assert mesh.resurrection_weight >= 100
    assert len(mesh.witness_families) >= 2


def test_tombstone_mesh_quarantines_heads_after_key_compromise_tombstone() -> None:
    target = sha256(b"rev0018 compromised key")
    now = 40_000
    cache = TombstoneCache()
    tomb = TombstoneRecord.create(keypair=kp(89), target_commitment=target, kind=TombstoneKind.KEY_COMPROMISED, issuer_family="owner", sequence=4, issued_at=now - 100, expires_at=now + 5_000)
    assert cache.add(tomb, now=now)
    tomb_report = cache.analyze(target_commitment=target, now=now + 10)
    head_event = HeadEvent(
        target_hex=target.hex(),
        seq=5,
        value_digest=sha256(b"value"),
        record_digest=sha256(b"record"),
        source_node_id=ident(501, "headsource").node_id,
        observed_at=now + 20,
        signer_public_key=kp(89).public_key_bytes,
        salt=b"",
    )

    mesh = analyze_tombstone_mesh(tombstone_report=tomb_report, head_events=(head_event,))

    assert mesh.decision.kind is TombMeshDecisionKind.QUARANTINE_HEAD_AFTER_COMPROMISE
    assert mesh.blocks_resurrection
    assert mesh.newest_head_seq == 5


def advert(n: int, *, weight: int = 1) -> Advertisement:
    key = bytes([n % 256]) + sha256(b"rev0018 advert" + bytes([n % 256]))[1:]
    return Advertisement(key=key, kind=AdvertKind.PROVIDER, namespace="blocks", weight=weight, last_published_at=0)


def test_region_receipts_bind_ledger_batches_to_garden_schedule_decisions() -> None:
    now = 50_000
    ledger = RegionLedger()
    ledger.ingest(tuple(advert(idx, weight=2) for idx in range(1, 5)), source_family="east", now=now)
    item = advert(90)
    ledger.ingest((item,), source_family="west", now=now)
    ledger.add_tombstone(RegionTombstone(key=item.key, kind=item.kind, namespace=item.namespace, issuer_family="owner", issued_at=now - 5, expires_at=now + 1_000, reason="withdrawn"))
    report = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=3, max_batch_weight=4), max_batches=4, large_batch_threshold=99))

    bridge = bridge_region_ledger_to_garden_schedule(
        report,
        garden_keypair=kp(120),
        garden_node_id=ident(120, "garden").node_id,
        requester_node_id=ident(121, "operator").node_id,
        requester_family="operator",
        start_at=now,
        schedule_kwargs={
            "schedule_policy": GardenSchedulePolicy(windows=1, refill_provider_records_per_window=0),
            "admission_policy": GardenAdmissionPolicy(max_provider_records=3, max_refusals_per_window=16),
        },
    )

    assert bridge.request_count == len(report.batches)
    assert bridge.all_receipts_verify
    assert bridge.accepted_count + bridge.refused_count + bridge.dropped_count == len(bridge.receipts)
    assert any(receipt.decision is RegionReceiptDecisionKind.REFUSED_USEFULLY for receipt in bridge.receipts)


def test_provider_wrapper_uses_canonical_provider_poison_memory_and_keeps_migration_visible() -> None:
    now = 60_000
    provider = ident(140, "provider")
    memory = ProviderNodeMemory(provider.node_id)
    receipt = ProviderProbeReceipt.create(
        witness_keypair=kp(141),
        witness_node_id=ident(141, "witness").node_id,
        provider_node_id=provider.node_id,
        namespace="blocks",
        content_key=sha256(b"provider content key"),
        outcome=ProviderProbeOutcome.CONTENT_MATCH,
        issued_at=now,
        expected_digest=sha256(b"expected"),
        received_digest=sha256(b"expected"),
        response_ms=250,
    )

    assessment, decision = observe_provider_receipt(memory, receipt, now=now + 1)
    migration = provider_wrapper_readiness(str(Path(__file__).resolve().parents[1]))
    direct_plan = plan_provider_surface_migration(str(Path(__file__).resolve().parents[1]))

    assert assessment.score_delta > 0
    assert decision.selectable
    assert memory.content_matches == 1
    assert migration.recommendation == direct_plan.recommendation
    assert migration.active_legacy_import_count == direct_plan.active_legacy_import_count
