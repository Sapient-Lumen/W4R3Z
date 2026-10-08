from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.gateaudit import DispatchHandlerSpec, DispatchObservation, GateAuditDecisionKind, audit_dispatch_gate
from i2p_dht_lab.gatefold import audit_gate_fold
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.interestmix import (
    InterestMixDecisionKind,
    InterestMixHistory,
    InterestMixPolicy,
    InterestTarget,
    InterestTargetKind,
    assess_interest_mix_round,
    plan_interest_mix_round,
)
from i2p_dht_lab.privateprovider import PrivateProbeBudget, ProviderCandidate
from i2p_dht_lab.routeattest import (
    RouteAttestation,
    RouteAttestationBook,
    RouteAttestationDecisionKind,
    RouteAttestationPolicy,
    assess_route_attestations,
)
from i2p_dht_lab.validatorwall import PayloadEnvelope, PayloadRole, ValidatorWallPolicy
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind

NOW = 1_765_318_000


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0024-gate-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def candidate(n: int, family: str, *, commit: bool = True) -> ProviderCandidate:
    return ProviderCandidate(provider_node_id=ident(n).node_id, family_id=family, distance_rank=n, latency_ms=100 + n, reliability_score=10, supports_commitment_probe=commit)


def target(name: str, kind: InterestTargetKind, priority: int = 1) -> InterestTarget:
    return InterestTarget(namespace="sync-heads", content_key=digest("target:" + name), kind=kind, label=name, priority=priority)


def test_interestmix_accepts_real_targets_with_cover_and_family_spread():
    candidates = [candidate(1, "fam-a"), candidate(2, "fam-b"), candidate(3, "fam-c"), candidate(4, "fam-d")]
    probe_budget = PrivateProbeBudget(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, max_content_key_exposures=1, require_decoy=True)
    policy = InterestMixPolicy(max_real_targets=1, min_cover_targets=2, min_cover_per_real=2, min_probe_families=3, max_per_probe_family=6, max_raw_key_exposures=1)
    round_ = plan_interest_mix_round(
        [target("real", InterestTargetKind.REAL, 10)],
        [target("cover-a", InterestTargetKind.COVER, 2), target("cover-b", InterestTargetKind.COVER, 1)],
        candidates,
        round_id=11,
        issued_at=NOW,
        seed_nonce=digest("seed"),
        policy=policy,
        probe_budget=probe_budget,
    )
    report = assess_interest_mix_round(round_, policy=policy, probe_budget=probe_budget)
    assert report.decision.kind is InterestMixDecisionKind.ACCEPT_MIXED_ROUND
    assert report.decision.accept
    assert b"content_key" not in round_.witness_payload


def test_interestmix_holds_repeated_real_target_before_probe_pressure_becomes_habit():
    candidates = [candidate(1, "fam-a"), candidate(2, "fam-b"), candidate(3, "fam-c"), candidate(4, "fam-d")]
    real = target("sticky", InterestTargetKind.REAL, 10)
    covers = [target("cover-a", InterestTargetKind.COVER), target("cover-b", InterestTargetKind.COVER)]
    policy = InterestMixPolicy(max_real_targets=1, min_cover_targets=2, min_cover_per_real=1, min_probe_families=2, max_per_probe_family=6, max_real_repeats_in_window=1)
    budget = PrivateProbeBudget(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, require_decoy=True)
    history = InterestMixHistory()
    first = plan_interest_mix_round([real], covers, candidates, round_id=3, issued_at=NOW, seed_nonce=digest("seed-a"), policy=policy, probe_budget=budget)
    history.record_round(first)
    second = plan_interest_mix_round([real], covers, candidates, round_id=4, issued_at=NOW + 1, seed_nonce=digest("seed-b"), policy=policy, probe_budget=budget)
    report = assess_interest_mix_round(second, policy=policy, probe_budget=budget, history=history)
    assert report.decision.kind is InterestMixDecisionKind.HOLD_LINKABLE_REPEAT
    assert report.repeated_targets == (real.target_digest,)


def test_interestmix_reduces_raw_key_exposure_when_commitments_are_not_supported():
    candidates = [candidate(1, "fam-a", commit=False), candidate(2, "fam-b", commit=False), candidate(3, "fam-c", commit=False)]
    policy = InterestMixPolicy(max_real_targets=1, min_cover_targets=1, min_cover_per_real=1, min_probe_families=2, max_per_probe_family=6, max_raw_key_exposures=0)
    budget = PrivateProbeBudget(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, max_content_key_exposures=5, require_decoy=True)
    round_ = plan_interest_mix_round([target("real", InterestTargetKind.REAL)], [target("cover", InterestTargetKind.COVER)], candidates, round_id=5, issued_at=NOW, seed_nonce=digest("raw"), policy=policy, probe_budget=budget)
    report = assess_interest_mix_round(round_, policy=policy, probe_budget=budget)
    assert report.decision.kind is InterestMixDecisionKind.REDUCE_RAW_KEY_EXPOSURE
    assert round_.raw_key_exposure_count >= 1


def lease(n: int, family: str, *, sequence: int = 1) -> ContactLease:
    return ContactLease.create(
        identity=ident(n),
        keypair=kp(n),
        family_id=family,
        purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE),
        sequence=sequence,
        issued_at=NOW,
        ttl=600,
    )


