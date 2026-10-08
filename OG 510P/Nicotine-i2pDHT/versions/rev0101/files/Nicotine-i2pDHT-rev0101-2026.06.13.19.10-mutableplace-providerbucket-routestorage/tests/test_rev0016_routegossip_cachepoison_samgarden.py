from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.cachepoison import CachePoisonDecisionKind, CachePoisonPolicy, CacheRound, analyze_cache_poison_rounds
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.lookuptranscript import LookupEvent, LookupEventKind, LookupKind, LookupPressurePolicy, LookupTranscript
from i2p_dht_lab.probewitness import WitnessClaimKind, WitnessReceipt
from i2p_dht_lab.provider_refactor import plan_provider_surface_migration
from i2p_dht_lab.routegossip import (
    RouteContact,
    RouteGossipBatch,
    RouteGossipBook,
    RouteGossipDecisionKind,
    RouteGossipPolicy,
)
from i2p_dht_lab.samgarden import SamGardenDecisionKind, SamGardenProfile, analyze_sam_garden_cases, make_sam_garden_cases
from i2p_dht_lab.samshadow import SamShadowDecisionKind, SamShadowFrame, SamShadowProfile, SamShadowTranscript
from i2p_dht_lab.witnesscache import WitnessCacheDecisionKind, WitnessCachePolicy, WitnessEvidenceCache


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "node") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def contact(n: int, family: str, introduced_by: str, *, at: int = 1_000, successes: int = 1, failures: int = 0) -> RouteContact:
    return RouteContact(
        node_id=ident(n, "route").node_id,
        destination_hint=f"route-{n}.b32.i2p",
        family_id=family,
        introduced_by=introduced_by,
        first_seen_at=at,
        last_seen_at=at,
        success_count=successes,
        failure_count=failures,
    )


def batch(issuer_n: int, issuer_family: str, target: bytes, contacts: tuple[RouteContact, ...], *, issued_at: int = 2_000) -> RouteGossipBatch:
    return RouteGossipBatch(issuer_node_id=ident(issuer_n, "issuer").node_id, issuer_family=issuer_family, target=target, issued_at=issued_at, contacts=contacts)


def test_route_gossip_evicts_stale_contacts_then_accepts_diverse_repair() -> None:
    target = sha256(b"route-target")
    book = RouteGossipBook()
    book.remember(contact(1, "old", "old-seed", at=0))
    contacts = tuple(contact(10 + idx, family, intro, at=399_000) for idx, (family, intro) in enumerate((
        ("east", "seed-east"),
        ("west", "seed-west"),
        ("north", "seed-north"),
        ("south", "seed-south"),
    )))
    report = book.ingest_gossip((batch(90, "garden-east", target, contacts),), now=400_000, policy=RouteGossipPolicy(min_repair_contacts=4, min_repair_families=4, max_per_family=1))

    assert report.decision.kind is RouteGossipDecisionKind.EVICT_STALE_THEN_REPAIR
    assert report.decision.accept
    assert len(report.stale_evictions) == 1
    assert report.selected_family_count == 4
    assert len(book.contacts) == 4
    fresh_book = RouteGossipBook()
    fresh_book.remember(contact(1, "old", "old-seed", at=0))
    repeat = fresh_book.ingest_gossip((batch(90, "garden-east", target, contacts),), now=400_000, policy=RouteGossipPolicy(min_repair_contacts=4, min_repair_families=4, max_per_family=1))
    assert report.transcript_digest == repeat.transcript_digest


def test_route_gossip_quarantines_one_introducer_capture_even_with_many_families() -> None:
    target = sha256(b"route-capture")
    contacts = tuple(contact(30 + idx, family, "captured-garden", at=5_000) for idx, family in enumerate(("east", "west", "north", "south")))
    report = RouteGossipBook().ingest_gossip((batch(91, "captured-garden", target, contacts),), now=5_100, policy=RouteGossipPolicy(min_repair_contacts=4, min_repair_families=4, max_per_family=1, max_issuer_fraction=0.50))

    assert report.decision.kind is RouteGossipDecisionKind.QUARANTINE_CAPTURED_GOSSIP
    assert not report.decision.accept
    assert report.issuer_family_fraction == 1.0
    assert len(report.quarantined_contacts) == 4


def test_route_gossip_low_diversity_keeps_pressure_open() -> None:
    target = sha256(b"route-low-diversity")
    contacts = tuple(contact(50 + idx, "same-family", f"intro-{idx}", at=5_000) for idx in range(4))
    report = RouteGossipBook().ingest_gossip((batch(92, "same-family", target, contacts),), now=5_100, policy=RouteGossipPolicy(min_repair_contacts=3, min_repair_families=2, max_per_family=2))

    assert report.decision.kind is RouteGossipDecisionKind.CONTINUE_LOW_DIVERSITY
    assert report.needs_more_gossip
    assert report.selected_family_count == 1


def witness_receipt(n: int, family: str, target: bytes, claim: WitnessClaimKind = WitnessClaimKind.PROVIDER_TRUE, *, issued_at: int = 10_000) -> WitnessReceipt:
    return WitnessReceipt.create(
        keypair=kp(n),
        witness_node_id=ident(n, "witness").node_id,
        witness_family=family,
        subject_node_id=ident(100 + n, "subject").node_id,
        target_commitment=target,
        claim=claim,
        evidence_digest=sha256(b"evidence" + bytes([n % 256]) + claim.value.encode()),
        issued_at=issued_at,
        ttl=100_000,
    )


def witness_summary(target: bytes, families: tuple[str, ...], *, now: int = 10_100, contradiction: bool = False):
    cache = WitnessEvidenceCache()
    receipts = [witness_receipt(idx + 1, family, target) for idx, family in enumerate(families)]
    if contradiction:
        subject = ident(999, "subject").node_id
        receipts.extend((
            WitnessReceipt.create(keypair=kp(77), witness_node_id=ident(77, "witness").node_id, witness_family="contradict", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_TRUE, evidence_digest=sha256(b"true"), issued_at=10_000, ttl=100_000),
            WitnessReceipt.create(keypair=kp(77), witness_node_id=ident(77, "witness").node_id, witness_family="contradict", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_FALSE, evidence_digest=sha256(b"false"), issued_at=10_001, ttl=100_000),
        ))
    cache.ingest(receipts, observed_at=now, now=now)
    return cache.summarize(target_commitment=target, now=now + 10, policy=WitnessCachePolicy(min_total_weight=250, min_families=3, max_per_family=1, max_age_seconds=100_000))


def lookup_event(seq: int, family: str, path: str, kind: LookupEventKind, completed: int) -> LookupEvent:
    return LookupEvent(sequence=seq, path_id=path, family_id=family, node_id=ident(20 + seq, "lookup").node_id, kind=kind, sent_at_ms=0, completed_at_ms=completed, payload_digest=sha256(b"payload" + bytes([seq % 256])))


def lookup(round_n: int, *, captured_fast: bool = False) -> LookupTranscript:
    if captured_fast:
        events = (
            lookup_event(1, "captured", "p1", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 90),
            lookup_event(2, "captured", "p2", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 95),
            lookup_event(3, "captured", "p3", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 100),
            lookup_event(4, "east", "p4", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 600 + round_n),
            lookup_event(5, "west", "p5", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 700 + round_n),
        )
    else:
        events = (
            lookup_event(1, "east", "p1", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 100 + round_n),
            lookup_event(2, "west", "p2", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 190 + round_n),
            lookup_event(3, "north", "p3", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 430 + round_n),
        )
    return LookupTranscript(lookup_id=sha256(b"lookup-round" + bytes([round_n])), kind=LookupKind.FIND_PROVIDER, target=sha256(b"provider-key"), events=events)


def test_cache_poison_accepts_stable_diverse_cache_across_distinct_rounds() -> None:
    target = sha256(b"cache-target")
    rounds = tuple(CacheRound(f"r{idx}", 20_000 + idx, lookup(idx), witness_summary(target, ("east", "west", "north"))) for idx in range(3))
    report = analyze_cache_poison_rounds(rounds, policy=CachePoisonPolicy(min_rounds=3, min_distinct_transcripts=2, min_witness_families=3, lookup_policy=LookupPressurePolicy(min_success_families=3, min_success_paths=3, fast_window_ms=25)))

    assert report.decision.kind is CachePoisonDecisionKind.ACCEPT_STABLE_DIVERSE_CACHE
    assert report.decision.accept
    assert report.accepted_witness_families == frozenset({"east", "west", "north"})


