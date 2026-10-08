from __future__ import annotations

import json
from pathlib import Path

from i2p_dht_lab.cubeaudit import audit_cube, summarize_findings
from i2p_dht_lab.familydiversity import FamilyDiversityPolicy, analyze_family_diversity, select_family_capped
from i2p_dht_lab.gardensentinel import (
    SentinelDecisionKind,
    SentinelEventKind,
    SentinelObservation,
    SentinelPolicy,
    analyze_sentinel_observations,
    observations_from_proof_report,
    observations_from_witness_mesh,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.privateprovider import PrivateProbeBudget, ProviderCandidate, plan_private_provider_probes
from i2p_dht_lab.probewitness import WitnessClaimKind, WitnessMeshDecisionKind, WitnessReceipt, analyze_witness_mesh
from i2p_dht_lab.proofhandshake import (
    ProviderAvailabilityClaim,
    ProviderProofResponse,
    ProviderProofResponseKind,
    proof_material_digest,
)
from i2p_dht_lab.proofprobe import (
    ProofProbeDecisionKind,
    ProofProbePolicy,
    analyze_proof_probe_session,
    make_attempt,
    make_challenge_for_probe,
)
from i2p_dht_lab.sweepgrid import SweepGridDecisionKind, SweepGridScenario, evaluate_sweep_grid_point, run_sweep_grid
from i2p_dht_lab.supersession import load_supersession_map


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int, prefix: str = "node") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def candidate(n: int, family: str, rank: int, *, commitment: bool = True) -> ProviderCandidate:
    return ProviderCandidate(
        provider_node_id=ident(n, "provider").node_id,
        family_id=family,
        distance_rank=rank,
        latency_ms=20 + rank,
        reliability_score=10,
        supports_commitment_probe=commitment,
    )


def claim_for_probe(probe, provider_n: int, expected_digest: bytes, now: int = 100) -> ProviderAvailabilityClaim:
    return ProviderAvailabilityClaim.create(
        provider_keypair=kp(provider_n),
        provider_node_id=probe.provider_node_id,
        family_id=probe.family_id,
        namespace=probe.namespace,
        content_key_commitment=probe.commitment,
        expected_content_digest=expected_digest,
        issued_at=now,
    )


def proof_response(provider_n: int, challenge, expected_digest: bytes, *, kind=ProviderProofResponseKind.PROOF, served_digest: bytes | None = None, now: int = 103) -> ProviderProofResponse:
    digest = expected_digest if served_digest is None else served_digest
    material = proof_material_digest(challenge=challenge, served_digest=digest) if len(digest) == 32 else sha256(b"no-proof")
    return ProviderProofResponse.create(
        provider_keypair=kp(provider_n),
        provider_node_id=ident(provider_n, "provider").node_id,
        challenge_digest=challenge.digest,
        kind=kind,
        served_digest=digest if kind is ProviderProofResponseKind.PROOF else b"",
        proof_material_digest=material,
        issued_at=now,
        retry_after_seconds=60 if kind is ProviderProofResponseKind.USEFUL_REFUSAL else 0,
        note="bounded refusal" if kind is ProviderProofResponseKind.USEFUL_REFUSAL else "",
    )


def make_plan(*, raw: bool = False):
    content_key = sha256(b"rev0014-content-key")
    providers = (
        candidate(10, "east", 0, commitment=not raw),
        candidate(11, "west", 1, commitment=not raw),
        candidate(12, "north", 2, commitment=True),
        candidate(13, "decoy", 3, commitment=True),
    )
    budget = PrivateProbeBudget(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, max_content_key_exposures=2, require_decoy=True, prefer_commitment_witnessing=True)
    return plan_private_provider_probes(providers, namespace="blocks", content_key=content_key, nonce=b"rev0014-nonce", issued_at=100, budget=budget), content_key


def attempts_for_plan(plan, *, kinds: dict[int, ProviderProofResponseKind] | None = None, wrong: set[int] | None = None):
    kinds = kinds or {}
    wrong = wrong or set()
    expected_digest = sha256(b"served bytes rev0014")
    attempts = []
    challenger = ident(99, "challenger")
    for idx, probe in enumerate(plan.probes):
        provider_n = 10 + idx
        claim = claim_for_probe(probe, provider_n, expected_digest)
        challenge = make_challenge_for_probe(
            probe=probe,
            claim=claim,
            challenger_keypair=kp(99),
            challenger_node_id=challenger.node_id,
            challenge_nonce=b"challenge" + bytes([idx]),
            issued_at=101,
            deadline_ms=1000,
        )
        kind = kinds.get(idx, ProviderProofResponseKind.PROOF)
        served = sha256(b"wrong" + bytes([idx])) if idx in wrong else expected_digest
        response = proof_response(provider_n, challenge, expected_digest, kind=kind, served_digest=served)
        attempts.append(make_attempt(probe=probe, claim=claim, challenge=challenge, response=response, now=104, observed_latency_ms=250))
    return tuple(attempts)


