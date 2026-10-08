from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.cubeaudit import audit_cube, summarize_findings
from i2p_dht_lab.headlog import LocalHeadMemory, head_record_digest, make_versioned_head_record
from i2p_dht_lab.headwitness import (
    HeadLookupDecisionKind,
    HeadLookupPolicy,
    HeadObservation,
    HeadWitnessClaimKind,
    HeadWitnessStatement,
    analyze_mutable_head_lookup,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.latencyforge import (
    FakeEndpoint,
    FakeEndpointState,
    LatencyDecisionKind,
    LatencyProbePolicy,
    run_latency_forge,
)
from i2p_dht_lab.proofhandshake import (
    ProofMode,
    ProofVisibility,
    ProviderAvailabilityClaim,
    ProviderProofChallenge,
    ProviderProofPolicy,
    ProviderProofResponse,
    ProviderProofResponseKind,
    ProviderProofVerdictKind,
    assess_provider_proof,
    proof_material_digest,
)


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int, prefix: str = "node") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def make_claim_and_challenge(*, provider_n: int = 10, challenger_n: int = 11, now: int = 100):
    provider = ident(provider_n, "provider")
    challenger = ident(challenger_n, "challenger")
    content_key = sha256(b"content-key")
    content_key_commitment = sha256(b"commitment" + content_key)
    expected_digest = sha256(b"served block bytes")
    claim = ProviderAvailabilityClaim.create(
        provider_keypair=kp(provider_n),
        provider_node_id=provider.node_id,
        family_id="provider-east",
        namespace="blocks",
        content_key_commitment=content_key_commitment,
        expected_content_digest=expected_digest,
        issued_at=now,
    )
    challenge = ProviderProofChallenge.create(
        challenger_keypair=kp(challenger_n),
        challenger_node_id=challenger.node_id,
        provider_node_id=provider.node_id,
        claim_digest=claim.digest,
        mode=ProofMode.BLOCK_CHALLENGE,
        visibility=ProofVisibility.COMMITMENT_ONLY,
        challenge_nonce=b"nonce-1",
        issued_at=now + 1,
        deadline_ms=1_000,
    )
    return provider, challenger, content_key, expected_digest, claim, challenge


def test_provider_proof_handshake_accepts_challenge_bound_digest() -> None:
    provider, _challenger, _content_key, expected_digest, claim, challenge = make_claim_and_challenge()
    response = ProviderProofResponse.create(
        provider_keypair=kp(10),
        provider_node_id=provider.node_id,
        challenge_digest=challenge.digest,
        kind=ProviderProofResponseKind.PROOF,
        served_digest=expected_digest,
        proof_material_digest=proof_material_digest(challenge=challenge, served_digest=expected_digest),
        issued_at=102,
    )
    verdict = assess_provider_proof(claim=claim, challenge=challenge, response=response, now=103, observed_latency_ms=250)
    assert verdict.kind is ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER
    assert verdict.accept
    assert not challenge.exposes_content_key
    assert b"content-key" not in challenge.witness_payload


def test_provider_proof_rejects_wrong_digest_and_challenge_replay() -> None:
    provider, _challenger, _content_key, expected_digest, claim, challenge = make_claim_and_challenge()
    wrong = ProviderProofResponse.create(
        provider_keypair=kp(10),
        provider_node_id=provider.node_id,
        challenge_digest=challenge.digest,
        kind=ProviderProofResponseKind.PROOF,
        served_digest=sha256(b"wrong bytes"),
        proof_material_digest=proof_material_digest(challenge=challenge, served_digest=expected_digest),
        issued_at=102,
    )
    wrong_verdict = assess_provider_proof(claim=claim, challenge=challenge, response=wrong, now=103, observed_latency_ms=250)
    assert wrong_verdict.kind is ProviderProofVerdictKind.REJECT_FALSE_PROVIDER

    replay = replace(wrong, served_digest=expected_digest, challenge_digest=sha256(b"different-challenge"))
    replay_verdict = assess_provider_proof(claim=claim, challenge=challenge, response=replay, now=103, observed_latency_ms=250)
    assert replay_verdict.kind is ProviderProofVerdictKind.REJECT_BAD_SIGNATURE


