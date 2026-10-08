from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.backpressuremesh import (
    BackpressureDecisionKind,
    BackpressureMode,
    assess_backpressure_mesh,
    make_backpressure_observation,
)
from i2p_dht_lab.edgefold import audit_edge_fold
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.liveadapter import (
    LiveAdapterDecisionKind,
    LiveAdapterMode,
    assess_live_adapter,
    make_live_adapter_plan,
)
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.profileedge import (
    ProfileEdgeDecisionKind,
    assess_profile_edge,
    make_profile_edge_capsule,
)

NOW = 90_000
PROFILE = "profile-rev0052"
SERVICE = "public-bridge-rev0052"
SCOPE = sha256(b"rev0052-scope")
REQUEST = sha256(b"rev0052-request")
PAYLOAD = sha256(b"rev0052-payload")
FRAME = sha256(b"rev0052-frame")
CALLER = sha256(b"rev0052-caller")
HANDLER = sha256(b"rev0052-handler")
SESSION = "sess-rev0052"
DESTINATION = "rev0052-dest.b32.i2p"


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, mode=None):
    return SimpleNamespace(
        report_digest=d(f"{label}:{accept}:{watch}:{quarantined}:{mode}"),
        transcript_digest=d(f"{label}:transcript:{accept}:{watch}:{quarantined}:{mode}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        mode=mode,
        decision_kind=SimpleNamespace(value="accept_with_watch" if watch else "accept"),
    )


def backpressure_reports(*, mode=BackpressureMode.BIDIRECTIONAL, hard_negatives=0, reserve=2, refusal=0, raw=1, units=(2, 2, 1)):
    router = component("router-canary")
    ingress = component("ingress-drain")
    o0 = make_backpressure_observation(
        keypair=kp(1),
        mode=mode,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        router_canary_report=router,
        ingress_drain_report=ingress,
        inbound_units=units[0],
        outbound_units=units[1],
        router_units=units[2],
        protected_reserve_units=reserve,
        raw_key_units=raw,
        useful_refusal_streak=refusal,
        hard_negative_count=hard_negatives,
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id="family-a",
        path_family="path-a",
    )
    o1 = make_backpressure_observation(
        keypair=kp(2),
        mode=mode,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        router_canary_report=router,
        ingress_drain_report=ingress,
        inbound_units=units[0],
        outbound_units=units[1],
        router_units=units[2],
        protected_reserve_units=reserve,
        raw_key_units=raw,
        useful_refusal_streak=refusal,
        hard_negative_count=hard_negatives,
        sequence=1,
        previous_observation_digest=o0.observation_digest,
        issued_at=NOW + 1,
        expires_at=NOW + 301,
        family_id="family-b",
        path_family="path-b",
    )
    report = assess_backpressure_mesh(
        (o0, o1),
        router_canary_report=router,
        ingress_drain_report=ingress,
        now=NOW + 2,
        expected_mode=mode,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        max_total_units=20,
        max_raw_key_units=5,
        protected_reserve_floor=1,
    )
    return report, router, ingress, (o0, o1)


def live_adapter_report(*, mode=LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK, backpressure=None, router=None, ingress=None, effect=None, payload=PAYLOAD, frame=FRAME):
    if backpressure is None:
        bp_mode = {
            LiveAdapterMode.OUTBOUND_PUBLIC_SEND: BackpressureMode.OUTBOUND,
            LiveAdapterMode.INBOUND_HANDLER_WORK: BackpressureMode.INBOUND,
            LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK: BackpressureMode.BIDIRECTIONAL,
        }[mode]
        backpressure, router, ingress, _ = backpressure_reports(mode=bp_mode)
    effect = effect or component("effect-ledger")
    router_arg = router if mode in (LiveAdapterMode.OUTBOUND_PUBLIC_SEND, LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK) else None
    ingress_arg = ingress if mode in (LiveAdapterMode.INBOUND_HANDLER_WORK, LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK) else None
    effect_arg = effect if mode in (LiveAdapterMode.OUTBOUND_PUBLIC_SEND, LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK) else None
    p0 = make_live_adapter_plan(
        keypair=kp(3),
        mode=mode,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        public_payload_digest=payload,
        frame_digest=frame,
        session_id=SESSION,
        destination=DESTINATION,
        caller_digest=CALLER,
        handler_digest=HANDLER,
        router_canary_report=router_arg,
        ingress_drain_report=ingress_arg,
        backpressure_report=backpressure,
        effect_ledger_report=effect_arg,
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id="family-a",
        path_family="path-a",
    )
    p1 = make_live_adapter_plan(
        keypair=kp(4),
        mode=mode,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        public_payload_digest=payload,
        frame_digest=frame,
        session_id=SESSION,
        destination=DESTINATION,
        caller_digest=CALLER,
        handler_digest=HANDLER,
        router_canary_report=router_arg,
        ingress_drain_report=ingress_arg,
        backpressure_report=backpressure,
        effect_ledger_report=effect_arg,
        sequence=1,
        previous_plan_digest=p0.plan_digest,
        issued_at=NOW + 1,
        expires_at=NOW + 301,
        family_id="family-b",
        path_family="path-b",
    )
    report = assess_live_adapter(
        (p0, p1),
        router_canary_report=router_arg,
        ingress_drain_report=ingress_arg,
        backpressure_report=backpressure,
        effect_ledger_report=effect_arg,
        now=NOW + 2,
        expected_mode=mode,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        expected_frame_digest=FRAME,
        expected_session_id=SESSION,
        expected_destination=DESTINATION,
        expected_caller_digest=CALLER,
        expected_handler_digest=HANDLER,
    )
    return report, backpressure, router_arg, ingress_arg, effect_arg, (p0, p1)


def profile_edge_report(*, mode=LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK, hard_negatives=0, budget=3, profile_generation=3, service_generation=5, live=None, backpressure=None, router=None, ingress=None):
    if live is None:
        live, backpressure, router, ingress, _effect, _plans = live_adapter_report(mode=mode)
    profile_budget = component("profile-budget")
    negative_scan = component("negative-scan")
    c0 = make_profile_edge_capsule(
        keypair=kp(5),
        mode=mode,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        public_payload_digest=PAYLOAD,
        live_adapter_report=live,
        backpressure_report=backpressure,
        router_canary_report=router,
        ingress_drain_report=ingress,
        profile_budget_report=profile_budget,
        negative_scan_report=negative_scan,
        profile_generation=profile_generation,
        service_generation=service_generation,
        edge_budget_units=budget,
        hard_negative_count=hard_negatives,
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id="family-a",
        path_family="path-a",
    )
    c1 = make_profile_edge_capsule(
        keypair=kp(6),
        mode=mode,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        public_payload_digest=PAYLOAD,
        live_adapter_report=live,
        backpressure_report=backpressure,
        router_canary_report=router,
        ingress_drain_report=ingress,
        profile_budget_report=profile_budget,
        negative_scan_report=negative_scan,
        profile_generation=profile_generation,
        service_generation=service_generation,
        edge_budget_units=budget,
        hard_negative_count=hard_negatives,
        sequence=1,
        previous_capsule_digest=c0.capsule_digest,
        issued_at=NOW + 1,
        expires_at=NOW + 301,
        family_id="family-b",
        path_family="path-b",
    )
    report = assess_profile_edge(
        (c0, c1),
        live_adapter_report=live,
        backpressure_report=backpressure,
        router_canary_report=router,
        ingress_drain_report=ingress,
        profile_budget_report=profile_budget,
        negative_scan_report=negative_scan,
        now=NOW + 2,
        expected_mode=mode,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        min_profile_generation=3,
        min_service_generation=5,
        max_total_edge_budget_units=10,
    )
    return report, (c0, c1)


def test_backpressure_accepts_diverse_bidirectional_budget() -> None:
    report, _router, _ingress, _obs = backpressure_reports()
    assert report.decision_kind is BackpressureDecisionKind.ACCEPT_BACKPRESSURE
    assert report.accept
    assert report.family_count == 2
    assert report.path_family_count == 2


def test_backpressure_sheds_bulk_before_it_quarantines() -> None:
    report, *_ = backpressure_reports(units=(4, 3, 1), refusal=1)
    assert report.decision_kind is BackpressureDecisionKind.ACCEPT_WITH_SHED_BULK
    assert report.accept and report.shed_bulk and report.watch


def test_backpressure_rejects_starved_reserve_and_hard_negative() -> None:
    starved, *_ = backpressure_reports(reserve=0)
    assert starved.decision_kind is BackpressureDecisionKind.QUARANTINE_PROTECTED_RESERVE_STARVED
    hard, *_ = backpressure_reports(hard_negatives=1)
    assert hard.decision_kind is BackpressureDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE


def test_backpressure_rejects_raw_key_budget() -> None:
    report, *_ = backpressure_reports(raw=4)
    assert report.decision_kind is BackpressureDecisionKind.QUARANTINE_METADATA_BUDGET


def test_live_adapter_accepts_bidirectional_bridge_tick() -> None:
    report, *_ = live_adapter_report()
    assert report.decision_kind is LiveAdapterDecisionKind.ACCEPT_LIVE_ADAPTER
    assert report.accept


def test_live_adapter_outbound_cannot_carry_ingress_digest() -> None:
    bp, router, ingress, _ = backpressure_reports(mode=BackpressureMode.OUTBOUND)
    effect = component("effect-ledger")
    plan = make_live_adapter_plan(
        keypair=kp(7),
        mode=LiveAdapterMode.OUTBOUND_PUBLIC_SEND,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        public_payload_digest=PAYLOAD,
        frame_digest=FRAME,
        session_id=SESSION,
        destination=DESTINATION,
        caller_digest=CALLER,
        handler_digest=HANDLER,
        router_canary_report=router,
        ingress_drain_report=ingress,
        backpressure_report=bp,
        effect_ledger_report=effect,
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id="family-a",
        path_family="path-a",
    )
    report = assess_live_adapter(
        (plan,),
        router_canary_report=router,
        ingress_drain_report=None,
        backpressure_report=bp,
        effect_ledger_report=effect,
        now=NOW + 1,
        expected_mode=LiveAdapterMode.OUTBOUND_PUBLIC_SEND,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        expected_frame_digest=FRAME,
        expected_session_id=SESSION,
        expected_destination=DESTINATION,
        expected_caller_digest=CALLER,
        expected_handler_digest=HANDLER,
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is LiveAdapterDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT


def test_live_adapter_rejects_backpressure_mode_mismatch_and_frame_drift() -> None:
    bp, router, ingress, _ = backpressure_reports(mode=BackpressureMode.INBOUND)
    report, *_ = live_adapter_report(mode=LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK, backpressure=bp, router=router, ingress=ingress)
    assert report.decision_kind is LiveAdapterDecisionKind.QUARANTINE_BACKPRESSURE_MODE
    drift, *_ = live_adapter_report(frame=d("other-frame"))
    assert drift.decision_kind is LiveAdapterDecisionKind.QUARANTINE_FRAME_DRIFT


def test_live_adapter_rejects_same_sequence_fork() -> None:
    good, bp, router, ingress, effect, plans = live_adapter_report()
    assert good.accept
    fork = replace(plans[0], public_payload_digest=d("fork-payload"))
    report = assess_live_adapter(
        (plans[0], fork),
        router_canary_report=router,
        ingress_drain_report=ingress,
        backpressure_report=bp,
        effect_ledger_report=effect,
        now=NOW + 2,
        expected_mode=LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        expected_frame_digest=FRAME,
        expected_session_id=SESSION,
        expected_destination=DESTINATION,
        expected_caller_digest=CALLER,
        expected_handler_digest=HANDLER,
    )
    assert report.decision_kind is LiveAdapterDecisionKind.QUARANTINE_BAD_SIGNATURE


def test_profile_edge_accepts_joined_public_boundary() -> None:
    report, _capsules = profile_edge_report()
    assert report.decision_kind is ProfileEdgeDecisionKind.ACCEPT_PROFILE_EDGE
    assert report.accept


def test_profile_edge_rejects_hard_negative_and_generation_rollback() -> None:
    hard, _ = profile_edge_report(hard_negatives=1)
    assert hard.decision_kind is ProfileEdgeDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE
    old, _ = profile_edge_report(profile_generation=2)
    assert old.decision_kind is ProfileEdgeDecisionKind.QUARANTINE_GENERATION_ROLLBACK


def test_profile_edge_rejects_total_budget_and_component_watch_without_carry() -> None:
    budget, _ = profile_edge_report(budget=6)
    assert budget.decision_kind is ProfileEdgeDecisionKind.QUARANTINE_EDGE_BUDGET_EXCEEDED
    watched_live = component("live-adapter", watch=True)
    backpressure = component("backpressure", mode=BackpressureMode.BIDIRECTIONAL)
    router = component("router")
    ingress = component("ingress")
    report, _ = profile_edge_report(live=watched_live, backpressure=backpressure, router=router, ingress=ingress)
    assert report.decision_kind is ProfileEdgeDecisionKind.HOLD_COMPONENT_WATCH


def test_edgefold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_edge_fold(root, revision="rev0052", artifact_stem=root.name)
    assert report.status == "pass"
