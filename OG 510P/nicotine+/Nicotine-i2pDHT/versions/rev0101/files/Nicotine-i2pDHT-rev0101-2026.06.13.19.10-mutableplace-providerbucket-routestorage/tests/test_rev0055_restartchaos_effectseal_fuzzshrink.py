from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.effectseal import EffectSealDecisionKind, assess_effect_seal, make_effect_seal_capsule
from i2p_dht_lab.fuzzshrink import FuzzShrinkCandidate, FuzzShrinkDecisionKind, assess_fuzz_shrink
from i2p_dht_lab.fuzzledger import FuzzLedgerDecisionKind, assess_fuzz_ledger, make_fuzz_ledger_entry
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.restartchaos import RestartChaosDecisionKind, RestartCutLane, assess_restart_chaos, make_restart_chaos_cut
from i2p_dht_lab.restartfold import audit_restart_fold
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectPhase

NOW = 550_000
PROFILE = "rev0055-profile"
SERVICE = "rev0055-public-edge"
SCOPE = sha256(b"rev0055-scope")
REQUEST = sha256(b"rev0055-request")
PAYLOAD = sha256(b"rev0055-payload")
IDEM = sha256(b"rev0055-idempotency")
GENERATOR = sha256(b"rev0055-generator")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, final_phase: SideEffectPhase | None = None, action: SideEffectAction = SideEffectAction.INBOUND_HANDLER_WORK, cooldown_until: int = 0, failing_count: int = 0, required_mutations: tuple[str, ...] = (), observed_mutations: tuple[str, ...] = (), observation_digests: tuple[bytes, ...] = ()):
    return SimpleNamespace(
        report_digest=d(label),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        final_phase=final_phase,
        action=action,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        cooldown_until=cooldown_until,
        failing_count=failing_count,
        required_mutations=required_mutations,
        observed_mutations=observed_mutations,
        observation_digests=observation_digests,
        decision_kind=SimpleNamespace(value="accept" if accept else "hold_component"),
    )