def test_provider_proof_accepts_useful_refusal_but_rejects_late_response() -> None:
    provider, _challenger, _content_key, expected_digest, claim, challenge = make_claim_and_challenge()
    refusal = ProviderProofResponse.create(
        provider_keypair=kp(10),
        provider_node_id=provider.node_id,
        challenge_digest=challenge.digest,
        kind=ProviderProofResponseKind.USEFUL_REFUSAL,
        served_digest=b"",
        proof_material_digest=sha256(b"busy"),
        issued_at=102,
        retry_after_seconds=60,
        note="garden overloaded but alive",
    )
    refused = assess_provider_proof(claim=claim, challenge=challenge, response=refusal, now=103, observed_latency_ms=200)
    assert refused.kind is ProviderProofVerdictKind.ACCEPT_USEFUL_REFUSAL
    assert refused.useful

    proof = ProviderProofResponse.create(
        provider_keypair=kp(10),
        provider_node_id=provider.node_id,
        challenge_digest=challenge.digest,
        kind=ProviderProofResponseKind.PROOF,
        served_digest=expected_digest,
        proof_material_digest=proof_material_digest(challenge=challenge, served_digest=expected_digest),
        issued_at=102,
    )
    late = assess_provider_proof(claim=claim, challenge=challenge, response=proof, now=103, observed_latency_ms=10_000)
    assert late.kind is ProviderProofVerdictKind.REJECT_EXPIRED


def test_provider_proof_metadata_budget_can_reject_raw_key_exposure() -> None:
    provider, challenger, content_key, expected_digest, claim, _challenge = make_claim_and_challenge()
    raw_challenge = ProviderProofChallenge.create(
        challenger_keypair=kp(11),
        challenger_node_id=challenger.node_id,
        provider_node_id=provider.node_id,
        claim_digest=claim.digest,
        mode=ProofMode.BLOCK_CHALLENGE,
        visibility=ProofVisibility.RAW_CONTENT_KEY,
        challenge_nonce=b"raw-nonce",
        issued_at=101,
        content_key=content_key,
    )
    response = ProviderProofResponse.create(
        provider_keypair=kp(10),
        provider_node_id=provider.node_id,
        challenge_digest=raw_challenge.digest,
        kind=ProviderProofResponseKind.PROOF,
        served_digest=expected_digest,
        proof_material_digest=proof_material_digest(challenge=raw_challenge, served_digest=expected_digest),
        issued_at=102,
    )
    verdict = assess_provider_proof(
        claim=claim,
        challenge=raw_challenge,
        response=response,
        now=103,
        observed_latency_ms=250,
        policy=ProviderProofPolicy(max_raw_key_exposures=0),
    )
    assert verdict.kind is ProviderProofVerdictKind.CONTINUE_METADATA_EXPOSURE_HIGH
    assert raw_challenge.exposes_content_key
    assert content_key not in raw_challenge.witness_payload


def head_record(seq: int, pointer_seed: bytes, *, prev: bytes = b"", salt: bytes = b"slot"):
    return make_versioned_head_record(
        keypair=kp(80),
        kind="seed-head",
        pointer=sha256(pointer_seed),
        seq=seq,
        salt=salt,
        prev=prev,
        manifest_digest=sha256(b"manifest" + pointer_seed),
        now=100 + seq,
    )


def head_obs(record, n: int, family: str, at: int) -> HeadObservation:
    return HeadObservation(record=record, source_node_id=ident(n, "head-source").node_id, path_family=family, observed_at=at)


def head_witness(n: int, family: str, record, claim: HeadWitnessClaimKind, at: int = 120) -> HeadWitnessStatement:
    return HeadWitnessStatement.create(
        witness_keypair=kp(n),
        witness_node_id=ident(n, "head-witness").node_id,
        witness_family=family,
        target_hex=record.target_hex,
        claim=claim,
        observed_seq=record.seq,
        observed_record_digest=head_record_digest(record),
        evidence_digest=sha256(b"head-evidence" + bytes([n]) + claim.value.encode()),
        issued_at=at,
    )


