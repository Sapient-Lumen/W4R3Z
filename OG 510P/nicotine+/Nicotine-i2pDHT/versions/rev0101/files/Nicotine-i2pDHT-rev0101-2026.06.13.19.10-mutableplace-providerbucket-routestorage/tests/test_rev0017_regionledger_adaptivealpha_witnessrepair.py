from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.adaptivealpha import AdaptiveLookupDecisionKind, AdaptiveAlphaPolicy, recommend_adaptive_lookup
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.lookuptranscript import LookupEvent, LookupEventKind, LookupKind, LookupTranscript
from i2p_dht_lab.provider_refactor import plan_provider_surface_migration
from i2p_dht_lab.probewitness import WitnessClaimKind, WitnessReceipt
from i2p_dht_lab.regionledger import RegionLedger, RegionLedgerDecisionKind, RegionLedgerPolicy, RegionTombstone
from i2p_dht_lab.sweep import AdvertKind, Advertisement, SweepPolicy
from i2p_dht_lab.tombstonecache import TombstoneCache, TombstoneCacheDecisionKind, TombstoneCachePolicy, TombstoneKind, TombstoneRecord
from i2p_dht_lab.witnesscache import WitnessCacheDecisionKind, WitnessCachePolicy, WitnessEvidenceCache
from i2p_dht_lab.witnessrepair import WitnessRepairActionKind, WitnessRepairDecisionKind, WitnessRepairPolicy, plan_witness_repair


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "node") -> NodeIdentity:
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
        payload_digest=sha256(b"payload" + bytes([seq % 256])),
    )


def transcript(name: bytes, events: tuple[LookupEvent, ...]) -> LookupTranscript:
    return LookupTranscript(lookup_id=sha256(b"lookup:" + name), kind=LookupKind.FIND_PROVIDER, target=sha256(b"target:" + name), events=events)


def test_adaptive_alpha_quarantines_fast_captured_window_before_acceptance() -> None:
    tx = transcript(b"fast-capture", (
        event(1, "captured", "p1", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 90),
        event(2, "captured", "p2", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 95),
        event(3, "captured", "p3", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 100),
        event(4, "east", "p4", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 800),
        event(5, "west", "p5", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 900),
    ))
    report = recommend_adaptive_lookup((tx,), policy=AdaptiveAlphaPolicy(base_alpha=3, max_alpha=8, fast_window_ms=20))

    assert report.decision.kind is AdaptiveLookupDecisionKind.QUARANTINE_FAST_CAPTURE
    assert report.needs_more_rounds
    assert report.next_knobs.alpha > 3
    assert report.next_knobs.beta > 3
    assert report.next_knobs.require_new_family


def test_adaptive_alpha_expands_for_timeouts_but_holds_for_useful_refusals() -> None:
    timeout_tx = transcript(b"timeouts", (
        event(1, "east", "p1", LookupEventKind.TIMEOUT, 3_000),
        event(2, "west", "p2", LookupEventKind.TIMEOUT, 3_100),
        event(3, "north", "p3", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 2_200),
        event(4, "south", "p4", LookupEventKind.TIMEOUT, 3_200),
    ))
    timeout_report = recommend_adaptive_lookup((timeout_tx,), policy=AdaptiveAlphaPolicy(timeout_expand_fraction=0.50, timeout_ms=2_000, max_timeout_ms=6_000))
    assert timeout_report.decision.kind is AdaptiveLookupDecisionKind.WIDEN_FOR_TIMEOUT_PRESSURE
    assert timeout_report.next_knobs.alpha > 3
    assert timeout_report.next_knobs.timeout_ms > 2_000

    refusal_tx = transcript(b"refusals", (
        event(1, "east", "p1", LookupEventKind.USEFUL_REFUSAL, 300),
        event(2, "west", "p2", LookupEventKind.USEFUL_REFUSAL, 350),
        event(3, "north", "p3", LookupEventKind.USEFUL_REFUSAL, 360),
        event(4, "south", "p4", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 900),
    ))
    refusal_report = recommend_adaptive_lookup((refusal_tx,), policy=AdaptiveAlphaPolicy(refusal_hold_fraction=0.50))
    assert refusal_report.decision.kind is AdaptiveLookupDecisionKind.HOLD_FOR_USEFUL_REFUSAL
    assert refusal_report.next_knobs.alpha == 3


def test_adaptive_alpha_accepts_diverse_success_without_poison_pressure() -> None:
    tx = transcript(b"diverse", (
        event(1, "east", "p1", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 100),
        event(2, "west", "p2", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 500),
        event(3, "north", "p3", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 900),
    ))
    report = recommend_adaptive_lookup((tx,), policy=AdaptiveAlphaPolicy(fast_window_ms=25))
    assert report.decision.kind is AdaptiveLookupDecisionKind.ACCEPT_READY
    assert report.decision.accept
    assert not report.next_knobs.require_new_family


