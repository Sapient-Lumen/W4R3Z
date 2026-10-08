from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.compactionaudit import CompactionAuditDecisionKind, CompactionAuditPlan, assess_compaction_audit
from i2p_dht_lab.effectreconcile import EffectReconcileDecisionKind
from i2p_dht_lab.finalityledger import FinalityMarkerKind, assess_finality_ledger, make_finality_marker
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.idempotencyrepair import IdempotencyRepairDecisionKind, IdempotencyRepairPlan, assess_idempotency_repair
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.pruneguard import PrunePlan, assess_prune_guard
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectPhase
from i2p_dht_lab.terminalfold import audit_terminal_fold
from i2p_dht_lab.terminalreceipt import TerminalReceiptDecisionKind, assess_terminal_receipts, make_terminal_receipt

NOW = 590_000
PROFILE = "rev0059-terminal-profile"
SERVICE = "rev0059-terminal-service"
SCOPE = sha256(DOMAIN + b":rev0059-terminal:scope")
REQUEST = sha256(DOMAIN + b":rev0059-terminal:request")
PAYLOAD = sha256(DOMAIN + b":rev0059-terminal:payload")
IDEM = sha256(DOMAIN + b":rev0059-terminal:idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0059-terminal-test:" + label.encode())


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def component(label: str, *, decision_kind=None, watch: bool = False, retry_required: bool = False, dead_letter_required: bool = False, final_phase=SideEffectPhase.COMMIT):
    return SimpleNamespace(
        report_digest=d(label),
        decision_kind=decision_kind,
        accept=True,
        watch=watch,
        quarantined=False,
        action=SideEffectAction.OUTBOUND_PUBLIC_SEND,
        final_phase=final_phase,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        hard_negative_count=0,
        retry_required=retry_required,
        dead_letter_required=dead_letter_required,
        family_count=2,
        path_family_count=2,
    )


