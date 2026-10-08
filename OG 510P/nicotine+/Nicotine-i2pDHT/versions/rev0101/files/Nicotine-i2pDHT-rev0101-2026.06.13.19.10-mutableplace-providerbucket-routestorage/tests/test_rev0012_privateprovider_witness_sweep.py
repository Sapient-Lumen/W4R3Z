from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.chaossweep import SweepDecisionKind, SweepScenario, evaluate_sweep_scenario, run_capture_sweep
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.privateprovider import (
    PrivateProbeBudget,
    PrivateProbeDecisionKind,
    ProbePurpose,
    ProbeVisibility,
    ProviderCandidate,
    assess_private_probe_plan,
    decoy_key,
    plan_private_provider_probes,
    provider_probe_commitment,
)
from i2p_dht_lab.probewitness import (
    WitnessClaimKind,
    WitnessMeshDecisionKind,
    WitnessMeshPolicy,
    WitnessReceipt,
    analyze_witness_mesh,
)
from i2p_dht_lab.wiretranscript import WireFrame, WireFrameKind, make_transcript


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int, prefix: str = "node") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def candidate(n: int, family: str, *, rank: int | None = None, commitment: bool = True) -> ProviderCandidate:
    return ProviderCandidate(
        provider_node_id=ident(n, "provider").node_id,
        family_id=family,
        distance_rank=n if rank is None else rank,
        latency_ms=10 + n,
        reliability_score=100 - n,
        supports_commitment_probe=commitment,
    )


def test_private_provider_plan_bounds_exposure_and_adds_decoys() -> None:
    content_key = sha256(b"real-content-key")
    nonce = b"rev0012-private-probe"
    candidates = (
        candidate(1, "fast-captured", rank=0, commitment=False),
        candidate(2, "fast-captured", rank=1, commitment=False),
        candidate(3, "honest-east", rank=2),
        candidate(4, "honest-west", rank=3),
        candidate(5, "decoy-north", rank=4),
    )
    budget = PrivateProbeBudget(max_real_probes=3, max_decoy_probes=2, min_families=3, max_per_family=1, max_content_key_exposures=1, require_decoy=True)
    plan = plan_private_provider_probes(candidates, namespace="files", content_key=content_key, nonce=nonce, issued_at=100, budget=budget)
    assessment = assess_private_probe_plan(plan, budget=budget)

    assert len(plan.real_probes) == 3
    assert len(plan.decoy_probes) == 2
    assert plan.content_key_exposure_count == 1
    assert plan.real_families == frozenset({"fast-captured", "honest-east", "honest-west"})
    assert assessment.kind is PrivateProbeDecisionKind.ACCEPT_PRESSURED_PLAN
    assert all(probe.purpose is ProbePurpose.DECOY and probe.visibility is ProbeVisibility.COMMITMENT_ONLY for probe in plan.decoy_probes)
    assert "content_key" not in plan.decoy_probes[0].wire_hint


def test_private_probe_rejects_family_monoculture_even_with_many_candidates() -> None:
    content_key = sha256(b"monoculture-key")
    candidates = tuple(candidate(n, "one-family", rank=n) for n in range(1, 7))
    budget = PrivateProbeBudget(max_real_probes=4, max_decoy_probes=2, min_families=2, max_per_family=4, require_decoy=True)
    plan = plan_private_provider_probes(candidates, namespace="files", content_key=content_key, nonce=b"mono", issued_at=100, budget=budget)
    assessment = assess_private_probe_plan(plan, budget=budget)
    assert assessment.kind is PrivateProbeDecisionKind.CONTINUE_INSUFFICIENT_FAMILIES
    assert not assessment.accept


def test_private_probe_commitments_and_decoys_are_deterministic_and_distinct() -> None:
    content_key = sha256(b"commitment-key")
    provider = ident(9, "provider").node_id
    nonce = b"nonce"
    real_commitment = provider_probe_commitment(namespace="x", content_key=content_key, nonce=nonce, provider_node_id=provider, purpose=ProbePurpose.REAL)
    decoy_content_key = decoy_key(namespace="x", content_key=content_key, nonce=nonce, counter=0)
    decoy_commitment = provider_probe_commitment(namespace="x", content_key=decoy_content_key, nonce=nonce, provider_node_id=provider, purpose=ProbePurpose.DECOY)
    assert real_commitment == provider_probe_commitment(namespace="x", content_key=content_key, nonce=nonce, provider_node_id=provider, purpose=ProbePurpose.REAL)
    assert real_commitment != decoy_commitment
    assert decoy_content_key != content_key


def receipt(n: int, family: str, subject: bytes, target: bytes, claim: WitnessClaimKind, *, now: int = 100, ttl: int = 3600) -> WitnessReceipt:
    return WitnessReceipt.create(
        keypair=kp(n),
        witness_node_id=ident(n, "witness").node_id,
        witness_family=family,
        subject_node_id=subject,
        target_commitment=target,
        claim=claim,
        evidence_digest=sha256(b"evidence" + bytes([n]) + claim.value.encode()),
        issued_at=now,
        ttl=ttl,
    )


