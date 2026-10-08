from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

from i2p_dht_lab.finalityledger import FinalityLedgerDecisionKind
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.pruneguard import PruneGuardDecisionKind
from i2p_dht_lab.settlementlane import SettlementKind
from i2p_dht_lab.settlementstore import SettlementStoreDecisionKind, assess_settlement_store
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectPhase
from i2p_dht_lab.terminalreceipt import (
    TerminalReceiptDecisionKind,
    TerminalReceiptKind,
    assess_terminal_receipts,
    make_terminal_receipt,
)

NOW = 590_500
PROFILE = "rev0059-store-profile"
SERVICE = "rev0059-store-service"
SCOPE = sha256(DOMAIN + b":rev0059-store:scope")
REQUEST = sha256(DOMAIN + b":rev0059-store:request")
PAYLOAD = sha256(DOMAIN + b":rev0059-store:payload")
IDEM = sha256(DOMAIN + b":rev0059-store:idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0059-store-test:" + label.encode())


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def base(label: str, *, decision_kind=None, accept=True, watch=False, terminal=False, final_phase=None, family_count=2, path_family_count=2, hard=0, request=None, retry_required=False, dead_letter_required=False):
    return SimpleNamespace(
        report_digest=d(label),
        accepted_marker_digest=d(label + ":marker"),
        accepted_entry_digest=d(label + ":entry"),
        accepted_pack_digest=d(label + ":pack"),
        plan_digest=d(label + ":plan"),
        decision_kind=decision_kind,
        accept=accept,
        watch=watch,
        quarantined=False,
        terminal=terminal,
        final_phase=final_phase,
        action=SideEffectAction.OUTBOUND_PUBLIC_SEND,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=request or REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        family_count=family_count,
        path_family_count=path_family_count,
        hard_negative_count=hard,
        retry_required=retry_required,
        dead_letter_required=dead_letter_required,
    )


def finality_terminal(label="finality"):
    return base(label, decision_kind=FinalityLedgerDecisionKind.ACCEPT_TERMINAL_COMMIT, terminal=True, final_phase=SideEffectPhase.COMMIT)


def finality_retry(label="finality-retry"):
    return base(label, decision_kind=FinalityLedgerDecisionKind.ACCEPT_RETRY_PENDING, watch=True, terminal=False, final_phase=SideEffectPhase.PREPARE, retry_required=True, dead_letter_required=True)


def settlement(label="settlement", *, kind=SettlementKind.COMMIT_SETTLED, watch=False, retry_required=False, dead_letter_required=False, request=None):
    r = base(label, decision_kind=SimpleNamespace(value="settlement"), watch=watch, request=request, retry_required=retry_required, dead_letter_required=dead_letter_required)
    r.settlement_kind = kind
    return r


def prune(label="prune", *, decision_kind=PruneGuardDecisionKind.ACCEPT_TERMINAL_SOFT_PRUNE, watch=False, request=None):
    return base(label, decision_kind=decision_kind, watch=watch, request=request)


def accepted_component(label: str):
    return base(label, decision_kind=SimpleNamespace(value="accept"))


def test_settlement_store_accepts_terminal_branch_reconciled_with_prune_and_tombstone_repair() -> None:
    verdict = assess_settlement_store(
        finality_report=finality_terminal(),
        settlement_report=settlement(),
        attestation_pack_report=accepted_component("attestation"),
        tombstone_repair_report=accepted_component("tombrepair"),
        prune_guard_report=prune(),
    )
    assert verdict.decision_kind is SettlementStoreDecisionKind.ACCEPT_TERMINAL_STORE
    assert verdict.terminal
    assert not verdict.watch