def test_familydiversity_caps_same_family_without_claiming_independence() -> None:
    items = ["a1", "a2", "b1", "c1"]
    capped = select_family_capped(items, family_of=lambda value: value[0], limit=3, max_per_family=1)
    assert capped == ("a1", "b1", "c1")
    report = analyze_family_diversity(items, family_of=lambda value: value[0], policy=FamilyDiversityPolicy(min_families=3, max_per_family=1))
    assert report.passes(FamilyDiversityPolicy(min_families=3, max_per_family=1))
    assert report.uncapped_family_counts["a"] == 2


def test_proof_probe_accepts_diverse_true_commitment_proofs() -> None:
    plan, _content_key = make_plan()
    attempts = attempts_for_plan(plan)[:2]
    report = analyze_proof_probe_session(plan, attempts, policy=ProofProbePolicy(min_true_proofs=2, min_true_families=2, max_per_family=1))
    assert report.decision.kind is ProofProbeDecisionKind.ACCEPT_DIVERSE_TRUE_PROOFS
    assert report.true_families == frozenset({"east", "west"})
    assert report.metadata_exposures == 0
    assert len(report.transcript_digest) == 32


def test_proof_probe_quarantines_false_provider_pressure_before_acceptance() -> None:
    plan, _content_key = make_plan()
    attempts = attempts_for_plan(plan, wrong={1})[:2]
    report = analyze_proof_probe_session(plan, attempts, policy=ProofProbePolicy(min_true_proofs=1, min_true_families=1, max_false_proofs=0))
    assert report.decision.kind is ProofProbeDecisionKind.QUARANTINE_FALSE_PROVIDER_PRESSURE
    assert len(report.false_attempts) == 1


def test_proof_probe_quarantines_decoy_true_proof_and_metadata_pressure() -> None:
    plan, _content_key = make_plan()
    attempts = attempts_for_plan(plan)
    # The third probe is a decoy. A true provider proof to a decoy-shaped query is
    # not accepted as truth; it is treated as evidence that the probe surface is
    # being gamed or the decoy model is too weak.
    decoy_report = analyze_proof_probe_session(plan, attempts, policy=ProofProbePolicy(min_true_proofs=2, min_true_families=2))
    assert decoy_report.decision.kind is ProofProbeDecisionKind.QUARANTINE_DECOY_TRUE_PROOF

    raw_plan, _ = make_plan(raw=True)
    raw_attempts = attempts_for_plan(raw_plan)[:2]
    raw_report = analyze_proof_probe_session(raw_plan, raw_attempts, policy=ProofProbePolicy(max_raw_key_exposures=0))
    assert raw_report.decision.kind is ProofProbeDecisionKind.CONTINUE_METADATA_EXPOSURE_HIGH
    assert raw_report.metadata_exposures > 0


def test_proof_probe_treats_useful_refusals_as_liveness_not_availability() -> None:
    plan, _content_key = make_plan()
    attempts = attempts_for_plan(plan, kinds={0: ProviderProofResponseKind.USEFUL_REFUSAL, 1: ProviderProofResponseKind.USEFUL_REFUSAL})[:2]
    report = analyze_proof_probe_session(plan, attempts, policy=ProofProbePolicy(min_true_proofs=2, min_true_families=2))
    assert report.decision.kind is ProofProbeDecisionKind.CONTINUE_USEFUL_REFUSALS_ONLY
    assert len(report.useful_refusals) == 2


def test_garden_sentinel_prefers_diverse_truth_but_quarantines_semantic_lies() -> None:
    plan, _content_key = make_plan()
    good_report = analyze_proof_probe_session(plan, attempts_for_plan(plan)[:2], policy=ProofProbePolicy(min_true_proofs=2, min_true_families=2))
    good_scores = analyze_sentinel_observations(observations_from_proof_report(good_report, issued_at=200), policy=SentinelPolicy(min_events=1, min_positive_families=1, prefer_threshold=8))
    assert all(score.decision is SentinelDecisionKind.PREFER_AS_GARDEN for score in good_scores)

    bad_obs = (
        SentinelObservation(ident(77, "bad").node_id, "bad-family", SentinelEventKind.PROVIDER_FALSE, sha256(b"lie-a"), 201),
        SentinelObservation(ident(77, "bad").node_id, "bad-family", SentinelEventKind.PROVIDER_FALSE, sha256(b"lie-b"), 202),
    )
    bad_score = analyze_sentinel_observations(bad_obs, policy=SentinelPolicy(min_events=1))[0]
    assert bad_score.decision is SentinelDecisionKind.QUARANTINE
    assert bad_score.score <= -70