def test_head_lookup_accepts_latest_with_diverse_paths_and_witness() -> None:
    base = head_record(0, b"base")
    latest = head_record(1, b"latest", prev=head_record_digest(base))
    report = analyze_mutable_head_lookup(
        (
            head_obs(base, 1, "old-east", 100),
            head_obs(latest, 2, "east", 101),
            head_obs(latest, 3, "west", 102),
        ),
        memory=LocalHeadMemory(),
        witness_statements=(head_witness(10, "garden-east", latest, HeadWitnessClaimKind.LATEST),),
        now=130,
        policy=HeadLookupPolicy(min_latest_families=2, min_latest_observations=2, max_per_family=2),
    )
    assert report.decision.kind is HeadLookupDecisionKind.ACCEPT_LATEST_DIVERSE
    assert report.accepted_record == latest
    assert report.latest_families == frozenset({"east", "west"})
    assert report.stale_observation_count == 1


def test_head_lookup_accepts_but_requests_watch_without_witnesses() -> None:
    base = head_record(0, b"base-watch")
    latest = head_record(1, b"latest-watch", prev=head_record_digest(base))
    report = analyze_mutable_head_lookup(
        (head_obs(base, 4, "old", 100), head_obs(latest, 5, "east", 101), head_obs(latest, 6, "west", 102)),
        memory=LocalHeadMemory(),
        now=130,
        policy=HeadLookupPolicy(min_latest_families=2, min_latest_observations=2, max_per_family=2, watch_if_no_witnesses=True),
    )
    assert report.decision.kind is HeadLookupDecisionKind.ACCEPT_LATEST_WITH_WATCH
    assert report.should_continue_lookup


def test_head_lookup_rejects_latest_family_monoculture() -> None:
    latest = head_record(1, b"mono")
    report = analyze_mutable_head_lookup(
        (head_obs(latest, 7, "one-family", 101), head_obs(latest, 8, "one-family", 102)),
        memory=LocalHeadMemory(),
        now=130,
        policy=HeadLookupPolicy(min_latest_families=2, min_latest_observations=2, max_per_family=2, require_prev=False),
    )
    assert report.decision.kind is HeadLookupDecisionKind.CONTINUE_INSUFFICIENT_DIVERSITY
    assert not report.decision.accept


def test_head_lookup_keeps_same_sequence_fork_pressure_out_of_accept_path() -> None:
    base = head_record(0, b"fork-base")
    prev = head_record_digest(base)
    latest_a = head_record(1, b"fork-a", prev=prev)
    latest_b = head_record(1, b"fork-b", prev=prev)
    report = analyze_mutable_head_lookup(
        (head_obs(base, 9, "old", 100), head_obs(latest_a, 10, "east", 101), head_obs(latest_b, 11, "west", 102)),
        memory=LocalHeadMemory(),
        witness_statements=(
            head_witness(20, "garden-east", latest_a, HeadWitnessClaimKind.FORK),
            head_witness(21, "garden-west", latest_b, HeadWitnessClaimKind.FORK),
        ),
        now=130,
        policy=HeadLookupPolicy(min_latest_families=2, min_latest_observations=1, max_per_family=2),
    )
    assert report.decision.kind is HeadLookupDecisionKind.CONTINUE_FORK_PRESSURE
    assert report.fork_observation_count >= 1
    assert report.accepted_record is None


def test_head_lookup_prev_mismatch_continues_even_when_signature_valid() -> None:
    base = head_record(0, b"prev-base")
    wrong_prev = sha256(b"not-the-base-head")
    latest = head_record(1, b"prev-latest", prev=wrong_prev)
    report = analyze_mutable_head_lookup(
        (head_obs(base, 12, "old", 100), head_obs(latest, 13, "east", 101), head_obs(latest, 14, "west", 102)),
        memory=LocalHeadMemory(),
        now=130,
        policy=HeadLookupPolicy(min_latest_families=2, min_latest_observations=2, max_per_family=2),
    )
    assert report.decision.kind is HeadLookupDecisionKind.CONTINUE_PREV_MISMATCH
    assert report.prev_mismatch_count >= 1