def advert(n: int, family: str, *, last_published_at: int = 0, weight: int = 1) -> Advertisement:
    # Use deterministic keys with varied leading bytes so region grouping is visible.
    key = bytes([n % 256]) + sha256(b"advert" + bytes([n % 256]))[1:]
    return Advertisement(key=key, kind=AdvertKind.PROVIDER, namespace="blocks", weight=weight, last_published_at=last_published_at)


def test_region_ledger_suppresses_live_tombstoned_advertisement_and_reannounces_tombstone() -> None:
    now = 10_000
    ledger = RegionLedger()
    item = advert(5, "east")
    ledger.ingest((item,), source_family="east", now=now)
    ledger.add_tombstone(RegionTombstone(key=item.key, kind=item.kind, namespace=item.namespace, issuer_family="owner", issued_at=now - 10, expires_at=now + 1_000, reason="withdrawn"))

    report = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=4, max_batch_weight=10)))

    assert report.decision.kind is RegionLedgerDecisionKind.TOMBSTONE_ONLY
    assert report.decision.accept
    assert len(report.suppressed_advertisements) == 1
    assert report.batches[0].tombstones
    assert not report.batches[0].advertisements


def test_region_ledger_quarantines_large_source_monoculture_before_garden_sweep() -> None:
    now = 20_000
    ledger = RegionLedger()
    ledger.ingest(tuple(advert(idx, "captured") for idx in range(12)), source_family="captured", now=now)

    report = ledger.plan(now=now, policy=RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=4, max_batch_weight=100), large_batch_threshold=10, min_source_families_for_large_batch=2))

    assert report.decision.kind is RegionLedgerDecisionKind.QUARANTINE_SOURCE_MONOCULTURE
    assert not report.decision.accept
    assert report.source_family_counts == {"captured": 12}


def test_region_ledger_plans_region_fair_batches_and_marks_published() -> None:
    now = 30_000
    ledger = RegionLedger()
    ledger.ingest(tuple(advert(idx, "east", weight=2) for idx in range(4)), source_family="east", now=now)
    ledger.ingest(tuple(advert(10 + idx, "west", weight=2) for idx in range(4)), source_family="west", now=now)

    policy = RegionLedgerPolicy(sweep_policy=SweepPolicy(interval_seconds=100, expiration_seconds=1_000, region_prefix_bits=3, max_batch_weight=4), max_batches=4, max_per_source_family=4, large_batch_threshold=99)
    report = ledger.plan(now=now, policy=policy)

    assert report.decision.kind is RegionLedgerDecisionKind.PLAN_READY
    assert report.batch_count > 1
    assert all(batch.total_weight <= 4 for batch in report.batches)
    old_digest = report.transcript_digest
    ledger.mark_published(report.batches[0], published_at=now)
    report_after_publish = ledger.plan(now=now + 10, policy=policy)
    assert report_after_publish.transcript_digest != old_digest


def receipt(n: int, family: str, target: bytes, claim: WitnessClaimKind, *, issued_at: int = 50_000) -> WitnessReceipt:
    return WitnessReceipt.create(
        keypair=kp(n),
        witness_node_id=ident(n, "witness").node_id,
        witness_family=family,
        subject_node_id=ident(200 + n, "subject").node_id,
        target_commitment=target,
        claim=claim,
        evidence_digest=sha256(b"witness evidence" + bytes([n % 256]) + claim.value.encode()),
        issued_at=issued_at,
        ttl=100_000,
    )


def witness_summary(target: bytes, claims: tuple[tuple[int, str, WitnessClaimKind], ...], *, now: int = 50_010):
    cache = WitnessEvidenceCache()
    cache.ingest(tuple(receipt(n, family, target, claim, issued_at=now - 10) for n, family, claim in claims), observed_at=now, now=now)
    return cache.summarize(target_commitment=target, now=now + 5, policy=WitnessCachePolicy(min_total_weight=100, min_families=1, max_per_family=3, max_age_seconds=100_000))


def test_tombstone_cache_blocks_cached_provider_resurrection_pressure() -> None:
    target = sha256(b"tombstoned provider")
    now = 60_000
    cache = TombstoneCache()
    tomb = TombstoneRecord.create(keypair=kp(91), target_commitment=target, kind=TombstoneKind.PROVIDER_WITHDRAWN, issuer_family="owner", sequence=7, issued_at=now - 100, expires_at=now + 5_000, reason="provider withdrew")
    assert cache.add(tomb, now=now)
    summary = witness_summary(target, ((1, "east", WitnessClaimKind.PROVIDER_TRUE), (2, "west", WitnessClaimKind.PROVIDER_TRUE)), now=now)

    report = cache.analyze(target_commitment=target, now=now + 10, witness_summary=summary, policy=TombstoneCachePolicy(resurrection_claim_weight=100))

    assert report.decision.kind is TombstoneCacheDecisionKind.BLOCK_RESURRECTION_PRESSURE
    assert report.blocks_resurrection
    assert report.resurrection_weight >= 100


