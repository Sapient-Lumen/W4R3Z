from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.adapterfuzz import AdapterFuzzDecisionKind, AdapterFuzzObservation, summarize_adapter_fuzz
from i2p_dht_lab.fuzzledger import FuzzLedgerDecisionKind, assess_fuzz_ledger, make_fuzz_ledger_entry
from i2p_dht_lab.handlercapsule import HandlerCapsuleDecisionKind, HandlerWorkKind, assess_handler_capsules, make_handler_capsule
from i2p_dht_lab.handlerquench import HandlerAttemptObservation, HandlerQuenchDecisionKind, assess_handler_quench
from i2p_dht_lab.handlerreplay import HandlerReplayDecisionKind, ReplayLane, assess_handler_replay, make_handler_replay_frame
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.liveadapter import LiveAdapterMode
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.replayfold import audit_replay_fold
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectJournalDecisionKind, SideEffectPhase, assess_side_effect_journal, make_side_effect_entry

NOW = 120_000
PROFILE = "profile-rev0054"
SERVICE = "public-bridge-rev0054"
SCOPE = sha256(b"rev0054-scope")
REQUEST = sha256(b"rev0054-request")
PAYLOAD = sha256(b"rev0054-payload")
CALLER = sha256(b"rev0054-caller")
HANDLER = sha256(b"rev0054-handler")
TARGET = sha256(b"rev0054-target")
IDEM = sha256(b"rev0054-idem")
GENERATOR = sha256(b"rev0054-deterministic-generator")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False):
    return SimpleNamespace(report_digest=d(f"{label}:{accept}:{watch}:{quarantined}"), transcript_digest=d(f"{label}:transcript:{accept}:{watch}:{quarantined}"), canary_digest=d(f"{label}:canary:{accept}:{watch}:{quarantined}"), accept=accept, watch=watch, quarantined=quarantined, decision_kind=SimpleNamespace(value="accept_with_watch" if watch else "accept"))


def base_components(*, watch: bool = False):
    return {
        "profile_edge": component("profile-edge", watch=watch),
        "live_adapter": component("live-adapter", watch=watch),
        "ingress": component("ingress", watch=watch),
        "backpressure": component("backpressure", watch=watch),
    }


def handler_report(*, comps=None, allow_watch=False, payload=PAYLOAD):
    comps = comps or base_components()
    h0 = make_handler_capsule(keypair=kp(1), mode=LiveAdapterMode.INBOUND_HANDLER_WORK, kind=HandlerWorkKind.PUBLIC_BRIDGE_REQUEST, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, inbound_payload_digest=payload, caller_digest=CALLER, handler_digest=HANDLER, profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], ingress_drain_report=comps["ingress"], backpressure_report=comps["backpressure"], metadata_units=1, handler_budget_units=1, raw_key_units=0, hard_negative_count=0, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    h1 = make_handler_capsule(keypair=kp(2), mode=LiveAdapterMode.INBOUND_HANDLER_WORK, kind=HandlerWorkKind.PUBLIC_BRIDGE_REQUEST, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, inbound_payload_digest=payload, caller_digest=CALLER, handler_digest=HANDLER, profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], ingress_drain_report=comps["ingress"], backpressure_report=comps["backpressure"], metadata_units=1, handler_budget_units=1, raw_key_units=0, hard_negative_count=0, sequence=1, previous_capsule_digest=h0.capsule_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    report = assess_handler_capsules((h0, h1), profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], ingress_drain_report=comps["ingress"], backpressure_report=comps["backpressure"], now=NOW + 2, expected_mode=LiveAdapterMode.INBOUND_HANDLER_WORK, expected_kind=HandlerWorkKind.PUBLIC_BRIDGE_REQUEST, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_inbound_payload_digest=PAYLOAD, expected_caller_digest=CALLER, expected_handler_digest=HANDLER, max_metadata_units=4, max_handler_budget_units=4, max_raw_key_units=1, allow_component_watch=allow_watch)
    return report, comps


def side_effect_report(*, handler=None, comps=None, allow_watch=False):
    comps = comps or base_components()
    if handler is None:
        handler, comps = handler_report(comps=comps)
    e0 = make_side_effect_entry(keypair=kp(3), phase=SideEffectPhase.PREPARE, action=SideEffectAction.INBOUND_HANDLER_WORK, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, side_effect_target_digest=TARGET, profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], handler_capsule_report=handler, hard_negative_count=0, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    e1 = make_side_effect_entry(keypair=kp(4), phase=SideEffectPhase.COMMIT, action=SideEffectAction.INBOUND_HANDLER_WORK, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, side_effect_target_digest=TARGET, profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], handler_capsule_report=handler, hard_negative_count=0, sequence=1, previous_entry_digest=e0.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    report = assess_side_effect_journal((e0, e1), profile_edge_report=comps["profile_edge"], live_adapter_report=comps["live_adapter"], handler_capsule_report=handler, now=NOW + 2, expected_action=SideEffectAction.INBOUND_HANDLER_WORK, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, expected_idempotency_key=IDEM, expected_side_effect_target_digest=TARGET, allow_component_watch=allow_watch)
    return report