def test_garden_sentinel_ingests_witness_mesh_without_making_quorum_truth() -> None:
    target = sha256(b"provider-target")
    evidence = sha256(b"provider-evidence")
    subject = ident(50, "subject").node_id
    r1 = WitnessReceipt.create(keypair=kp(1), witness_node_id=ident(1, "wit").node_id, witness_family="east", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_TRUE, evidence_digest=evidence, issued_at=100)
    r2 = WitnessReceipt.create(keypair=kp(2), witness_node_id=ident(2, "wit").node_id, witness_family="west", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_TRUE, evidence_digest=evidence, issued_at=100)
    mesh = analyze_witness_mesh((r1, r2), now=101)
    assert mesh.decision.kind is WitnessMeshDecisionKind.CONTINUE_INSUFFICIENT_DIVERSITY
    obs = observations_from_witness_mesh(mesh, issued_at=102)
    scores = analyze_sentinel_observations(obs, policy=SentinelPolicy(min_events=1))
    assert all(score.decision in {SentinelDecisionKind.BACKOFF, SentinelDecisionKind.KEEP_WATCHING} for score in scores)

    contradiction_a = WitnessReceipt.create(keypair=kp(3), witness_node_id=ident(3, "wit").node_id, witness_family="north", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_TRUE, evidence_digest=evidence, issued_at=100)
    contradiction_b = WitnessReceipt.create(keypair=kp(3), witness_node_id=ident(3, "wit").node_id, witness_family="north", subject_node_id=subject, target_commitment=target, claim=WitnessClaimKind.PROVIDER_FALSE, evidence_digest=sha256(b"contradict"), issued_at=100)
    poisoned = analyze_witness_mesh((contradiction_a, contradiction_b), now=101)
    assert poisoned.decision.kind is WitnessMeshDecisionKind.QUARANTINE_CONTRADICTIONS
    poison_score = analyze_sentinel_observations(observations_from_witness_mesh(poisoned, issued_at=102), policy=SentinelPolicy(min_events=1))[0]
    assert poison_score.decision is SentinelDecisionKind.QUARANTINE


def test_sweepgrid_exposes_fast_capture_and_combined_pressure() -> None:
    low = evaluate_sweep_grid_point(SweepGridScenario(family_count=8, captured_families=0, false_provider_fraction=0.0, stale_head_fraction=0.0, latency_advantage_ms=0))
    assert low.decision is SweepGridDecisionKind.ACCEPT_LOW_PRESSURE

    fast = evaluate_sweep_grid_point(SweepGridScenario(family_count=8, captured_families=2, false_provider_fraction=0.0, stale_head_fraction=0.0, latency_advantage_ms=200))
    assert fast.decision is SweepGridDecisionKind.CONTINUE_FAST_WINDOW_CAPTURE
    assert fast.fast_captured_fraction > fast.captured_fraction

    combined = evaluate_sweep_grid_point(SweepGridScenario(family_count=8, captured_families=4, false_provider_fraction=0.5, stale_head_fraction=0.5, latency_advantage_ms=200))
    assert combined.decision is SweepGridDecisionKind.QUARANTINE_COMBINED_PRESSURE

    summary = run_sweep_grid(family_counts=(4,), captured_family_counts=(0, 1, 2, 4), false_provider_fractions=(0.0, 0.25), stale_head_fractions=(0.0, 0.5), latency_advantages_ms=(0, 200))
    assert summary.decision_counts[SweepGridDecisionKind.ACCEPT_LOW_PRESSURE.value] > 0
    assert summary.decision_counts[SweepGridDecisionKind.QUARANTINE_COMBINED_PRESSURE.value] > 0
    assert summary.transcript_digest == run_sweep_grid(family_counts=(4,), captured_family_counts=(0, 1, 2, 4), false_provider_fractions=(0.0, 0.25), stale_head_fractions=(0.0, 0.5), latency_advantages_ms=(0, 200)).transcript_digest


def test_supersession_map_turns_historical_duplicates_into_info(tmp_path: Path) -> None:
    (tmp_path / "adr").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "src" / "i2p_dht_lab").mkdir(parents=True)
    (tmp_path / "adr" / "0001-old.md").write_text("old", encoding="utf-8")
    (tmp_path / "adr" / "0001-new.md").write_text("new", encoding="utf-8")
    (tmp_path / "docs" / "01-old.md").write_text("old", encoding="utf-8")
    (tmp_path / "docs" / "01-new.md").write_text("new", encoding="utf-8")
    (tmp_path / "src" / "i2p_dht_lab" / "foo_bar.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "i2p_dht_lab" / "foobar.py").write_text("", encoding="utf-8")
    (tmp_path / "HISTORICAL_SUPERSESSION.json").write_text(json.dumps({
        "entries": [
            {"old_path": "adr/0001-old.md", "superseded_by": "adr/0001-new.md", "reason": "test"},
            {"old_path": "docs/01-old.md", "superseded_by": "docs/01-new.md", "reason": "test"},
            {"old_path": "src/i2p_dht_lab/foobar.py", "superseded_by": "src/i2p_dht_lab/foo_bar.py", "reason": "test"},
        ]
    }), encoding="utf-8")
    supersession = load_supersession_map(tmp_path)
    assert supersession.covers_any(["adr/0001-old.md"])
    report = audit_cube(tmp_path)
    summary = summarize_findings(report.findings)
    assert report.status == "pass"
    assert report.warning_count == 0
    assert report.info_count == 3
    assert summary["duplicate_adr_number"] == 1
    assert summary["duplicate_doc_number"] == 1
    assert summary["near_duplicate_module_name"] == 1
