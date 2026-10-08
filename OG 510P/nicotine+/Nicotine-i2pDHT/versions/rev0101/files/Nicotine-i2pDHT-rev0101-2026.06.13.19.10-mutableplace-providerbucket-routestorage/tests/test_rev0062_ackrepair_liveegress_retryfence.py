from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.ackarchive import assess_ack_archive, make_ack_archive_entry
from i2p_dht_lab.ackprunejoin import assess_ack_prune_join
from i2p_dht_lab.ackrepairjoin import AckRepairJoinDecisionKind, assess_ack_repair_join
from i2p_dht_lab.deliveryrepair import assess_delivery_repair, make_delivery_repair_probe
from i2p_dht_lab.deliverysettlement import assess_delivery_settlement, make_delivery_settlement_marker
from i2p_dht_lab.deliverywitness import assess_delivery_witness, make_delivery_receipt
from i2p_dht_lab.egressrepairfold import audit_egress_repair_fold
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.liveegress import LiveEgressDecisionKind, LiveEgressIntentKind, assess_live_egress
from i2p_dht_lab.livesendgate import assess_live_send_gate
from i2p_dht_lab.repairpruneguard import RepairPruneGuardDecisionKind, assess_repair_prune_guard
from i2p_dht_lab.retryfence import RetryFenceDecisionKind, assess_retry_fence, make_retry_fence_marker
from i2p_dht_lab.rollbackprobe import RollbackProbeDecisionKind, RollbackProbeObservationKind, assess_rollback_probe, make_rollback_observation
from i2p_dht_lab.sendfence import assess_send_fence, make_send_fence_marker
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0062-profile"
SERVICE = "rev0062-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0062:scope")
REQUEST = sha256(DOMAIN + b":rev0062:request")
PAYLOAD = sha256(DOMAIN + b":rev0062:payload")
IDEM = sha256(DOMAIN + b":rev0062:idem")
SESSION = sha256(DOMAIN + b":rev0062:session")
DESTINATION = sha256(DOMAIN + b":rev0062:destination")
ENDPOINT = sha256(DOMAIN + b":rev0062:endpoint")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0062-test:" + label.encode())


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
    return assess_live_send_gate(
        canary_join_report=report("canary"),
        settlement_store_report=report("settlement-store"),
        tomb_repair_join_report=report("tomb-repair"),
        side_effect_journal_report=report("side-effect-journal"),
        outbox_drain_report=report("outbox-drain"),
        public_payload_bytes=512,
    )


def terminal_ack_path():
    gate = accepted_gate()
    r1 = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="a", path_family_id="pa")
    r2 = make_delivery_receipt(live_send_gate_report=gate, sequence=2, previous_digest=r1.receipt_digest, family_id="b", path_family_id="pb")
    witness = assess_delivery_witness(live_send_gate_report=gate, receipts=(r1, r2), previous_digest=r1.previous_digest)
    f1 = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    f2 = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=witness, sequence=2, previous_digest=f1.marker_digest, family_id="b", path_family_id="pb")
    fence = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=witness, markers=(f1, f2), previous_digest=f1.previous_digest)
    s1 = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    s2 = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=2, previous_digest=s1.marker_digest, family_id="b", path_family_id="pb")
    settlement = assess_delivery_settlement(send_fence_report=fence, delivery_witness_report=witness, markers=(s1, s2), previous_digest=s1.previous_digest)
    a1 = make_ack_archive_entry(delivery_settlement_report=settlement, sequence=1, family_id="a", path_family_id="pa")
    a2 = make_ack_archive_entry(delivery_settlement_report=settlement, sequence=2, previous_digest=a1.entry_digest, family_id="b", path_family_id="pb")
    archive = assess_ack_archive(delivery_settlement_report=settlement, entries=(a1, a2), previous_digest=a1.previous_digest)
    prune = assess_ack_prune_join(delivery_settlement_report=settlement, ack_archive_report=archive, send_fence_report=fence, delivery_witness_report=witness)
    return gate, witness, fence, settlement, archive, prune


