from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.effectreconcile import EffectReconcileDecisionKind
from i2p_dht_lab.finalityfold import audit_finality_fold
from i2p_dht_lab.finalityledger import (
    FinalityLedgerDecisionKind,
    FinalityMarkerKind,
    assess_finality_ledger,
    make_finality_marker,
)
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.pruneguard import PruneGuardDecisionKind, PrunePlan, assess_prune_guard
from i2p_dht_lab.retryescrow import RetryEscrowDecisionKind, assess_retry_escrow, make_retry_escrow_ticket
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectPhase

NOW = 10_000


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0058-test:" + label.encode())


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def report(label: str, *, decision_kind=None, accept=True, watch=False, final_phase=None, retry_required=False, dead_letter_required=False, hard=0, request=None):
    return SimpleNamespace(
        decision_kind=decision_kind,
        accept=accept,
        watch=watch,
        quarantined=False,
        action=SideEffectAction.OUTBOUND_PUBLIC_SEND,
        final_phase=final_phase,
        profile_id="profile-rev58",
        service_name="bridge-publication",
        scope_digest=d("scope"),
        request_digest=request or d("request"),
        payload_digest=d("payload"),
        idempotency_key=d("idem"),
        hard_negative_count=hard,
        retry_required=retry_required,
        dead_letter_required=dead_letter_required,
        report_digest=d(label),
    )


def terminal_components(phase=SideEffectPhase.COMMIT):
    decision = EffectReconcileDecisionKind.ACCEPT_RECONCILED_COMMIT if phase is SideEffectPhase.COMMIT else EffectReconcileDecisionKind.ACCEPT_RECONCILED_ABORT
    reconcile = report("reconcile-terminal-" + phase.value, decision_kind=decision, final_phase=phase)
    dead = report("dead-terminal", accept=True, watch=False, final_phase=phase)
    journal = report("journal-terminal", accept=True, watch=False, final_phase=phase)
    return reconcile, dead, journal


def retry_components():
    reconcile = report("reconcile-retry", decision_kind=EffectReconcileDecisionKind.ACCEPT_RETRY, final_phase=None, watch=True, retry_required=True, dead_letter_required=True)
    dead = report("dead-retry", accept=True, watch=True, final_phase=SideEffectPhase.PREPARE)
    retry = report("retry-quorum", accept=True, watch=True)
    journal = report("journal-retry", accept=True, watch=True, final_phase=SideEffectPhase.PREPARE)
    return reconcile, dead, retry, journal