def test_tombstone_cache_quarantines_same_sequence_tombstone_fork() -> None:
    target = sha256(b"forked tombstone")
    now = 70_000
    cache = TombstoneCache()
    a = TombstoneRecord.create(keypair=kp(92), target_commitment=target, kind=TombstoneKind.MUTABLE_DELETED, issuer_family="owner", sequence=3, issued_at=now - 100, expires_at=now + 5_000, reason="deleted")
    b = TombstoneRecord.create(keypair=kp(92), target_commitment=target, kind=TombstoneKind.MUTABLE_DELETED, issuer_family="owner", sequence=3, issued_at=now - 90, expires_at=now + 5_000, reason="different deleted reason")
    cache.ingest((a, b), now=now)

    report = cache.analyze(target_commitment=target, now=now + 1)
    assert report.decision.kind is TombstoneCacheDecisionKind.QUARANTINE_TOMBSTONE_FORK
    assert not report.decision.accept


def test_tombstone_cache_demands_diversity_for_key_compromise_tombstone() -> None:
    target = sha256(b"compromised key")
    now = 80_000
    cache = TombstoneCache()
    tomb = TombstoneRecord.create(keypair=kp(93), target_commitment=target, kind=TombstoneKind.KEY_COMPROMISED, issuer_family="owner", sequence=4, issued_at=now - 100, expires_at=now + 5_000)
    cache.add(tomb, now=now)

    report = cache.analyze(target_commitment=target, now=now + 1, policy=TombstoneCachePolicy(min_issuer_families=2, require_family_diversity_for_key_compromise=True))
    assert report.decision.kind is TombstoneCacheDecisionKind.CONTINUE_NEEDS_TOMBSTONE_DIVERSITY


def test_witness_repair_asks_missing_families_when_cache_is_too_narrow() -> None:
    target = sha256(b"repair target")
    summary = witness_summary(target, ((1, "east", WitnessClaimKind.PROVIDER_TRUE),), now=90_000)
    assert summary.decision.kind in {WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE, WitnessCacheDecisionKind.CONTINUE_INSUFFICIENT_DIVERSITY}
    # Re-summarize with stricter family requirement so repair has work to do.
    cache = WitnessEvidenceCache()
    cache.ingest((receipt(1, "east", target, WitnessClaimKind.PROVIDER_TRUE, issued_at=90_000),), observed_at=90_010, now=90_010)
    strict_summary = cache.summarize(target_commitment=target, now=90_020, policy=WitnessCachePolicy(min_total_weight=100, min_families=3, max_per_family=1, max_age_seconds=100_000))

    plan = plan_witness_repair(strict_summary, available_family_hints=("west", "north", "east"), policy=WitnessRepairPolicy(desired_families=3, max_actions=3))

    assert plan.decision.kind is WitnessRepairDecisionKind.REPAIR_NEEDED
    assert plan.needs_network
    assert [action.family_hint for action in plan.actions if action.kind is WitnessRepairActionKind.ASK_NEW_FAMILY] == ["west", "north"]


def test_witness_repair_quarantines_contradiction_instead_of_fetching_more() -> None:
    target = sha256(b"contradict repair")
    cache = WitnessEvidenceCache()
    subject = ident(999, "subject").node_id
    cache.ingest((
        WitnessReceipt.create(keypair=kp(77), witness_node_id=ident(77, "witness").node_id, witness_family="same", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_TRUE, evidence_digest=sha256(b"true"), issued_at=100_000, ttl=100_000),
        WitnessReceipt.create(keypair=kp(77), witness_node_id=ident(77, "witness").node_id, witness_family="same", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_FALSE, evidence_digest=sha256(b"false"), issued_at=100_001, ttl=100_000),
    ), observed_at=100_010, now=100_010)
    summary = cache.summarize(target_commitment=target, now=100_020, policy=WitnessCachePolicy(min_total_weight=100, min_families=1, max_per_family=2, max_age_seconds=100_000))
    assert summary.decision.kind is WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION

    plan = plan_witness_repair(summary)
    assert plan.decision.kind is WitnessRepairDecisionKind.QUARANTINE
    assert not plan.needs_network
    assert plan.actions[0].kind is WitnessRepairActionKind.QUARANTINE_CONTRADICTION


def test_provider_surface_migration_now_distinguishes_historical_legacy_imports() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = plan_provider_surface_migration(str(root))

    assert plan.legacy_import_count >= 1
    assert plan.historical_legacy_import_count >= 1
    assert any(item.historical and item.path.endswith("test_rev0011_providerpoison_gardenrefusal.py") for item in plan.legacy_imports)
    assert plan.recommendation in {"historical_imports_only_preserve_until_compat_surface", "migrate_active_legacy_callers_before_wrapper"}
