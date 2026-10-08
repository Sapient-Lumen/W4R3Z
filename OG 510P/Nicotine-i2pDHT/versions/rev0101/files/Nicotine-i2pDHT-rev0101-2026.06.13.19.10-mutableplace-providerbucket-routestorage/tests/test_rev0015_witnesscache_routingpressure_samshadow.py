from __future__ import annotations

from i2p_dht_lab.gardenrefusal import GardenAdmissionPolicy, GardenWorkKind, GardenWorkRequest
from i2p_dht_lab.gardenscheduler import GardenScheduleDecisionKind, GardenSchedulePolicy, plan_garden_schedule
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.lookuptranscript import (
    LookupEvent,
    LookupEventKind,
    LookupKind,
    LookupPressureDecisionKind,
    LookupPressurePolicy,
    LookupTranscript,
    analyze_lookup_pressure,
    compact_transcript_label,
)
from i2p_dht_lab.probewitness import WitnessClaimKind, WitnessReceipt
from i2p_dht_lab.samshadow import SamShadowDecisionKind, SamShadowFrame, SamShadowProfile, SamShadowTranscript, make_streaming_first_shadow
from i2p_dht_lab.witnesscache import WitnessCacheDecisionKind, WitnessCachePolicy, WitnessEvidenceCache


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "node") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def witness_receipt(n: int, family: str, target: bytes, claim: WitnessClaimKind = WitnessClaimKind.PROVIDER_TRUE, *, issued_at: int = 100, ttl: int = 100_000) -> WitnessReceipt:
    return WitnessReceipt.create(
        keypair=kp(n),
        witness_node_id=ident(n, "witness").node_id,
        witness_family=family,
        subject_node_id=ident(200 + n, "subject").node_id,
        target_commitment=target,
        claim=claim,
        evidence_digest=sha256(b"evidence" + bytes([n])),
        issued_at=issued_at,
        ttl=ttl,
    )


def test_witness_cache_preserves_diverse_fresh_evidence_and_deduplicates() -> None:
    target = sha256(b"target")
    cache = WitnessEvidenceCache()
    r1 = witness_receipt(1, "east", target)
    r2 = witness_receipt(2, "west", target)
    assert cache.ingest((r1, r2, r1), observed_at=110, now=110) == 3
    assert len(cache.receipts) == 2
    assert cache.receipts[r1.receipt_hash].seen_count == 2
    summary = cache.summarize(target_commitment=target, now=120, policy=WitnessCachePolicy(min_total_weight=150, min_families=2, max_per_family=1))
    assert summary.decision.kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE
    assert summary.total_weight >= 200
    assert summary.family_count == 2
    assert summary.transcript_digest == cache.summarize(target_commitment=target, now=120, policy=WitnessCachePolicy(min_total_weight=150, min_families=2, max_per_family=1)).transcript_digest


def test_witness_cache_caps_family_monoculture_and_decays_old_evidence() -> None:
    target = sha256(b"mono")
    cache = WitnessEvidenceCache()
    receipts = [witness_receipt(idx, "same-family", target, issued_at=0, ttl=200_000) for idx in range(1, 5)]
    cache.ingest(receipts, observed_at=0, now=1)
    summary = cache.summarize(target_commitment=target, now=10, policy=WitnessCachePolicy(min_total_weight=100, min_families=2, max_per_family=1))
    assert summary.decision.kind is WitnessCacheDecisionKind.CONTINUE_INSUFFICIENT_DIVERSITY
    assert summary.counted_count == 1

    decayed = cache.summarize(target_commitment=target, now=80_000, policy=WitnessCachePolicy(max_age_seconds=100_000, full_weight_seconds=0, min_total_weight=150, min_families=1, max_per_family=3))
    assert decayed.decision.kind is WitnessCacheDecisionKind.CONTINUE_INSUFFICIENT_WEIGHT
    assert 0 < decayed.total_weight < 150


def test_witness_cache_quarantines_self_contradicting_witness() -> None:
    target = sha256(b"contradiction")
    cache = WitnessEvidenceCache()
    subject = ident(333, "subject").node_id
    a = WitnessReceipt.create(keypair=kp(9), witness_node_id=ident(9, "witness").node_id, witness_family="north", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_TRUE, evidence_digest=sha256(b"true"), issued_at=100)
    b = WitnessReceipt.create(keypair=kp(9), witness_node_id=ident(9, "witness").node_id, witness_family="north", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_FALSE, evidence_digest=sha256(b"false"), issued_at=101)
    cache.ingest((a, b), observed_at=102, now=102)
    summary = cache.summarize(target_commitment=target, now=103)
    assert summary.decision.kind is WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION
    assert summary.contradictions


