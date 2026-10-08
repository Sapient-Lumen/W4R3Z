from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.ackrepairjoin import assess_ack_repair_join
from i2p_dht_lab.deliveryrepair import assess_delivery_repair, make_delivery_repair_probe
from i2p_dht_lab.deliverywitness import assess_delivery_witness
from i2p_dht_lab.egressjournal import EgressJournalDecisionKind, EgressJournalEntryKind, assess_egress_journal, make_egress_journal_entry
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.lateack import LateAckDecisionKind, assess_late_ack, make_late_ack_observation
from i2p_dht_lab.lateackfold import audit_late_ack_fold
from i2p_dht_lab.liveegress import LiveEgressDecisionKind, LiveEgressIntentKind, assess_live_egress
from i2p_dht_lab.repairpruneguard import assess_repair_prune_guard
from i2p_dht_lab.retryfence import RetryFenceDecisionKind, assess_retry_fence, make_retry_fence_marker
from i2p_dht_lab.retrysettlement import RetrySettlementDecisionKind, RetrySettlementMarkerKind, assess_retry_settlement, make_retry_settlement_marker
from i2p_dht_lab.rollbackprobe import assess_rollback_probe, make_rollback_observation
from i2p_dht_lab.sendfence import assess_send_fence
from i2p_dht_lab.sideeffectjournal import SideEffectAction
from i2p_dht_lab.withdrawrepair import WithdrawRepairDecisionKind, assess_withdraw_repair, make_withdraw_repair_marker

PROFILE = "rev0063-profile"
SERVICE = "rev0063-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0063:scope")
REQUEST = sha256(DOMAIN + b":rev0063:request")
PAYLOAD = sha256(DOMAIN + b":rev0063:payload")
IDEM = sha256(DOMAIN + b":rev0063:idem")
SESSION = sha256(DOMAIN + b":rev0063:session")
DESTINATION = sha256(DOMAIN + b":rev0063:destination")
ENDPOINT = sha256(DOMAIN + b":rev0063:endpoint")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0063-test:" + label.encode())


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
    from i2p_dht_lab.livesendgate import assess_live_send_gate

    return assess_live_send_gate(
        canary_join_report=report("canary"),
        settlement_store_report=report("settlement-store"),
        tomb_repair_join_report=report("tomb-repair"),
        side_effect_journal_report=report("side-effect-journal"),
        outbox_drain_report=report("outbox-drain"),
        public_payload_bytes=512,
    )


def repair_stack(intent=LiveEgressIntentKind.RETRY_PUBLIC_SEND):
    gate = accepted_gate()
    witness = assess_delivery_witness(live_send_gate_report=gate, receipts=())
    send_fence = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=witness, markers=())
    p1 = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=witness, send_fence_report=send_fence, sequence=1, family_id="a", path_family_id="pa")
    p2 = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=witness, send_fence_report=send_fence, sequence=2, previous_digest=p1.probe_digest, family_id="b", path_family_id="pb")
    repair = assess_delivery_repair(live_send_gate_report=gate, delivery_witness_report=witness, send_fence_report=send_fence, probes=(p1, p2), previous_digest=p1.previous_digest)
    o1 = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=send_fence, sequence=1, family_id="a", path_family_id="pa")
    o2 = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=send_fence, sequence=2, previous_digest=o1.observation_digest, family_id="b", path_family_id="pb")
    rollback = assess_rollback_probe(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=send_fence, observations=(o1, o2), previous_digest=o1.previous_digest)
    egress = assess_live_egress(intent_kind=intent, live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, send_fence_report=send_fence, delivery_witness_report=witness, payload_bytes=512, retry_attempt=1)
    joined = assess_ack_repair_join(live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, live_egress_report=egress, send_fence_report=send_fence, delivery_witness_report=witness)
    m1 = make_retry_fence_marker(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, sequence=1, family_id="a", path_family_id="pa")
    m2 = make_retry_fence_marker(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, sequence=2, previous_digest=m1.marker_digest, family_id="b", path_family_id="pb")
    fence = assess_retry_fence(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, markers=(m1, m2), previous_digest=m1.previous_digest)
    return gate, witness, send_fence, repair, rollback, egress, joined, fence


def accepted_late_ack(gate, retry_fence):
    a1 = make_late_ack_observation(live_send_gate_report=gate, retry_fence_report=retry_fence, sequence=1, family_id="a", path_family_id="pa")
    a2 = make_late_ack_observation(live_send_gate_report=gate, retry_fence_report=retry_fence, sequence=2, previous_digest=a1.observation_digest, family_id="b", path_family_id="pb")
    return assess_late_ack(live_send_gate_report=gate, retry_fence_report=retry_fence, observations=(a1, a2), previous_digest=a1.previous_digest)