def two_finality_markers(kind, reconcile, dead=None, retry=None, journal=None):
    m0 = make_finality_marker(keypair=kp(1), marker_kind=kind, effect_reconcile_report=reconcile, dead_letter_report=dead, retry_quorum_report=retry, side_effect_journal_report=journal, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    m1 = make_finality_marker(keypair=kp(2), marker_kind=kind, effect_reconcile_report=reconcile, dead_letter_report=dead, retry_quorum_report=retry, side_effect_journal_report=journal, sequence=1, previous_marker_digest=m0.marker_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    return m0, m1


def test_finality_accepts_terminal_commit_and_rejects_replay() -> None:
    reconcile, dead, journal = terminal_components()
    markers = two_finality_markers(FinalityMarkerKind.TERMINAL_COMMIT, reconcile, dead=dead, journal=journal)
    finality = assess_finality_ledger(markers, effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, now=NOW + 2)
    assert finality.decision_kind is FinalityLedgerDecisionKind.ACCEPT_TERMINAL_COMMIT
    assert finality.terminal
    assert not finality.watch

    replay = assess_finality_ledger((markers[0],), effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, now=NOW + 2, previous_seen_marker_digests=(markers[0].marker_digest,), min_family_count=1, min_path_family_count=1)
    assert replay.decision_kind is FinalityLedgerDecisionKind.QUARANTINE_REPLAY


def test_finality_keeps_retry_pending_and_rejects_premature_terminality() -> None:
    reconcile, dead, retry, journal = retry_components()
    markers = two_finality_markers(FinalityMarkerKind.RETRY_PENDING, reconcile, dead=dead, retry=retry, journal=journal)
    finality = assess_finality_ledger(markers, effect_reconcile_report=reconcile, dead_letter_report=dead, retry_quorum_report=retry, side_effect_journal_report=journal, now=NOW + 2)
    assert finality.decision_kind is FinalityLedgerDecisionKind.ACCEPT_RETRY_PENDING
    assert finality.watch
    assert not finality.terminal

    bad = two_finality_markers(FinalityMarkerKind.TERMINAL_COMMIT, reconcile, dead=dead, retry=retry, journal=journal)
    assert assess_finality_ledger(bad, effect_reconcile_report=reconcile, dead_letter_report=dead, retry_quorum_report=retry, side_effect_journal_report=journal, now=NOW + 2).decision_kind is FinalityLedgerDecisionKind.QUARANTINE_PREMATURE_TERMINALITY


def test_finality_rejects_same_sequence_fork_and_boundary_drift() -> None:
    reconcile, dead, journal = terminal_components()
    m0 = make_finality_marker(keypair=kp(3), marker_kind=FinalityMarkerKind.TERMINAL_COMMIT, effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    fork = make_finality_marker(keypair=kp(4), marker_kind=FinalityMarkerKind.TERMINAL_ABORT, effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, sequence=0, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    assert assess_finality_ledger((m0, fork), effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, now=NOW + 2).decision_kind is FinalityLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK

    drift = report("reconcile-drift", decision_kind=EffectReconcileDecisionKind.ACCEPT_RECONCILED_COMMIT, final_phase=SideEffectPhase.COMMIT, request=d("other-request"))
    assert assess_finality_ledger((m0,), effect_reconcile_report=drift, dead_letter_report=dead, side_effect_journal_report=journal, now=NOW + 2, min_family_count=1, min_path_family_count=1).decision_kind is FinalityLedgerDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_retry_escrow_accepts_retry_with_deadletter_carry_and_rejects_terminal_reconcile() -> None:
    reconcile, dead, retry, _ = retry_components()
    t0 = make_retry_escrow_ticket(keypair=kp(5), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, attempt_number=1, retry_after=NOW + 60, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    t1 = make_retry_escrow_ticket(keypair=kp(6), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, attempt_number=1, retry_after=NOW + 60, sequence=1, previous_ticket_digest=t0.ticket_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    escrow = assess_retry_escrow((t0, t1), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, now=NOW + 2)
    assert escrow.decision_kind is RetryEscrowDecisionKind.ACCEPT_RETRY_ESCROW
    assert escrow.carried_dead_letter_digest == dead.report_digest

    terminal, terminal_dead, _ = terminal_components()
    not_retry = assess_retry_escrow((t0,), effect_reconcile_report=terminal, retry_quorum_report=retry, dead_letter_report=terminal_dead, now=NOW + 2, min_family_count=1, min_path_family_count=1)
    assert not_retry.decision_kind is RetryEscrowDecisionKind.QUARANTINE_NOT_RETRY_RECONCILE


def test_retry_escrow_rejects_missing_carry_and_previous_mismatch() -> None:
    reconcile, dead, retry, _ = retry_components()
    t0 = make_retry_escrow_ticket(keypair=kp(7), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, attempt_number=1, retry_after=NOW + 60, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    bad_carry = replace(t0, carried_dead_letter_digest=ZERO_DIGEST)
    bad_carry = replace(bad_carry, signature=kp(7).sign(bad_carry.signature_payload()))
    assert assess_retry_escrow((bad_carry,), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, now=NOW + 1, min_family_count=1, min_path_family_count=1).decision_kind is RetryEscrowDecisionKind.QUARANTINE_MISSING_DEAD_LETTER_CARRY

    t1 = make_retry_escrow_ticket(keypair=kp(8), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, attempt_number=1, retry_after=NOW + 60, sequence=1, previous_ticket_digest=d("wrong-prev"), issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    assert assess_retry_escrow((t0, t1), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, now=NOW + 2).decision_kind is RetryEscrowDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_prune_guard_allows_terminal_soft_prune_but_preserves_hard_negative_and_finality() -> None:
    reconcile, dead, journal = terminal_components()
    markers = two_finality_markers(FinalityMarkerKind.TERMINAL_COMMIT, reconcile, dead=dead, journal=journal)
    finality = assess_finality_ledger(markers, effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, now=NOW + 2)
    plan = PrunePlan(action=finality.action, profile_id=finality.profile_id, service_name=finality.service_name, scope_digest=finality.scope_digest, request_digest=finality.request_digest, payload_digest=finality.payload_digest, idempotency_key=finality.idempotency_key, keep_digests=(finality.accepted_marker_digest, d("hard-a")), drop_digests=(dead.report_digest,), hard_negative_digests=(d("hard-a"),), accepted_finality_digest=finality.accepted_marker_digest, dead_letter_digest=dead.report_digest, retry_escrow_digest=ZERO_DIGEST, sequence=0)
    assert assess_prune_guard(prune_plan=plan, finality_report=finality, dead_letter_report=dead).decision_kind is PruneGuardDecisionKind.ACCEPT_TERMINAL_SOFT_PRUNE

    drops_finality = replace(plan, drop_digests=(finality.accepted_marker_digest,))
    assert assess_prune_guard(prune_plan=drops_finality, finality_report=finality, dead_letter_report=dead).decision_kind is PruneGuardDecisionKind.QUARANTINE_DROPS_ACCEPTED_FINALITY

    drops_hard = replace(plan, keep_digests=(finality.accepted_marker_digest,), hard_negative_digests=(d("hard-a"),))
    assert assess_prune_guard(prune_plan=drops_hard, finality_report=finality, dead_letter_report=dead).decision_kind is PruneGuardDecisionKind.QUARANTINE_DROPS_HARD_NEGATIVE


def test_prune_guard_keeps_pending_retry_and_deadletter_memory() -> None:
    reconcile, dead, retry, journal = retry_components()
    markers = two_finality_markers(FinalityMarkerKind.RETRY_PENDING, reconcile, dead=dead, retry=retry, journal=journal)
    finality = assess_finality_ledger(markers, effect_reconcile_report=reconcile, dead_letter_report=dead, retry_quorum_report=retry, side_effect_journal_report=journal, now=NOW + 2)
    t0 = make_retry_escrow_ticket(keypair=kp(9), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, attempt_number=1, retry_after=NOW + 60, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    t1 = make_retry_escrow_ticket(keypair=kp(10), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, attempt_number=1, retry_after=NOW + 60, sequence=1, previous_ticket_digest=t0.ticket_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    escrow = assess_retry_escrow((t0, t1), effect_reconcile_report=reconcile, retry_quorum_report=retry, dead_letter_report=dead, now=NOW + 2)
    plan = PrunePlan(action=finality.action, profile_id=finality.profile_id, service_name=finality.service_name, scope_digest=finality.scope_digest, request_digest=finality.request_digest, payload_digest=finality.payload_digest, idempotency_key=finality.idempotency_key, keep_digests=(finality.accepted_marker_digest, escrow.report_digest, dead.report_digest), drop_digests=(), hard_negative_digests=(), accepted_finality_digest=finality.accepted_marker_digest, dead_letter_digest=dead.report_digest, retry_escrow_digest=escrow.report_digest, sequence=0)
    assert assess_prune_guard(prune_plan=plan, finality_report=finality, retry_escrow_report=escrow, dead_letter_report=dead).decision_kind is PruneGuardDecisionKind.ACCEPT_PENDING_HOLD

    bad = replace(plan, drop_digests=(dead.report_digest,))
    assert assess_prune_guard(prune_plan=bad, finality_report=finality, retry_escrow_report=escrow, dead_letter_report=dead).decision_kind is PruneGuardDecisionKind.QUARANTINE_DROPS_DEAD_LETTER_WHILE_PENDING
    bad_retry = replace(plan, drop_digests=(escrow.report_digest,))
    assert assess_prune_guard(prune_plan=bad_retry, finality_report=finality, retry_escrow_report=escrow, dead_letter_report=dead).decision_kind is PruneGuardDecisionKind.QUARANTINE_DROPS_RETRY_ESCROW_WHILE_PENDING


def test_finalityfold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_finality_fold(root)
    assert report.status == "pass", report.findings
