from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.duplicateclosure import (
    DuplicateClosureDecisionKind,
    DuplicateClosureObservationKind,
    assess_duplicate_closure,
    make_duplicate_closure_observation,
)
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.repairackledger import (
    RepairAckDecisionKind,
    RepairAckKind,
    assess_repair_ack_ledger,
    make_repair_ack_observation,
)
from i2p_dht_lab.repairpublishfold import audit_repair_publish_fold
from i2p_dht_lab.repairpublishgate import (
    RepairPublishDecisionKind,
    RepairPublishIntentKind,
    assess_repair_publish_gate,
    make_repair_publish_marker,
)
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0066-profile"
SERVICE = "rev0066-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0066:scope")
REQUEST = sha256(DOMAIN + b":rev0066:request")
PAYLOAD = sha256(DOMAIN + b":rev0066:payload")
IDEM = sha256(DOMAIN + b":rev0066:idem")
RETRY_IDEM = sha256(DOMAIN + b":rev0066:retry-idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0066-test:" + label.encode())


def component(label: str, **kw):
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


def conflict_components():
    remote = component("remote-ledger", conflict_memory=True, benign_memory=False, absent_or_mixed_memory=False, accepted_round_digest=d("round"))
    outbox = component("repair-outbox", staged=True, withdraw_staged=True, notice_staged=True, accepted_marker_digest=d("outbox-marker"))
    cooldown = component("conflict-cooldown", cooldown_active=True, repair_allowed=True, released=False, accepted_observation_digest=d("cooldown-obs"))
    return remote, outbox, cooldown


def accepted_publish(outbox=None, cooldown=None):
    if outbox is None or cooldown is None:
        _, outbox, cooldown = conflict_components()
    m1 = make_repair_publish_marker(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, intent_kind=RepairPublishIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD, sequence=1, family_id="publish-a", path_family_id="path-a")
    m2 = make_repair_publish_marker(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, intent_kind=RepairPublishIntentKind.PUBLISH_REPAIR_NOTICE, sequence=2, previous_digest=m1.marker_digest, family_id="publish-b", path_family_id="path-b")
    publish = assess_repair_publish_gate(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, markers=(m1, m2), previous_digest=m1.previous_digest)
    assert publish.decision_kind is RepairPublishDecisionKind.ACCEPT_REPAIR_PUBLISH_READY
    return publish


def accepted_ack(publish=None):
    publish = publish or accepted_publish()
    a1 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_ACKED, sequence=1, repair_publish_report=publish, family_id="ack-a", path_family_id="path-a")
    a2 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_ACKED, sequence=2, previous_digest=a1.ack_digest, repair_publish_report=publish, family_id="ack-b", path_family_id="path-b")
    ack = assess_repair_ack_ledger(repair_publish_report=publish, observations=(a1, a2), previous_digest=a1.previous_digest)
    assert ack.decision_kind is RepairAckDecisionKind.ACCEPT_REPAIR_ACKED
    return ack


def test_repair_publish_ack_and_duplicate_closure_happy_path() -> None:
    remote, outbox, cooldown = conflict_components()
    publish = accepted_publish(outbox, cooldown)
    ack = accepted_ack(publish)
    c1 = make_duplicate_closure_observation(kind=DuplicateClosureObservationKind.REPAIR_ACKED, sequence=1, remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, family_id="close-a", path_family_id="path-a")
    c2 = make_duplicate_closure_observation(kind=DuplicateClosureObservationKind.REPAIR_ACKED, sequence=2, previous_digest=c1.observation_digest, remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, family_id="close-b", path_family_id="path-b")
    closure = assess_duplicate_closure(remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, observations=(c1, c2), previous_digest=c1.previous_digest)
    assert closure.decision_kind is DuplicateClosureDecisionKind.ACCEPT_DUPLICATE_CONFLICT_REPAIRED
    assert closure.accept and closure.duplicate_repaired and closure.contradiction_preserved


