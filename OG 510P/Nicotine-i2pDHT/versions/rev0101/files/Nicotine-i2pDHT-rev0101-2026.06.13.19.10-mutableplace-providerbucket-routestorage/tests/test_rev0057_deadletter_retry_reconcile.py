from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.chaosbudget import ChaosLane
from i2p_dht_lab.deadletter import DeadLetterDecisionKind, DeadLetterKind, assess_dead_letter, make_dead_letter_entry
from i2p_dht_lab.effectreconcile import EffectReconcileDecisionKind, assess_effect_reconcile
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.reconcilefold import audit_reconcile_fold
from i2p_dht_lab.retryquorum import RetryQuorumDecisionKind, RetryVoteKind, assess_retry_quorum, make_retry_vote
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectPhase

NOW = 570_000
PROFILE = "rev0057-profile"
SERVICE = "rev0057-public-edge"
SCOPE = sha256(b"rev0057-scope")
REQUEST = sha256(b"rev0057-request")
PAYLOAD = sha256(b"rev0057-payload")
IDEM = sha256(b"rev0057-idempotency")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def report(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, final_phase: SideEffectPhase | None = SideEffectPhase.PREPARE, lanes=()):
    return SimpleNamespace(
        report_digest=d(label),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        action=SideEffectAction.OUTBOUND_PUBLIC_SEND,
        final_phase=final_phase,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        hard_negative_count=0,
        lanes=tuple(lanes),
        decision_kind=SimpleNamespace(value="accept" if accept else "hold"),
    )


def base_components(*, final_phase: SideEffectPhase | None = SideEffectPhase.PREPARE, recovery_watch: bool = True, budget_lanes=(ChaosLane.DEAD_LETTER, ChaosLane.RETRY_PROBE)):
    effect = report("r57-effect", final_phase=final_phase)
    recovery = report("r57-recovery", watch=recovery_watch, final_phase=final_phase)
    journal = report("r57-journal", final_phase=final_phase)
    chaos = report("r57-chaos", final_phase=final_phase, lanes=budget_lanes)
    return effect, recovery, journal, chaos


