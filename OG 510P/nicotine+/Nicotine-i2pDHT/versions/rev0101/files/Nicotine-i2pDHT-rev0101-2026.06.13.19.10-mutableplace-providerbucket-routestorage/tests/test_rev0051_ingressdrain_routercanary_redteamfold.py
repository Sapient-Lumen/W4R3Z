from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.ingressdrain import (
    IngressDrainDecisionKind,
    IngressDrainPhase,
    assess_ingress_drain,
    make_ingress_drain_receipt,
)
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.redteamfold import audit_redteam_fold
from i2p_dht_lab.routercanary import (
    RouterCanaryAction,
    RouterCanaryDecisionKind,
    assess_router_canary,
    make_router_canary_observation,
)

NOW = 60_000
PROFILE = "profile-rev0051"
SERVICE = "public-bridge-rev0051"
SCOPE = sha256(b"rev0051-scope")
REQUEST = sha256(b"rev0051-request")
PAYLOAD = sha256(b"rev0051-payload")
FRAME = sha256(b"rev0051-frame")
ROUTER_PROFILE = sha256(b"rev0051-router-profile")
CALLER = sha256(b"rev0051-caller")
HANDLER = sha256(b"rev0051-handler")
INGRESS_REQUEST = sha256(b"rev0051-ingress-request")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, decision: str = "accept"):
    return SimpleNamespace(
        report_digest=d(f"{label}:{accept}:{watch}:{quarantined}:{decision}"),
        transcript_digest=d(f"{label}:transcript:{accept}:{watch}:{quarantined}:{decision}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        decision_kind=SimpleNamespace(value=decision),
    )


def router_components():
    sam = component("sam-canary")
    harness = component("router-harness")
    drain = component("outbox-drain")
    return sam, harness, drain


def router_observations(*, transit: bool = True, persistent: bool = True, http: bool = False, socks: bool = False, session: str = "sess", endpoint: str = "127.0.0.1:7656", destination: str = "abc.b32.i2p", frame: bytes = FRAME):
    sam, harness, drain = router_components()
    o0 = make_router_canary_observation(
        keypair=kp(1),
        action=RouterCanaryAction.PUBLIC_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        frame_digest=frame,
        sam_canary_digest=sam.report_digest,
        router_harness_digest=harness.report_digest,
        outbox_drain_digest=drain.report_digest,
        session_id=session,
        destination=destination,
        sam_endpoint=endpoint,
        router_profile_digest=ROUTER_PROFILE,
        router_ready=True,
        destination_persistent=persistent,
        transit_enabled=transit,
        http_proxy_enabled=http,
        socks_proxy_enabled=socks,
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id="family-a",
        path_family="path-a",
    )
    o1 = make_router_canary_observation(
        keypair=kp(2),
        action=RouterCanaryAction.PUBLIC_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        frame_digest=frame,
        sam_canary_digest=sam.report_digest,
        router_harness_digest=harness.report_digest,
        outbox_drain_digest=drain.report_digest,
        session_id=session,
        destination=destination,
        sam_endpoint=endpoint,
        router_profile_digest=ROUTER_PROFILE,
        router_ready=True,
        destination_persistent=persistent,
        transit_enabled=transit,
        http_proxy_enabled=http,
        socks_proxy_enabled=socks,
        sequence=1,
        previous_observation_digest=o0.observation_digest,
        issued_at=NOW + 1,
        expires_at=NOW + 301,
        family_id="family-b",
        path_family="path-b",
    )
    return (o0, o1), sam, harness, drain


def assess_good_router(*, observations=None, sam=None, harness=None, drain=None, **kwargs):
    if observations is None:
        observations, sam, harness, drain = router_observations(**kwargs)
    return assess_router_canary(
        observations,
        sam_canary_report=sam,
        router_harness_report=harness,
        outbox_drain_report=drain,
        now=NOW + 2,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_action=RouterCanaryAction.PUBLIC_REFRESH,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD,
        expected_frame_digest=FRAME,
        expected_session_id="sess",
        expected_destination="abc.b32.i2p",
        expected_sam_endpoint="127.0.0.1:7656",
        expected_router_profile_digest=ROUTER_PROFILE,
    )


def test_router_canary_accepts_persistent_non_proxy_transit_profile() -> None:
    report = assess_good_router()
    assert report.decision_kind is RouterCanaryDecisionKind.ACCEPT_ROUTER_CANARY
    assert report.accept
    assert report.family_count == 2
    assert report.path_family_count == 2


def test_router_canary_rejects_ephemeral_destination_state() -> None:
    report = assess_good_router(persistent=False)
    assert report.decision_kind is RouterCanaryDecisionKind.QUARANTINE_EPHEMERAL_DESTINATION


def test_router_canary_rejects_proxy_exposure_and_notransit_regression() -> None:
    assert assess_good_router(http=True).decision_kind is RouterCanaryDecisionKind.QUARANTINE_PROXY_EXPOSURE
    assert assess_good_router(transit=False).decision_kind is RouterCanaryDecisionKind.QUARANTINE_NOTRANSIT_REGRESSION


def test_router_canary_rejects_session_or_frame_drift() -> None:
    assert assess_good_router(session="other-session").decision_kind is RouterCanaryDecisionKind.QUARANTINE_SESSION_DRIFT
    assert assess_good_router(frame=d("other-frame")).decision_kind is RouterCanaryDecisionKind.QUARANTINE_FRAME_DRIFT


def test_router_canary_rejects_same_sequence_fork() -> None:
    observations, sam, harness, drain = router_observations()
    fork = make_router_canary_observation(
        keypair=kp(3),
        action=RouterCanaryAction.PUBLIC_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        frame_digest=d("fork-frame"),
        sam_canary_digest=sam.report_digest,
        router_harness_digest=harness.report_digest,
        outbox_drain_digest=drain.report_digest,
        session_id="sess",
        destination="abc.b32.i2p",
        sam_endpoint="127.0.0.1:7656",
        router_profile_digest=ROUTER_PROFILE,
        router_ready=True,
        destination_persistent=True,
        transit_enabled=True,
        http_proxy_enabled=False,
        socks_proxy_enabled=False,
        sequence=0,
        issued_at=NOW + 1,
        expires_at=NOW + 301,
        family_id="family-c",
        path_family="path-c",
    )
    report = assess_good_router(observations=(observations[0], fork), sam=sam, harness=harness, drain=drain)
    assert report.decision_kind is RouterCanaryDecisionKind.QUARANTINE_SEQUENCE_FORK


def ingress_components():
    return component("ingress-gate"), component("service-ticket"), component("load-sheath"), component("continuity")


def ingress_receipts(*, phases=(IngressDrainPhase.ACCEPT_WORK, IngressDrainPhase.COMPLETE_WORK), metadata=(1, 1)):
    gate, ticket, load, continuity = ingress_components()
    receipts = []
    prev = ZERO_DIGEST
    for idx, phase in enumerate(phases):
        receipt = make_ingress_drain_receipt(
            keypair=kp(10 + idx),
            phase=phase,
            profile_id=PROFILE,
            service_name=SERVICE,
            scope_digest=SCOPE,
            request_digest=REQUEST,
            caller_digest=CALLER,
            handler_digest=HANDLER,
            ingress_gate_digest=gate.report_digest,
            service_ticket_digest=ticket.report_digest,
            load_sheath_digest=load.report_digest,
            continuity_digest=continuity.report_digest,
            ingress_request_digest=INGRESS_REQUEST,
            metadata_units=metadata[idx],
            refusal_reason_digest=d("refusal") if phase is IngressDrainPhase.USEFUL_REFUSAL else ZERO_DIGEST,
            sequence=idx,
            previous_receipt_digest=prev,
            issued_at=NOW + idx,
            expires_at=NOW + 300 + idx,
            family_id=f"family-{idx}",
            path_family=f"path-{idx}",
        )
        receipts.append(receipt)
        prev = receipt.receipt_digest
    return tuple(receipts), gate, ticket, load, continuity


def assess_good_ingress(*, receipts=None, gate=None, ticket=None, load=None, continuity=None, max_metadata_units: int = 8, previous_refusal_streak: int = 0):
    if receipts is None:
        receipts, gate, ticket, load, continuity = ingress_receipts()
    return assess_ingress_drain(
        receipts,
        ingress_gate_report=gate,
        service_ticket_report=ticket,
        load_sheath_report=load,
        continuity_report=continuity,
        now=NOW + 2,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_caller_digest=CALLER,
        expected_handler_digest=HANDLER,
        expected_ingress_request_digest=INGRESS_REQUEST,
        max_metadata_units=max_metadata_units,
        previous_refusal_streak=previous_refusal_streak,
    )


def test_ingress_drain_accepts_complete_work_with_diverse_receipts() -> None:
    report = assess_good_ingress()
    assert report.decision_kind is IngressDrainDecisionKind.ACCEPT_INGRESS_DRAIN
    assert report.accept
    assert report.metadata_units == 2


def test_ingress_drain_rejects_metadata_budget_overrun() -> None:
    receipts, gate, ticket, load, continuity = ingress_receipts(metadata=(4, 5))
    report = assess_good_ingress(receipts=receipts, gate=gate, ticket=ticket, load=load, continuity=continuity, max_metadata_units=8)
    assert report.decision_kind is IngressDrainDecisionKind.QUARANTINE_METADATA_BUDGET


def test_ingress_drain_rejects_completion_after_useful_refusal() -> None:
    receipts, gate, ticket, load, continuity = ingress_receipts(phases=(IngressDrainPhase.USEFUL_REFUSAL, IngressDrainPhase.COMPLETE_WORK))
    report = assess_good_ingress(receipts=receipts, gate=gate, ticket=ticket, load=load, continuity=continuity)
    assert report.decision_kind is IngressDrainDecisionKind.QUARANTINE_COMPLETION_AFTER_REFUSAL


def test_ingress_drain_holds_refusal_only_loop() -> None:
    receipts, gate, ticket, load, continuity = ingress_receipts(phases=(IngressDrainPhase.USEFUL_REFUSAL, IngressDrainPhase.USEFUL_REFUSAL))
    report = assess_good_ingress(receipts=receipts, gate=gate, ticket=ticket, load=load, continuity=continuity, previous_refusal_streak=1)
    assert report.decision_kind is IngressDrainDecisionKind.HOLD_REFUSAL_ONLY_LOOP


def test_ingress_drain_rejects_component_digest_drift() -> None:
    receipts, gate, ticket, load, continuity = ingress_receipts()
    bad_ticket = component("service-ticket-other")
    report = assess_good_ingress(receipts=receipts, gate=gate, ticket=bad_ticket, load=load, continuity=continuity)
    assert report.decision_kind is IngressDrainDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT


def test_redteam_fold_pins_rev0051_current_path() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_redteam_fold(root)
    assert report.status == "pass"
    assert report.error_count == 0