def test_released_cooldown_blocks_repair_publication() -> None:
    _, outbox, cooldown = conflict_components()
    cooldown = component("released", cooldown_active=False, repair_allowed=False, released=True, accepted_observation_digest=d("released"))
    marker = make_repair_publish_marker(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, intent_kind=RepairPublishIntentKind.PUBLISH_REPAIR_NOTICE, sequence=1)
    publish = assess_repair_publish_gate(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, markers=(marker,), min_family_count=1, min_path_family_count=1)
    assert publish.decision_kind is RepairPublishDecisionKind.HOLD_RELEASED_NO_REPAIR
    assert not publish.repair_publish_ready


def test_repair_publish_rejects_component_digest_drift() -> None:
    _, outbox, cooldown = conflict_components()
    good = make_repair_publish_marker(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, intent_kind=RepairPublishIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD, sequence=1, family_id="publish-a", path_family_id="path-a")
    bad = make_repair_publish_marker(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, intent_kind=RepairPublishIntentKind.PUBLISH_REPAIR_NOTICE, sequence=2, previous_digest=good.marker_digest, family_id="publish-b", path_family_id="path-b")
    bad = type(bad)(**{**bad.__dict__, "conflict_cooldown_digest": d("wrong-cooldown")})
    publish = assess_repair_publish_gate(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, markers=(good, bad), previous_digest=good.previous_digest)
    assert publish.decision_kind is RepairPublishDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_repair_ack_ledger_holds_single_family_ack() -> None:
    publish = accepted_publish()
    a1 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_ACKED, sequence=1, repair_publish_report=publish, family_id="same", path_family_id="path-a")
    a2 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_ACKED, sequence=2, previous_digest=a1.ack_digest, repair_publish_report=publish, family_id="same", path_family_id="path-b")
    ack = assess_repair_ack_ledger(repair_publish_report=publish, observations=(a1, a2), previous_digest=a1.previous_digest)
    assert ack.decision_kind is RepairAckDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_repair_ack_nack_or_mixed_holds_not_closes() -> None:
    publish = accepted_publish()
    a1 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_ACKED, sequence=1, repair_publish_report=publish, family_id="ack-a", path_family_id="path-a")
    a2 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_NACKED, sequence=2, previous_digest=a1.ack_digest, repair_publish_report=publish, family_id="ack-b", path_family_id="path-b")
    ack = assess_repair_ack_ledger(repair_publish_report=publish, observations=(a1, a2), previous_digest=a1.previous_digest)
    assert ack.decision_kind is RepairAckDecisionKind.HOLD_NACK_OR_MIXED
    remote, outbox, cooldown = conflict_components()
    closure = assess_duplicate_closure(remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack)
    assert closure.decision_kind is DuplicateClosureDecisionKind.HOLD_REPAIR_ACK_PENDING


def test_duplicate_closure_rejects_dropped_contradiction_memory() -> None:
    remote, outbox, cooldown = conflict_components()
    publish = accepted_publish(outbox, cooldown)
    ack = accepted_ack(publish)
    c1 = make_duplicate_closure_observation(kind=DuplicateClosureObservationKind.REPAIR_ACKED, sequence=1, remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, contradiction_carried=False, family_id="close-a", path_family_id="path-a")
    c2 = make_duplicate_closure_observation(kind=DuplicateClosureObservationKind.REPAIR_ACKED, sequence=2, previous_digest=c1.observation_digest, remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, contradiction_carried=True, family_id="close-b", path_family_id="path-b")
    closure = assess_duplicate_closure(remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, observations=(c1, c2), previous_digest=c1.previous_digest)
    assert closure.decision_kind is DuplicateClosureDecisionKind.QUARANTINE_CONTRADICTION_NOT_CARRIED


def test_repairpublishfold_current_path_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_repair_publish_fold(root, revision="rev0066", artifact_stem=root.name)
    assert fold.status == "pass"
    assert fold.error_count == 0
