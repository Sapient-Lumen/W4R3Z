from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.chaosbudget import ChaosBudgetDecisionKind, ChaosLane, assess_chaos_budget, make_chaos_budget_grant
from i2p_dht_lab.corpuswitness import CorpusWitnessDecisionKind, CorpusWitnessKind, assess_corpus_witnesses, make_corpus_witness_receipt
from i2p_dht_lab.effectseal import EffectSealDecisionKind, assess_effect_seal, make_effect_seal_capsule
from i2p_dht_lab.fuzzledger import FuzzLedgerDecisionKind, assess_fuzz_ledger, make_fuzz_ledger_entry
from i2p_dht_lab.fuzzshrink import FuzzShrinkCandidate, FuzzShrinkDecisionKind, assess_fuzz_shrink
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.recoveryfold import audit_recovery_fold
from i2p_dht_lab.recoverymesh import RecoveryMeshDecisionKind, assess_recovery_mesh
from i2p_dht_lab.restartchaos import RestartChaosDecisionKind, RestartCutLane, assess_restart_chaos, make_restart_chaos_cut
from i2p_dht_lab.safecleanup import CleanupItemKind, SafeCleanupDecisionKind, assess_safe_cleanup, make_safe_cleanup_ticket
from i2p_dht_lab.sealreplay import SealReplayDecisionKind, assess_seal_replay, make_seal_replay_observation
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectPhase

NOW = 560_000
PROFILE = "rev0056-profile"
SERVICE = "rev0056-public-edge"
SCOPE = sha256(b"rev0056-scope")
REQUEST = sha256(b"rev0056-request")
PAYLOAD = sha256(b"rev0056-payload")
IDEM = sha256(b"rev0056-idempotency")
GENERATOR = sha256(b"rev0056-generator")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, final_phase: SideEffectPhase | None = None, action: SideEffectAction = SideEffectAction.INBOUND_HANDLER_WORK, cooldown_until: int = 0, failing_count: int = 0, required_mutations: tuple[str, ...] = (), observed_mutations: tuple[str, ...] = (), observation_digests: tuple[bytes, ...] = ()):  # noqa: E501
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