def test_late_ack_after_retry_fence_aborts_retry_and_journals_cleanly() -> None:
    gate, _, _, _, _, egress, _, retry_fence = repair_stack()
    assert egress.decision_kind is LiveEgressDecisionKind.ACCEPT_RETRY_READY
    assert retry_fence.decision_kind is RetryFenceDecisionKind.ACCEPT_RETRY_FENCED

    late = accepted_late_ack(gate, retry_fence)
    assert late.decision_kind is LateAckDecisionKind.ACCEPT_LATE_ACK_AFTER_RETRY_FENCE
    assert late.accept and late.watch and late.late_ack_present

    pending = assess_retry_settlement(retry_fence_report=retry_fence, live_egress_report=egress, late_ack_report=late)
    assert pending.decision_kind is RetrySettlementDecisionKind.HOLD_LATE_ACK_PENDING_ABORT_MARKER

    s1 = make_retry_settlement_marker(retry_fence_report=retry_fence, live_egress_report=egress, late_ack_report=late, kind=RetrySettlementMarkerKind.RETRY_ABORTED_BY_LATE_ACK, sequence=1, family_id="a", path_family_id="pa")
    s2 = make_retry_settlement_marker(retry_fence_report=retry_fence, live_egress_report=egress, late_ack_report=late, kind=RetrySettlementMarkerKind.RETRY_ABORTED_BY_LATE_ACK, sequence=2, previous_digest=s1.marker_digest, family_id="b", path_family_id="pb")
    settlement = assess_retry_settlement(retry_fence_report=retry_fence, live_egress_report=egress, late_ack_report=late, markers=(s1, s2), previous_digest=s1.previous_digest)
    assert settlement.decision_kind is RetrySettlementDecisionKind.ACCEPT_RETRY_ABORTED_BY_LATE_ACK
    assert settlement.terminal and settlement.aborted_by_late_ack and not settlement.retry_terminal

    j1 = make_egress_journal_entry(kind=EgressJournalEntryKind.LATE_ACK, sequence=1, base_report=settlement, late_ack_report=late, retry_settlement_report=settlement, family_id="a", path_family_id="pa")
    j2 = make_egress_journal_entry(kind=EgressJournalEntryKind.RETRY_SETTLEMENT, sequence=2, previous_digest=j1.entry_digest, base_report=settlement, late_ack_report=late, retry_settlement_report=settlement, family_id="b", path_family_id="pb")
    journal = assess_egress_journal(late_ack_report=late, retry_settlement_report=settlement, entries=(j1, j2), previous_digest=j1.previous_digest)
    assert journal.decision_kind is EgressJournalDecisionKind.ACCEPT_JOURNAL_COMPACTED
    assert journal.accept and journal.compacted and not journal.contradiction_retained


def test_retry_delivered_conflicts_with_late_ack_unless_contradiction_is_retained() -> None:
    gate, _, _, _, _, egress, _, retry_fence = repair_stack()
    late = accepted_late_ack(gate, retry_fence)
    s1 = make_retry_settlement_marker(retry_fence_report=retry_fence, live_egress_report=egress, late_ack_report=late, kind=RetrySettlementMarkerKind.RETRY_DELIVERED, sequence=1, family_id="a", path_family_id="pa")
    s2 = make_retry_settlement_marker(retry_fence_report=retry_fence, live_egress_report=egress, late_ack_report=late, kind=RetrySettlementMarkerKind.RETRY_DELIVERED, sequence=2, previous_digest=s1.marker_digest, family_id="b", path_family_id="pb")
    conflict = assess_retry_settlement(retry_fence_report=retry_fence, live_egress_report=egress, late_ack_report=late, markers=(s1, s2), previous_digest=s1.previous_digest)
    assert conflict.decision_kind is RetrySettlementDecisionKind.QUARANTINE_LATE_ACK_RETRY_CONFLICT

    # A toy external report can still force the journal to prove it retained contradiction evidence.
    forced = SimpleNamespace(**{**conflict.__dict__, "quarantined": False, "accept": True, "retry_terminal": True, "terminal": True})
    dropped = make_egress_journal_entry(kind=EgressJournalEntryKind.RETRY_SETTLEMENT, sequence=1, base_report=forced, late_ack_report=late, retry_settlement_report=forced, family_id="a", path_family_id="pa")
    dropped2 = make_egress_journal_entry(kind=EgressJournalEntryKind.COMPACTION_SUMMARY, sequence=2, previous_digest=dropped.entry_digest, base_report=forced, late_ack_report=late, retry_settlement_report=forced, family_id="b", path_family_id="pb")
    assert assess_egress_journal(late_ack_report=late, retry_settlement_report=forced, entries=(dropped, dropped2), previous_digest=dropped.previous_digest).decision_kind is EgressJournalDecisionKind.QUARANTINE_DROPPED_CONTRADICTION

    c1 = make_egress_journal_entry(kind=EgressJournalEntryKind.CONTRADICTION, sequence=1, base_report=forced, late_ack_report=late, retry_settlement_report=forced, family_id="a", path_family_id="pa")
    c2 = make_egress_journal_entry(kind=EgressJournalEntryKind.COMPACTION_SUMMARY, sequence=2, previous_digest=c1.entry_digest, base_report=forced, late_ack_report=late, retry_settlement_report=forced, family_id="b", path_family_id="pb")
    retained = assess_egress_journal(late_ack_report=late, retry_settlement_report=forced, entries=(c1, c2), previous_digest=c1.previous_digest)
    assert retained.decision_kind is EgressJournalDecisionKind.ACCEPT_JOURNAL_RETAINS_CONTRADICTION