def test_witness_mesh_does_not_count_one_family_as_quorum() -> None:
    subject = ident(50, "provider").node_id
    target = sha256(b"target")
    receipts = tuple(receipt(n, "one-garden-family", subject, target, WitnessClaimKind.PROVIDER_FALSE) for n in (1, 2, 3, 4))
    report = analyze_witness_mesh(receipts, now=120, policy=WitnessMeshPolicy(min_witnesses=3, min_families=2, max_per_family=2))
    assert report.decision.kind is WitnessMeshDecisionKind.CONTINUE_INSUFFICIENT_DIVERSITY
    assert report.family_counts == {"one-garden-family": 2}


def test_witness_mesh_escalates_diverse_evidence_but_not_truth() -> None:
    subject = ident(51, "provider").node_id
    target = sha256(b"target-diverse")
    receipts = (
        receipt(1, "east", subject, target, WitnessClaimKind.PROVIDER_FALSE),
        receipt(2, "west", subject, target, WitnessClaimKind.PROVIDER_FALSE),
        receipt(3, "north", subject, target, WitnessClaimKind.PROVIDER_FALSE),
    )
    report = analyze_witness_mesh(receipts, now=120, policy=WitnessMeshPolicy(min_witnesses=3, min_families=3, max_per_family=2))
    assert report.decision.kind is WitnessMeshDecisionKind.ESCALATE_DIVERSE_EVIDENCE
    assert report.decision.accept_as_evidence
    assert "not declare truth" in report.decision.reason


def test_witness_mesh_quarantines_self_contradiction() -> None:
    subject = ident(52, "provider").node_id
    target = sha256(b"target-contradiction")
    good = receipt(1, "east", subject, target, WitnessClaimKind.PROVIDER_TRUE)
    bad_same_witness = WitnessReceipt.create(
        keypair=kp(1),
        witness_node_id=good.witness_node_id,
        witness_family="east",
        subject_node_id=subject,
        target_commitment=target,
        claim=WitnessClaimKind.PROVIDER_FALSE,
        evidence_digest=sha256(b"contradiction"),
        issued_at=101,
    )
    report = analyze_witness_mesh((good, bad_same_witness, receipt(2, "west", subject, target, WitnessClaimKind.PROVIDER_FALSE), receipt(3, "north", subject, target, WitnessClaimKind.PROVIDER_FALSE)), now=120)
    assert report.decision.kind is WitnessMeshDecisionKind.QUARANTINE_CONTRADICTIONS
    assert report.contradictions


def test_witness_mesh_ignores_expired_and_tampered_receipts() -> None:
    subject = ident(53, "provider").node_id
    target = sha256(b"target-invalid")
    expired = receipt(1, "east", subject, target, WitnessClaimKind.PATH_EMPTY, now=10, ttl=1)
    valid = receipt(2, "west", subject, target, WitnessClaimKind.PATH_EMPTY, now=100)
    tampered = replace(valid, evidence_digest=sha256(b"tampered"))
    report = analyze_witness_mesh((expired, tampered), now=120)
    assert report.decision.kind is WitnessMeshDecisionKind.IGNORE_INVALID_ONLY
    assert report.invalid_count == 2


def test_chaos_sweep_flags_fast_window_capture_and_family_caps_mitigate() -> None:
    captured = evaluate_sweep_scenario(SweepScenario(captured_families=1, honest_families=3, paths=5, max_per_family=3, fast_window_size=3), min_families=3)
    capped = evaluate_sweep_scenario(SweepScenario(captured_families=1, honest_families=3, paths=5, max_per_family=1, fast_window_size=3), min_families=3)
    assert captured.decision is SweepDecisionKind.CONTINUE_FAST_WINDOW_CAPTURED
    assert capped.captured_fast_fraction < captured.captured_fast_fraction


def test_capture_sweep_has_worst_point_and_not_every_point_is_captured() -> None:
    report = run_capture_sweep(captured_family_options=(0, 1, 3), honest_family_options=(1, 4), path_options=(3, 5), family_cap_options=(1, 2), fast_window_size=3)
    assert report.worst_point.captured_fast_fraction >= 0
    assert report.captured_points
    assert any(point.decision is SweepDecisionKind.ACCEPT_PRESSURE for point in report.points)


def test_wire_transcript_signatures_digest_and_duplicate_sequence_detection() -> None:
    sender = ident(61, "sender")
    receiver = ident(62, "receiver")
    request_id = sha256(b"request")
    frame1 = WireFrame.create(
        keypair=kp(61),
        sender_node_id=sender.node_id,
        receiver_node_id=receiver.node_id,
        request_id=request_id,
        kind=WireFrameKind.FIND_PROVIDER,
        sequence=0,
        issued_at=100,
        payload={b"target": sha256(b"x"), b"alpha": 3},
    )
    frame2 = WireFrame.create(
        keypair=kp(61),
        sender_node_id=sender.node_id,
        receiver_node_id=receiver.node_id,
        request_id=request_id,
        kind=WireFrameKind.PROVIDER_PROBE,
        sequence=0,
        issued_at=101,
        payload={b"commitment": sha256(b"commitment")},
    )
    transcript = make_transcript((frame1, frame2))
    assert frame1.verify()
    assert transcript.verify_all()
    assert transcript.duplicate_sequences() == ((request_id, 0),)
    assert transcript.digest == make_transcript((frame1, frame2)).digest

    tampered = replace(frame1, payload={b"target": sha256(b"other"), b"alpha": 3})
    assert not tampered.verify()
