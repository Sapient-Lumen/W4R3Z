from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.closurehandoff import ClosureHandoffAudience
from i2p_dht_lab.handoffimport import HandoffImportClass, HandoffImportDecisionKind, assess_handoff_import, make_handoff_import_marker
from i2p_dht_lab.handoffreceipt import HandoffReceiptDecisionKind, HandoffReceiptKind, assess_handoff_receipts, make_handoff_receipt_entry
from i2p_dht_lab.handoffreceiptfold import audit_handoff_receipt_fold
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.summarylineage import SummaryLineageDecisionKind, SummaryLineageKind, assess_summary_lineage, make_summary_lineage_entry
from test_rev0070_exportreceipt_retentiongc_handoff import accepted_handoff


def accepted_receipt(handoff=None):
    handoff = handoff or accepted_handoff()
    r1 = make_handoff_receipt_entry(kind=HandoffReceiptKind.OPERATOR_ACK, audience=ClosureHandoffAudience.LOCAL_OPERATOR, sequence=1, closure_handoff_report=handoff, family_id="receipt-a", path_family_id="path-a")
    r2 = make_handoff_receipt_entry(kind=HandoffReceiptKind.GARDEN_ACK, audience=ClosureHandoffAudience.GARDEN_WITNESS, sequence=2, previous_digest=r1.entry_digest, closure_handoff_report=handoff, family_id="receipt-b", path_family_id="path-b")
    report = assess_handoff_receipts(closure_handoff_report=handoff, entries=(r1, r2), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is HandoffReceiptDecisionKind.ACCEPT_HANDOFF_RECEIPTED
    return report


def accepted_import(receipt=None):
    receipt = receipt or accepted_receipt()
    markers = []
    prev = ZERO_DIGEST
    classes = [
        HandoffImportClass.HANDOFF_RECEIPT_MARKER,
        HandoffImportClass.CLOSURE_HANDOFF_MARKER,
        HandoffImportClass.CONTRADICTION_MEMORY,
        HandoffImportClass.REDACTED_SUMMARY_MEMORY,
        HandoffImportClass.LOCAL_RECIPIENT_STATE,
    ]
    for seq, cls in enumerate(classes, start=1):
        marker = make_handoff_import_marker(import_class=cls, sequence=seq, previous_digest=prev, handoff_receipt_report=receipt, family_id=f"import-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_handoff_import(handoff_receipt_report=receipt, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is HandoffImportDecisionKind.ACCEPT_HANDOFF_IMPORTED
    return report


def accepted_summary(import_report=None):
    import_report = import_report or accepted_import()
    s1 = make_summary_lineage_entry(kind=SummaryLineageKind.OPERATOR_LOCAL_SUMMARY, sequence=1, handoff_import_report=import_report, family_id="summary-a", path_family_id="path-a")
    s2 = make_summary_lineage_entry(kind=SummaryLineageKind.GARDEN_WITNESS_SUMMARY, sequence=2, previous_digest=s1.entry_digest, handoff_import_report=import_report, family_id="summary-b", path_family_id="path-b")
    report = assess_summary_lineage(handoff_import_report=import_report, entries=(s1, s2), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryLineageDecisionKind.ACCEPT_SUMMARY_LINEAGE
    return report


def test_handoff_receipt_import_and_summary_happy_path() -> None:
    receipt = accepted_receipt()
    imported = accepted_import(receipt)
    summary = accepted_summary(imported)
    assert receipt.handoff_receipted and receipt.contradiction_carried
    assert imported.handoff_imported and imported.contradiction_preserved
    assert summary.summary_lineage_accepted and summary.redacted


def test_handoff_receipt_rejects_raw_leak() -> None:
    handoff = accepted_handoff()
    r1 = make_handoff_receipt_entry(kind=HandoffReceiptKind.OPERATOR_ACK, audience=ClosureHandoffAudience.LOCAL_OPERATOR, sequence=1, closure_handoff_report=handoff, raw_payload_exposed=True, family_id="receipt-a", path_family_id="path-a")
    r2 = make_handoff_receipt_entry(kind=HandoffReceiptKind.GARDEN_ACK, audience=ClosureHandoffAudience.GARDEN_WITNESS, sequence=2, previous_digest=r1.entry_digest, closure_handoff_report=handoff, family_id="receipt-b", path_family_id="path-b")
    report = assess_handoff_receipts(closure_handoff_report=handoff, entries=(r1, r2))
    assert report.decision_kind is HandoffReceiptDecisionKind.QUARANTINE_RAW_LEAK


def test_handoff_receipt_detects_sequence_fork() -> None:
    handoff = accepted_handoff()
    r1 = make_handoff_receipt_entry(kind=HandoffReceiptKind.OPERATOR_ACK, audience=ClosureHandoffAudience.LOCAL_OPERATOR, sequence=1, closure_handoff_report=handoff, family_id="receipt-a", path_family_id="path-a")
    r2 = make_handoff_receipt_entry(kind=HandoffReceiptKind.GARDEN_ACK, audience=ClosureHandoffAudience.GARDEN_WITNESS, sequence=1, closure_handoff_report=handoff, family_id="receipt-b", path_family_id="path-b")
    report = assess_handoff_receipts(closure_handoff_report=handoff, entries=(r1, r2), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is HandoffReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_handoff_receipt_import_refusal_becomes_watch_not_accept() -> None:
    handoff = accepted_handoff()
    r1 = make_handoff_receipt_entry(kind=HandoffReceiptKind.IMPORT_REFUSED, audience=ClosureHandoffAudience.LOCAL_OPERATOR, sequence=1, closure_handoff_report=handoff, family_id="receipt-a", path_family_id="path-a")
    report = assess_handoff_receipts(closure_handoff_report=handoff, entries=(r1,), min_family_count=1, min_path_family_count=1, required_audiences=(ClosureHandoffAudience.LOCAL_OPERATOR,))
    assert report.decision_kind is HandoffReceiptDecisionKind.WATCH_IMPORT_REFUSAL
    assert report.watch and not report.accept


def test_handoff_import_holds_missing_required_class() -> None:
    receipt = accepted_receipt()
    m1 = make_handoff_import_marker(import_class=HandoffImportClass.HANDOFF_RECEIPT_MARKER, sequence=1, handoff_receipt_report=receipt, family_id="import-a", path_family_id="path-a")
    m2 = make_handoff_import_marker(import_class=HandoffImportClass.CLOSURE_HANDOFF_MARKER, sequence=2, previous_digest=m1.marker_digest, handoff_receipt_report=receipt, family_id="import-b", path_family_id="path-b")
    report = assess_handoff_import(handoff_receipt_report=receipt, markers=(m1, m2), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is HandoffImportDecisionKind.HOLD_MISSING_REQUIRED_CLASS


def test_handoff_import_quarantines_contradiction_drop() -> None:
    receipt = accepted_receipt()
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((HandoffImportClass.HANDOFF_RECEIPT_MARKER, HandoffImportClass.CLOSURE_HANDOFF_MARKER, HandoffImportClass.CONTRADICTION_MEMORY, HandoffImportClass.REDACTED_SUMMARY_MEMORY, HandoffImportClass.LOCAL_RECIPIENT_STATE), start=1):
        marker = make_handoff_import_marker(import_class=cls, sequence=seq, previous_digest=prev, handoff_receipt_report=receipt, contradiction_carried=False, family_id=f"import-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_handoff_import(handoff_receipt_report=receipt, markers=tuple(markers), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is HandoffImportDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_summary_lineage_rejects_raw_leak_and_contradiction_drop() -> None:
    imported = accepted_import()
    s1 = make_summary_lineage_entry(kind=SummaryLineageKind.OPERATOR_LOCAL_SUMMARY, sequence=1, handoff_import_report=imported, raw_boundary_exposed=True, family_id="summary-a", path_family_id="path-a")
    s2 = make_summary_lineage_entry(kind=SummaryLineageKind.GARDEN_WITNESS_SUMMARY, sequence=2, previous_digest=s1.entry_digest, handoff_import_report=imported, family_id="summary-b", path_family_id="path-b")
    raw = assess_summary_lineage(handoff_import_report=imported, entries=(s1, s2))
    assert raw.decision_kind is SummaryLineageDecisionKind.QUARANTINE_RAW_LEAK

    c1 = make_summary_lineage_entry(kind=SummaryLineageKind.OPERATOR_LOCAL_SUMMARY, sequence=1, handoff_import_report=imported, contradiction_carried=False, family_id="summary-a", path_family_id="path-a")
    c2 = make_summary_lineage_entry(kind=SummaryLineageKind.GARDEN_WITNESS_SUMMARY, sequence=2, previous_digest=c1.entry_digest, handoff_import_report=imported, contradiction_carried=False, family_id="summary-b", path_family_id="path-b")
    dropped = assess_summary_lineage(handoff_import_report=imported, entries=(c1, c2))
    assert dropped.decision_kind is SummaryLineageDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_handoff_receipt_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_handoff_receipt_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
