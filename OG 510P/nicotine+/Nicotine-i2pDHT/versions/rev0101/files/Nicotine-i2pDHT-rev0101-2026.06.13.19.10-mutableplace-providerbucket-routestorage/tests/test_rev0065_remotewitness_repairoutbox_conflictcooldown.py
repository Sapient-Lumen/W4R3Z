from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.deliveryrepairmesh import (
    DeliveryRepairMeshDecisionKind,
    RemoteDeliveryWitnessKind,
    assess_delivery_repair_mesh,
    make_remote_delivery_witness,
)
from i2p_dht_lab.egressjournal import EgressJournalDecisionKind
from i2p_dht_lab.idempotencymesh import IdempotencyMeshDecisionKind, IdempotencyObservationKind, assess_idempotency_mesh, make_idempotency_observation
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.remotewitnessledger import (
    RemoteWitnessLedgerDecisionKind,
    RemoteWitnessRoundKind,
    assess_remote_witness_ledger,
    make_remote_witness_round,
)
from i2p_dht_lab.repairoutbox import (
    RepairOutboxDecisionKind,
    RepairOutboxIntentKind,
    assess_repair_outbox,
    make_repair_outbox_marker,
)
from i2p_dht_lab.conflictcooldown import (
    ConflictCooldownDecisionKind,
    ConflictCooldownObservationKind,
    assess_conflict_cooldown,
    make_conflict_cooldown_observation,
)
from i2p_dht_lab.retrypublish import RetryPublishIntentKind, assess_retry_publish, make_retry_publish_marker
from i2p_dht_lab.retrysettlement import RetrySettlementDecisionKind
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0065-profile"
SERVICE = "rev0065-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0065:scope")
REQUEST = sha256(DOMAIN + b":rev0065:request")
PAYLOAD = sha256(DOMAIN + b":rev0065:payload")
IDEM = sha256(DOMAIN + b":rev0065:idem")
RETRY_IDEM = sha256(DOMAIN + b":rev0065:retry-idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0065-test:" + label.encode())


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
        retry_idempotency_key=RETRY_IDEM,
        hard_negative_count=0,
        family_count=2,
        path_family_count=2,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def retry_settlement(label: str = "settlement"):
    return report(
        label,
        decision_kind=RetrySettlementDecisionKind.ACCEPT_RETRY_DELIVERED,
        terminal=True,
        retry_terminal=True,
        withdraw_terminal=False,
        aborted_by_late_ack=False,
        retry_pending=False,
        accepted_marker_digest=d(label + ":marker"),
    )


def egress_journal(label: str = "journal", *, contradiction: bool = True):
    return report(
        label,
        decision_kind=EgressJournalDecisionKind.ACCEPT_JOURNAL_RETAINS_CONTRADICTION if contradiction else EgressJournalDecisionKind.ACCEPT_JOURNAL_COMPACTED,
        compacted=True,
        contradiction_retained=contradiction,
        pending=False,
        accepted_entry_digest=d(label + ":entry"),
    )


def accepted_retry_publish(settlement, journal):
    p1 = make_retry_publish_marker(retry_settlement_report=settlement, egress_journal_report=journal, intent_kind=RetryPublishIntentKind.RETRY_PUBLIC_RECORD, sequence=1, family_id="pub-a", path_family_id="path-a")
    p2 = make_retry_publish_marker(retry_settlement_report=settlement, egress_journal_report=journal, intent_kind=RetryPublishIntentKind.RETRY_PUBLIC_RECORD, sequence=2, previous_digest=p1.marker_digest, family_id="pub-b", path_family_id="path-b")
    return assess_retry_publish(retry_settlement_report=settlement, egress_journal_report=journal, markers=(p1, p2), previous_digest=p1.previous_digest)