def terminal_finality_and_prune():
    reconcile = component("reconcile-commit", decision_kind=EffectReconcileDecisionKind.ACCEPT_RECONCILED_COMMIT, final_phase=SideEffectPhase.COMMIT)
    dead = component("dead-terminal")
    journal = component("journal-terminal")
    m0 = make_finality_marker(keypair=kp(1), marker_kind=FinalityMarkerKind.TERMINAL_COMMIT, effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    m1 = make_finality_marker(keypair=kp(2), marker_kind=FinalityMarkerKind.TERMINAL_COMMIT, effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, sequence=1, previous_marker_digest=m0.marker_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    finality = assess_finality_ledger((m0, m1), effect_reconcile_report=reconcile, dead_letter_report=dead, side_effect_journal_report=journal, now=NOW + 2)
    assert finality.accept and finality.terminal
    plan = PrunePlan(action=finality.action, profile_id=finality.profile_id, service_name=finality.service_name, scope_digest=finality.scope_digest, request_digest=finality.request_digest, payload_digest=finality.payload_digest, idempotency_key=finality.idempotency_key, keep_digests=(finality.accepted_marker_digest,), drop_digests=(dead.report_digest,), hard_negative_digests=(), accepted_finality_digest=finality.accepted_marker_digest, dead_letter_digest=dead.report_digest, retry_escrow_digest=ZERO_DIGEST, sequence=0)
    prune = assess_prune_guard(prune_plan=plan, finality_report=finality, dead_letter_report=dead)
    assert prune.accept and not prune.watch
    return finality, prune, dead


def terminal_receipt_report():
    finality, prune, dead = terminal_finality_and_prune()
    r0 = make_terminal_receipt(keypair=kp(3), finality_report=finality, prune_guard_report=prune, sequence=0, issued_at=NOW + 3, expires_at=NOW + 303, family_id="family-a", path_family="path-a")
    r1 = make_terminal_receipt(keypair=kp(4), finality_report=finality, prune_guard_report=prune, sequence=1, previous_receipt_digest=r0.receipt_digest, issued_at=NOW + 4, expires_at=NOW + 304, family_id="family-b", path_family="path-b")
    receipt = assess_terminal_receipts((r0, r1), finality_report=finality, prune_guard_report=prune, now=NOW + 5)
    assert receipt.accept
    return finality, prune, dead, receipt


def test_terminal_receipt_accepts_terminal_commit_and_rejects_replay() -> None:
    finality, prune, _ = terminal_finality_and_prune()
    r0 = make_terminal_receipt(keypair=kp(5), finality_report=finality, prune_guard_report=prune, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    r1 = make_terminal_receipt(keypair=kp(6), finality_report=finality, prune_guard_report=prune, sequence=1, previous_receipt_digest=r0.receipt_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    report = assess_terminal_receipts((r0, r1), finality_report=finality, prune_guard_report=prune, now=NOW + 2)
    assert report.decision_kind is TerminalReceiptDecisionKind.ACCEPT_TERMINAL_COMMIT_RECEIPT
    assert report.terminal

    replay = assess_terminal_receipts((r0,), finality_report=finality, prune_guard_report=prune, now=NOW + 2, previous_seen_receipt_digests=(r0.receipt_digest,), min_family_count=1, min_path_family_count=1)
    assert replay.decision_kind is TerminalReceiptDecisionKind.QUARANTINE_REPLAY


def test_terminal_receipt_rejects_nonterminal_finality_and_digest_drift() -> None:
    finality, prune, _ = terminal_finality_and_prune()
    pending = replace(finality, terminal=False, watch=True)
    assert assess_terminal_receipts((), finality_report=pending, prune_guard_report=prune, now=NOW).decision_kind is TerminalReceiptDecisionKind.QUARANTINE_NONTERMINAL_FINALITY

    r0 = make_terminal_receipt(keypair=kp(7), finality_report=finality, prune_guard_report=prune, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    drift_prune = replace(prune, report_digest=d("other-prune"))
    assert assess_terminal_receipts((r0,), finality_report=finality, prune_guard_report=drift_prune, now=NOW + 1, min_family_count=1, min_path_family_count=1).decision_kind is TerminalReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_idempotency_repair_accepts_terminal_and_retry_lineage_paths() -> None:
    finality, prune, dead, receipt = terminal_receipt_report()
    terminal_plan = IdempotencyRepairPlan(action=receipt.action, profile_id=receipt.profile_id, service_name=receipt.service_name, scope_digest=receipt.scope_digest, request_digest=receipt.request_digest, payload_digest=receipt.payload_digest, idempotency_key=receipt.idempotency_key, terminal_receipt_digest=receipt.report_digest, finality_digest=finality.report_digest, prune_guard_digest=prune.report_digest, retry_escrow_digest=ZERO_DIGEST, dead_letter_digest=ZERO_DIGEST, carried_dead_letter_digest=ZERO_DIGEST, previous_attempt_number=0, resolved_attempt_number=0, sequence=0)
    terminal_repair = assess_idempotency_repair(repair_plan=terminal_plan, terminal_receipt_report=receipt, finality_report=finality, prune_guard_report=prune)
    assert terminal_repair.decision_kind is IdempotencyRepairDecisionKind.ACCEPT_TERMINAL_REPAIR

    retry = component("retry-escrow-old", watch=False)
    retry_plan = IdempotencyRepairPlan(action=receipt.action, profile_id=receipt.profile_id, service_name=receipt.service_name, scope_digest=receipt.scope_digest, request_digest=receipt.request_digest, payload_digest=receipt.payload_digest, idempotency_key=receipt.idempotency_key, terminal_receipt_digest=receipt.report_digest, finality_digest=finality.report_digest, prune_guard_digest=prune.report_digest, retry_escrow_digest=retry.report_digest, dead_letter_digest=dead.report_digest, carried_dead_letter_digest=dead.report_digest, previous_attempt_number=1, resolved_attempt_number=2, sequence=1)
    retry_repair = assess_idempotency_repair(repair_plan=retry_plan, terminal_receipt_report=receipt, finality_report=finality, prune_guard_report=prune, retry_escrow_report=retry, dead_letter_report=dead)
    assert retry_repair.decision_kind is IdempotencyRepairDecisionKind.ACCEPT_RETRY_LINEAGE_REPAIR


def test_idempotency_repair_rejects_attempt_regression_and_missing_deadletter_carry() -> None:
    finality, prune, dead, receipt = terminal_receipt_report()
    retry = component("retry-escrow-old")
    bad_attempt = IdempotencyRepairPlan(action=receipt.action, profile_id=receipt.profile_id, service_name=receipt.service_name, scope_digest=receipt.scope_digest, request_digest=receipt.request_digest, payload_digest=receipt.payload_digest, idempotency_key=receipt.idempotency_key, terminal_receipt_digest=receipt.report_digest, finality_digest=finality.report_digest, prune_guard_digest=prune.report_digest, retry_escrow_digest=retry.report_digest, dead_letter_digest=dead.report_digest, carried_dead_letter_digest=dead.report_digest, previous_attempt_number=2, resolved_attempt_number=2, sequence=0)
    assert assess_idempotency_repair(repair_plan=bad_attempt, terminal_receipt_report=receipt, finality_report=finality, prune_guard_report=prune, retry_escrow_report=retry, dead_letter_report=dead).decision_kind is IdempotencyRepairDecisionKind.QUARANTINE_ATTEMPT_REGRESSION

    missing_carry = replace(bad_attempt, previous_attempt_number=1, resolved_attempt_number=2, carried_dead_letter_digest=ZERO_DIGEST)
    assert assess_idempotency_repair(repair_plan=missing_carry, terminal_receipt_report=receipt, finality_report=finality, prune_guard_report=prune, retry_escrow_report=retry, dead_letter_report=dead).decision_kind is IdempotencyRepairDecisionKind.QUARANTINE_MISSING_DEAD_LETTER_CARRY


def test_compaction_audit_accepts_preserving_terminal_and_rejects_drops() -> None:
    finality, prune, _, receipt = terminal_receipt_report()
    repair_plan = IdempotencyRepairPlan(action=receipt.action, profile_id=receipt.profile_id, service_name=receipt.service_name, scope_digest=receipt.scope_digest, request_digest=receipt.request_digest, payload_digest=receipt.payload_digest, idempotency_key=receipt.idempotency_key, terminal_receipt_digest=receipt.report_digest, finality_digest=finality.report_digest, prune_guard_digest=prune.report_digest, retry_escrow_digest=ZERO_DIGEST, dead_letter_digest=ZERO_DIGEST, carried_dead_letter_digest=ZERO_DIGEST, previous_attempt_number=0, resolved_attempt_number=0, sequence=0)
    repair = assess_idempotency_repair(repair_plan=repair_plan, terminal_receipt_report=receipt, finality_report=finality, prune_guard_report=prune)
    hard = d("hard-preserved")
    plan = CompactionAuditPlan(action=receipt.action, profile_id=receipt.profile_id, service_name=receipt.service_name, scope_digest=receipt.scope_digest, request_digest=receipt.request_digest, payload_digest=receipt.payload_digest, idempotency_key=receipt.idempotency_key, terminal_receipt_digest=receipt.report_digest, idempotency_repair_digest=repair.report_digest, finality_digest=finality.report_digest, prune_guard_digest=prune.report_digest, keep_digests=(receipt.report_digest, repair.report_digest, finality.report_digest, prune.report_digest, hard), drop_digests=(), hard_negative_digests=(hard,), sequence=0)
    audit = assess_compaction_audit(compaction_plan=plan, terminal_receipt_report=receipt, idempotency_repair_report=repair, finality_report=finality, prune_guard_report=prune)
    assert audit.decision_kind is CompactionAuditDecisionKind.ACCEPT_COMPACTION

    drops_terminal = replace(plan, keep_digests=(repair.report_digest, finality.report_digest, prune.report_digest, hard), drop_digests=(receipt.report_digest,))
    assert assess_compaction_audit(compaction_plan=drops_terminal, terminal_receipt_report=receipt, idempotency_repair_report=repair, finality_report=finality, prune_guard_report=prune).decision_kind is CompactionAuditDecisionKind.QUARANTINE_DROPS_TERMINAL_RECEIPT
    drops_hard = replace(plan, keep_digests=(receipt.report_digest, repair.report_digest, finality.report_digest, prune.report_digest), drop_digests=(hard,))
    assert assess_compaction_audit(compaction_plan=drops_hard, terminal_receipt_report=receipt, idempotency_repair_report=repair, finality_report=finality, prune_guard_report=prune).decision_kind is CompactionAuditDecisionKind.QUARANTINE_DROPS_HARD_NEGATIVE


def test_terminalfold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_terminal_fold(root)
    assert report.status == "pass", report.findings