def test_cache_poison_quarantines_replayed_transcript_monoculture() -> None:
    target = sha256(b"cache-replay")
    repeated_lookup = lookup(1)
    rounds = tuple(CacheRound(f"r{idx}", 20_000 + idx, repeated_lookup, witness_summary(target, ("east", "west", "north"))) for idx in range(3))
    report = analyze_cache_poison_rounds(rounds, policy=CachePoisonPolicy(min_rounds=3, min_distinct_transcripts=2, max_replay_fraction=0.67))

    assert report.decision.kind is CachePoisonDecisionKind.QUARANTINE_REPLAY_MONOCULTURE
    assert report.replay_fraction == 1.0
    assert report.distinct_transcript_count == 1


def test_cache_poison_quarantines_repeated_fast_capture_even_with_cache_evidence() -> None:
    target = sha256(b"cache-fast-capture")
    rounds = tuple(CacheRound(f"r{idx}", 20_000 + idx, lookup(idx, captured_fast=True), witness_summary(target, ("east", "west", "north"))) for idx in range(3))
    report = analyze_cache_poison_rounds(rounds, policy=CachePoisonPolicy(min_rounds=3, min_distinct_transcripts=2, min_witness_families=3, max_fast_capture_round_fraction=0.50, lookup_policy=LookupPressurePolicy(min_success_families=3, min_success_paths=3, fast_window_ms=25)))

    assert report.decision.kind is CachePoisonDecisionKind.QUARANTINE_FAST_CAPTURE_REINFORCED
    assert report.fast_capture_rounds == 3


def test_cache_poison_quarantines_cached_witness_contradiction() -> None:
    target = sha256(b"cache-contradiction")
    summary = witness_summary(target, ("east", "west", "north"), contradiction=True)
    assert summary.decision.kind is WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION
    rounds = tuple(CacheRound(f"r{idx}", 20_000 + idx, lookup(idx), summary) for idx in range(3))
    report = analyze_cache_poison_rounds(rounds)

    assert report.decision.kind is CachePoisonDecisionKind.QUARANTINE_CONTRADICTION


def test_sam_garden_shadow_validates_streaming_first_family_with_negative_datagram_probe() -> None:
    profile = SamGardenProfile.default()
    cases = make_sam_garden_cases(profile, remote_destination="peer-destination.b32.i2p")
    report = analyze_sam_garden_cases(cases, profile=profile)

    assert report.decision is SamGardenDecisionKind.VALID_GARDEN_STREAMING_FAMILY
    assert report.ok
    assert {case.kind.value for case in report.cases} >= {"outbound_connect", "inbound_accept", "reconnect_after_close", "naming_failure", "datagram_assumption_probe"}
    assert any(validation.kind is SamShadowDecisionKind.INVALID_FEATURE_ASSUMPTION for validation in report.validations)


def test_sam_garden_rejects_ephemeral_destination_profile() -> None:
    shadow = SamShadowProfile(session_id="i2pdht-garden", destination_name="TRANSIENT", persistent_destination=False)
    profile = SamGardenProfile(shadow_profile=shadow)
    cases = make_sam_garden_cases(profile, remote_destination="peer-destination.b32.i2p")
    report = analyze_sam_garden_cases(cases, profile=profile)

    assert report.decision is SamGardenDecisionKind.INVALID_NO_PERSISTENT_DESTINATION
    assert not report.ok


def test_sam_shadow_accepts_stream_accept_after_session_and_rejects_before_session() -> None:
    profile = SamShadowProfile(session_id="i2pdht", destination_name="/profile/dht.keys")
    inbound = SamShadowTranscript((*profile.initial_frames(), profile.accept_frame()))
    assert inbound.validate(profile=profile).kind is SamShadowDecisionKind.VALID_STREAMING_FIRST

    accept_first = SamShadowTranscript((SamShadowFrame.command("HELLO VERSION", MIN="3.1", MAX="3.3"), profile.accept_frame()))
    assert accept_first.validate(profile=profile).kind is SamShadowDecisionKind.INVALID_MISSING_SESSION


def test_provider_surface_migration_plan_keeps_legacy_visible_until_callers_move() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = plan_provider_surface_migration(str(root))

    assert plan.audit.canonical_module.endswith("provider_poison")
    assert plan.legacy_import_count >= 1
    assert plan.recommendation in {"migrate_legacy_callers_before_wrapper", "historical_imports_only_preserve_until_compat_surface", "migrate_active_legacy_callers_before_wrapper"}
    assert any(import_ref.path.endswith("test_rev0011_providerpoison_gardenrefusal.py") for import_ref in plan.legacy_imports)