def components():
    handler_replay = component("handler-replay")
    journal = component("side-effect-journal", final_phase=SideEffectPhase.COMMIT)
    quench = component("handler-quench")
    fuzz = component("fuzz-report", required_mutations=("payload_drift", "idempotency_conflict"), observed_mutations=("payload_drift", "idempotency_conflict"), observation_digests=(d("obs-payload"), d("obs-idem")))
    fl0 = make_fuzz_ledger_entry(keypair=kp(31), fuzz_report=fuzz, generator_digest=GENERATOR, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    fl1 = make_fuzz_ledger_entry(keypair=kp(32), fuzz_report=fuzz, generator_digest=GENERATOR, sequence=1, previous_entry_digest=fl0.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    ledger = assess_fuzz_ledger((fl0, fl1), fuzz_report=fuzz, generator_digest=GENERATOR, now=NOW + 2)
    assert ledger.decision_kind is FuzzLedgerDecisionKind.ACCEPT_FUZZ_LEDGER
    return handler_replay, journal, quench, fuzz, ledger


def restart_cuts(handler_replay, journal, quench, ledger):
    c0 = make_restart_chaos_cut(keypair=kp(1), lane=RestartCutLane.HANDLER_REPLAY, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=handler_replay, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    c1 = make_restart_chaos_cut(keypair=kp(2), lane=RestartCutLane.SIDE_EFFECT_JOURNAL, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=journal, phase=SideEffectPhase.COMMIT, sequence=1, previous_cut_digest=c0.cut_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    c2 = make_restart_chaos_cut(keypair=kp(3), lane=RestartCutLane.HANDLER_QUENCH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=quench, sequence=2, previous_cut_digest=c1.cut_digest, issued_at=NOW + 2, expires_at=NOW + 302, family_id="family-c", path_family="path-c")
    c3 = make_restart_chaos_cut(keypair=kp(4), lane=RestartCutLane.FUZZ_LEDGER, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=ledger, sequence=3, previous_cut_digest=c2.cut_digest, issued_at=NOW + 3, expires_at=NOW + 303, family_id="family-d", path_family="path-d")
    return c0, c1, c2, c3


def accepted_restart(handler_replay, journal, quench, ledger):
    report = assess_restart_chaos(restart_cuts(handler_replay, journal, quench, ledger), handler_replay_report=handler_replay, side_effect_journal_report=journal, handler_quench_report=quench, fuzz_ledger_report=ledger, now=NOW + 4, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert report.decision_kind is RestartChaosDecisionKind.ACCEPT_RESTART_COMMITTED
    return report


def shrink_candidates(fuzz_report, ledger):
    return (
        FuzzShrinkCandidate("handlercapsule", "payload_drift", "quarantine_", "quarantine_payload_drift", d("obs-payload"), d("shrunk-payload"), GENERATOR, 100, 7, "family-a", "path-a"),
        FuzzShrinkCandidate("sideeffectjournal", "idempotency_conflict", "quarantine_", "quarantine_idempotency_conflict", d("obs-idem"), d("shrunk-idem"), GENERATOR, 120, 8, "family-b", "path-b"),
    )


def accepted_shrink(fuzz_report, ledger):
    shrink = assess_fuzz_shrink(shrink_candidates(fuzz_report, ledger), fuzz_report=fuzz_report, fuzz_ledger_report=ledger, generator_digest=GENERATOR)
    assert shrink.decision_kind is FuzzShrinkDecisionKind.ACCEPT_SHRUNK_COVERAGE
    assert shrink.saved_units > 0
    return shrink


def accepted_seal(handler_replay, journal, quench, ledger, restart, shrink):
    s0 = make_effect_seal_capsule(keypair=kp(10), side_effect_journal_report=journal, handler_replay_report=handler_replay, handler_quench_report=quench, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, sequence=0, issued_at=NOW + 5, expires_at=NOW + 305, family_id="family-a", path_family="path-a")
    s1 = make_effect_seal_capsule(keypair=kp(11), side_effect_journal_report=journal, handler_replay_report=handler_replay, handler_quench_report=quench, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, sequence=1, previous_seal_digest=s0.seal_digest, issued_at=NOW + 6, expires_at=NOW + 306, family_id="family-b", path_family="path-b")
    seal = assess_effect_seal((s0, s1), handler_replay_report=handler_replay, handler_quench_report=quench, side_effect_journal_report=journal, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, now=NOW + 7)
    assert seal.decision_kind is EffectSealDecisionKind.ACCEPT_EFFECT_COMMITTED
    return seal


def test_restart_chaos_accepts_committed_crash_cut() -> None:
    handler_replay, journal, quench, fuzz, ledger = components()
    report = accepted_restart(handler_replay, journal, quench, ledger)
    assert report.accept
    assert report.family_count == 4
    assert report.final_phase is SideEffectPhase.COMMIT


def test_restart_chaos_holds_prepare_only_and_rejects_cut_drift() -> None:
    handler_replay, journal, quench, fuzz, ledger = components()
    prepare_journal = component("side-effect-prepare", final_phase=SideEffectPhase.PREPARE)
    held = assess_restart_chaos(restart_cuts(handler_replay, prepare_journal, quench, ledger), handler_replay_report=handler_replay, side_effect_journal_report=prepare_journal, handler_quench_report=quench, fuzz_ledger_report=ledger, now=NOW + 4, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert held.decision_kind is RestartChaosDecisionKind.HOLD_PREPARE_ONLY
    cuts = list(restart_cuts(handler_replay, journal, quench, ledger))
    bad = replace(cuts[1], phase=SideEffectPhase.ABORT.value)
    bad = replace(bad, signature=kp(2).sign(replace(bad, signature=b"").signature_payload()))
    drift = assess_restart_chaos((cuts[0], bad, cuts[2], cuts[3]), handler_replay_report=handler_replay, side_effect_journal_report=journal, handler_quench_report=quench, fuzz_ledger_report=ledger, now=NOW + 4, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert drift.decision_kind is RestartChaosDecisionKind.QUARANTINE_PHASE_DRIFT


def test_fuzz_shrink_preserves_required_mutations_and_rejects_bad_shrink() -> None:
    handler_replay, journal, quench, fuzz, ledger = components()
    shrink = accepted_shrink(fuzz, ledger)
    assert shrink.selected_mutations == ("idempotency_conflict", "payload_drift")
    missing = assess_fuzz_shrink(shrink_candidates(fuzz, ledger)[:1], fuzz_report=fuzz, fuzz_ledger_report=ledger, generator_digest=GENERATOR)
    assert missing.decision_kind is FuzzShrinkDecisionKind.HOLD_MISSING_MUTATIONS
    bad = (replace(shrink_candidates(fuzz, ledger)[0], observed_decision="accept_handler_capsule"), shrink_candidates(fuzz, ledger)[1])
    lost = assess_fuzz_shrink(bad, fuzz_report=fuzz, fuzz_ledger_report=ledger, generator_digest=GENERATOR)
    assert lost.decision_kind is FuzzShrinkDecisionKind.QUARANTINE_LOST_EXPECTED_DECISION


def test_effect_seal_accepts_joined_committed_boundary() -> None:
    handler_replay, journal, quench, fuzz, ledger = components()
    restart = accepted_restart(handler_replay, journal, quench, ledger)
    shrink = accepted_shrink(fuzz, ledger)
    seal = accepted_seal(handler_replay, journal, quench, ledger, restart, shrink)
    assert seal.accept
    assert seal.family_count == 2
    assert seal.final_phase is SideEffectPhase.COMMIT


def test_effect_seal_rejects_quench_cooldown_replay_and_component_drift() -> None:
    handler_replay, journal, quench, fuzz, ledger = components()
    restart = accepted_restart(handler_replay, journal, quench, ledger)
    shrink = accepted_shrink(fuzz, ledger)
    cooldown = component("handler-quench-cooldown", cooldown_until=NOW + 99)
    held = assess_effect_seal((), handler_replay_report=handler_replay, handler_quench_report=cooldown, side_effect_journal_report=journal, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, now=NOW + 7)
    assert held.decision_kind is EffectSealDecisionKind.EMPTY_NO_SEALS
    s0 = make_effect_seal_capsule(keypair=kp(10), side_effect_journal_report=journal, handler_replay_report=handler_replay, handler_quench_report=quench, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, sequence=0, issued_at=NOW + 5, expires_at=NOW + 305, family_id="family-a", path_family="path-a")
    replay = assess_effect_seal((s0,), handler_replay_report=handler_replay, handler_quench_report=quench, side_effect_journal_report=journal, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, now=NOW + 7, previous_seen_seal_digests=(s0.seal_digest,))
    assert replay.decision_kind is EffectSealDecisionKind.QUARANTINE_REPLAY
    other_shrink = replace(shrink, report_digest=d("other-shrink"))
    drift = assess_effect_seal((s0,), handler_replay_report=handler_replay, handler_quench_report=quench, side_effect_journal_report=journal, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=other_shrink, now=NOW + 7)
    assert drift.decision_kind is EffectSealDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT


def test_restartfold_audit_passes_current_path() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_restart_fold(root, revision="rev0055", artifact_stem=root.name)
    assert report.status == "pass"