def event(seq: int, family: str, path: str, kind: LookupEventKind, completed: int, *, node: int | None = None) -> LookupEvent:
    node = seq if node is None else node
    return LookupEvent(
        sequence=seq,
        path_id=path,
        family_id=family,
        node_id=ident(node, "lookup").node_id,
        kind=kind,
        sent_at_ms=0,
        completed_at_ms=completed,
        payload_digest=sha256(b"payload" + bytes([seq])),
    )


def test_lookup_transcript_accepts_diverse_find_node_success() -> None:
    transcript = LookupTranscript(
        lookup_id=sha256(b"lookup-1"),
        kind=LookupKind.FIND_NODE,
        target=sha256(b"target-1"),
        events=(
            event(1, "east", "p1", LookupEventKind.RESPONSE_NODES, 100),
            event(2, "west", "p2", LookupEventKind.RESPONSE_NODES, 140),
            event(3, "north", "p3", LookupEventKind.RESPONSE_NODES, 500),
        ),
    )
    report = analyze_lookup_pressure(transcript, policy=LookupPressurePolicy(min_success_families=3, min_success_paths=3, fast_window_ms=25))
    assert report.decision.kind is LookupPressureDecisionKind.ACCEPT_DIVERSE_SUCCESS
    assert report.transcript_digest == transcript.digest
    assert compact_transcript_label(transcript).startswith("find_node:")


def test_lookup_transcript_quarantines_captured_fast_window_before_speed_greed() -> None:
    transcript = LookupTranscript(
        lookup_id=sha256(b"lookup-capture"),
        kind=LookupKind.FIND_PROVIDER,
        target=sha256(b"target-provider"),
        events=(
            event(1, "captured", "p1", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 90),
            event(2, "captured", "p2", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 95),
            event(3, "captured", "p3", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 100),
            event(4, "honest-east", "p4", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 600),
            event(5, "honest-west", "p5", LookupEventKind.RESPONSE_PROVIDER_CLAIM, 640),
        ),
    )
    report = analyze_lookup_pressure(transcript, policy=LookupPressurePolicy(min_success_families=3, min_success_paths=3, max_fast_family_fraction=0.6, fast_window_ms=25))
    assert report.decision.kind is LookupPressureDecisionKind.QUARANTINE_FAST_WINDOW_CAPTURE
    assert report.fast_window_family_fraction == 1.0


def test_lookup_transcript_keeps_provider_proof_as_evidence_only() -> None:
    transcript = LookupTranscript(
        lookup_id=sha256(b"lookup-proof"),
        kind=LookupKind.PROVIDER_PROOF,
        target=sha256(b"target-proof"),
        events=(
            event(1, "east", "p1", LookupEventKind.PROOF_ATTEMPT, 200),
            event(2, "west", "p2", LookupEventKind.PROOF_ATTEMPT, 260),
            event(3, "north", "p3", LookupEventKind.PROOF_ATTEMPT, 520),
        ),
    )
    report = analyze_lookup_pressure(transcript, policy=LookupPressurePolicy(min_success_families=3, min_success_paths=3, fast_window_ms=25))
    assert report.decision.kind is LookupPressureDecisionKind.EVIDENCE_ONLY
    assert not report.decision.accept


def test_sam_shadow_builds_and_validates_streaming_first_profile() -> None:
    profile = SamShadowProfile(session_id="i2pdht", destination_name="/profile/dht.keys")
    transcript = make_streaming_first_shadow(profile, "peer-destination.b32.i2p")
    validation = transcript.validate(profile=profile)
    assert validation.kind is SamShadowDecisionKind.VALID_STREAMING_FIRST
    assert validation.ok
    assert validation.transcript_digest == transcript.digest

    parsed = SamShadowTranscript.from_lines(frame.raw for frame in transcript.frames)
    assert parsed.digest == transcript.digest


def test_sam_shadow_rejects_stream_before_session_and_ephemeral_destination() -> None:
    profile = SamShadowProfile(session_id="i2pdht", destination_name="/profile/dht.keys")
    stream_first = SamShadowTranscript((SamShadowFrame.command("HELLO VERSION", MIN="3.1", MAX="3.3"), profile.connect_frame("peer.b32.i2p")))
    assert stream_first.validate(profile=profile).kind is SamShadowDecisionKind.INVALID_MISSING_SESSION

    transient = SamShadowTranscript((
        SamShadowFrame.command("HELLO VERSION", MIN="3.1", MAX="3.3"),
        SamShadowFrame.command("DEST GENERATE", SIGNATURE_TYPE=7),
        SamShadowFrame.command("SESSION CREATE", STYLE="STREAM", ID="i2pdht", DESTINATION="TRANSIENT"),
    ))
    assert transient.validate(profile=profile).kind is SamShadowDecisionKind.INVALID_EPHEMERAL_DESTINATION