def duplicate_idempotency_mesh(*, label: str = "dup", journal=None, settlement=None, publish=None, late=None):
    settlement = settlement or retry_settlement(label + ":settlement")
    journal = journal or egress_journal(label + ":journal", contradiction=True)
    publish = publish or accepted_retry_publish(settlement, journal)
    late = late or report(label + ":late", late_ack_present=True, accepted_observation_digest=d(label + ":lateobs"))
    o1 = make_idempotency_observation(kind=IdempotencyObservationKind.CONTRADICTION, sequence=1, base_report=settlement, late_ack_report=late, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, family_id="idem-a", path_family_id="path-a")
    o2 = make_idempotency_observation(kind=IdempotencyObservationKind.RETRY_PUBLICATION, sequence=2, previous_digest=o1.observation_digest, base_report=settlement, late_ack_report=late, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, family_id="idem-b", path_family_id="path-b")
    mesh = assess_idempotency_mesh(late_ack_report=late, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, observations=(o1, o2), previous_digest=o1.previous_digest)
    assert mesh.decision_kind is IdempotencyMeshDecisionKind.HOLD_DUPLICATE_DELIVERY_INVESTIGATION
    return settlement, journal, publish, mesh


def conflict_delivery_repair():
    settlement, journal, publish, mesh = duplicate_idempotency_mesh(label="conflict")
    w1 = make_remote_delivery_witness(kind=RemoteDeliveryWitnessKind.REMOTE_DUPLICATE_CONFLICT, sequence=1, idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, remote_state_digest=d("remote-conflict-a"), family_id="remote-a", path_family_id="path-a")
    w2 = make_remote_delivery_witness(kind=RemoteDeliveryWitnessKind.REMOTE_DUPLICATE_CONFLICT, sequence=2, previous_digest=w1.witness_digest, idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, remote_state_digest=d("remote-conflict-b"), family_id="remote-b", path_family_id="path-b")
    repair = assess_delivery_repair_mesh(idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, remote_witnesses=(w1, w2), previous_digest=w1.previous_digest)
    assert repair.decision_kind is DeliveryRepairMeshDecisionKind.ACCEPT_REPAIR_REQUIRED_REMOTE_CONFLICT
    return repair


def benign_delivery_repair():
    settlement, journal, publish, mesh = duplicate_idempotency_mesh(label="benign")
    w1 = make_remote_delivery_witness(kind=RemoteDeliveryWitnessKind.REMOTE_MATCHES_PAYLOAD, sequence=1, idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, family_id="remote-a", path_family_id="path-a")
    w2 = make_remote_delivery_witness(kind=RemoteDeliveryWitnessKind.REMOTE_MATCHES_PAYLOAD, sequence=2, previous_digest=w1.witness_digest, idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, family_id="remote-b", path_family_id="path-b")
    repair = assess_delivery_repair_mesh(idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, remote_witnesses=(w1, w2), previous_digest=w1.previous_digest)
    assert repair.decision_kind is DeliveryRepairMeshDecisionKind.ACCEPT_DUPLICATE_BENIGN_WITH_WITNESS
    return repair


def accepted_remote_conflict_ledger(repair=None):
    repair = repair or conflict_delivery_repair()
    r1 = make_remote_witness_round(kind=RemoteWitnessRoundKind.REMOTE_CONFLICT, sequence=1, delivery_repair_mesh_report=repair, family_id="round-a", path_family_id="path-a")
    r2 = make_remote_witness_round(kind=RemoteWitnessRoundKind.REMOTE_CONFLICT, sequence=2, previous_digest=r1.round_digest, delivery_repair_mesh_report=repair, family_id="round-b", path_family_id="path-b")
    ledger = assess_remote_witness_ledger(delivery_repair_mesh_report=repair, rounds=(r1, r2), previous_digest=r1.previous_digest)
    assert ledger.decision_kind is RemoteWitnessLedgerDecisionKind.ACCEPT_REMOTE_CONFLICT_ROUND
    return repair, ledger


