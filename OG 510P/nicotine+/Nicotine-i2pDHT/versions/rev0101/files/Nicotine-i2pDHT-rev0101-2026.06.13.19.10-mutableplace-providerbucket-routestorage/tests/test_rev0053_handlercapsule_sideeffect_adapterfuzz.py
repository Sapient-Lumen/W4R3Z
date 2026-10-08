from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.adapterfuzz import AdapterFuzzDecisionKind, AdapterFuzzObservation, summarize_adapter_fuzz
from i2p_dht_lab.handlercapsule import (
    HandlerCapsuleDecisionKind,
    HandlerWorkKind,
    assess_handler_capsules,
    make_handler_capsule,
)
from i2p_dht_lab.handlerfold import audit_handler_fold
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.liveadapter import LiveAdapterMode
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.sideeffectjournal import (
    SideEffectAction,
    SideEffectJournalDecisionKind,
    SideEffectPhase,
    action_from_live_adapter_mode,
    assess_side_effect_journal,
    make_side_effect_entry,
)

NOW = 100_000
PROFILE = "profile-rev0053"
SERVICE = "public-bridge-rev0053"
SCOPE = sha256(b"rev0053-scope")
REQUEST = sha256(b"rev0053-request")
PAYLOAD = sha256(b"rev0053-payload")
TARGET = sha256(b"rev0053-side-effect-target")
IDEM = sha256(b"rev0053-idempotency")
CALLER = sha256(b"rev0053-caller")
HANDLER = sha256(b"rev0053-handler")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False):
    return SimpleNamespace(
        report_digest=d(f"{label}:{accept}:{watch}:{quarantined}"),
        transcript_digest=d(f"{label}:transcript:{accept}:{watch}:{quarantined}"),
        canary_digest=d(f"{label}:canary:{accept}:{watch}:{quarantined}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        decision_kind=SimpleNamespace(value="accept_with_watch" if watch else "accept"),
    )


def base_components(*, watch: bool = False):
    return {
        "profile_edge": component("profile-edge", watch=watch),
        "live_adapter": component("live-adapter", watch=watch),
        "ingress": component("ingress-drain", watch=watch),
        "backpressure": component("backpressure", watch=watch),
        "sam_canary": component("sam-canary", watch=watch),
    }


def handler_report(*, payload=PAYLOAD, mode=LiveAdapterMode.INBOUND_HANDLER_WORK, hard=0, metadata=1, raw=0, budget=1, comps=None, allow_watch=False):
    comps = comps or base_components()
    h0 = make_handler_capsule(
        keypair=kp(1),
        mode=mode,
        kind=HandlerWorkKind.PUBLIC_BRIDGE_REQUEST,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        inbound_payload_digest=payload,
        caller_digest=CALLER,
        handler_digest=HANDLER,
        profile_edge_report=comps["profile_edge"],
        live_adapter_report=comps["live_adapter"],
        ingress_drain_report=comps["ingress"],
        backpressure_report=comps["backpressure"],
        metadata_units=metadata,
        handler_budget_units=budget,
        raw_key_units=raw,
        hard_negative_count=hard,
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id="family-a",
        path_family="path-a",
    )
    h1 = make_handler_capsule(
        keypair=kp(2),
        mode=mode,
        kind=HandlerWorkKind.PUBLIC_BRIDGE_REQUEST,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        inbound_payload_digest=payload,
        caller_digest=CALLER,
        handler_digest=HANDLER,
        profile_edge_report=comps["profile_edge"],
        live_adapter_report=comps["live_adapter"],
        ingress_drain_report=comps["ingress"],
        backpressure_report=comps["backpressure"],
        metadata_units=metadata,
        handler_budget_units=budget,
        raw_key_units=raw,
        hard_negative_count=hard,
        sequence=1,
        previous_capsule_digest=h0.capsule_digest,
        issued_at=NOW + 1,
        expires_at=NOW + 301,
        family_id="family-b",
        path_family="path-b",
    )
    report = assess_handler_capsules(
        (h0, h1),
        profile_edge_report=comps["profile_edge"],
        live_adapter_report=comps["live_adapter"],
        ingress_drain_report=comps["ingress"],
        backpressure_report=comps["backpressure"],
        now=NOW + 2,
        expected_mode=mode,
        expected_kind=HandlerWorkKind.PUBLIC_BRIDGE_REQUEST,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_inbound_payload_digest=PAYLOAD,
        expected_caller_digest=CALLER,
        expected_handler_digest=HANDLER,
        max_metadata_units=4,
        max_handler_budget_units=4,
        max_raw_key_units=1,
        allow_component_watch=allow_watch,
    )
    return report, (h0, h1), comps


def test_handler_capsule_accepts_inbound_exact_boundary() -> None:
    report, _capsules, _comps = handler_report()
    assert report.decision_kind is HandlerCapsuleDecisionKind.ACCEPT_HANDLER_CAPSULE
    assert report.accept
    assert report.family_count == 2
    assert report.path_family_count == 2


def test_handler_capsule_rejects_outbound_mode_and_payload_drift() -> None:
    outbound, _capsules, _ = handler_report(mode=LiveAdapterMode.OUTBOUND_PUBLIC_SEND)
    assert outbound.decision_kind is HandlerCapsuleDecisionKind.QUARANTINE_MODE_COMPONENT_MISMATCH
    drift, _capsules, _ = handler_report(payload=d("payload-drift"))
    assert drift.decision_kind is HandlerCapsuleDecisionKind.QUARANTINE_PAYLOAD_DRIFT


def test_handler_capsule_rejects_component_drift_and_budget_pressure() -> None:
    good, capsules, comps = handler_report()
    assert good.accept
    drift_comps = dict(comps)
    drift_comps["live_adapter"] = component("live-adapter-other")
    drift = assess_handler_capsules(
        capsules,
        profile_edge_report=drift_comps["profile_edge"],
        live_adapter_report=drift_comps["live_adapter"],
        ingress_drain_report=drift_comps["ingress"],
        backpressure_report=drift_comps["backpressure"],
        now=NOW + 2,
        expected_mode=LiveAdapterMode.INBOUND_HANDLER_WORK,
        expected_kind=HandlerWorkKind.PUBLIC_BRIDGE_REQUEST,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_inbound_payload_digest=PAYLOAD,
        expected_caller_digest=CALLER,
        expected_handler_digest=HANDLER,
        max_metadata_units=4,
        max_handler_budget_units=4,
        max_raw_key_units=1,
    )
    assert drift.decision_kind is HandlerCapsuleDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT
    metadata, _capsules, _ = handler_report(metadata=3)
    assert metadata.decision_kind is HandlerCapsuleDecisionKind.QUARANTINE_METADATA_BUDGET
    hard, _capsules, _ = handler_report(hard=1)
    assert hard.decision_kind is HandlerCapsuleDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE


def test_handler_capsule_watch_must_be_carried_explicitly() -> None:
    comps = base_components(watch=True)
    report, _capsules, _ = handler_report(comps=comps)
    assert report.decision_kind is HandlerCapsuleDecisionKind.HOLD_COMPONENT_WATCH
    carried, _capsules, _ = handler_report(comps=comps, allow_watch=True)
    assert carried.decision_kind is HandlerCapsuleDecisionKind.ACCEPT_WITH_WATCH
    assert carried.accept and carried.watch


def side_effect_report(*, phase2=SideEffectPhase.COMMIT, payload=PAYLOAD, idem=IDEM, target=TARGET, hard=0, comps=None, handler=None, allow_watch=False):
    comps = comps or base_components()
    if handler is None:
        handler, _capsules, _ = handler_report(comps=comps, allow_watch=allow_watch)
    e0 = make_side_effect_entry(
        keypair=kp(3),
        phase=SideEffectPhase.PREPARE,
        action=SideEffectAction.INBOUND_HANDLER_WORK,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=payload,
        idempotency_key=idem,
        side_effect_target_digest=target,
        profile_edge_report=comps["profile_edge"],
        live_adapter_report=comps["live_adapter"],
        handler_capsule_report=handler,
        hard_negative_count=hard,
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id="family-a",
        path_family="path-a",
    )
    e1 = make_side_effect_entry(
        keypair=kp(4),
        phase=phase2,
        action=SideEffectAction.INBOUND_HANDLER_WORK,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=payload,
        idempotency_key=idem,
        side_effect_target_digest=target,
        profile_edge_report=comps["profile_edge"],
        live_adapter_report=comps["live_adapter"],
        handler_capsule_report=handler,
        hard_negative_count=hard,
        sequence=1,
        previous_entry_digest=e0.entry_digest,
        issued_at=NOW + 1,
        expires_at=NOW + 301,
        family_id="family-b",
        path_family="path-b",
    )
    report = assess_side_effect_journal(
        (e0, e1),
        profile_edge_report=comps["profile_edge"],
        live_adapter_report=comps["live_adapter"],
        handler_capsule_report=handler,
        now=NOW + 2,
        expected_action=SideEffectAction.INBOUND_HANDLER_WORK,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD,
        expected_idempotency_key=IDEM,
        expected_side_effect_target_digest=TARGET,
        allow_component_watch=allow_watch,
    )
    return report, (e0, e1), comps, handler


def test_side_effect_journal_accepts_prepare_commit_for_handler() -> None:
    report, _entries, _comps, _handler = side_effect_report()
    assert report.decision_kind is SideEffectJournalDecisionKind.ACCEPT_COMMIT
    assert report.accept
    assert report.final_phase is SideEffectPhase.COMMIT
    assert action_from_live_adapter_mode(LiveAdapterMode.INBOUND_HANDLER_WORK) is SideEffectAction.INBOUND_HANDLER_WORK


def test_side_effect_journal_rejects_phase_regression_and_idempotency_conflict() -> None:
    comps = base_components()
    handler, _capsules, _ = handler_report(comps=comps)
    commit = make_side_effect_entry(keypair=kp(5), phase=SideEffectPhase.COMMIT, action=SideEffectAction.INBOUND_HANDLER_WORK, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, side_effect_target_digest=TARGET, profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], handler_capsule_report=handler, hard_negative_count=0, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    prepare = make_side_effect_entry(keypair=kp(6), phase=SideEffectPhase.PREPARE, action=SideEffectAction.INBOUND_HANDLER_WORK, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, side_effect_target_digest=TARGET, profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], handler_capsule_report=handler, hard_negative_count=0, sequence=1, previous_entry_digest=commit.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    phase = assess_side_effect_journal((commit, prepare), profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], handler_capsule_report=handler, now=NOW + 2, expected_action=SideEffectAction.INBOUND_HANDLER_WORK, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, expected_idempotency_key=IDEM, expected_side_effect_target_digest=TARGET)
    assert phase.decision_kind is SideEffectJournalDecisionKind.QUARANTINE_PHASE_REGRESSION

    good, entries, comps, handler = side_effect_report()
    assert good.accept
    conflict = replace(entries[1], side_effect_target_digest=d("other-target"))
    # Re-sign the changed entry so the conflict detector, not signature validation, is what fires.
    conflict = replace(conflict, signature=kp(4).sign(conflict.signature_payload()))
    conflict_report = assess_side_effect_journal((entries[0], conflict), profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], handler_capsule_report=handler, now=NOW + 2, expected_action=SideEffectAction.INBOUND_HANDLER_WORK, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, expected_idempotency_key=IDEM, expected_side_effect_target_digest=TARGET)
    assert conflict_report.decision_kind is SideEffectJournalDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT


def test_side_effect_journal_holds_missing_sam_for_outbound_and_hard_negative() -> None:
    comps = base_components()
    outbound = make_side_effect_entry(keypair=kp(7), phase=SideEffectPhase.PREPARE, action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, side_effect_target_digest=TARGET, profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], hard_negative_count=0, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    report = assess_side_effect_journal((outbound,), profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], now=NOW + 1, expected_action=SideEffectAction.OUTBOUND_PUBLIC_SEND, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, expected_idempotency_key=IDEM, expected_side_effect_target_digest=TARGET, min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SideEffectJournalDecisionKind.HOLD_SAM_CANARY
    hard, _entries, _comps, _handler = side_effect_report(hard=1)
    assert hard.decision_kind is SideEffectJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE


def test_adapter_fuzz_accepts_required_quarantine_coverage() -> None:
    handler_payload, *_ = handler_report(payload=d("payload-drift"))
    side_payload, *_ = side_effect_report(payload=d("payload-drift"))
    obs = (
        AdapterFuzzObservation("handlercapsule", "payload_drift", "quarantine_", handler_payload.decision_kind.value, handler_payload.report_digest, "family-a", "path-a"),
        AdapterFuzzObservation("sideeffectjournal", "payload_drift", "quarantine_", side_payload.decision_kind.value, side_payload.report_digest, "family-b", "path-b"),
        AdapterFuzzObservation("handlercapsule", "component_drift", "quarantine_", d("fake-quarantine" ).hex()[:0] + "quarantine_component_digest_drift", d("component-drift"), "family-c", "path-c"),
    )
    report = summarize_adapter_fuzz(obs, required_mutations=("payload_drift", "component_drift"), min_surface_count=2)
    assert report.decision_kind is AdapterFuzzDecisionKind.ACCEPT_FUZZ_COVERAGE
    assert report.accept


def test_adapter_fuzz_quarantines_unexpected_accept_and_missing_mutation() -> None:
    obs = (AdapterFuzzObservation("handlercapsule", "payload_drift", "quarantine_", "accept_handler_capsule", d("bad"), "family-a", "path-a"),)
    bad = summarize_adapter_fuzz(obs, required_mutations=("payload_drift",), min_surface_count=1)
    assert bad.decision_kind is AdapterFuzzDecisionKind.QUARANTINE_UNEXPECTED_ACCEPT
    missing = summarize_adapter_fuzz(obs, required_mutations=("payload_drift", "request_drift"), min_surface_count=1)
    assert missing.decision_kind is AdapterFuzzDecisionKind.HOLD_MISSING_MUTATION


def test_handlerfold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_handler_fold(root, revision="rev0053", artifact_stem=root.name)
    assert report.status == "pass"