def test_retry_delivered_without_late_ack_settles_independently() -> None:
    _, _, _, _, _, egress, _, retry_fence = repair_stack()
    m1 = make_retry_settlement_marker(retry_fence_report=retry_fence, live_egress_report=egress, kind=RetrySettlementMarkerKind.RETRY_DELIVERED, sequence=1, family_id="a", path_family_id="pa")
    m2 = make_retry_settlement_marker(retry_fence_report=retry_fence, live_egress_report=egress, kind=RetrySettlementMarkerKind.RETRY_DELIVERED, sequence=2, previous_digest=m1.marker_digest, family_id="b", path_family_id="pb")
    settled = assess_retry_settlement(retry_fence_report=retry_fence, live_egress_report=egress, markers=(m1, m2), previous_digest=m1.previous_digest)
    assert settled.decision_kind is RetrySettlementDecisionKind.ACCEPT_RETRY_DELIVERED
    assert settled.retry_terminal and settled.terminal


def test_withdraw_repair_publication_memory_is_separate() -> None:
    _, _, _, _, _, egress, _, retry_fence = repair_stack(intent=LiveEgressIntentKind.WITHDRAW_PUBLIC_RECORD)
    assert egress.decision_kind is LiveEgressDecisionKind.ACCEPT_WITHDRAW_READY
    s1 = make_retry_settlement_marker(retry_fence_report=retry_fence, live_egress_report=egress, kind=RetrySettlementMarkerKind.WITHDRAW_REPAIRED, sequence=1, family_id="a", path_family_id="pa")
    s2 = make_retry_settlement_marker(retry_fence_report=retry_fence, live_egress_report=egress, kind=RetrySettlementMarkerKind.WITHDRAW_REPAIRED, sequence=2, previous_digest=s1.marker_digest, family_id="b", path_family_id="pb")
    settlement = assess_retry_settlement(retry_fence_report=retry_fence, live_egress_report=egress, markers=(s1, s2), previous_digest=s1.previous_digest)
    assert settlement.decision_kind is RetrySettlementDecisionKind.ACCEPT_WITHDRAW_REPAIRED

    w1 = make_withdraw_repair_marker(retry_settlement_report=settlement, live_egress_report=egress, sequence=1, family_id="a", path_family_id="pa")
    w2 = make_withdraw_repair_marker(retry_settlement_report=settlement, live_egress_report=egress, sequence=2, previous_digest=w1.marker_digest, family_id="b", path_family_id="pb")
    withdraw = assess_withdraw_repair(retry_settlement_report=settlement, live_egress_report=egress, markers=(w1, w2), previous_digest=w1.previous_digest)
    assert withdraw.decision_kind is WithdrawRepairDecisionKind.ACCEPT_WITHDRAW_REPAIR_TERMINAL

    j1 = make_egress_journal_entry(kind=EgressJournalEntryKind.WITHDRAW_REPAIR, sequence=1, base_report=withdraw, retry_settlement_report=settlement, withdraw_repair_report=withdraw, family_id="a", path_family_id="pa")
    j2 = make_egress_journal_entry(kind=EgressJournalEntryKind.COMPACTION_SUMMARY, sequence=2, previous_digest=j1.entry_digest, base_report=withdraw, retry_settlement_report=settlement, withdraw_repair_report=withdraw, family_id="b", path_family_id="pb")
    journal = assess_egress_journal(retry_settlement_report=settlement, withdraw_repair_report=withdraw, entries=(j1, j2), previous_digest=j1.previous_digest)
    assert journal.decision_kind is EgressJournalDecisionKind.ACCEPT_JOURNAL_COMPACTED


def test_lateackfold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_late_ack_fold(root, revision="rev0063", artifact_stem=root.name)
    assert fold.status == "pass", fold.findings