def test_sam_shadow_rejects_primary_datagram_feature_assumption_for_bundle_path() -> None:
    profile = SamShadowProfile(session_id="i2pdht", destination_name="/profile/dht.keys", require_primary_subsessions=True, router_flavor="i2pd")
    transcript = SamShadowTranscript((*profile.initial_frames(), SamShadowFrame.command("DATAGRAM SEND", ID="i2pdht", DESTINATION="peer", SIZE=10)))
    assert transcript.validate(profile=profile).kind is SamShadowDecisionKind.INVALID_FEATURE_ASSUMPTION


def req(n: int, family: str, kind: GardenWorkKind, *, provider_cost: int = 0, watch_cost: int = 0, issued_at: int = 100, ttl: int = 10_000, bonus: int = 0) -> GardenWorkRequest:
    return GardenWorkRequest(
        requester_node_id=ident(n, "requester").node_id,
        family_id=family,
        kind=kind,
        target=sha256(b"target" + bytes([n % 256])),
        issued_at=issued_at,
        ttl=ttl,
        stream_cost=1,
        provider_record_cost=provider_cost,
        mutable_watch_cost=watch_cost,
        priority_bonus=bonus,
    )


def test_garden_scheduler_protects_head_and_witness_work_from_bulk_flood() -> None:
    requests = tuple(req(n, "bulk", GardenWorkKind.BULK_PROVIDER, provider_cost=900) for n in range(1, 9)) + (
        req(50, "east", GardenWorkKind.HEAD_WATCH, watch_cost=1),
        req(51, "west", GardenWorkKind.WITNESS_QUERY),
        req(52, "north", GardenWorkKind.SEED_GATE),
    )
    report = plan_garden_schedule(
        requests,
        garden_keypair=kp(88),
        garden_node_id=ident(88, "garden").node_id,
        start_at=100,
        schedule_policy=GardenSchedulePolicy(windows=3, window_seconds=600, refill_streams_per_window=4, refill_provider_records_per_window=600, refill_mutable_watches_per_window=10),
        admission_policy=GardenAdmissionPolicy(max_streams=4, max_provider_records=1200, max_mutable_watches=10, max_accepts_per_family=2, max_refusals_per_window=20, retry_base_seconds=120),
    )
    assert report.protected_accepted_count == 3
    assert report.refused_count > 0
    assert report.decision.kind in {GardenScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, GardenScheduleDecisionKind.STARVATION_PRESSURE}
    assert len(report.transcript_digest) == 32


def test_garden_scheduler_flags_starvation_of_protected_work() -> None:
    requests = (
        req(60, "east", GardenWorkKind.HEAD_WATCH, watch_cost=10, issued_at=100, ttl=2_000),
        req(61, "west", GardenWorkKind.WITNESS_QUERY, issued_at=100, ttl=2_000),
    )
    report = plan_garden_schedule(
        requests,
        garden_keypair=kp(89),
        garden_node_id=ident(89, "garden").node_id,
        start_at=100,
        schedule_policy=GardenSchedulePolicy(windows=1, window_seconds=600, refill_streams_per_window=0, refill_provider_records_per_window=0, refill_mutable_watches_per_window=0),
        admission_policy=GardenAdmissionPolicy(max_streams=0, max_provider_records=0, max_mutable_watches=0, max_accepts_per_family=1, max_refusals_per_window=5),
    )
    assert report.accepted_count == 0
    assert report.decision.kind is GardenScheduleDecisionKind.STARVATION_PRESSURE
    assert all(decision.receipt is not None for window in report.windows for decision in window.batch.refused)

from i2p_dht_lab.provider_refactor import audit_provider_surfaces


def test_provider_refactor_audit_keeps_legacy_explicit_until_migration() -> None:
    audit = audit_provider_surfaces()
    assert audit.canonical_module.endswith("provider_poison")
    assert audit.legacy_module.endswith("providerpoison")
    assert "ProviderProbeReceipt" in audit.shared_public_names
    assert audit.has_overlap
    assert audit.should_keep_legacy_for_now