def base_components():
    handler_replay = component("r56-handler-replay")
    journal = component("r56-side-effect-journal", final_phase=SideEffectPhase.COMMIT)
    quench = component("r56-handler-quench")
    fuzz = component(
        "r56-fuzz-report",
        required_mutations=("payload_drift", "idempotency_conflict"),
        observed_mutations=("payload_drift", "idempotency_conflict"),
        observation_digests=(d("r56-obs-payload"), d("r56-obs-idem")),
    )
    fl0 = make_fuzz_ledger_entry(keypair=kp(41), fuzz_report=fuzz, generator_digest=GENERATOR, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    fl1 = make_fuzz_ledger_entry(keypair=kp(42), fuzz_report=fuzz, generator_digest=GENERATOR, sequence=1, previous_entry_digest=fl0.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    ledger = assess_fuzz_ledger((fl0, fl1), fuzz_report=fuzz, generator_digest=GENERATOR, now=NOW + 2)
    assert ledger.decision_kind is FuzzLedgerDecisionKind.ACCEPT_FUZZ_LEDGER
    return handler_replay, journal, quench, fuzz, ledger


def restart_report(handler_replay, journal, quench, ledger):
    c0 = make_restart_chaos_cut(keypair=kp(1), lane=RestartCutLane.HANDLER_REPLAY, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=handler_replay, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    c1 = make_restart_chaos_cut(keypair=kp(2), lane=RestartCutLane.SIDE_EFFECT_JOURNAL, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=journal, phase=SideEffectPhase.COMMIT, sequence=1, previous_cut_digest=c0.cut_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    c2 = make_restart_chaos_cut(keypair=kp(3), lane=RestartCutLane.HANDLER_QUENCH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=quench, sequence=2, previous_cut_digest=c1.cut_digest, issued_at=NOW + 2, expires_at=NOW + 302, family_id="family-c", path_family="path-c")
    c3 = make_restart_chaos_cut(keypair=kp(4), lane=RestartCutLane.FUZZ_LEDGER, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, component_report=ledger, sequence=3, previous_cut_digest=c2.cut_digest, issued_at=NOW + 3, expires_at=NOW + 303, family_id="family-d", path_family="path-d")
    report = assess_restart_chaos((c0, c1, c2, c3), handler_replay_report=handler_replay, side_effect_journal_report=journal, handler_quench_report=quench, fuzz_ledger_report=ledger, now=NOW + 4, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert report.decision_kind is RestartChaosDecisionKind.ACCEPT_RESTART_COMMITTED
    return report


def shrink_report(fuzz, ledger):
    candidates = (
        FuzzShrinkCandidate("handlercapsule", "payload_drift", "quarantine_", "quarantine_payload_drift", d("r56-obs-payload"), d("r56-shrunk-payload"), GENERATOR, 100, 7, "family-a", "path-a"),
        FuzzShrinkCandidate("sideeffectjournal", "idempotency_conflict", "quarantine_", "quarantine_idempotency_conflict", d("r56-obs-idem"), d("r56-shrunk-idem"), GENERATOR, 120, 8, "family-b", "path-b"),
    )
    shrink = assess_fuzz_shrink(candidates, fuzz_report=fuzz, fuzz_ledger_report=ledger, generator_digest=GENERATOR)
    assert shrink.decision_kind is FuzzShrinkDecisionKind.ACCEPT_SHRUNK_COVERAGE
    return shrink


def seal_report(handler_replay, journal, quench, ledger, restart, shrink):
    s0 = make_effect_seal_capsule(keypair=kp(10), side_effect_journal_report=journal, handler_replay_report=handler_replay, handler_quench_report=quench, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, sequence=0, issued_at=NOW + 5, expires_at=NOW + 305, family_id="family-a", path_family="path-a")
    s1 = make_effect_seal_capsule(keypair=kp(11), side_effect_journal_report=journal, handler_replay_report=handler_replay, handler_quench_report=quench, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, sequence=1, previous_seal_digest=s0.seal_digest, issued_at=NOW + 6, expires_at=NOW + 306, family_id="family-b", path_family="path-b")
    seal = assess_effect_seal((s0, s1), handler_replay_report=handler_replay, handler_quench_report=quench, side_effect_journal_report=journal, restart_chaos_report=restart, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, now=NOW + 7)
    assert seal.decision_kind is EffectSealDecisionKind.ACCEPT_EFFECT_COMMITTED
    return seal


def full_reports():
    handler_replay, journal, quench, fuzz, ledger = base_components()
    restart = restart_report(handler_replay, journal, quench, ledger)
    shrink = shrink_report(fuzz, ledger)
    seal = seal_report(handler_replay, journal, quench, ledger, restart, shrink)
    return handler_replay, journal, quench, fuzz, ledger, restart, shrink, seal


def replay_report(seal, restart, journal):
    r0 = make_seal_replay_observation(keypair=kp(21), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, generation=0, issued_at=NOW + 8, expires_at=NOW + 308, family_id="family-a", path_family="path-a")
    r1 = make_seal_replay_observation(keypair=kp(22), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, generation=1, previous_observation_digest=r0.observation_digest, issued_at=NOW + 9, expires_at=NOW + 309, family_id="family-b", path_family="path-b")
    report = assess_seal_replay((r0, r1), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, now=NOW + 10)
    assert report.decision_kind is SealReplayDecisionKind.ACCEPT_REPLAY_COMMITTED
    return report


def corpus_report(ledger, shrink):
    w0 = make_corpus_witness_receipt(keypair=kp(51), kind=CorpusWitnessKind.SHRINK_PRESERVED, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, generator_digest=GENERATOR, sequence=0, issued_at=NOW + 10, expires_at=NOW + 310, family_id="family-a", path_family="path-a")
    w1 = make_corpus_witness_receipt(keypair=kp(52), kind=CorpusWitnessKind.SHRINK_PRESERVED, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, generator_digest=GENERATOR, sequence=1, previous_receipt_digest=w0.receipt_digest, issued_at=NOW + 11, expires_at=NOW + 311, family_id="family-b", path_family="path-b")
    report = assess_corpus_witnesses((w0, w1), fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, generator_digest=GENERATOR, now=NOW + 12)
    assert report.decision_kind is CorpusWitnessDecisionKind.ACCEPT_CORPUS_WITNESSES
    return report


def recovery_report(seal, replay, restart, corpus):
    recovery = assess_recovery_mesh(effect_seal_report=seal, seal_replay_report=replay, restart_chaos_report=restart, corpus_witness_report=corpus)
    assert recovery.decision_kind is RecoveryMeshDecisionKind.ACCEPT_RECOVERED_COMMITTED
    return recovery


def test_seal_replay_accepts_committed_restart_generations_and_rejects_replay() -> None:
    _, journal, _, _, _, restart, _, seal = full_reports()
    r0 = make_seal_replay_observation(keypair=kp(21), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, generation=0, issued_at=NOW + 8, expires_at=NOW + 308, family_id="family-a", path_family="path-a")
    r1 = make_seal_replay_observation(keypair=kp(22), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, generation=1, previous_observation_digest=r0.observation_digest, issued_at=NOW + 9, expires_at=NOW + 309, family_id="family-b", path_family="path-b")
    accepted = assess_seal_replay((r0, r1), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, now=NOW + 10)
    assert accepted.accept
    replayed = assess_seal_replay((r0,), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, now=NOW + 10, previous_seen_observation_digests=(r0.observation_digest,))
    assert replayed.decision_kind is SealReplayDecisionKind.QUARANTINE_REPLAY


def test_seal_replay_rejects_generation_fork_and_phase_drift() -> None:
    _, journal, _, _, _, restart, _, seal = full_reports()
    r0 = make_seal_replay_observation(keypair=kp(21), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, generation=0, issued_at=NOW + 8, expires_at=NOW + 308, family_id="family-a", path_family="path-a")
    fork = make_seal_replay_observation(keypair=kp(22), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, generation=0, issued_at=NOW + 9, expires_at=NOW + 309, family_id="family-b", path_family="path-b")
    assert assess_seal_replay((r0, fork), effect_seal_report=seal, restart_chaos_report=restart, side_effect_journal_report=journal, now=NOW + 10).decision_kind is SealReplayDecisionKind.QUARANTINE_GENERATION_FORK
    bad_seal = replace(seal, final_phase=SideEffectPhase.ABORT)
    assert assess_seal_replay((r0,), effect_seal_report=bad_seal, restart_chaos_report=restart, side_effect_journal_report=journal, now=NOW + 10).decision_kind is SealReplayDecisionKind.QUARANTINE_PHASE_DRIFT


def test_corpus_witness_accepts_shrink_and_rejects_refutation() -> None:
    _, _, _, _, ledger, _, shrink, _ = full_reports()
    report = corpus_report(ledger, shrink)
    assert report.family_count == 2
    refute = make_corpus_witness_receipt(keypair=kp(53), kind=CorpusWitnessKind.SHRINK_REFUTED, fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, generator_digest=GENERATOR, sequence=0, issued_at=NOW + 10, expires_at=NOW + 310, family_id="family-a", path_family="path-a")
    bad = assess_corpus_witnesses((refute,), fuzz_ledger_report=ledger, fuzz_shrink_report=shrink, generator_digest=GENERATOR, now=NOW + 12)
    assert bad.decision_kind is CorpusWitnessDecisionKind.QUARANTINE_REFUTED_SHRINK


def test_recovery_mesh_accepts_only_joined_exact_boundary() -> None:
    _, journal, _, _, ledger, restart, shrink, seal = full_reports()
    replay = replay_report(seal, restart, journal)
    corpus = corpus_report(ledger, shrink)
    recovery = recovery_report(seal, replay, restart, corpus)
    assert recovery.accept
    drifted_replay = replace(replay, request_digest=d("other-request"))
    assert assess_recovery_mesh(effect_seal_report=seal, seal_replay_report=drifted_replay, restart_chaos_report=restart, corpus_witness_report=corpus).decision_kind is RecoveryMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT
    hard = replace(corpus, hard_negative_count=1)
    assert assess_recovery_mesh(effect_seal_report=seal, seal_replay_report=replay, restart_chaos_report=restart, corpus_witness_report=hard).decision_kind is RecoveryMeshDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE


def test_safe_cleanup_preserves_hard_negatives_and_accepted_seal() -> None:
    _, journal, _, _, ledger, restart, shrink, seal = full_reports()
    replay = replay_report(seal, restart, journal)
    corpus = corpus_report(ledger, shrink)
    recovery = recovery_report(seal, replay, restart, corpus)
    hard = d("hard-negative-preserved")
    t0 = make_safe_cleanup_ticket(keypair=kp(61), recovery_mesh_report=recovery, effect_seal_report=seal, removable_items=((CleanupItemKind.SOFT_FUZZ_CASE, d("old-soft-case")),), preserved_hard_negative_digests=(hard,), sequence=0, issued_at=NOW + 13, expires_at=NOW + 313, family_id="family-a", path_family="path-a")
    t1 = make_safe_cleanup_ticket(keypair=kp(62), recovery_mesh_report=recovery, effect_seal_report=seal, removable_items=((CleanupItemKind.CRASH_CUT_DEBRIS, d("old-crash-cut")),), preserved_hard_negative_digests=(hard,), sequence=1, previous_ticket_digest=t0.ticket_digest, issued_at=NOW + 14, expires_at=NOW + 314, family_id="family-b", path_family="path-b")
    cleanup = assess_safe_cleanup((t0, t1), recovery_mesh_report=recovery, effect_seal_report=seal, now=NOW + 15, hard_negative_digests_required=(hard,))
    assert cleanup.decision_kind is SafeCleanupDecisionKind.ACCEPT_SAFE_CLEANUP
    dropping = make_safe_cleanup_ticket(keypair=kp(63), recovery_mesh_report=recovery, effect_seal_report=seal, removable_items=((CleanupItemKind.HARD_NEGATIVE, hard),), sequence=0, issued_at=NOW + 13, expires_at=NOW + 313, family_id="family-a", path_family="path-a")
    assert assess_safe_cleanup((dropping,), recovery_mesh_report=recovery, effect_seal_report=seal, now=NOW + 15, hard_negative_digests_required=(hard,)).decision_kind is SafeCleanupDecisionKind.QUARANTINE_DROPS_HARD_NEGATIVE


def test_chaos_budget_bounds_repeated_recovery_pressure() -> None:
    _, journal, _, _, ledger, restart, shrink, seal = full_reports()
    replay = replay_report(seal, restart, journal)
    corpus = corpus_report(ledger, shrink)
    recovery = recovery_report(seal, replay, restart, corpus)
    hard = d("hard-negative-preserved")
    t0 = make_safe_cleanup_ticket(keypair=kp(61), recovery_mesh_report=recovery, effect_seal_report=seal, removable_items=((CleanupItemKind.SOFT_FUZZ_CASE, d("old-soft-case")),), preserved_hard_negative_digests=(hard,), sequence=0, issued_at=NOW + 13, expires_at=NOW + 313, family_id="family-a", path_family="path-a")
    t1 = make_safe_cleanup_ticket(keypair=kp(62), recovery_mesh_report=recovery, effect_seal_report=seal, removable_items=((CleanupItemKind.CRASH_CUT_DEBRIS, d("old-crash-cut")),), preserved_hard_negative_digests=(hard,), sequence=1, previous_ticket_digest=t0.ticket_digest, issued_at=NOW + 14, expires_at=NOW + 314, family_id="family-b", path_family="path-b")
    cleanup = assess_safe_cleanup((t0, t1), recovery_mesh_report=recovery, effect_seal_report=seal, now=NOW + 15, hard_negative_digests_required=(hard,))
    g0 = make_chaos_budget_grant(keypair=kp(71), lane=ChaosLane.EFFECT_RECOVERY, effect_seal_report=seal, recovery_mesh_report=recovery, safe_cleanup_report=cleanup, restart_chaos_report=restart, fuzz_shrink_report=shrink, budget_units=10, raw_key_units=1, protected_reserve_units=3, sequence=0, issued_at=NOW + 16, expires_at=NOW + 316, family_id="family-a", path_family="path-a")
    g1 = make_chaos_budget_grant(keypair=kp(72), lane=ChaosLane.SAFE_CLEANUP, effect_seal_report=seal, recovery_mesh_report=recovery, safe_cleanup_report=cleanup, restart_chaos_report=restart, fuzz_shrink_report=shrink, budget_units=12, raw_key_units=0, protected_reserve_units=3, sequence=1, previous_grant_digest=g0.grant_digest, issued_at=NOW + 17, expires_at=NOW + 317, family_id="family-b", path_family="path-b")
    ok = assess_chaos_budget((g0, g1), effect_seal_report=seal, recovery_mesh_report=recovery, safe_cleanup_report=cleanup, restart_chaos_report=restart, fuzz_shrink_report=shrink, now=NOW + 18, total_budget_cap=30, raw_key_budget_cap=2)
    assert ok.decision_kind is ChaosBudgetDecisionKind.ACCEPT_BUDGET
    too_much = assess_chaos_budget((g0, g1), effect_seal_report=seal, recovery_mesh_report=recovery, safe_cleanup_report=cleanup, restart_chaos_report=restart, fuzz_shrink_report=shrink, now=NOW + 18, total_budget_cap=20, raw_key_budget_cap=2)
    assert too_much.decision_kind is ChaosBudgetDecisionKind.QUARANTINE_TOTAL_BUDGET_EXCEEDED
    replayed = assess_chaos_budget((g0,), effect_seal_report=seal, recovery_mesh_report=recovery, safe_cleanup_report=cleanup, restart_chaos_report=restart, fuzz_shrink_report=shrink, now=NOW + 18, previous_seen_grant_digests=(g0.grant_digest,))
    assert replayed.decision_kind is ChaosBudgetDecisionKind.QUARANTINE_REPLAY


def test_recoveryfold_audit_passes_current_path() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_recovery_fold(root, revision="rev0056", artifact_stem=root.name)
    assert report.status == "pass"