def accepted_repair_outbox(repair=None, ledger=None):
    repair, ledger = (repair, ledger) if repair is not None and ledger is not None else accepted_remote_conflict_ledger()
    m1 = make_repair_outbox_marker(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, intent_kind=RepairOutboxIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD, sequence=1, family_id="repair-a", path_family_id="path-a")
    m2 = make_repair_outbox_marker(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, intent_kind=RepairOutboxIntentKind.PUBLISH_REPAIR_NOTICE, sequence=2, previous_digest=m1.marker_digest, family_id="repair-b", path_family_id="path-b")
    outbox = assess_repair_outbox(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, markers=(m1, m2), previous_digest=m1.previous_digest)
    assert outbox.decision_kind is RepairOutboxDecisionKind.ACCEPT_REPAIR_OUTBOX_STAGED
    return repair, ledger, outbox


def test_remote_conflict_rounds_stage_repair_outbox_and_start_cooldown() -> None:
    repair, ledger, outbox = accepted_repair_outbox()
    c1 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.REMOTE_CONFLICT, sequence=1, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="cool-a", path_family_id="path-a")
    c2 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.REPAIR_STAGED, sequence=2, previous_digest=c1.observation_digest, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="cool-b", path_family_id="path-b")
    c3 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.REMOTE_CONFLICT, sequence=3, previous_digest=c2.observation_digest, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="cool-c", path_family_id="path-c")
    cooldown = assess_conflict_cooldown(remote_witness_ledger_report=ledger, repair_outbox_report=outbox, observations=(c1, c2, c3), previous_digest=c1.previous_digest)
    assert cooldown.decision_kind is ConflictCooldownDecisionKind.ACCEPT_CONFLICT_COOLDOWN_ACTIVE
    assert cooldown.cooldown_active and cooldown.repair_allowed and cooldown.watch


def test_benign_remote_round_holds_outbox_and_releases_cooldown() -> None:
    repair = benign_delivery_repair()
    r1 = make_remote_witness_round(kind=RemoteWitnessRoundKind.BENIGN_DUPLICATE, sequence=1, delivery_repair_mesh_report=repair, family_id="round-a", path_family_id="path-a")
    r2 = make_remote_witness_round(kind=RemoteWitnessRoundKind.BENIGN_DUPLICATE, sequence=2, previous_digest=r1.round_digest, delivery_repair_mesh_report=repair, family_id="round-b", path_family_id="path-b")
    ledger = assess_remote_witness_ledger(delivery_repair_mesh_report=repair, rounds=(r1, r2), previous_digest=r1.previous_digest)
    assert ledger.decision_kind is RemoteWitnessLedgerDecisionKind.ACCEPT_BENIGN_DUPLICATE_ROUND
    outbox = assess_repair_outbox(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger)
    assert outbox.decision_kind is RepairOutboxDecisionKind.HOLD_NO_REPAIR_REQUIRED
    b1 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.BENIGN_WITNESS, sequence=1, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="cool-a", path_family_id="path-a")
    b2 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.BENIGN_WITNESS, sequence=2, previous_digest=b1.observation_digest, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="cool-b", path_family_id="path-b")
    released = assess_conflict_cooldown(remote_witness_ledger_report=ledger, repair_outbox_report=outbox, observations=(b1, b2), previous_digest=b1.previous_digest)
    assert released.decision_kind is ConflictCooldownDecisionKind.ACCEPT_RELEASE_AFTER_BENIGN
    assert released.released and not released.cooldown_active


def test_remote_witness_replay_across_rounds_quarantines() -> None:
    repair = conflict_delivery_repair()
    r1 = make_remote_witness_round(kind=RemoteWitnessRoundKind.REMOTE_CONFLICT, sequence=1, delivery_repair_mesh_report=repair, family_id="round-a", path_family_id="path-a")
    ledger = assess_remote_witness_ledger(delivery_repair_mesh_report=repair, rounds=(r1,), seen_round_digests=(r1.round_digest,), min_family_count=1, min_path_family_count=1)
    assert ledger.decision_kind is RemoteWitnessLedgerDecisionKind.QUARANTINE_REPLAY
    assert ledger.quarantined