def test_settlement_store_accepts_retry_held_only_with_retry_escrow_carry() -> None:
    finality = finality_retry()
    held = settlement(kind=SettlementKind.RETRY_HELD, watch=True, retry_required=True, dead_letter_required=True)
    without_escrow = assess_settlement_store(
        finality_report=finality,
        settlement_report=held,
        attestation_pack_report=accepted_component("attestation"),
        tombstone_repair_report=accepted_component("tombrepair"),
        prune_guard_report=prune(decision_kind=SimpleNamespace(value="accept_pending_hold")),
        retry_escrow_report=None,
    )
    assert without_escrow.decision_kind is SettlementStoreDecisionKind.QUARANTINE_RETRY_WITHOUT_ESCROW

    with_escrow = assess_settlement_store(
        finality_report=finality,
        settlement_report=held,
        attestation_pack_report=accepted_component("attestation"),
        tombstone_repair_report=accepted_component("tombrepair"),
        prune_guard_report=prune(decision_kind=SimpleNamespace(value="accept_pending_hold")),
        retry_escrow_report=accepted_component("retry-escrow"),
    )
    assert with_escrow.decision_kind is SettlementStoreDecisionKind.ACCEPT_RETRY_HELD_STORE
    assert with_escrow.watch
    assert with_escrow.retry_required and with_escrow.dead_letter_required


def test_settlement_store_rejects_terminal_pending_drift_and_boundary_drift() -> None:
    drift = assess_settlement_store(
        finality_report=finality_terminal(),
        settlement_report=settlement(kind=SettlementKind.RETRY_HELD, watch=True, retry_required=True, dead_letter_required=True),
        attestation_pack_report=accepted_component("attestation"),
        tombstone_repair_report=accepted_component("tombrepair"),
        prune_guard_report=prune(),
        retry_escrow_report=accepted_component("retry-escrow"),
    )
    assert drift.decision_kind is SettlementStoreDecisionKind.QUARANTINE_FINALITY_SETTLEMENT_DRIFT

    boundary = assess_settlement_store(
        finality_report=finality_terminal(),
        settlement_report=settlement(request=d("other-request")),
        attestation_pack_report=accepted_component("attestation"),
        tombstone_repair_report=accepted_component("tombrepair"),
        prune_guard_report=prune(),
    )
    assert boundary.decision_kind is SettlementStoreDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_terminal_receipt_accepts_diverse_terminal_receipt_and_rejects_replay() -> None:
    finality = finality_terminal()
    prune_report = prune()
    r0 = make_terminal_receipt(keypair=kp(1), finality_report=finality, prune_guard_report=prune_report, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    r1 = make_terminal_receipt(keypair=kp(2), finality_report=finality, prune_guard_report=prune_report, sequence=1, previous_receipt_digest=r0.receipt_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    report = assess_terminal_receipts((r0, r1), finality_report=finality, prune_guard_report=prune_report, now=NOW + 2)
    assert report.decision_kind is TerminalReceiptDecisionKind.ACCEPT_TERMINAL_COMMIT_RECEIPT
    assert report.receipt_kind is TerminalReceiptKind.TERMINAL_COMMIT

    replay = assess_terminal_receipts((r0,), finality_report=finality, prune_guard_report=prune_report, now=NOW + 2, previous_seen_receipt_digests=(r0.receipt_digest,), min_family_count=1, min_path_family_count=1)
    assert replay.decision_kind is TerminalReceiptDecisionKind.QUARANTINE_REPLAY


def test_terminal_receipt_rejects_nonterminal_finality_and_digest_drift() -> None:
    nonterminal = finality_retry()
    prune_report = prune()
    assert assess_terminal_receipts((), finality_report=nonterminal, prune_guard_report=prune_report, now=NOW).decision_kind is TerminalReceiptDecisionKind.QUARANTINE_NONTERMINAL_FINALITY

    finality = finality_terminal()
    r0 = make_terminal_receipt(keypair=kp(3), finality_report=finality, prune_guard_report=prune_report, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    bad = replace(r0, plan_digest=d("wrong-plan"), signature=b"")
    bad = replace(bad, signature=kp(3).sign(bad.signature_payload()))
    verdict = assess_terminal_receipts((bad,), finality_report=finality, prune_guard_report=prune_report, now=NOW + 1, min_family_count=1, min_path_family_count=1)
    assert verdict.decision_kind is TerminalReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT
