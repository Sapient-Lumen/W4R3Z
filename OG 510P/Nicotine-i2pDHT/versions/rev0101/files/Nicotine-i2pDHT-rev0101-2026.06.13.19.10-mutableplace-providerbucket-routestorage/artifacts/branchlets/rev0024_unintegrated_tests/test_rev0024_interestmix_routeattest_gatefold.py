from dataclasses import replace

from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.gateaudit import DispatchHandlerSpec, DispatchObservation, GateAuditDecisionKind, audit_dispatch_gate
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
    RouteAttestationDecisionKind,
    RouteAttestationPolicy,
    assess_route_attestations,
)
from i2p_dht_lab.validatorwall import PayloadEnvelope, PayloadRole
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind


def h(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def keypair(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(h("seed:" + label))


def identity(label: str) -> tuple[DhtKeypair, NodeIdentity]:
    kp = keypair(label)
    return kp, NodeIdentity.create(destination=f"{label}.b32.i2p", keypair=kp)


def candidates(count: int = 8, *, same_family: bool = False, supports_commitment: bool = True) -> tuple[ProviderCandidate, ...]:
    return tuple(
        ProviderCandidate(
            provider_node_id=h(f"provider:{idx}"),
            family_id="same" if same_family else f"fam{idx}",
            distance_rank=idx,
            latency_ms=20 + idx,
            supports_commitment_probe=supports_commitment,
        )
        for idx in range(count)
    )


def target(label: str, kind: InterestTargetKind) -> InterestTarget:
    return InterestTarget(namespace="test", content_key=h("content:" + label), kind=kind, label=label, priority=10)


def probe_budget(**kwargs) -> PrivateProbeBudget:
    defaults = dict(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, max_content_key_exposures=1, require_decoy=True)
    defaults.update(kwargs)
    return PrivateProbeBudget(**defaults)


def test_interest_mix_accepts_real_probe_with_cover_targets_and_family_spread():
    mix = plan_interest_mix_round(
        [target("real-a", InterestTargetKind.REAL)],
        [target("cover-a", InterestTargetKind.COVER), target("cover-b", InterestTargetKind.COVER)],
        candidates(),
        round_id=7,
        issued_at=100,
        seed_nonce=h("nonce"),
        probe_budget=probe_budget(),
    )
    report = assess_interest_mix_round(mix, probe_budget=probe_budget())
    assert report.decision.kind is InterestMixDecisionKind.ACCEPT_MIXED_ROUND
    assert report.decision.accept
    assert mix.raw_key_exposure_count == 0
    assert b"content:real-a" not in mix.witness_payload
    assert len(report.family_counts) >= 3


def test_interest_mix_holds_when_cover_is_missing():
    mix = plan_interest_mix_round(
        [target("real-a", InterestTargetKind.REAL)],
        [],
        candidates(),
        round_id=8,
        issued_at=100,
        seed_nonce=h("nonce2"),
        probe_budget=probe_budget(),
    )
    report = assess_interest_mix_round(mix, probe_budget=probe_budget())
    assert report.decision.kind is InterestMixDecisionKind.HOLD_INSUFFICIENT_COVER
    assert not report.decision.accept


def test_interest_mix_rejects_linkable_repeated_real_target():
    real = target("real-repeat", InterestTargetKind.REAL)
    history = InterestMixHistory()
    history.real_rounds_by_key[real.content_key] = [10, 11]
    mix = plan_interest_mix_round(
        [real],
        [target("cover-a", InterestTargetKind.COVER), target("cover-b", InterestTargetKind.COVER)],
        candidates(),
        round_id=12,
        issued_at=100,
        seed_nonce=h("nonce3"),
        probe_budget=probe_budget(),
    )
    report = assess_interest_mix_round(mix, history=history, probe_budget=probe_budget())
    assert report.decision.kind is InterestMixDecisionKind.HOLD_LINKABLE_REPEAT
    assert report.repeated_targets


def test_interest_mix_tracks_raw_key_exposure_separately_from_private_plan_acceptance():
    mix = plan_interest_mix_round(
        [target("real-raw", InterestTargetKind.REAL)],
        [target("cover-a", InterestTargetKind.COVER), target("cover-b", InterestTargetKind.COVER)],
        candidates(supports_commitment=False),
        round_id=13,
        issued_at=100,
        seed_nonce=h("nonce4"),
        probe_budget=probe_budget(max_content_key_exposures=10),
    )
    report = assess_interest_mix_round(
        mix,
        policy=InterestMixPolicy(require_private_probe_acceptance=False, max_raw_key_exposures=1),
        probe_budget=probe_budget(max_content_key_exposures=10),
    )
    assert report.decision.kind is InterestMixDecisionKind.REDUCE_RAW_KEY_EXPOSURE
    assert mix.raw_key_exposure_count > 1


def lease(label: str, family: str, *, sequence: int = 1, purpose=ContactLeasePurpose.ROUTE) -> ContactLease:
    kp, ident = identity("contact:" + label)
    return ContactLease.create(identity=ident, keypair=kp, family_id=family, purposes=(purpose,), sequence=sequence, issued_at=100, ttl=500)


def attest(label: str, lease_obj: ContactLease, *, attester_family: str, path_family: str, sequence: int = 1) -> RouteAttestation:
    kp, ident = identity("attester:" + label)
    return RouteAttestation.create(
        keypair=kp,
        attester_node_id=ident.node_id,
        attester_family=attester_family,
        path_family=path_family,
        lease=lease_obj,
        purpose=ContactLeasePurpose.ROUTE,
        sequence=sequence,
        issued_at=110,
        ttl=300,
    )


def test_route_attestations_accept_diverse_lease_bound_route_set():
    leases = tuple(lease(f"l{idx}", f"contactfam{idx % 3}") for idx in range(4))
    attestations = tuple(attest(f"a{idx}", leases[idx], attester_family=f"attfam{idx % 3}", path_family=f"path{idx % 2}") for idx in range(4))
    report = assess_route_attestations(attestations, leases, now=120, target=h("route-target"), policy=RouteAttestationPolicy(min_valid_attestations=4, min_contact_families=3, min_attester_families=3, min_path_families=2))
    assert report.decision.kind is RouteAttestationDecisionKind.ACCEPT_ATTESTED_ROUTE_SET
    assert report.decision.accept
    assert len(report.selected_attestations) == 4


def test_route_attestations_quarantine_path_monoculture_even_with_attester_diversity():
    leases = tuple(lease(f"mono{idx}", f"contactfam{idx % 3}") for idx in range(4))
    attestations = tuple(attest(f"mono{idx}", leases[idx], attester_family=f"attfam{idx % 3}", path_family="single-path") for idx in range(4))
    report = assess_route_attestations(attestations, leases, now=120, target=h("route-target"), policy=RouteAttestationPolicy(min_valid_attestations=4, min_contact_families=3, min_attester_families=3, min_path_families=2))
    assert report.decision.kind is RouteAttestationDecisionKind.QUARANTINE_ATTESTER_MONOCULTURE
    assert report.quarantined


def test_route_attestations_quarantine_same_sequence_attestation_fork():
    one_lease = lease("fork", "contactfam0")
    first = attest("forker", one_lease, attester_family="attfam0", path_family="p0", sequence=1)
    forked = replace(first, path_family="p1")
    forked = replace(forked, signature=keypair("attester:forker").sign(forked.unsigned_payload()))
    report = assess_route_attestations([first, forked], [one_lease], now=120, policy=RouteAttestationPolicy(min_valid_attestations=1, min_contact_families=1, min_attester_families=1, min_path_families=1))
    assert report.decision.kind is RouteAttestationDecisionKind.QUARANTINE_ATTESTATION_FORK
    assert report.quarantined


def frame_and_payload(kind: WireMessageKind, role: PayloadRole, *, namespace="i2p-dht-store", request_id=None, body=b"body", scope=None):
    kp, ident = identity("wire:" + kind.value + role.value + str(body))
    scope_id = scope or h("scope")
    env = PayloadEnvelope.create(namespace=namespace, role=role, scope_id=scope_id, body=body, issued_at=100, ttl=300)
    payload = env.to_bytes()
    frame = WireFrame.create(keypair=kp, sender_node_id=ident.node_id, message_kind=kind, request_id=request_id or h("request:" + kind.value), payload=payload, issued_at=100, ttl=300)
    return frame, payload, body, scope_id


def test_gate_audit_accepts_validated_payload_with_registered_handler():
    frame, payload, body, scope = frame_and_payload(WireMessageKind.STORE_RECORD, PayloadRole.STORE_REQUEST)
    handler = DispatchHandlerSpec("store-request", "i2p-dht-store", WireMessageKind.STORE_RECORD, PayloadRole.STORE_REQUEST, risk_tier="store")
    report = audit_dispatch_gate([DispatchObservation(frame, payload, body, scope)], handlers=[handler], now=120)
    assert report.decision.kind is GateAuditDecisionKind.ACCEPT_DISPATCH_WINDOW
    assert report.decision.accept
    assert report.matched_handlers == (handler,)


def test_gate_audit_quarantines_same_request_id_conflict_after_validator_acceptance():
    request_id = h("same-request")
    first = frame_and_payload(WireMessageKind.STORE_RECORD, PayloadRole.STORE_REQUEST, request_id=request_id, body=b"body-one")
    second = frame_and_payload(WireMessageKind.STORE_RECORD, PayloadRole.STORE_REQUEST, request_id=request_id, body=b"body-two")
    handler = DispatchHandlerSpec("store-request", "i2p-dht-store", WireMessageKind.STORE_RECORD, PayloadRole.STORE_REQUEST)
    report = audit_dispatch_gate([DispatchObservation(*first), DispatchObservation(*second)], handlers=[handler], now=120)
    assert report.decision.kind is GateAuditDecisionKind.QUARANTINE_REQUEST_ID_CONFLICT
    assert report.quarantined


def test_gate_audit_rejects_validated_payload_without_registered_handler():
    frame, payload, body, scope = frame_and_payload(WireMessageKind.STORE_RECORD, PayloadRole.STORE_REQUEST)
    report = audit_dispatch_gate([DispatchObservation(frame, payload, body, scope)], handlers=[], now=120)
    assert report.decision.kind is GateAuditDecisionKind.REJECT_HANDLER_NAMESPACE
    assert not report.decision.accept


def test_gate_audit_rejects_role_kind_mismatch_before_handler_dispatch():
    # FIND_PROVIDER frames may carry provider claims, not STORE_REQUEST envelopes.
    frame, payload, body, scope = frame_and_payload(WireMessageKind.FIND_PROVIDER, PayloadRole.STORE_REQUEST)
    handler = DispatchHandlerSpec("provider", "i2p-dht-store", WireMessageKind.FIND_PROVIDER, PayloadRole.STORE_REQUEST)
    report = audit_dispatch_gate([DispatchObservation(frame, payload, body, scope)], handlers=[handler], now=120)
    assert report.decision.kind is GateAuditDecisionKind.REJECT_VALIDATOR_FAILURE
    assert not report.decision.accept

from i2p_dht_lab.gatefold import audit_gate_fold


def test_interest_mix_holds_too_many_real_targets_for_one_budget():
    mix = plan_interest_mix_round(
        [target("real-a", InterestTargetKind.REAL), target("real-b", InterestTargetKind.REAL), target("real-c", InterestTargetKind.REAL)],
        [target("cover-a", InterestTargetKind.COVER), target("cover-b", InterestTargetKind.COVER), target("cover-c", InterestTargetKind.COVER)],
        candidates(),
        round_id=14,
        issued_at=100,
        seed_nonce=h("nonce5"),
        policy=InterestMixPolicy(max_real_targets=2, min_cover_targets=2, min_cover_per_real=1),
        probe_budget=probe_budget(),
    )
    report = assess_interest_mix_round(mix, policy=InterestMixPolicy(max_real_targets=2, min_cover_targets=2, min_cover_per_real=1), probe_budget=probe_budget())
    assert report.decision.kind is InterestMixDecisionKind.HOLD_TOO_MANY_REAL_TARGETS
    assert mix.omitted_real_count == 1


def test_interest_mix_holds_no_real_targets_even_with_cover_noise():
    mix = plan_interest_mix_round(
        [],
        [target("cover-a", InterestTargetKind.COVER), target("cover-b", InterestTargetKind.COVER)],
        candidates(),
        round_id=15,
        issued_at=100,
        seed_nonce=h("nonce6"),
        probe_budget=probe_budget(),
    )
    report = assess_interest_mix_round(mix, probe_budget=probe_budget())
    assert report.decision.kind is InterestMixDecisionKind.HOLD_NO_REAL_TARGETS
    assert not report.decision.accept


def test_route_attestations_reject_unknown_lease_reference():
    actual_lease = lease("unknown", "contactfam0")
    route_attestation = attest("unknown", actual_lease, attester_family="attfam0", path_family="p0")
    report = assess_route_attestations([route_attestation], [], now=120, policy=RouteAttestationPolicy(min_valid_attestations=1, min_contact_families=1, min_attester_families=1, min_path_families=1))
    assert report.decision.kind is RouteAttestationDecisionKind.CONTINUE_NO_VALID_ATTESTATIONS
    assert len(report.invalid_attestations) == 1


def test_gatefold_audit_passes_current_merged_branchlet_surface():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    report = audit_gate_fold(root, revision="rev0024")
    assert report.status == "pass"
    assert report.warning_count == 0


# ---------------- audit/refactor ----------------


def test_gatefold_audit_sees_folded_rev0024_surfaces():
    from pathlib import Path

    from i2p_dht_lab.gatefold import audit_gate_fold

    root = Path(__file__).resolve().parents[1]
    report = audit_gate_fold(root, revision="rev0024")
    assert report.status == "pass", report.findings
    assert "src/i2p_dht_lab/interestmix.py" in report.expected_surfaces
    assert "src/i2p_dht_lab/gateaudit.py" in report.expected_surfaces