def attest(attester: int, attester_family: str, path_family: str, item: ContactLease, *, sequence: int = 1) -> RouteAttestation:
    return RouteAttestation.create(
        keypair=kp(attester),
        attester_node_id=ident(attester).node_id,
        attester_family=attester_family,
        path_family=path_family,
        lease=item,
        purpose=ContactLeasePurpose.ROUTE,
        sequence=sequence,
        issued_at=NOW,
        ttl=600,
    )


def test_route_attest_accepts_contact_attester_and_path_diversity():
    leases = [lease(1, "contact-a"), lease(2, "contact-b"), lease(3, "contact-c"), lease(4, "contact-d")]
    attestations = [
        attest(20, "att-a", "path-a", leases[0]),
        attest(21, "att-b", "path-a", leases[1]),
        attest(22, "att-c", "path-b", leases[2]),
        attest(23, "att-d", "path-b", leases[3]),
    ]
    policy = RouteAttestationPolicy(min_valid_attestations=3, min_contact_families=3, min_attester_families=3, min_path_families=2, max_per_contact_family=2, max_per_attester_family=2)
    report = assess_route_attestations(attestations, leases, now=NOW + 10, target=digest("route-target"), policy=policy)
    assert report.decision.kind is RouteAttestationDecisionKind.ACCEPT_ATTESTED_ROUTE_SET
    assert report.decision.accept


def test_route_attest_quarantines_same_sequence_attester_fork():
    item = lease(5, "contact-a")
    first = attest(30, "att-a", "path-a", item, sequence=2)
    fork = attest(30, "att-a", "path-b", item, sequence=2)
    policy = RouteAttestationPolicy(min_valid_attestations=1, min_contact_families=1, min_attester_families=1, min_path_families=1)
    report = assess_route_attestations((first, fork), (item,), now=NOW + 10, policy=policy, attestation_book=RouteAttestationBook())
    assert report.decision.kind is RouteAttestationDecisionKind.QUARANTINE_ATTESTATION_FORK
    assert report.quarantined


def observation(*, body: bytes = b"epoch-body", request_id: bytes | None = None, role: PayloadRole = PayloadRole.MUTABLE_HEAD, kind: WireMessageKind = WireMessageKind.EPOCH_HEAD):
    envelope = PayloadEnvelope.create(namespace="i2p-dht-control", role=role, scope_id=digest("scope"), body=body, issued_at=NOW, ttl=300)
    payload = envelope.to_bytes()
    frame = WireFrame.create(
        keypair=kp(80),
        sender_node_id=ident(80).node_id,
        message_kind=kind,
        request_id=request_id or digest("request"),
        payload=payload,
        issued_at=NOW,
        ttl=300,
        flags=("mutable-head",),
    )
    return DispatchObservation(frame=frame, payload=payload, body=body, expected_scope_id=digest("scope"))


def test_gateaudit_accepts_validated_payload_with_matching_handler():
    handler = DispatchHandlerSpec("epoch-head", "i2p-dht-control", WireMessageKind.EPOCH_HEAD, PayloadRole.MUTABLE_HEAD)
    report = audit_dispatch_gate((observation(),), handlers=(handler,), now=NOW + 1, validator_policy=ValidatorWallPolicy(required_flags_by_role={PayloadRole.MUTABLE_HEAD: frozenset({"mutable-head"})}))
    assert report.decision.kind is GateAuditDecisionKind.ACCEPT_DISPATCH_WINDOW
    assert report.matched_handlers == (handler,)


def test_gateaudit_rejects_valid_payload_without_registered_role_handler():
    handler = DispatchHandlerSpec("provider", "i2p-dht-control", WireMessageKind.EPOCH_HEAD, PayloadRole.PROVIDER_CLAIM)
    report = audit_dispatch_gate((observation(),), handlers=(handler,), now=NOW + 1, validator_policy=ValidatorWallPolicy(required_flags_by_role={PayloadRole.MUTABLE_HEAD: frozenset({"mutable-head"})}))
    assert report.decision.kind is GateAuditDecisionKind.REJECT_HANDLER_ROLE


def test_gateaudit_quarantines_request_id_conflict_after_validation():
    handler = DispatchHandlerSpec("epoch-head", "i2p-dht-control", WireMessageKind.EPOCH_HEAD, PayloadRole.MUTABLE_HEAD)
    request_id = digest("conflict-request")
    one = observation(body=b"one", request_id=request_id)
    two = observation(body=b"two", request_id=request_id)
    report = audit_dispatch_gate((one, two), handlers=(handler,), now=NOW + 1, validator_policy=ValidatorWallPolicy(required_flags_by_role={PayloadRole.MUTABLE_HEAD: frozenset({"mutable-head"})}))
    assert report.decision.kind is GateAuditDecisionKind.QUARANTINE_REQUEST_ID_CONFLICT
    assert report.quarantined


def test_gatefold_surfaces_rev0024_branchlet_without_warnings():
    root = Path(__file__).resolve().parents[1]
    report = audit_gate_fold(root, revision="rev0024")
    assert report.status == "pass"
