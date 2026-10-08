from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.deliveryrepairmesh import (
    DeliveryRepairMeshDecisionKind,
    RemoteDeliveryWitnessKind,
    assess_delivery_repair_mesh,
    make_remote_delivery_witness,
)
from i2p_dht_lab.egressjournal import EgressJournalDecisionKind
from i2p_dht_lab.idempotencymesh import (
    IdempotencyMeshDecisionKind,
    IdempotencyObservationKind,
    assess_idempotency_mesh,
    make_idempotency_observation,
)
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.retrypublish import (
    RetryPublishDecisionKind,
    RetryPublishIntentKind,
    assess_retry_publish,
    make_retry_publish_marker,
)
from i2p_dht_lab.retrypublishfold import audit_retry_publish_fold
from i2p_dht_lab.retrysettlement import RetrySettlementDecisionKind
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0064-profile"
SERVICE = "rev0064-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0064:scope")
REQUEST = sha256(DOMAIN + b":rev0064:request")
PAYLOAD = sha256(DOMAIN + b":rev0064:payload")
IDEM = sha256(DOMAIN + b":rev0064:idem")
RETRY_IDEM = sha256(DOMAIN + b":rev0064:retry-idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0064-test:" + label.encode())


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


def retry_settlement(*, retry_terminal: bool = False, aborted: bool = False, withdraw: bool = False, pending: bool = False, label: str = "settlement"):
    if retry_terminal:
        kind = RetrySettlementDecisionKind.ACCEPT_RETRY_DELIVERED
    elif aborted:
        kind = RetrySettlementDecisionKind.ACCEPT_RETRY_ABORTED_BY_LATE_ACK
    elif withdraw:
        kind = RetrySettlementDecisionKind.ACCEPT_WITHDRAW_REPAIRED
    else:
        kind = RetrySettlementDecisionKind.HOLD_RETRY_PENDING
    return report(
        label,
        decision_kind=kind,
        terminal=retry_terminal or aborted or withdraw,
        retry_terminal=retry_terminal,
        withdraw_terminal=withdraw,
        aborted_by_late_ack=aborted,
        retry_pending=pending,
        accepted_marker_digest=d(label + ":marker"),
    )


def egress_journal(*, contradiction_retained: bool = False, label: str = "egress-journal"):
    return report(
        label,
        decision_kind=EgressJournalDecisionKind.ACCEPT_JOURNAL_RETAINS_CONTRADICTION if contradiction_retained else EgressJournalDecisionKind.ACCEPT_JOURNAL_COMPACTED,
        compacted=True,
        contradiction_retained=contradiction_retained,
        pending=False,
        accepted_entry_digest=d(label + ":entry"),
    )


def late_ack(*, present: bool = True, label: str = "late-ack"):
    return report(label, late_ack_present=present, accepted_observation_digest=d(label + ":obs"))


def accepted_retry_publish(settlement, journal):
    p1 = make_retry_publish_marker(retry_settlement_report=settlement, egress_journal_report=journal, intent_kind=RetryPublishIntentKind.RETRY_PUBLIC_RECORD, sequence=1, family_id="a", path_family_id="pa")
    p2 = make_retry_publish_marker(retry_settlement_report=settlement, egress_journal_report=journal, intent_kind=RetryPublishIntentKind.RETRY_PUBLIC_RECORD, sequence=2, previous_digest=p1.marker_digest, family_id="b", path_family_id="pb")
    return assess_retry_publish(retry_settlement_report=settlement, egress_journal_report=journal, markers=(p1, p2), previous_digest=p1.previous_digest)


def idempotency_obs_pair(*, base, kind1, kind2, late=None, settlement=None, publish=None, journal=None):
    i1 = make_idempotency_observation(kind=kind1, sequence=1, base_report=base, late_ack_report=late, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, family_id="a", path_family_id="pa")
    i2 = make_idempotency_observation(kind=kind2, sequence=2, previous_digest=i1.observation_digest, base_report=base, late_ack_report=late, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, family_id="b", path_family_id="pb")
    return i1, i2


def test_retry_delivered_stages_publication_and_mesh_accepts_retry_only() -> None:
    settlement = retry_settlement(retry_terminal=True)
    journal = egress_journal()
    publish = accepted_retry_publish(settlement, journal)
    assert publish.decision_kind is RetryPublishDecisionKind.ACCEPT_RETRY_PUBLICATION_STAGED
    assert publish.accept and publish.retry_staged

    obs = idempotency_obs_pair(base=settlement, kind1=IdempotencyObservationKind.RETRY_SETTLEMENT, kind2=IdempotencyObservationKind.RETRY_PUBLICATION, settlement=settlement, publish=publish, journal=journal)
    mesh = assess_idempotency_mesh(retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, observations=obs, previous_digest=obs[0].previous_digest)
    assert mesh.decision_kind is IdempotencyMeshDecisionKind.ACCEPT_RETRY_ONLY_LINEAGE
    assert mesh.accept and mesh.retry_lineage_terminal and not mesh.duplicate_delivery_possible

    repair = assess_delivery_repair_mesh(idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal)
    assert repair.decision_kind is DeliveryRepairMeshDecisionKind.ACCEPT_RETRY_PUBLICATION_READY
    assert repair.retry_publication_ready and not repair.repair_required