def fuzz_report(*, watch=False):
    report = summarize_adapter_fuzz((
        AdapterFuzzObservation("handlercapsule", "payload_drift", "quarantine_", "quarantine_payload_drift", d("fuzz-handler"), "family-a", "path-a"),
        AdapterFuzzObservation("sideeffectjournal", "idempotency_conflict", "quarantine_", "quarantine_idempotency_conflict", d("fuzz-journal"), "family-b", "path-b"),
    ), required_mutations=("payload_drift", "idempotency_conflict"), min_surface_count=2)
    assert report.decision_kind is AdapterFuzzDecisionKind.ACCEPT_FUZZ_COVERAGE
    if watch:
        return replace(report, watch=True)
    return report


def replay_frames(handler, journal, fuzz=None):
    r0 = make_handler_replay_frame(keypair=kp(5), lane=ReplayLane.HANDLER_CAPSULE, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=handler, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    r1 = make_handler_replay_frame(keypair=kp(6), lane=ReplayLane.SIDE_EFFECT_JOURNAL, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=journal, sequence=1, previous_frame_digest=r0.frame_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    if fuzz is None:
        return (r0, r1)
    r2 = make_handler_replay_frame(keypair=kp(7), lane=ReplayLane.ADAPTER_FUZZ, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=fuzz, sequence=2, previous_frame_digest=r1.frame_digest, issued_at=NOW + 2, expires_at=NOW + 302, family_id="family-c", path_family="path-c")
    return (r0, r1, r2)


def test_handler_replay_accepts_restart_window_with_all_lanes() -> None:
    handler, comps = handler_report()
    journal = side_effect_report(handler=handler, comps=comps)
    fuzz = fuzz_report()
    report = assess_handler_replay(replay_frames(handler, journal, fuzz), component_reports={ReplayLane.HANDLER_CAPSULE: handler, ReplayLane.SIDE_EFFECT_JOURNAL: journal, ReplayLane.ADAPTER_FUZZ: fuzz}, now=NOW + 3, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_lanes=(ReplayLane.HANDLER_CAPSULE, ReplayLane.SIDE_EFFECT_JOURNAL, ReplayLane.ADAPTER_FUZZ))
    assert report.decision_kind is HandlerReplayDecisionKind.ACCEPT_REPLAY_WINDOW
    assert report.accept
    assert report.family_count == 3


def test_handler_replay_rejects_replay_previous_mismatch_and_component_drift() -> None:
    handler, comps = handler_report()
    journal = side_effect_report(handler=handler, comps=comps, allow_watch=True)
    frames = replay_frames(handler, journal)
    replay = assess_handler_replay(frames, component_reports={ReplayLane.HANDLER_CAPSULE: handler, ReplayLane.SIDE_EFFECT_JOURNAL: journal}, now=NOW + 3, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previous_seen_frame_digests=(frames[0].frame_digest,))
    assert replay.decision_kind is HandlerReplayDecisionKind.QUARANTINE_REPLAY
    bad_prev = (frames[0], replace(frames[1], previous_frame_digest=ZERO_DIGEST, signature=kp(6).sign(replace(frames[1], previous_frame_digest=ZERO_DIGEST, signature=b"").signature_payload())))
    prev = assess_handler_replay(bad_prev, component_reports={ReplayLane.HANDLER_CAPSULE: handler, ReplayLane.SIDE_EFFECT_JOURNAL: journal}, now=NOW + 3, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert prev.decision_kind is HandlerReplayDecisionKind.QUARANTINE_PREVIOUS_MISMATCH
    other_handler = replace(handler, report_digest=d("other-handler-report"))
    drift = assess_handler_replay(frames, component_reports={ReplayLane.HANDLER_CAPSULE: other_handler, ReplayLane.SIDE_EFFECT_JOURNAL: journal}, now=NOW + 3, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert drift.decision_kind is HandlerReplayDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT


def test_handler_replay_watch_must_be_carried_after_restart() -> None:
    comps = base_components(watch=True)
    handler, comps = handler_report(comps=comps, allow_watch=True)
    journal = side_effect_report(handler=handler, comps=comps, allow_watch=True)
    frames = replay_frames(handler, journal)
    held = assess_handler_replay(frames, component_reports={ReplayLane.HANDLER_CAPSULE: handler, ReplayLane.SIDE_EFFECT_JOURNAL: journal}, now=NOW + 3, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert held.decision_kind is HandlerReplayDecisionKind.HOLD_COMPONENT_WATCH
    carried = assess_handler_replay(frames, component_reports={ReplayLane.HANDLER_CAPSULE: handler, ReplayLane.SIDE_EFFECT_JOURNAL: journal}, now=NOW + 3, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, allow_component_watch=True)
    assert carried.decision_kind is HandlerReplayDecisionKind.ACCEPT_WITH_WATCH


def obs(n: int, *, decision="accept_handler_capsule", family=None, path=None, raw=0, refusal=False, hard=0, request=REQUEST):
    return HandlerAttemptObservation(decision, PROFILE, SERVICE, SCOPE, request, CALLER, HANDLER, d(f"obs-{n}-{decision}-{family}-{path}-{raw}-{refusal}-{hard}"), metadata_units=1, raw_key_units=raw, useful_refusal=refusal, hard_negative_count=hard, observed_at=NOW + n, family_id=family or f"family-{n}", path_family=path or f"path-{n}")


def test_handler_quench_allows_balanced_window_and_cools_near_misses() -> None:
    allowed = assess_handler_quench((obs(1), obs(2)), now=NOW + 3, window_seconds=30, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_caller_digest=CALLER, expected_handler_digest=HANDLER)
    assert allowed.decision_kind is HandlerQuenchDecisionKind.ALLOW_HANDLER_WINDOW
    loop = assess_handler_quench((obs(1, decision="hold_component_watch"), obs(2, decision="accept_with_watch"), obs(3, decision="hold_low_family_diversity", family="family-c", path="path-c")), now=NOW + 4, window_seconds=30, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_caller_digest=CALLER, expected_handler_digest=HANDLER, max_near_misses=3)
    assert loop.decision_kind is HandlerQuenchDecisionKind.COOLDOWN_ALMOST_PASSING_LOOP
    assert loop.cooldown_until > NOW + 4


def test_handler_quench_rejects_raw_key_replay_and_drift() -> None:
    raw = assess_handler_quench((obs(1, raw=1), obs(2, raw=1)), now=NOW + 3, window_seconds=30, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_caller_digest=CALLER, expected_handler_digest=HANDLER, max_raw_key_units=1)
    assert raw.decision_kind is HandlerQuenchDecisionKind.QUENCH_RAW_KEY_PRESSURE
    replayed = obs(1)
    replay = assess_handler_quench((replayed,), now=NOW + 3, window_seconds=30, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_caller_digest=CALLER, expected_handler_digest=HANDLER, previous_seen_report_digests=(replayed.report_digest,))
    assert replay.decision_kind is HandlerQuenchDecisionKind.QUARANTINE_REPLAY
    drift = assess_handler_quench((obs(1, request=d("wrong-request")), obs(2)), now=NOW + 3, window_seconds=30, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_caller_digest=CALLER, expected_handler_digest=HANDLER)
    assert drift.decision_kind is HandlerQuenchDecisionKind.QUARANTINE_REQUEST_DRIFT


def test_fuzz_ledger_accepts_persistent_coverage_and_rejects_drift() -> None:
    fuzz = fuzz_report()
    f0 = make_fuzz_ledger_entry(keypair=kp(8), fuzz_report=fuzz, generator_digest=GENERATOR, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    f1 = make_fuzz_ledger_entry(keypair=kp(9), fuzz_report=fuzz, generator_digest=GENERATOR, sequence=1, previous_entry_digest=f0.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    report = assess_fuzz_ledger((f0, f1), fuzz_report=fuzz, generator_digest=GENERATOR, now=NOW + 2)
    assert report.decision_kind is FuzzLedgerDecisionKind.ACCEPT_FUZZ_LEDGER
    assert report.accept
    drift = assess_fuzz_ledger((f0, f1), fuzz_report=fuzz, generator_digest=d("other-generator"), now=NOW + 2)
    assert drift.decision_kind is FuzzLedgerDecisionKind.QUARANTINE_GENERATOR_DRIFT
    prev = replace(f1, previous_entry_digest=ZERO_DIGEST)
    prev = replace(prev, signature=kp(9).sign(replace(prev, signature=b"").signature_payload()))
    bad_prev = assess_fuzz_ledger((f0, prev), fuzz_report=fuzz, generator_digest=GENERATOR, now=NOW + 2)
    assert bad_prev.decision_kind is FuzzLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_fuzz_ledger_requires_accepted_fuzz_and_family_diversity() -> None:
    fuzz = fuzz_report()
    bad_fuzz = replace(fuzz, accept=False, watch=True)
    f0 = make_fuzz_ledger_entry(keypair=kp(8), fuzz_report=fuzz, generator_digest=GENERATOR, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    held = assess_fuzz_ledger((f0,), fuzz_report=bad_fuzz, generator_digest=GENERATOR, now=NOW + 2)
    assert held.decision_kind is FuzzLedgerDecisionKind.HOLD_FUZZ_REPORT
    low = assess_fuzz_ledger((f0,), fuzz_report=fuzz, generator_digest=GENERATOR, now=NOW + 2, min_family_count=2)
    assert low.decision_kind is FuzzLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_replayfold_audit_passes_current_path() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_replay_fold(root, revision="rev0054", artifact_stem=root.name)
    assert report.status == "pass"