def test_remote_conflict_that_drops_contradiction_memory_quarantines() -> None:
    repair = conflict_delivery_repair()
    r1 = make_remote_witness_round(kind=RemoteWitnessRoundKind.REMOTE_CONFLICT, sequence=1, delivery_repair_mesh_report=repair, contradiction_carried=False, family_id="round-a", path_family_id="path-a")
    r2 = make_remote_witness_round(kind=RemoteWitnessRoundKind.REMOTE_CONFLICT, sequence=2, previous_digest=r1.round_digest, delivery_repair_mesh_report=repair, contradiction_carried=True, family_id="round-b", path_family_id="path-b")
    ledger = assess_remote_witness_ledger(delivery_repair_mesh_report=repair, rounds=(r1, r2), previous_digest=r1.previous_digest)
    assert ledger.decision_kind is RemoteWitnessLedgerDecisionKind.QUARANTINE_CONTRADICTION_NOT_CARRIED


def test_repair_outbox_rejects_marker_digest_drift() -> None:
    repair, ledger = accepted_remote_conflict_ledger()
    good = make_repair_outbox_marker(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, intent_kind=RepairOutboxIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD, sequence=1, family_id="repair-a", path_family_id="path-a")
    bad = make_repair_outbox_marker(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, intent_kind=RepairOutboxIntentKind.PUBLISH_REPAIR_NOTICE, sequence=2, previous_digest=good.marker_digest, family_id="repair-b", path_family_id="path-b")
    bad = type(bad)(**{**bad.__dict__, "remote_witness_ledger_digest": d("wrong-ledger")})
    outbox = assess_repair_outbox(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, markers=(good, bad), previous_digest=good.previous_digest)
    assert outbox.decision_kind is RepairOutboxDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_repair_outbox_same_sequence_fork_quarantines() -> None:
    repair, ledger = accepted_remote_conflict_ledger()
    m1 = make_repair_outbox_marker(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, intent_kind=RepairOutboxIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD, sequence=1, family_id="repair-a", path_family_id="path-a")
    m2 = make_repair_outbox_marker(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, intent_kind=RepairOutboxIntentKind.PUBLISH_REPAIR_NOTICE, sequence=1, family_id="repair-b", path_family_id="path-b")
    outbox = assess_repair_outbox(delivery_repair_mesh_report=repair, remote_witness_ledger_report=ledger, markers=(m1, m2), previous_digest=m1.previous_digest)
    assert outbox.decision_kind is RepairOutboxDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_conflict_cooldown_rejects_cross_boundary_observation() -> None:
    repair, ledger, outbox = accepted_repair_outbox()
    c1 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.REMOTE_CONFLICT, sequence=1, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="cool-a", path_family_id="path-a")
    c2 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.REMOTE_CONFLICT, sequence=2, previous_digest=c1.observation_digest, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="cool-b", path_family_id="path-b")
    c2 = type(c2)(**{**c2.__dict__, "request_digest": d("wrong-request")})
    cooldown = assess_conflict_cooldown(remote_witness_ledger_report=ledger, repair_outbox_report=outbox, observations=(c1, c2), previous_digest=c1.previous_digest)
    assert cooldown.decision_kind is ConflictCooldownDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_conflict_cooldown_holds_low_diversity() -> None:
    repair, ledger, outbox = accepted_repair_outbox()
    c1 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.REMOTE_CONFLICT, sequence=1, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="same", path_family_id="same-path")
    c2 = make_conflict_cooldown_observation(kind=ConflictCooldownObservationKind.REMOTE_CONFLICT, sequence=2, previous_digest=c1.observation_digest, remote_witness_ledger_report=ledger, repair_outbox_report=outbox, family_id="same", path_family_id="same-path")
    cooldown = assess_conflict_cooldown(remote_witness_ledger_report=ledger, repair_outbox_report=outbox, observations=(c1, c2), previous_digest=c1.previous_digest)
    assert cooldown.decision_kind is ConflictCooldownDecisionKind.HOLD_LOW_FAMILY_DIVERSITY
