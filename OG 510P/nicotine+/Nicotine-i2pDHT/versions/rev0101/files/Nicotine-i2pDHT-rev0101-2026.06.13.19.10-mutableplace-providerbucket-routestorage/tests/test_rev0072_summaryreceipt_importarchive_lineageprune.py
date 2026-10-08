from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.importarchive import ImportArchiveClass, ImportArchiveDecisionKind, assess_import_archive, make_import_archive_marker
from i2p_dht_lab.lineageprune import LineagePruneClass, LineagePruneDecisionKind, assess_lineage_prune, make_lineage_prune_marker
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.summaryreceipt import SummaryReceiptDecisionKind, SummaryReceiptKind, assess_summary_receipts, make_summary_receipt_entry
from i2p_dht_lab.summaryreceiptfold import audit_summary_receipt_fold
from test_rev0071_handoffreceipt_import_summarylineage import accepted_summary


def accepted_summary_receipt(summary=None):
    summary = summary or accepted_summary()
    r1 = make_summary_receipt_entry(kind=SummaryReceiptKind.OPERATOR_SUMMARY_ACK, sequence=1, summary_lineage_report=summary, family_id="receipt-a", path_family_id="path-a")
    r2 = make_summary_receipt_entry(kind=SummaryReceiptKind.GARDEN_SUMMARY_ACK, sequence=2, previous_digest=r1.entry_digest, summary_lineage_report=summary, family_id="receipt-b", path_family_id="path-b")
    report = assess_summary_receipts(summary_lineage_report=summary, entries=(r1, r2), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryReceiptDecisionKind.ACCEPT_SUMMARY_RECEIPTED
    return report


def accepted_import_archive(receipt=None):
    receipt = receipt or accepted_summary_receipt()
    classes = [
        ImportArchiveClass.SUMMARY_RECEIPT_MARKER,
        ImportArchiveClass.SUMMARY_LINEAGE_MARKER,
        ImportArchiveClass.HANDOFF_IMPORT_MARKER,
        ImportArchiveClass.CONTRADICTION_MEMORY,
        ImportArchiveClass.REDACTED_SUMMARY_MEMORY,
        ImportArchiveClass.LOCAL_ARCHIVE_STATE,
    ]
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        marker = make_import_archive_marker(archive_class=cls, sequence=seq, previous_digest=prev, summary_receipt_report=receipt, family_id=f"archive-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_import_archive(summary_receipt_report=receipt, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is ImportArchiveDecisionKind.ACCEPT_IMPORT_ARCHIVED
    return report


def accepted_lineage_prune(receipt=None, archive=None):
    receipt = receipt or accepted_summary_receipt()
    archive = archive or accepted_import_archive(receipt)
    classes = [
        LineagePruneClass.SUMMARY_RECEIPT,
        LineagePruneClass.SUMMARY_LINEAGE,
        LineagePruneClass.IMPORT_ARCHIVE,
        LineagePruneClass.HANDOFF_IMPORT,
        LineagePruneClass.CONTRADICTION_MEMORY,
        LineagePruneClass.REDACTED_SUMMARY_MEMORY,
        LineagePruneClass.LOCAL_ARCHIVE_MARKER,
    ]
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        marker = make_lineage_prune_marker(prune_class=cls, sequence=seq, previous_digest=prev, summary_receipt_report=receipt, import_archive_report=archive, family_id=f"prune-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_lineage_prune(summary_receipt_report=receipt, import_archive_report=archive, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is LineagePruneDecisionKind.ACCEPT_LINEAGE_PRUNE_GUARDED
    return report


def test_summary_receipt_archive_prune_happy_path() -> None:
    receipt = accepted_summary_receipt()
    archive = accepted_import_archive(receipt)
    prune = accepted_lineage_prune(receipt, archive)
    assert receipt.summary_receipted and receipt.contradiction_carried
    assert archive.import_archived and archive.contradiction_preserved
    assert prune.lineage_prune_guarded and prune.contradiction_preserved


def test_summary_refusal_is_watch_not_accept() -> None:
    summary = accepted_summary()
    refusal = make_summary_receipt_entry(kind=SummaryReceiptKind.SUMMARY_REFUSED, sequence=1, summary_lineage_report=summary, family_id="receipt-a", path_family_id="path-a")
    report = assess_summary_receipts(summary_lineage_report=summary, entries=(refusal,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryReceiptDecisionKind.WATCH_SUMMARY_REFUSAL
    assert report.watch and not report.accept


def test_summary_receipt_rejects_raw_payload_leak() -> None:
    summary = accepted_summary()
    r1 = make_summary_receipt_entry(kind=SummaryReceiptKind.OPERATOR_SUMMARY_ACK, sequence=1, summary_lineage_report=summary, raw_payload_exposed=True, family_id="receipt-a", path_family_id="path-a")
    r2 = make_summary_receipt_entry(kind=SummaryReceiptKind.GARDEN_SUMMARY_ACK, sequence=2, previous_digest=r1.entry_digest, summary_lineage_report=summary, family_id="receipt-b", path_family_id="path-b")
    report = assess_summary_receipts(summary_lineage_report=summary, entries=(r1, r2))
    assert report.decision_kind is SummaryReceiptDecisionKind.QUARANTINE_RAW_LEAK


def test_import_archive_holds_missing_required_class() -> None:
    receipt = accepted_summary_receipt()
    m1 = make_import_archive_marker(archive_class=ImportArchiveClass.SUMMARY_RECEIPT_MARKER, sequence=1, summary_receipt_report=receipt, family_id="archive-a", path_family_id="path-a")
    m2 = make_import_archive_marker(archive_class=ImportArchiveClass.SUMMARY_LINEAGE_MARKER, sequence=2, previous_digest=m1.marker_digest, summary_receipt_report=receipt, family_id="archive-b", path_family_id="path-b")
    report = assess_import_archive(summary_receipt_report=receipt, markers=(m1, m2), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ImportArchiveDecisionKind.HOLD_MISSING_REQUIRED_CLASS


def test_import_archive_quarantines_contradiction_drop() -> None:
    receipt = accepted_summary_receipt()
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((ImportArchiveClass.SUMMARY_RECEIPT_MARKER, ImportArchiveClass.SUMMARY_LINEAGE_MARKER, ImportArchiveClass.HANDOFF_IMPORT_MARKER, ImportArchiveClass.CONTRADICTION_MEMORY, ImportArchiveClass.REDACTED_SUMMARY_MEMORY, ImportArchiveClass.LOCAL_ARCHIVE_STATE), start=1):
        marker = make_import_archive_marker(archive_class=cls, sequence=seq, previous_digest=prev, summary_receipt_report=receipt, contradiction_carried=False, family_id=f"archive-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_import_archive(summary_receipt_report=receipt, markers=tuple(markers), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ImportArchiveDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_lineage_prune_rejects_boundary_and_digest_drift() -> None:
    receipt = accepted_summary_receipt()
    archive = accepted_import_archive(receipt)
    bad = make_lineage_prune_marker(prune_class=LineagePruneClass.SUMMARY_RECEIPT, sequence=1, summary_receipt_report=receipt, import_archive_report=archive, family_id="prune-a", path_family_id="path-a")
    drift = make_lineage_prune_marker(prune_class=LineagePruneClass.SUMMARY_LINEAGE, sequence=2, previous_digest=bad.marker_digest, summary_receipt_report=receipt, import_archive_report=archive, family_id="prune-b", path_family_id="path-b")
    object.__setattr__(drift, "summary_lineage_digest", ZERO_DIGEST)
    report = assess_lineage_prune(summary_receipt_report=receipt, import_archive_report=archive, markers=(bad, drift), min_family_count=1, min_path_family_count=1, required_classes=(LineagePruneClass.SUMMARY_RECEIPT, LineagePruneClass.SUMMARY_LINEAGE))
    assert report.decision_kind is LineagePruneDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_lineage_prune_rejects_missing_contradiction_memory() -> None:
    receipt = accepted_summary_receipt()
    archive = accepted_import_archive(receipt)
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((LineagePruneClass.SUMMARY_RECEIPT, LineagePruneClass.SUMMARY_LINEAGE, LineagePruneClass.IMPORT_ARCHIVE, LineagePruneClass.HANDOFF_IMPORT, LineagePruneClass.CONTRADICTION_MEMORY, LineagePruneClass.REDACTED_SUMMARY_MEMORY, LineagePruneClass.LOCAL_ARCHIVE_MARKER), start=1):
        marker = make_lineage_prune_marker(prune_class=cls, sequence=seq, previous_digest=prev, summary_receipt_report=receipt, import_archive_report=archive, contradiction_carried=False, family_id=f"prune-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_lineage_prune(summary_receipt_report=receipt, import_archive_report=archive, markers=tuple(markers), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is LineagePruneDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_summary_receipt_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_receipt_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