def repair_path():
    gate = accepted_gate()
    witness = assess_delivery_witness(live_send_gate_report=gate, receipts=())
    fence = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=witness, markers=())
    p1 = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=witness, send_fence_report=fence, sequence=1, family_id="a", path_family_id="pa")
    p2 = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=witness, send_fence_report=fence, sequence=2, previous_digest=p1.probe_digest, family_id="b", path_family_id="pb")
    repair = assess_delivery_repair(live_send_gate_report=gate, delivery_witness_report=witness, send_fence_report=fence, probes=(p1, p2), previous_digest=p1.previous_digest)
    o1 = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, sequence=1, family_id="a", path_family_id="pa")
    o2 = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, sequence=2, previous_digest=o1.observation_digest, family_id="b", path_family_id="pb")
    rollback = assess_rollback_probe(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, observations=(o1, o2), previous_digest=o1.previous_digest)
    egress = assess_live_egress(intent_kind=LiveEgressIntentKind.RETRY_PUBLIC_SEND, live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, send_fence_report=fence, delivery_witness_report=witness, payload_bytes=512, retry_attempt=1)
    return gate, witness, fence, repair, rollback, egress


def test_ack_repair_join_accepts_terminal_ack_path() -> None:
    gate, witness, fence, settlement, archive, prune = terminal_ack_path()
    joined = assess_ack_repair_join(live_send_gate_report=gate, delivery_settlement_report=settlement, ack_archive_report=archive, ack_prune_join_report=prune, send_fence_report=fence, delivery_witness_report=witness)
    assert joined.decision_kind is AckRepairJoinDecisionKind.ACCEPT_TERMINAL_ACK_PATH
    assert joined.accept and joined.terminal and not joined.repair_allowed


def test_ack_repair_join_accepts_repair_path_and_blocks_terminal_conflict() -> None:
    gate, witness, fence, repair, rollback, egress = repair_path()
    joined = assess_ack_repair_join(live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, live_egress_report=egress, send_fence_report=fence, delivery_witness_report=witness)
    assert joined.decision_kind is AckRepairJoinDecisionKind.ACCEPT_RETRY_REPAIR_PATH
    assert joined.accept and joined.retry_allowed and joined.repair_allowed
    assert egress.decision_kind is LiveEgressDecisionKind.ACCEPT_RETRY_READY

    gate2, witness2, fence2, settlement, archive, prune = terminal_ack_path()
    # The repair reports are for the same boundary values.  That should be a hard conflict.
    conflict = assess_ack_repair_join(live_send_gate_report=gate2, delivery_settlement_report=settlement, ack_archive_report=archive, ack_prune_join_report=prune, delivery_repair_report=repair, rollback_probe_report=rollback, live_egress_report=egress, send_fence_report=fence2, delivery_witness_report=witness2)
    assert conflict.decision_kind is AckRepairJoinDecisionKind.QUARANTINE_ACK_REPAIR_CONFLICT


def test_ack_repair_join_quarantines_remote_commit_and_idempotency_collision() -> None:
    gate, witness, fence, repair, _, _ = repair_path()
    commit = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, kind=RollbackProbeObservationKind.REMOTE_COMMIT_SEEN, sequence=1, family_id="a", path_family_id="pa")
    rollback = assess_rollback_probe(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, observations=(commit,), min_family_count=1, min_path_family_count=1)
    assert rollback.decision_kind is RollbackProbeDecisionKind.QUARANTINE_REMOTE_COMMIT_SEEN
    egress = assess_live_egress(intent_kind=LiveEgressIntentKind.RETRY_PUBLIC_SEND, live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, send_fence_report=fence, delivery_witness_report=witness)
    joined = assess_ack_repair_join(live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, live_egress_report=egress, send_fence_report=fence, delivery_witness_report=witness)
    assert joined.decision_kind is AckRepairJoinDecisionKind.QUARANTINE_REMOTE_COMMIT_SEEN

    good_gate, good_witness, good_fence, good_repair, good_rollback, good_egress = repair_path()
    bad_egress = SimpleNamespace(**{**good_egress.__dict__, "retry_idempotency_key": good_gate.idempotency_key})
    bad_join = assess_ack_repair_join(live_send_gate_report=good_gate, delivery_repair_report=good_repair, rollback_probe_report=good_rollback, live_egress_report=bad_egress, send_fence_report=good_fence, delivery_witness_report=good_witness)
    assert bad_join.decision_kind is AckRepairJoinDecisionKind.QUARANTINE_RETRY_IDEMPOTENCY_COLLISION


