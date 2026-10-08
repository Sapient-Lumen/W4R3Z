from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.publicledger import PublicLedgerClass, PublicLedgerDecisionKind, assess_public_ledger, make_public_ledger_entry
from i2p_dht_lab.redactiongc import RedactionGCClass, RedactionGCDecisionKind, assess_redaction_gc, make_redaction_gc_proposal
from i2p_dht_lab.summarysettlement import SummarySettlementClass, SummarySettlementDecisionKind, assess_summary_settlement, make_summary_settlement_marker
from i2p_dht_lab.summarysettlementfold import audit_summary_settlement_fold
from test_rev0073_summarypublish_redactionwitness_importpruneaudit import accepted_import_prune_audit, accepted_redaction_witness, accepted_summary_publish


def accepted_summary_settlement(publish=None, witness=None, audit=None):
    publish = publish or accepted_summary_publish()
    witness = witness or accepted_redaction_witness(publish)
    audit = audit or accepted_import_prune_audit(publish=publish, witness=witness)
    classes = [
        SummarySettlementClass.PUBLICATION_READY,
        SummarySettlementClass.REDACTION_WITNESSED,
        SummarySettlementClass.IMPORT_PRUNE_AUDITED,
        SummarySettlementClass.CONTRADICTION_MEMORY,
        SummarySettlementClass.REDACTED_SUMMARY_MEMORY,
        SummarySettlementClass.LOCAL_SETTLEMENT_STATE,
    ]
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_settlement_marker(settlement_class=cls, sequence=seq, previous_digest=prev, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, family_id=f"settle-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_settlement(summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummarySettlementDecisionKind.ACCEPT_SUMMARY_SETTLED
    return report


def accepted_public_ledger(settlement=None):
    settlement = settlement or accepted_summary_settlement()
    classes = [
        PublicLedgerClass.SUMMARY_SETTLEMENT,
        PublicLedgerClass.SUMMARY_PUBLICATION,
        PublicLedgerClass.REDACTION_WITNESS,
        PublicLedgerClass.IMPORT_PRUNE_AUDIT,
        PublicLedgerClass.CONTRADICTION_MEMORY,
        PublicLedgerClass.REDACTED_PUBLIC_SUMMARY,
        PublicLedgerClass.LOCAL_LEDGER_STATE,
    ]
    entries = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        entry = make_public_ledger_entry(ledger_class=cls, sequence=seq, previous_digest=prev, summary_settlement_report=settlement, family_id=f"ledger-{seq}", path_family_id=f"path-{seq}")
        entries.append(entry)
        prev = entry.entry_digest
    report = assess_public_ledger(summary_settlement_report=settlement, entries=tuple(entries), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is PublicLedgerDecisionKind.ACCEPT_PUBLIC_SUMMARY_LEDGERED
    return report


def accepted_redaction_gc(settlement=None, ledger=None):
    settlement = settlement or accepted_summary_settlement()
    ledger = ledger or accepted_public_ledger(settlement)
    classes = [
        RedactionGCClass.SUMMARY_SETTLEMENT,
        RedactionGCClass.PUBLIC_SUMMARY_LEDGER,
        RedactionGCClass.SUMMARY_PUBLICATION,
        RedactionGCClass.REDACTION_WITNESS,
        RedactionGCClass.IMPORT_PRUNE_AUDIT,
        RedactionGCClass.CONTRADICTION_MEMORY,
        RedactionGCClass.REDACTED_SUMMARY_MEMORY,
        RedactionGCClass.SOFT_WORKING_SET_DROPPED,
    ]
    proposals = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        proposal = make_redaction_gc_proposal(gc_class=cls, sequence=seq, previous_digest=prev, summary_settlement_report=settlement, public_ledger_report=ledger, family_id=f"gc-{seq}", path_family_id=f"path-{seq}")
        proposals.append(proposal)
        prev = proposal.proposal_digest
    report = assess_redaction_gc(summary_settlement_report=settlement, public_ledger_report=ledger, proposals=tuple(proposals), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is RedactionGCDecisionKind.ACCEPT_REDACTION_GC_GUARDED
    return report


def test_summary_settlement_public_ledger_redaction_gc_happy_path() -> None:
    settlement = accepted_summary_settlement()
    ledger = accepted_public_ledger(settlement)
    gc = accepted_redaction_gc(settlement, ledger)
    assert settlement.summary_settled and settlement.contradiction_preserved
    assert ledger.public_summary_ledgered and ledger.contradiction_preserved
    assert gc.redaction_gc_guarded and gc.contradiction_retained


def test_summary_settlement_rejects_component_digest_drift() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    object.__setattr__(witness, "summary_publish_digest", ZERO_DIGEST)
    marker = make_summary_settlement_marker(settlement_class=SummarySettlementClass.PUBLICATION_READY, sequence=1, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, family_id="settle-a", path_family_id="path-a")
    report = assess_summary_settlement(summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, markers=(marker,), min_family_count=1, min_path_family_count=1, required_classes=(SummarySettlementClass.PUBLICATION_READY,))
    assert report.decision_kind is SummarySettlementDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_public_ledger_rejects_raw_payload_leak() -> None:
    settlement = accepted_summary_settlement()
    e1 = make_public_ledger_entry(ledger_class=PublicLedgerClass.SUMMARY_SETTLEMENT, sequence=1, summary_settlement_report=settlement, raw_payload_exposed=True, family_id="ledger-a", path_family_id="path-a")
    report = assess_public_ledger(summary_settlement_report=settlement, entries=(e1,), min_family_count=1, min_path_family_count=1, required_classes=(PublicLedgerClass.SUMMARY_SETTLEMENT,))
    assert report.decision_kind is PublicLedgerDecisionKind.QUARANTINE_RAW_LEAK


def test_public_ledger_holds_missing_required_class() -> None:
    settlement = accepted_summary_settlement()
    e1 = make_public_ledger_entry(ledger_class=PublicLedgerClass.SUMMARY_SETTLEMENT, sequence=1, summary_settlement_report=settlement, family_id="ledger-a", path_family_id="path-a")
    report = assess_public_ledger(summary_settlement_report=settlement, entries=(e1,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is PublicLedgerDecisionKind.HOLD_MISSING_REQUIRED_CLASS


def test_redaction_gc_rejects_contradiction_drop() -> None:
    settlement = accepted_summary_settlement()
    ledger = accepted_public_ledger(settlement)
    proposals = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((RedactionGCClass.SUMMARY_SETTLEMENT, RedactionGCClass.PUBLIC_SUMMARY_LEDGER, RedactionGCClass.SUMMARY_PUBLICATION, RedactionGCClass.REDACTION_WITNESS, RedactionGCClass.IMPORT_PRUNE_AUDIT, RedactionGCClass.CONTRADICTION_MEMORY, RedactionGCClass.REDACTED_SUMMARY_MEMORY), start=1):
        proposal = make_redaction_gc_proposal(gc_class=cls, sequence=seq, previous_digest=prev, summary_settlement_report=settlement, public_ledger_report=ledger, contradiction_retained=False, family_id=f"gc-{seq}", path_family_id=f"path-{seq}")
        proposals.append(proposal)
        prev = proposal.proposal_digest
    report = assess_redaction_gc(summary_settlement_report=settlement, public_ledger_report=ledger, proposals=tuple(proposals), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionGCDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_redaction_gc_rejects_public_ledger_digest_drift() -> None:
    settlement = accepted_summary_settlement()
    ledger = accepted_public_ledger(settlement)
    object.__setattr__(ledger, "summary_settlement_digest", ZERO_DIGEST)
    proposal = make_redaction_gc_proposal(gc_class=RedactionGCClass.SUMMARY_SETTLEMENT, sequence=1, summary_settlement_report=settlement, public_ledger_report=ledger, family_id="gc-a", path_family_id="path-a")
    report = assess_redaction_gc(summary_settlement_report=settlement, public_ledger_report=ledger, proposals=(proposal,), min_family_count=1, min_path_family_count=1, required_classes=(RedactionGCClass.SUMMARY_SETTLEMENT,))
    assert report.decision_kind is RedactionGCDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_summary_settlement_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_settlement_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