def dead_report(*, final_phase: SideEffectPhase | None = SideEffectPhase.PREPARE, recovery_watch: bool = True, budget_lanes=(ChaosLane.DEAD_LETTER, ChaosLane.RETRY_PROBE)):
    effect, recovery, journal, chaos = base_components(final_phase=final_phase, recovery_watch=recovery_watch, budget_lanes=budget_lanes)
    e0 = make_dead_letter_entry(keypair=kp(1), kind=DeadLetterKind.PREPARED_ONLY, effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    e1 = make_dead_letter_entry(keypair=kp(2), kind=DeadLetterKind.PREPARED_ONLY, effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, sequence=1, previous_entry_digest=e0.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    dead = assess_dead_letter((e0, e1), effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, now=NOW + 2)
    assert dead.accept
    return effect, recovery, journal, chaos, dead


def retry_report(dead, recovery, chaos):
    v0 = make_retry_vote(keypair=kp(11), vote_kind=RetryVoteKind.RETRY_READY, recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=chaos, attempt_number=1, sequence=0, issued_at=NOW + 3, expires_at=NOW + 303, family_id="family-a", path_family="path-a")
    v1 = make_retry_vote(keypair=kp(12), vote_kind=RetryVoteKind.RETRY_READY, recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=chaos, attempt_number=1, sequence=1, previous_vote_digest=v0.vote_digest, issued_at=NOW + 4, expires_at=NOW + 304, family_id="family-b", path_family="path-b")
    retry = assess_retry_quorum((v0, v1), recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=chaos, now=NOW + 5)
    assert retry.decision_kind is RetryQuorumDecisionKind.ACCEPT_RETRY_QUORUM
    return retry


def test_deadletter_accepts_prepared_only_with_budget_and_diversity() -> None:
    _, _, _, _, dead = dead_report()
    assert dead.decision_kind is DeadLetterDecisionKind.ACCEPT_WITH_RETRY_WATCH
    assert dead.watch
    assert dead.family_count == 2
    assert dead.observed_phase is SideEffectPhase.PREPARE


def test_deadletter_rejects_missing_dead_letter_budget_and_replay() -> None:
    effect, recovery, journal, chaos = base_components(budget_lanes=(ChaosLane.RETRY_PROBE,))
    entry = make_dead_letter_entry(keypair=kp(3), kind=DeadLetterKind.PREPARED_ONLY, effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    missing_budget = assess_dead_letter((entry,), effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, now=NOW + 1, min_family_count=1, min_path_family_count=1)
    assert missing_budget.decision_kind is DeadLetterDecisionKind.QUARANTINE_MISSING_DEAD_LETTER_BUDGET

    effect, recovery, journal, chaos, dead = dead_report()
    replayed = assess_dead_letter((), effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, now=NOW + 2, previous_seen_entry_digests=dead.entry_digests)
    assert replayed.decision_kind is DeadLetterDecisionKind.EMPTY_NO_ENTRIES
    e0 = make_dead_letter_entry(keypair=kp(1), kind=DeadLetterKind.PREPARED_ONLY, effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    replayed = assess_dead_letter((e0,), effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, now=NOW + 1, previous_seen_entry_digests=(e0.entry_digest,), min_family_count=1, min_path_family_count=1)
    assert replayed.decision_kind is DeadLetterDecisionKind.QUARANTINE_REPLAY


def test_deadletter_rejects_phase_and_sequence_forks() -> None:
    effect, recovery, journal, chaos = base_components(final_phase=SideEffectPhase.COMMIT)
    bad_phase = make_dead_letter_entry(keypair=kp(4), kind=DeadLetterKind.PREPARED_ONLY, effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, observed_phase=SideEffectPhase.PREPARE, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    assert assess_dead_letter((bad_phase,), effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, now=NOW + 1, min_family_count=1, min_path_family_count=1).decision_kind is DeadLetterDecisionKind.QUARANTINE_PHASE_DRIFT

    effect, recovery, journal, chaos = base_components()
    e0 = make_dead_letter_entry(keypair=kp(5), kind=DeadLetterKind.PREPARED_ONLY, effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    fork = make_dead_letter_entry(keypair=kp(6), kind=DeadLetterKind.COMPONENT_WATCH, effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, sequence=0, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    assert assess_dead_letter((e0, fork), effect_seal_report=effect, recovery_mesh_report=recovery, side_effect_journal_report=journal, chaos_budget_report=chaos, now=NOW + 2).decision_kind is DeadLetterDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_retry_quorum_accepts_diverse_retry_votes_and_rejects_missing_budget() -> None:
    effect, recovery, journal, chaos, dead = dead_report()
    retry = retry_report(dead, recovery, chaos)
    assert retry.ready_count == 2
    assert retry.accept

    no_retry_budget = report("r57-chaos-no-retry", lanes=(ChaosLane.DEAD_LETTER,))
    v0 = make_retry_vote(keypair=kp(13), vote_kind=RetryVoteKind.RETRY_READY, recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=no_retry_budget, attempt_number=1, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    missing = assess_retry_quorum((v0,), recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=no_retry_budget, now=NOW + 1, min_family_count=1, min_path_family_count=1)
    assert missing.decision_kind is RetryQuorumDecisionKind.QUARANTINE_MISSING_RETRY_BUDGET


def test_retry_quorum_handles_refusal_backoff_and_previous_mismatch() -> None:
    _, recovery, _, chaos, dead = dead_report()
    r0 = make_retry_vote(keypair=kp(14), vote_kind=RetryVoteKind.REFUSE_USEFULLY, recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=chaos, attempt_number=1, sequence=0, retry_after=NOW + 60, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    r1 = make_retry_vote(keypair=kp(15), vote_kind=RetryVoteKind.REFUSE_USEFULLY, recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=chaos, attempt_number=1, sequence=1, previous_vote_digest=r0.vote_digest, retry_after=NOW + 80, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    backoff = assess_retry_quorum((r0, r1), recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=chaos, now=NOW + 2)
    assert backoff.decision_kind is RetryQuorumDecisionKind.ACCEPT_REFUSAL_BACKOFF
    bad_link = replace(r1, previous_vote_digest=d("wrong-prev"), signature=kp(15).sign(replace(r1, previous_vote_digest=d("wrong-prev"), signature=b"").signature_payload()))
    assert assess_retry_quorum((r0, bad_link), recovery_mesh_report=recovery, dead_letter_report=dead, chaos_budget_report=chaos, now=NOW + 2).decision_kind is RetryQuorumDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_effect_reconcile_accepts_retry_without_erasing_dead_letter() -> None:
    effect, recovery, journal, chaos, dead = dead_report()
    retry = retry_report(dead, recovery, chaos)
    recon = assess_effect_reconcile(effect_seal_report=effect, recovery_mesh_report=recovery, dead_letter_report=dead, retry_quorum_report=retry, side_effect_journal_report=journal)
    assert recon.decision_kind is EffectReconcileDecisionKind.ACCEPT_RETRY
    assert recon.dead_letter_required
    assert recon.retry_required


def test_effect_reconcile_accepts_terminal_commit_and_quarantines_conflict() -> None:
    effect, recovery, journal, chaos, dead = dead_report(final_phase=SideEffectPhase.COMMIT, recovery_watch=False)
    recon = assess_effect_reconcile(effect_seal_report=effect, recovery_mesh_report=recovery, dead_letter_report=dead, side_effect_journal_report=journal)
    assert recon.decision_kind is EffectReconcileDecisionKind.ACCEPT_RECONCILED_COMMIT

    conflicting_dead = replace(dead, kinds=(DeadLetterKind.AMBIGUOUS_ABORT,), observed_phase=SideEffectPhase.COMMIT)
    conflict = assess_effect_reconcile(effect_seal_report=effect, recovery_mesh_report=recovery, dead_letter_report=conflicting_dead, side_effect_journal_report=journal)
    assert conflict.decision_kind is EffectReconcileDecisionKind.QUARANTINE_PHASE_CONFLICT


def test_effect_reconcile_holds_watch_without_retry_and_rejects_boundary_drift() -> None:
    effect, recovery, journal, _, dead = dead_report()
    held = assess_effect_reconcile(effect_seal_report=effect, recovery_mesh_report=recovery, dead_letter_report=dead, side_effect_journal_report=journal)
    assert held.decision_kind is EffectReconcileDecisionKind.HOLD_COMPONENT_WATCH

    drift = replace(dead, request_digest=d("other-request"))
    assert assess_effect_reconcile(effect_seal_report=effect, recovery_mesh_report=recovery, dead_letter_report=drift, side_effect_journal_report=journal).decision_kind is EffectReconcileDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_reconcilefold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_reconcile_fold(root)
    assert report.status == "pass", report.findings
