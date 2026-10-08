from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.deliverywitness import DeliveryWitnessDecisionKind, assess_delivery_witness, expected_ack_digest, make_delivery_receipt
from i2p_dht_lab.fenceaudit import audit_fence_fold
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.livesendgate import LiveSendGateDecisionKind, assess_live_send_gate
from i2p_dht_lab.sendfence import SendFenceDecisionKind, assess_send_fence, make_send_fence_marker
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0060-profile"
SERVICE = "rev0060-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0060:scope")
REQUEST = sha256(DOMAIN + b":rev0060:request")
PAYLOAD = sha256(DOMAIN + b":rev0060:payload")
IDEM = sha256(DOMAIN + b":rev0060:idem")
SESSION = sha256(DOMAIN + b":rev0060:session")
DESTINATION = sha256(DOMAIN + b":rev0060:destination")
ENDPOINT = sha256(DOMAIN + b":rev0060:endpoint")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0060-test:" + label.encode())


def report(label: str, **kw):
    base = dict(
        report_digest=d(label),
        accept=True,
        watch=False,
        quarantined=False,
        action=ACTION,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        session_digest=SESSION,
        destination_digest=DESTINATION,
        endpoint_digest=ENDPOINT,
        family_count=2,
        path_family_count=2,
        hard_negative_count=0,
        terminal=True,
        retry_required=False,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def accepted_gate():
    canary = report("canary")
    store = report("settlement-store")
    tomb = report("tomb-repair")
    journal = report("journal")
    outbox = report("outbox")
    return assess_live_send_gate(canary_join_report=canary, settlement_store_report=store, tomb_repair_join_report=tomb, side_effect_journal_report=journal, outbox_drain_report=outbox, public_payload_bytes=512)


def test_live_send_gate_accepts_terminal_exact_boundary() -> None:
    gate = accepted_gate()
    assert gate.decision_kind is LiveSendGateDecisionKind.ACCEPT_TERMINAL_SEND_READY
    assert gate.accept and not gate.watch
    assert gate.session_digest == SESSION


def test_live_send_gate_holds_watchful_retry_canary() -> None:
    canary = report("canary-watch", watch=True)
    store = report("store-watch", watch=True, terminal=False, retry_required=True)
    tomb = report("tomb")
    held = assess_live_send_gate(canary_join_report=canary, settlement_store_report=store, tomb_repair_join_report=tomb, public_payload_bytes=128)
    assert held.decision_kind is LiveSendGateDecisionKind.HOLD_WATCHFUL_CANARY
    assert held.watch and not held.accept


def test_live_send_gate_rejects_drift_budget_and_missing_endpoint() -> None:
    canary = report("canary")
    store = report("store")
    tomb = report("tomb", request_digest=d("other-request"))
    drift = assess_live_send_gate(canary_join_report=canary, settlement_store_report=store, tomb_repair_join_report=tomb)
    assert drift.decision_kind is LiveSendGateDecisionKind.QUARANTINE_BOUNDARY_DRIFT

    budget = assess_live_send_gate(canary_join_report=canary, settlement_store_report=store, tomb_repair_join_report=report("tomb-ok"), public_payload_bytes=4096, max_public_payload_bytes=1024)
    assert budget.decision_kind is LiveSendGateDecisionKind.QUARANTINE_PAYLOAD_BUDGET_EXCEEDED

    missing = assess_live_send_gate(canary_join_report=report("canary-no-endpoint", session_digest=b""), settlement_store_report=store, tomb_repair_join_report=report("tomb-ok-2"), public_payload_bytes=8)
    assert missing.decision_kind is LiveSendGateDecisionKind.HOLD_MISSING_ENDPOINT_PROOF


def test_delivery_witness_accepts_diverse_exact_ack() -> None:
    gate = accepted_gate()
    r1 = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="a", path_family_id="pa")
    r2 = make_delivery_receipt(live_send_gate_report=gate, sequence=2, previous_digest=r1.receipt_digest, family_id="b", path_family_id="pb")
    witness = assess_delivery_witness(live_send_gate_report=gate, receipts=(r1, r2), last_sequence=0, previous_digest=r1.previous_digest)
    assert witness.decision_kind is DeliveryWitnessDecisionKind.ACCEPT_DELIVERED
    assert witness.accept and witness.accepted_receipt_digest == r2.receipt_digest


def test_delivery_witness_catches_ack_drift_replay_fork_and_diversity() -> None:
    gate = accepted_gate()
    good = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="a", path_family_id="pa")
    bad_ack = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="a", path_family_id="pa", ack_digest=d("wrong-ack"))
    assert assess_delivery_witness(live_send_gate_report=gate, receipts=(bad_ack,)).decision_kind is DeliveryWitnessDecisionKind.QUARANTINE_PAYLOAD_ACK_DRIFT
    assert assess_delivery_witness(live_send_gate_report=gate, receipts=(good,), seen_receipt_digests=(good.receipt_digest,)).decision_kind is DeliveryWitnessDecisionKind.QUARANTINE_RECEIPT_REPLAY
    fork = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="b", path_family_id="pb")
    assert assess_delivery_witness(live_send_gate_report=gate, receipts=(good, fork)).decision_kind is DeliveryWitnessDecisionKind.QUARANTINE_SEQUENCE_FORK
    low = assess_delivery_witness(live_send_gate_report=gate, receipts=(good,), min_family_count=2)
    assert low.decision_kind is DeliveryWitnessDecisionKind.HOLD_LOW_FAMILY_DIVERSITY
    assert expected_ack_digest(gate) == good.ack_digest


def test_send_fence_accepts_delivered_and_holds_pending() -> None:
    gate = accepted_gate()
    r1 = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="a", path_family_id="pa")
    r2 = make_delivery_receipt(live_send_gate_report=gate, sequence=2, previous_digest=r1.receipt_digest, family_id="b", path_family_id="pb")
    witness = assess_delivery_witness(live_send_gate_report=gate, receipts=(r1, r2), previous_digest=r1.previous_digest)
    m1 = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    m2 = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=witness, sequence=2, previous_digest=m1.marker_digest, family_id="b", path_family_id="pb")
    fence = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=witness, markers=(m1, m2), previous_digest=m1.previous_digest)
    assert fence.decision_kind is SendFenceDecisionKind.ACCEPT_DELIVERED_FENCE
    assert fence.accept

    pending = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=None, markers=())
    assert pending.decision_kind is SendFenceDecisionKind.HOLD_PENDING_DELIVERY
    assert pending.watch


def test_send_fence_rejects_marker_replay_and_boundary_drift() -> None:
    gate = accepted_gate()
    r1 = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="a", path_family_id="pa")
    r2 = make_delivery_receipt(live_send_gate_report=gate, sequence=2, previous_digest=r1.receipt_digest, family_id="b", path_family_id="pb")
    witness = assess_delivery_witness(live_send_gate_report=gate, receipts=(r1, r2), previous_digest=r1.previous_digest)
    m = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    replay = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=witness, markers=(m,), seen_marker_digests=(m.marker_digest,))
    assert replay.decision_kind is SendFenceDecisionKind.QUARANTINE_REPLAY

    other_gate = report("other-gate")
    drift_marker = make_send_fence_marker(live_send_gate_report=other_gate, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    drift = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=witness, markers=(drift_marker,))
    assert drift.decision_kind is SendFenceDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_fenceaudit_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_fence_fold(root, revision="rev0060", artifact_stem=root.name)
    assert fold.status == "pass", fold.findings
