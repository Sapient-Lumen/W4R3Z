from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.closurearchive import (
    ClosureArchiveDecisionKind,
    ClosureArchiveEntryKind,
    assess_closure_archive,
    make_closure_archive_entry,
)
from i2p_dht_lab.duplicateclosure import (
    DuplicateClosureDecisionKind,
    DuplicateClosureObservationKind,
    assess_duplicate_closure,
    make_duplicate_closure_observation,
)
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.repairackledger import RepairAckKind, assess_repair_ack_ledger, make_repair_ack_observation
from i2p_dht_lab.repairprune import (
    RepairPruneDecisionKind,
    RepairPruneProposalKind,
    assess_repair_prune,
    make_repair_prune_proposal,
)
from i2p_dht_lab.repairpublishgate import RepairPublishDecisionKind, RepairPublishIntentKind, assess_repair_publish_gate, make_repair_publish_marker
from i2p_dht_lab.repairsettlement import (
    RepairSettlementDecisionKind,
    RepairSettlementObservationKind,
    assess_repair_settlement,
    make_repair_settlement_observation,
)
from i2p_dht_lab.repairsettlementfold import audit_repair_settlement_fold
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0067-profile"
SERVICE = "rev0067-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0067:scope")
REQUEST = sha256(DOMAIN + b":rev0067:request")
PAYLOAD = sha256(DOMAIN + b":rev0067:payload")
IDEM = sha256(DOMAIN + b":rev0067:idem")
RETRY_IDEM = sha256(DOMAIN + b":rev0067:retry-idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0067-test:" + label.encode())


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
    p1 = make_repair_publish_marker(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, intent_kind=RepairPublishIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD, sequence=1, family_id="publish-a", path_family_id="path-a")
    p2 = make_repair_publish_marker(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, intent_kind=RepairPublishIntentKind.PUBLISH_REPAIR_NOTICE, sequence=2, previous_digest=p1.marker_digest, family_id="publish-b", path_family_id="path-b")
    publish = assess_repair_publish_gate(repair_outbox_report=outbox, conflict_cooldown_report=cooldown, markers=(p1, p2), previous_digest=p1.previous_digest)
    assert publish.decision_kind is RepairPublishDecisionKind.ACCEPT_REPAIR_PUBLISH_READY
    return publish


def accepted_ack(publish=None):
    publish = publish or accepted_publish()
    a1 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_ACKED, sequence=1, repair_publish_report=publish, family_id="ack-a", path_family_id="path-a")
    a2 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_ACKED, sequence=2, previous_digest=a1.ack_digest, repair_publish_report=publish, family_id="ack-b", path_family_id="path-b")
    ack = assess_repair_ack_ledger(repair_publish_report=publish, observations=(a1, a2), previous_digest=a1.previous_digest)
    assert ack.accept
    return ack


def accepted_closure(remote=None, outbox=None, cooldown=None, publish=None, ack=None):
    if remote is None or outbox is None or cooldown is None:
        remote, outbox, cooldown = conflict_components()
    publish = publish or accepted_publish(outbox, cooldown)
    ack = ack or accepted_ack(publish)
    c1 = make_duplicate_closure_observation(kind=DuplicateClosureObservationKind.REPAIR_ACKED, sequence=1, remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, family_id="close-a", path_family_id="path-a")
    c2 = make_duplicate_closure_observation(kind=DuplicateClosureObservationKind.REPAIR_ACKED, sequence=2, previous_digest=c1.observation_digest, remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, family_id="close-b", path_family_id="path-b")
    closure = assess_duplicate_closure(remote_witness_ledger_report=remote, repair_outbox_report=outbox, conflict_cooldown_report=cooldown, repair_publish_report=publish, repair_ack_ledger_report=ack, observations=(c1, c2), previous_digest=c1.previous_digest)
    assert closure.decision_kind is DuplicateClosureDecisionKind.ACCEPT_DUPLICATE_CONFLICT_REPAIRED
    return remote, outbox, cooldown, publish, ack, closure


def accepted_settlement(publish=None, ack=None, closure=None):
    if closure is None:
        _, _, _, publish, ack, closure = accepted_closure()
    s1 = make_repair_settlement_observation(kind=RepairSettlementObservationKind.DUPLICATE_CLOSURE_SETTLED, sequence=1, repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure, family_id="settle-a", path_family_id="path-a")
    s2 = make_repair_settlement_observation(kind=RepairSettlementObservationKind.DUPLICATE_CLOSURE_SETTLED, sequence=2, previous_digest=s1.observation_digest, repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure, family_id="settle-b", path_family_id="path-b")
    settlement = assess_repair_settlement(repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure, observations=(s1, s2), previous_digest=s1.previous_digest)
    assert settlement.decision_kind is RepairSettlementDecisionKind.ACCEPT_REPAIR_SETTLED
    return settlement


def accepted_archive(settlement=None):
    settlement = settlement or accepted_settlement()
    e1 = make_closure_archive_entry(kind=ClosureArchiveEntryKind.SETTLEMENT_ARCHIVED, sequence=1, repair_settlement_report=settlement, family_id="archive-a", path_family_id="path-a")
    e2 = make_closure_archive_entry(kind=ClosureArchiveEntryKind.CONTRADICTION_ARCHIVED, sequence=2, previous_digest=e1.entry_digest, repair_settlement_report=settlement, family_id="archive-b", path_family_id="path-b")
    archive = assess_closure_archive(repair_settlement_report=settlement, entries=(e1, e2), previous_digest=e1.previous_digest)
    assert archive.decision_kind is ClosureArchiveDecisionKind.ACCEPT_CLOSURE_ARCHIVED
    return archive


def test_repair_settlement_archive_and_prune_happy_path() -> None:
    settlement = accepted_settlement()
    archive = accepted_archive(settlement)
    p1 = make_repair_prune_proposal(kind=RepairPruneProposalKind.SOFT_REPAIR_TRACE_PRUNE, sequence=1, repair_settlement_report=settlement, closure_archive_report=archive, family_id="prune-a", path_family_id="path-a")
    p2 = make_repair_prune_proposal(kind=RepairPruneProposalKind.SOFT_REPAIR_TRACE_PRUNE, sequence=2, previous_digest=p1.proposal_digest, repair_settlement_report=settlement, closure_archive_report=archive, family_id="prune-b", path_family_id="path-b")
    prune = assess_repair_prune(repair_settlement_report=settlement, closure_archive_report=archive, proposals=(p1, p2), previous_digest=p1.previous_digest)
    assert prune.decision_kind is RepairPruneDecisionKind.ACCEPT_SOFT_REPAIR_PRUNE
    assert prune.accept and prune.soft_prune_allowed and prune.contradiction_preserved


def test_repair_settlement_holds_when_ack_is_mixed() -> None:
    remote, outbox, cooldown = conflict_components()
    publish = accepted_publish(outbox, cooldown)
    a1 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_ACKED, sequence=1, repair_publish_report=publish, family_id="ack-a", path_family_id="path-a")
    a2 = make_repair_ack_observation(kind=RepairAckKind.REPAIR_NACKED, sequence=2, previous_digest=a1.ack_digest, repair_publish_report=publish, family_id="ack-b", path_family_id="path-b")
    ack = assess_repair_ack_ledger(repair_publish_report=publish, observations=(a1, a2), previous_digest=a1.previous_digest)
    _, _, _, _, _, closure = accepted_closure(remote, outbox, cooldown, publish, accepted_ack(publish))
    settlement = assess_repair_settlement(repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure)
    assert settlement.decision_kind is RepairSettlementDecisionKind.HOLD_CLOSURE_PENDING
    assert settlement.watch and not settlement.accept


def test_repair_settlement_quarantines_when_contradiction_memory_drops() -> None:
    _, _, _, publish, ack, closure = accepted_closure()
    s1 = make_repair_settlement_observation(kind=RepairSettlementObservationKind.DUPLICATE_CLOSURE_SETTLED, sequence=1, repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure, contradiction_carried=False, family_id="settle-a", path_family_id="path-a")
    settlement = assess_repair_settlement(repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure, observations=(s1,), min_family_count=1, min_path_family_count=1)
    assert settlement.decision_kind is RepairSettlementDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_closure_archive_quarantines_missing_contradiction_entry() -> None:
    settlement = accepted_settlement()
    e1 = make_closure_archive_entry(kind=ClosureArchiveEntryKind.SETTLEMENT_ARCHIVED, sequence=1, repair_settlement_report=settlement, contradiction_archived=False, family_id="archive-a", path_family_id="path-a")
    e2 = make_closure_archive_entry(kind=ClosureArchiveEntryKind.SOFT_NOTE, sequence=2, previous_digest=e1.entry_digest, repair_settlement_report=settlement, contradiction_archived=False, family_id="archive-b", path_family_id="path-b")
    archive = assess_closure_archive(repair_settlement_report=settlement, entries=(e1, e2), previous_digest=e1.previous_digest)
    assert archive.decision_kind is ClosureArchiveDecisionKind.QUARANTINE_CONTRADICTION_NOT_ARCHIVED


def test_closure_archive_detects_same_sequence_fork() -> None:
    settlement = accepted_settlement()
    e1 = make_closure_archive_entry(kind=ClosureArchiveEntryKind.SETTLEMENT_ARCHIVED, sequence=1, repair_settlement_report=settlement, family_id="archive-a", path_family_id="path-a")
    e2 = make_closure_archive_entry(kind=ClosureArchiveEntryKind.CONTRADICTION_ARCHIVED, sequence=1, previous_digest=e1.previous_digest, repair_settlement_report=settlement, family_id="archive-b", path_family_id="path-b")
    archive = assess_closure_archive(repair_settlement_report=settlement, entries=(e1, e2), previous_digest=e1.previous_digest)
    assert archive.decision_kind is ClosureArchiveDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_repair_prune_blocks_contradiction_drop() -> None:
    settlement = accepted_settlement()
    archive = accepted_archive(settlement)
    p1 = make_repair_prune_proposal(kind=RepairPruneProposalKind.DROP_CONTRADICTION, sequence=1, repair_settlement_report=settlement, closure_archive_report=archive, family_id="prune-a", path_family_id="path-a")
    prune = assess_repair_prune(repair_settlement_report=settlement, closure_archive_report=archive, proposals=(p1,), min_family_count=1, min_path_family_count=1)
    assert prune.decision_kind is RepairPruneDecisionKind.QUARANTINE_FORBIDDEN_DROP
    assert not prune.soft_prune_allowed


def test_repair_prune_holds_until_archive_accepts() -> None:
    settlement = accepted_settlement()
    archive = SimpleNamespace(**{**accepted_archive(settlement).__dict__, "archived": False, "decision_kind": ClosureArchiveDecisionKind.HOLD_SETTLEMENT_PENDING})
    p1 = make_repair_prune_proposal(kind=RepairPruneProposalKind.SOFT_REPAIR_TRACE_PRUNE, sequence=1, repair_settlement_report=settlement, closure_archive_report=archive, family_id="prune-a", path_family_id="path-a")
    prune = assess_repair_prune(repair_settlement_report=settlement, closure_archive_report=archive, proposals=(p1,), min_family_count=1, min_path_family_count=1)
    assert prune.decision_kind is RepairPruneDecisionKind.HOLD_ARCHIVE_PENDING


def test_repairsettlement_fold_audit_passes() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    report = audit_repair_settlement_fold(root, revision="rev0067", artifact_stem=root.name)
    assert report.status == "pass"
