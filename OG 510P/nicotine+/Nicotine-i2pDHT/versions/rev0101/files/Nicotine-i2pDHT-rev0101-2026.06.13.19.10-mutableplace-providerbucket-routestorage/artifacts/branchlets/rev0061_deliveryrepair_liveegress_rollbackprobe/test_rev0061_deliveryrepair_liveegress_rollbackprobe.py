from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.deliveryrepair import DeliveryRepairDecisionKind, DeliveryRepairProbeKind, assess_delivery_repair, make_delivery_repair_probe
from i2p_dht_lab.deliverywitness import assess_delivery_witness, make_delivery_receipt
from i2p_dht_lab.egressfold import audit_egress_fold
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.liveegress import LiveEgressDecisionKind, LiveEgressIntentKind, assess_live_egress, derive_retry_idempotency_key
from i2p_dht_lab.livesendgate import assess_live_send_gate
from i2p_dht_lab.rollbackprobe import RollbackProbeDecisionKind, RollbackProbeObservationKind, assess_rollback_probe, make_rollback_observation
from i2p_dht_lab.sendfence import SendFenceDecisionKind, assess_send_fence, make_send_fence_marker
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0061-profile"
SERVICE = "rev0061-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0061:scope")
REQUEST = sha256(DOMAIN + b":rev0061:request")
PAYLOAD = sha256(DOMAIN + b":rev0061:payload")
IDEM = sha256(DOMAIN + b":rev0061:idem")
SESSION = sha256(DOMAIN + b":rev0061:session")
DESTINATION = sha256(DOMAIN + b":rev0061:destination")
ENDPOINT = sha256(DOMAIN + b":rev0061:endpoint")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0061-test:" + label.encode())


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
        side_effect_journal_report=report("journal"),
        outbox_drain_report=report("outbox"),
        public_payload_bytes=512,
    )


def pending_components():
    gate = accepted_gate()
    delivery = assess_delivery_witness(live_send_gate_report=gate, receipts=())
    fence = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=delivery, markers=())
    assert delivery.watch
    assert fence.decision_kind is SendFenceDecisionKind.HOLD_PENDING_DELIVERY
    return gate, delivery, fence


def accepted_repair():
    gate, delivery, fence = pending_components()
    p1 = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, sequence=1, family_id="a", path_family_id="pa")
    p2 = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, sequence=2, previous_digest=p1.probe_digest, family_id="b", path_family_id="pb")
    repair = assess_delivery_repair(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, probes=(p1, p2), previous_digest=p1.probe_digest)
    assert repair.accept
    return gate, delivery, fence, repair


def accepted_rollback():
    gate, delivery, fence, repair = accepted_repair()
    o1 = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, sequence=1, family_id="a", path_family_id="pa")
    o2 = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, sequence=2, previous_digest=o1.observation_digest, family_id="b", path_family_id="pb")
    rollback = assess_rollback_probe(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, observations=(o1, o2), previous_digest=o1.observation_digest)
    assert rollback.accept
    return gate, delivery, fence, repair, rollback


def test_delivery_repair_accepts_missing_ack_probe() -> None:
    gate, delivery, fence, repair = accepted_repair()
    assert repair.decision_kind is DeliveryRepairDecisionKind.ACCEPT_REPAIR_PROBE
    assert repair.live_send_gate_digest == gate.report_digest
    assert repair.delivery_witness_digest == delivery.report_digest
    assert repair.send_fence_digest == fence.report_digest


def test_delivery_repair_holds_delivered_and_catches_drift_replay_fork() -> None:
    gate = accepted_gate()
    r1 = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="a", path_family_id="pa")
    r2 = make_delivery_receipt(live_send_gate_report=gate, sequence=2, previous_digest=r1.receipt_digest, family_id="b", path_family_id="pb")
    delivered = assess_delivery_witness(live_send_gate_report=gate, receipts=(r1, r2), previous_digest=r1.previous_digest)
    m1 = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=delivered, sequence=1, family_id="a", path_family_id="pa")
    m2 = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=delivered, sequence=2, previous_digest=m1.marker_digest, family_id="b", path_family_id="pb")
    fenced = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=delivered, markers=(m1, m2), previous_digest=m1.previous_digest)
    held = assess_delivery_repair(live_send_gate_report=gate, delivery_witness_report=delivered, send_fence_report=fenced)
    assert held.decision_kind is DeliveryRepairDecisionKind.HOLD_ALREADY_DELIVERED

    gate, delivery, fence = pending_components()
    p = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, sequence=1)
    replay = assess_delivery_repair(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, probes=(p,), seen_probe_digests=(p.probe_digest,))
    assert replay.decision_kind is DeliveryRepairDecisionKind.QUARANTINE_REPLAY
    fork = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, sequence=1, family_id="b", path_family_id="pb")
    assert assess_delivery_repair(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, probes=(p, fork)).decision_kind is DeliveryRepairDecisionKind.QUARANTINE_SEQUENCE_FORK
    drift = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=report("different-fence"), sequence=1)
    assert assess_delivery_repair(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, probes=(drift,)).decision_kind is DeliveryRepairDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT


def test_delivery_repair_accepts_withdraw_variant() -> None:
    gate, delivery, fence = pending_components()
    p1 = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, sequence=1, kind=DeliveryRepairProbeKind.WITHDRAW_PUBLIC_RECORD, family_id="a", path_family_id="pa")
    p2 = make_delivery_repair_probe(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, sequence=2, kind=DeliveryRepairProbeKind.WITHDRAW_PUBLIC_RECORD, previous_digest=p1.probe_digest, family_id="b", path_family_id="pb")
    repair = assess_delivery_repair(live_send_gate_report=gate, delivery_witness_report=delivery, send_fence_report=fence, probes=(p1, p2), previous_digest=p1.probe_digest)
    assert repair.decision_kind is DeliveryRepairDecisionKind.ACCEPT_WITHDRAW_REPAIR


def test_rollback_probe_accepts_no_remote_commit_and_rejects_commit() -> None:
    gate, delivery, fence, repair, rollback = accepted_rollback()
    assert rollback.decision_kind is RollbackProbeDecisionKind.ACCEPT_NO_REMOTE_COMMIT
    assert rollback.accept

    commit = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, kind=RollbackProbeObservationKind.REMOTE_COMMIT_SEEN, sequence=1, family_id="a", path_family_id="pa")
    no_commit = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, sequence=2, previous_digest=commit.observation_digest, family_id="b", path_family_id="pb")
    danger = assess_rollback_probe(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, observations=(commit, no_commit), previous_digest=commit.observation_digest)
    assert danger.decision_kind is RollbackProbeDecisionKind.QUARANTINE_REMOTE_COMMIT_SEEN

    unreachable = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, kind=RollbackProbeObservationKind.ENDPOINT_UNREACHABLE, sequence=1, family_id="a", path_family_id="pa")
    held = assess_rollback_probe(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, observations=(unreachable,), min_family_count=1, min_path_family_count=1)
    assert held.decision_kind is RollbackProbeDecisionKind.HOLD_UNREACHABLE
    assert delivery.watch


def test_live_egress_accepts_retry_only_after_repair_and_rollback() -> None:
    gate, delivery, fence, repair, rollback = accepted_rollback()
    egress = assess_live_egress(intent_kind=LiveEgressIntentKind.RETRY_PUBLIC_SEND, live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, send_fence_report=fence, delivery_witness_report=delivery, payload_bytes=512, retry_attempt=1)
    assert egress.decision_kind is LiveEgressDecisionKind.ACCEPT_RETRY_READY
    assert egress.accept
    assert egress.retry_idempotency_key == derive_retry_idempotency_key(live_send_gate_report=gate, retry_attempt=1)
    assert egress.retry_idempotency_key != gate.idempotency_key


def test_live_egress_blocks_duplicate_delivered_budget_and_bad_rollback() -> None:
    gate, delivery, fence, repair, rollback = accepted_rollback()
    over = assess_live_egress(intent_kind=LiveEgressIntentKind.RETRY_PUBLIC_SEND, live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, send_fence_report=fence, delivery_witness_report=delivery, payload_bytes=4096, max_payload_bytes=1024)
    assert over.decision_kind is LiveEgressDecisionKind.QUARANTINE_PAYLOAD_BUDGET_EXCEEDED
    exhausted = assess_live_egress(intent_kind=LiveEgressIntentKind.RETRY_PUBLIC_SEND, live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, send_fence_report=fence, delivery_witness_report=delivery, retry_attempt=4, max_retry_attempts=3)
    assert exhausted.decision_kind is LiveEgressDecisionKind.HOLD_RETRY_BUDGET_EXHAUSTED
    bad_idem = assess_live_egress(intent_kind=LiveEgressIntentKind.RETRY_PUBLIC_SEND, live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=rollback, send_fence_report=fence, delivery_witness_report=delivery, retry_idempotency_key=gate.idempotency_key)
    assert bad_idem.decision_kind is LiveEgressDecisionKind.QUARANTINE_IDEMPOTENCY_DRIFT

    commit = make_rollback_observation(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, kind=RollbackProbeObservationKind.REMOTE_COMMIT_SEEN, sequence=1, family_id="a", path_family_id="pa")
    commit_report = assess_rollback_probe(live_send_gate_report=gate, delivery_repair_report=repair, send_fence_report=fence, observations=(commit,), min_family_count=1, min_path_family_count=1)
    blocked = assess_live_egress(intent_kind=LiveEgressIntentKind.RETRY_PUBLIC_SEND, live_send_gate_report=gate, delivery_repair_report=repair, rollback_probe_report=commit_report, send_fence_report=fence, delivery_witness_report=delivery)
    assert blocked.decision_kind is LiveEgressDecisionKind.QUARANTINE_REMOTE_COMMIT_SEEN


def test_egressfold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_egress_fold(root, revision="rev0061", artifact_stem=root.name)
    assert fold.status == "pass", fold.findings
