from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.archivejournal import (
    ArchiveJournalDecisionKind,
    ArchiveJournalEntryKind,
    assess_archive_journal,
    make_archive_journal_entry,
)
from i2p_dht_lab.archivejournalfold import audit_archive_journal_fold
from i2p_dht_lab.closurearchive import ClosureArchiveDecisionKind, ClosureArchiveEntryKind, assess_closure_archive, make_closure_archive_entry
from i2p_dht_lab.closureaudit import (
    ClosureAuditDecisionKind,
    ClosureAuditMarkerKind,
    assess_closure_audit,
    make_closure_audit_marker,
)
from i2p_dht_lab.duplicateclosure import DuplicateClosureDecisionKind, DuplicateClosureObservationKind, assess_duplicate_closure, make_duplicate_closure_observation
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.prunereplay import (
    PruneReplayDecisionKind,
    PruneReplayObservationKind,
    assess_prune_replay,
    make_prune_replay_observation,
)
from i2p_dht_lab.repairackledger import RepairAckKind, assess_repair_ack_ledger, make_repair_ack_observation
from i2p_dht_lab.repairprune import RepairPruneDecisionKind, RepairPruneProposalKind, assess_repair_prune, make_repair_prune_proposal
from i2p_dht_lab.repairpublishgate import RepairPublishDecisionKind, RepairPublishIntentKind, assess_repair_publish_gate, make_repair_publish_marker
from i2p_dht_lab.repairsettlement import RepairSettlementDecisionKind, RepairSettlementObservationKind, assess_repair_settlement, make_repair_settlement_observation
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0068-profile"
SERVICE = "rev0068-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0068:scope")
REQUEST = sha256(DOMAIN + b":rev0068:request")
PAYLOAD = sha256(DOMAIN + b":rev0068:payload")
IDEM = sha256(DOMAIN + b":rev0068:idem")
RETRY_IDEM = sha256(DOMAIN + b":rev0068:retry-idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0068-test:" + label.encode())


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


def accepted_settlement_archive_prune():
    _, _, _, publish, ack, closure = accepted_closure()
    s1 = make_repair_settlement_observation(kind=RepairSettlementObservationKind.DUPLICATE_CLOSURE_SETTLED, sequence=1, repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure, family_id="settle-a", path_family_id="path-a")
    s2 = make_repair_settlement_observation(kind=RepairSettlementObservationKind.DUPLICATE_CLOSURE_SETTLED, sequence=2, previous_digest=s1.observation_digest, repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure, family_id="settle-b", path_family_id="path-b")
    settlement = assess_repair_settlement(repair_publish_report=publish, repair_ack_ledger_report=ack, duplicate_closure_report=closure, observations=(s1, s2), previous_digest=s1.previous_digest)
    assert settlement.decision_kind is RepairSettlementDecisionKind.ACCEPT_REPAIR_SETTLED
    e1 = make_closure_archive_entry(kind=ClosureArchiveEntryKind.SETTLEMENT_ARCHIVED, sequence=1, repair_settlement_report=settlement, family_id="archive-a", path_family_id="path-a")
    e2 = make_closure_archive_entry(kind=ClosureArchiveEntryKind.CONTRADICTION_ARCHIVED, sequence=2, previous_digest=e1.entry_digest, repair_settlement_report=settlement, family_id="archive-b", path_family_id="path-b")
    archive = assess_closure_archive(repair_settlement_report=settlement, entries=(e1, e2), previous_digest=e1.previous_digest)
    assert archive.decision_kind is ClosureArchiveDecisionKind.ACCEPT_CLOSURE_ARCHIVED
    p1 = make_repair_prune_proposal(kind=RepairPruneProposalKind.SOFT_REPAIR_TRACE_PRUNE, sequence=1, repair_settlement_report=settlement, closure_archive_report=archive, family_id="prune-a", path_family_id="path-a")
    p2 = make_repair_prune_proposal(kind=RepairPruneProposalKind.SOFT_REPAIR_TRACE_PRUNE, sequence=2, previous_digest=p1.proposal_digest, repair_settlement_report=settlement, closure_archive_report=archive, family_id="prune-b", path_family_id="path-b")
    prune = assess_repair_prune(repair_settlement_report=settlement, closure_archive_report=archive, proposals=(p1, p2), previous_digest=p1.previous_digest)
    assert prune.decision_kind is RepairPruneDecisionKind.ACCEPT_SOFT_REPAIR_PRUNE
    return settlement, archive, prune


def accepted_archive_journal(settlement=None, archive=None, prune=None):
    if settlement is None or archive is None or prune is None:
        settlement, archive, prune = accepted_settlement_archive_prune()
    j1 = make_archive_journal_entry(kind=ArchiveJournalEntryKind.SETTLEMENT_ARCHIVE_PRUNE_JOURNALED, sequence=1, restart_generation=2, repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, family_id="journal-a", path_family_id="path-a")
    j2 = make_archive_journal_entry(kind=ArchiveJournalEntryKind.CONTRADICTION_MEMORY_JOURNALED, sequence=2, previous_digest=j1.entry_digest, restart_generation=2, repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, family_id="journal-b", path_family_id="path-b")
    journal = assess_archive_journal(repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, entries=(j1, j2), previous_digest=j1.previous_digest)
    assert journal.decision_kind is ArchiveJournalDecisionKind.ACCEPT_ARCHIVE_JOURNALED
    return journal


def accepted_prune_replay(prune=None, journal=None):
    if prune is None or journal is None:
        settlement, archive, prune = accepted_settlement_archive_prune()
        journal = accepted_archive_journal(settlement, archive, prune)
    r1 = make_prune_replay_observation(kind=PruneReplayObservationKind.SOFT_PRUNE_REPLAYED_WITH_ARCHIVE, sequence=1, repair_prune_report=prune, archive_journal_report=journal, family_id="replay-a", path_family_id="path-a")
    r2 = make_prune_replay_observation(kind=PruneReplayObservationKind.CONTRADICTION_MEMORY_REPLAYED, sequence=2, previous_digest=r1.observation_digest, repair_prune_report=prune, archive_journal_report=journal, family_id="replay-b", path_family_id="path-b")
    replay = assess_prune_replay(repair_prune_report=prune, archive_journal_report=journal, observations=(r1, r2), previous_digest=r1.previous_digest, min_restart_generation=2)
    assert replay.decision_kind is PruneReplayDecisionKind.ACCEPT_PRUNE_REPLAY_STABLE
    return replay


def test_archive_journal_prune_replay_and_closure_audit_happy_path() -> None:
    settlement, archive, prune = accepted_settlement_archive_prune()
    journal = accepted_archive_journal(settlement, archive, prune)
    replay = accepted_prune_replay(prune, journal)
    m1 = make_closure_audit_marker(kind=ClosureAuditMarkerKind.RESTART_CLOSURE_AUDITED, sequence=1, repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, archive_journal_report=journal, prune_replay_report=replay, family_id="audit-a", path_family_id="path-a")
    m2 = make_closure_audit_marker(kind=ClosureAuditMarkerKind.CONTRADICTION_MEMORY_AUDITED, sequence=2, previous_digest=m1.marker_digest, repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, archive_journal_report=journal, prune_replay_report=replay, family_id="audit-b", path_family_id="path-b")
    audit = assess_closure_audit(repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, archive_journal_report=journal, prune_replay_report=replay, markers=(m1, m2), previous_digest=m1.previous_digest)
    assert audit.decision_kind is ClosureAuditDecisionKind.ACCEPT_CLOSURE_AUDITED
    assert audit.accept and audit.closure_audited and audit.contradiction_preserved


def test_archive_journal_quarantines_contradiction_drop() -> None:
    settlement, archive, prune = accepted_settlement_archive_prune()
    j1 = make_archive_journal_entry(kind=ArchiveJournalEntryKind.CONTRADICTION_MEMORY_JOURNALED, sequence=1, repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, contradiction_journaled=False, family_id="journal-a", path_family_id="path-a")
    journal = assess_archive_journal(repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, entries=(j1,), min_family_count=1, min_path_family_count=1)
    assert journal.decision_kind is ArchiveJournalDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_archive_journal_detects_digest_drift() -> None:
    settlement, archive, prune = accepted_settlement_archive_prune()
    j1 = make_archive_journal_entry(kind=ArchiveJournalEntryKind.PRUNE_BOUNDARY_JOURNALED, sequence=1, repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, family_id="journal-a", path_family_id="path-a")
    bad = SimpleNamespace(**{**prune.__dict__, "report_digest": d("different-prune")})
    journal = assess_archive_journal(repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=bad, entries=(j1,), min_family_count=1, min_path_family_count=1)
    assert journal.decision_kind is ArchiveJournalDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_prune_replay_rejects_generation_rollback() -> None:
    settlement, archive, prune = accepted_settlement_archive_prune()
    journal = accepted_archive_journal(settlement, archive, prune)
    r1 = make_prune_replay_observation(kind=PruneReplayObservationKind.SOFT_PRUNE_REPLAYED_WITH_ARCHIVE, sequence=1, restart_generation=1, repair_prune_report=prune, archive_journal_report=journal, family_id="replay-a", path_family_id="path-a")
    replay = assess_prune_replay(repair_prune_report=prune, archive_journal_report=journal, observations=(r1,), min_restart_generation=2, min_family_count=1, min_path_family_count=1)
    assert replay.decision_kind is PruneReplayDecisionKind.QUARANTINE_GENERATION_ROLLBACK


def test_prune_replay_rejects_memory_drop() -> None:
    settlement, archive, prune = accepted_settlement_archive_prune()
    journal = accepted_archive_journal(settlement, archive, prune)
    r1 = make_prune_replay_observation(kind=PruneReplayObservationKind.PRUNE_MARKER_REPLAYED, sequence=1, repair_prune_report=prune, archive_journal_report=journal, preserved_prune_marker=False, family_id="replay-a", path_family_id="path-a")
    replay = assess_prune_replay(repair_prune_report=prune, archive_journal_report=journal, observations=(r1,), min_family_count=1, min_path_family_count=1)
    assert replay.decision_kind is PruneReplayDecisionKind.QUARANTINE_MEMORY_DROPPED


def test_closure_audit_quarantines_boundary_drift() -> None:
    settlement, archive, prune = accepted_settlement_archive_prune()
    journal = accepted_archive_journal(settlement, archive, prune)
    replay = accepted_prune_replay(prune, journal)
    drifted = SimpleNamespace(**{**journal.__dict__, "request_digest": d("other-request")})
    audit = assess_closure_audit(repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, archive_journal_report=drifted, prune_replay_report=replay)
    assert audit.decision_kind is ClosureAuditDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_closure_audit_quarantines_same_sequence_fork() -> None:
    settlement, archive, prune = accepted_settlement_archive_prune()
    journal = accepted_archive_journal(settlement, archive, prune)
    replay = accepted_prune_replay(prune, journal)
    m1 = make_closure_audit_marker(kind=ClosureAuditMarkerKind.RESTART_CLOSURE_AUDITED, sequence=1, repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, archive_journal_report=journal, prune_replay_report=replay, family_id="audit-a", path_family_id="path-a")
    m2 = make_closure_audit_marker(kind=ClosureAuditMarkerKind.PRUNE_REPLAY_AUDITED, sequence=1, previous_digest=m1.previous_digest, repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, archive_journal_report=journal, prune_replay_report=replay, family_id="audit-b", path_family_id="path-b")
    audit = assess_closure_audit(repair_settlement_report=settlement, closure_archive_report=archive, repair_prune_report=prune, archive_journal_report=journal, prune_replay_report=replay, markers=(m1, m2), previous_digest=m1.previous_digest)
    assert audit.decision_kind is ClosureAuditDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_archivejournalfold_audit_passes() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    report = audit_archive_journal_fold(root, revision="rev0068", artifact_stem=root.name)
    assert report.status == "pass"