def test_late_ack_aborts_retry_and_suppresses_publication_without_repair() -> None:
    settlement = retry_settlement(aborted=True)
    journal = egress_journal()
    late = late_ack()
    publish = assess_retry_publish(retry_settlement_report=settlement, egress_journal_report=journal)
    assert publish.decision_kind is RetryPublishDecisionKind.HOLD_RETRY_SUPPRESSED_BY_LATE_ACK
    assert publish.retry_suppressed and publish.watch

    obs = idempotency_obs_pair(base=settlement, kind1=IdempotencyObservationKind.ORIGINAL_ACK, kind2=IdempotencyObservationKind.RETRY_SETTLEMENT, late=late, settlement=settlement, publish=publish, journal=journal)
    mesh = assess_idempotency_mesh(late_ack_report=late, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, observations=obs, previous_digest=obs[0].previous_digest)
    assert mesh.decision_kind is IdempotencyMeshDecisionKind.ACCEPT_ORIGINAL_ACK_SUPPRESSED_RETRY
    assert mesh.accept and mesh.original_lineage_terminal

    repair = assess_delivery_repair_mesh(idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal)
    assert repair.decision_kind is DeliveryRepairMeshDecisionKind.ACCEPT_NO_REPAIR_NEEDED


def test_duplicate_late_ack_and_retry_terminal_requires_remote_witness_then_accepts_benign() -> None:
    settlement = retry_settlement(retry_terminal=True)
    journal = egress_journal(contradiction_retained=True)
    late = late_ack()
    publish = accepted_retry_publish(settlement, journal)
    obs = idempotency_obs_pair(base=settlement, kind1=IdempotencyObservationKind.CONTRADICTION, kind2=IdempotencyObservationKind.RETRY_PUBLICATION, late=late, settlement=settlement, publish=publish, journal=journal)
    mesh = assess_idempotency_mesh(late_ack_report=late, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, observations=obs, previous_digest=obs[0].previous_digest)
    assert mesh.decision_kind is IdempotencyMeshDecisionKind.HOLD_DUPLICATE_DELIVERY_INVESTIGATION
    assert mesh.watch and mesh.duplicate_delivery_possible

    held = assess_delivery_repair_mesh(idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal)
    assert held.decision_kind is DeliveryRepairMeshDecisionKind.HOLD_DUPLICATE_DELIVERY_REQUIRES_REMOTE_WITNESS

    w1 = make_remote_delivery_witness(kind=RemoteDeliveryWitnessKind.REMOTE_MATCHES_PAYLOAD, sequence=1, idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, family_id="a", path_family_id="pa")
    w2 = make_remote_delivery_witness(kind=RemoteDeliveryWitnessKind.REMOTE_MATCHES_PAYLOAD, sequence=2, previous_digest=w1.witness_digest, idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, family_id="b", path_family_id="pb")
    benign = assess_delivery_repair_mesh(idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, remote_witnesses=(w1, w2), previous_digest=w1.previous_digest)
    assert benign.decision_kind is DeliveryRepairMeshDecisionKind.ACCEPT_DUPLICATE_BENIGN_WITH_WITNESS
    assert benign.accept and benign.duplicate_benign


def test_remote_duplicate_conflict_requires_repair_and_preserves_watch() -> None:
    settlement = retry_settlement(retry_terminal=True)
    journal = egress_journal(contradiction_retained=True)
    late = late_ack()
    publish = accepted_retry_publish(settlement, journal)
    obs = idempotency_obs_pair(base=settlement, kind1=IdempotencyObservationKind.CONTRADICTION, kind2=IdempotencyObservationKind.RETRY_PUBLICATION, late=late, settlement=settlement, publish=publish, journal=journal)
    mesh = assess_idempotency_mesh(late_ack_report=late, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, observations=obs, previous_digest=obs[0].previous_digest)

    w1 = make_remote_delivery_witness(kind=RemoteDeliveryWitnessKind.REMOTE_DUPLICATE_CONFLICT, sequence=1, idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, remote_state_digest=d("remote-conflict-a"), family_id="a", path_family_id="pa")
    w2 = make_remote_delivery_witness(kind=RemoteDeliveryWitnessKind.REMOTE_DUPLICATE_CONFLICT, sequence=2, previous_digest=w1.witness_digest, idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, remote_state_digest=d("remote-conflict-b"), family_id="b", path_family_id="pb")
    conflict = assess_delivery_repair_mesh(idempotency_mesh_report=mesh, retry_publish_report=publish, egress_journal_report=journal, remote_witnesses=(w1, w2), previous_digest=w1.previous_digest)
    assert conflict.decision_kind is DeliveryRepairMeshDecisionKind.ACCEPT_REPAIR_REQUIRED_REMOTE_CONFLICT
    assert conflict.accept and conflict.watch and conflict.repair_required and conflict.withdraw_repair_ready


def test_mesh_quarantines_payload_drift_even_when_components_are_valid() -> None:
    settlement = retry_settlement(retry_terminal=True)
    journal = egress_journal()
    publish = accepted_retry_publish(settlement, journal)
    o1 = make_idempotency_observation(kind=IdempotencyObservationKind.RETRY_SETTLEMENT, sequence=1, base_report=settlement, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, family_id="a", path_family_id="pa")
    drift_base = report("drift-base", payload_digest=d("other-payload"))
    o2 = make_idempotency_observation(kind=IdempotencyObservationKind.RETRY_PUBLICATION, sequence=2, previous_digest=o1.observation_digest, base_report=drift_base, retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, family_id="b", path_family_id="pb")
    drift = assess_idempotency_mesh(retry_settlement_report=settlement, retry_publish_report=publish, egress_journal_report=journal, observations=(o1, o2), previous_digest=ZERO_DIGEST)
    assert drift.decision_kind is IdempotencyMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_retrypublishfold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_retry_publish_fold(root, revision="rev0064", artifact_stem=root.name)
    assert fold.status == "pass", fold.findings