def test_retry_fence_accepts_retry_and_rejects_replay_previous_and_collision() -> None:
    gate, witness, fence, repair, rollback, egress = repair_path()
    joined = assess_ack_repair_join(live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, live_egress_report=egress, send_fence_report=fence, delivery_witness_report=witness)
    m1 = make_retry_fence_marker(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, sequence=1, family_id="a", path_family_id="pa")
    m2 = make_retry_fence_marker(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, sequence=2, previous_digest=m1.marker_digest, family_id="b", path_family_id="pb")
    fenced = assess_retry_fence(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, markers=(m1, m2), previous_digest=m1.previous_digest)
    assert fenced.decision_kind is RetryFenceDecisionKind.ACCEPT_RETRY_FENCED
    assert fenced.accept and fenced.retry_fenced

    replay = assess_retry_fence(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, markers=(m1,), seen_marker_digests=(m1.marker_digest,))
    assert replay.decision_kind is RetryFenceDecisionKind.QUARANTINE_REPLAY
    prev = assess_retry_fence(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, markers=(m1,), previous_digest=d("wrong-prev"))
    assert prev.decision_kind is RetryFenceDecisionKind.QUARANTINE_PREVIOUS_MISMATCH

    collision = make_retry_fence_marker(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, sequence=1, family_id="a", path_family_id="pa")
    collision = SimpleNamespace(**{**collision.__dict__, "retry_idempotency_key": collision.original_idempotency_key, "marker_digest": d("not-used")})
    assert assess_retry_fence(ack_repair_join_report=joined, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, markers=(collision,), min_family_count=1, min_path_family_count=1).decision_kind is RetryFenceDecisionKind.QUARANTINE_IDEMPOTENCY_REUSE


def test_repair_prune_guard_separates_terminal_prune_from_repair_debt() -> None:
    gate, witness, fence, settlement, archive, prune = terminal_ack_path()
    terminal = assess_ack_repair_join(live_send_gate_report=gate, delivery_settlement_report=settlement, ack_archive_report=archive, ack_prune_join_report=prune, send_fence_report=fence, delivery_witness_report=witness)
    guard = assess_repair_prune_guard(ack_repair_join_report=terminal, ack_prune_join_report=prune)
    assert guard.decision_kind is RepairPruneGuardDecisionKind.ACCEPT_PRUNE_TERMINAL_ACK
    assert guard.prune_allowed and not guard.retain_repair_debt

    rgate, rwitness, rfence, repair, rollback, egress = repair_path()
    repair_join = assess_ack_repair_join(live_send_gate_report=rgate, delivery_repair_report=repair, rollback_probe_report=rollback, live_egress_report=egress, send_fence_report=rfence, delivery_witness_report=rwitness)
    pending = assess_repair_prune_guard(ack_repair_join_report=repair_join)
    assert pending.decision_kind is RepairPruneGuardDecisionKind.HOLD_REPAIR_FENCE_PENDING
    assert pending.retain_repair_debt

    m1 = make_retry_fence_marker(ack_repair_join_report=repair_join, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, sequence=1, family_id="a", path_family_id="pa")
    m2 = make_retry_fence_marker(ack_repair_join_report=repair_join, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, sequence=2, previous_digest=m1.marker_digest, family_id="b", path_family_id="pb")
    fence_report = assess_retry_fence(ack_repair_join_report=repair_join, live_egress_report=egress, delivery_repair_report=repair, rollback_probe_report=rollback, markers=(m1, m2), previous_digest=m1.previous_digest)
    guarded = assess_repair_prune_guard(ack_repair_join_report=repair_join, retry_fence_report=fence_report)
    assert guarded.decision_kind is RepairPruneGuardDecisionKind.ACCEPT_RETAIN_REPAIR_DEBT
    assert guarded.retain_repair_debt and not guarded.prune_allowed


def test_egress_repair_fold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_egress_repair_fold(root, revision="rev0062", artifact_stem=root.name)
    assert fold.status == "pass", fold.findings