def endpoint(n: int, family: str, delay: int, state: FakeEndpointState = FakeEndpointState.OK) -> FakeEndpoint:
    return FakeEndpoint(node_id=ident(n, "latency").node_id, family_id=family, delay_ms=delay, state=state, reliability_score=100 - n)


def test_latency_forge_retries_past_timeouts_to_get_diverse_families() -> None:
    endpoints = (
        endpoint(1, "east", 50, FakeEndpointState.TIMEOUT),
        endpoint(2, "west", 60, FakeEndpointState.OK),
        endpoint(3, "north", 70, FakeEndpointState.OK),
        endpoint(4, "south", 80, FakeEndpointState.OK),
        endpoint(5, "deep", 90, FakeEndpointState.OK),
    )
    report = run_latency_forge(
        endpoints,
        target=sha256(b"latency-target"),
        request_id=sha256(b"latency-request"),
        policy=LatencyProbePolicy(alpha=2, min_response_families=3, max_per_family_per_round=1, timeout_ms=100, retry_budget=2),
    )
    assert report.decision.kind is LatencyDecisionKind.ACCEPT_DIVERSE_RESPONSES
    assert len(report.responding_families) >= 3
    assert report.retry_events >= 1
    assert report.transcript_digest == run_latency_forge(endpoints, target=sha256(b"latency-target"), request_id=sha256(b"latency-request"), policy=LatencyProbePolicy(alpha=2, min_response_families=3, max_per_family_per_round=1, timeout_ms=100, retry_budget=2)).transcript_digest


def test_latency_forge_flags_captured_fast_window_when_retries_cannot_fix_it() -> None:
    endpoints = (
        endpoint(10, "captured", 10, FakeEndpointState.LYING),
        endpoint(11, "captured", 11, FakeEndpointState.LYING),
        endpoint(12, "captured", 12, FakeEndpointState.LYING),
        endpoint(13, "honest-slow", 500, FakeEndpointState.OK),
    )
    report = run_latency_forge(
        endpoints,
        target=sha256(b"captured-target"),
        request_id=sha256(b"captured-request"),
        policy=LatencyProbePolicy(alpha=3, min_response_families=2, max_per_family_per_round=3, timeout_ms=100, retry_budget=0, fast_window_ms=50),
    )
    assert report.decision.kind is LatencyDecisionKind.CONTINUE_FAST_WINDOW_CAPTURED
    assert report.fast_window_families == frozenset({"captured"})


def test_latency_forge_counts_useful_refusals_as_reachable_capacity_signal() -> None:
    endpoints = (
        endpoint(20, "east", 10, FakeEndpointState.REFUSING),
        endpoint(21, "west", 20, FakeEndpointState.OK),
        endpoint(22, "north", 30, FakeEndpointState.OK),
    )
    report = run_latency_forge(
        endpoints,
        target=sha256(b"refusal-target"),
        request_id=sha256(b"refusal-request"),
        policy=LatencyProbePolicy(alpha=3, min_response_families=3, retry_budget=0, count_refusals_as_reachable=True),
    )
    assert report.decision.kind is LatencyDecisionKind.ACCEPT_DIVERSE_RESPONSES
    assert "east" in report.responding_families


def test_cube_audit_reports_transient_and_duplicate_surfaces_without_failing(tmp_path: Path) -> None:
    (tmp_path / "adr").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "src" / "i2p_dht_lab").mkdir(parents=True)
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / "adr" / "0001-first.md").write_text("x", encoding="utf-8")
    (tmp_path / "adr" / "0001-second.md").write_text("x", encoding="utf-8")
    (tmp_path / "docs" / "01-first.md").write_text("x", encoding="utf-8")
    (tmp_path / "docs" / "01-second.md").write_text("x", encoding="utf-8")
    (tmp_path / "src" / "i2p_dht_lab" / "providerpoison.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "i2p_dht_lab" / "provider_poison.py").write_text("", encoding="utf-8")
    report = audit_cube(tmp_path)
    summary = summarize_findings(report.findings)
    assert report.status == "warn"
    assert summary["transient_packaging_surface"] == 1
    assert summary["duplicate_adr_number"] == 1
    assert summary["duplicate_doc_number"] == 1
    assert summary["near_duplicate_module_name"] == 1
