from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.exportretentionaudit import ExportRetentionClass, ExportRetentionDecisionKind, assess_export_retention_audit, make_export_retention_marker
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.summaryexportreceipt import SummaryExportReceiptClass, SummaryExportReceiptDecisionKind, assess_summary_export_receipt, make_summary_export_receipt_marker
from i2p_dht_lab.summaryimportgate import SummaryImportClass, SummaryImportDecisionKind, assess_summary_import_gate, make_summary_import_marker
from i2p_dht_lab.summaryexportreceiptfold import audit_summary_export_receipt_fold
from test_rev0078_summaryreplay_ackclosure_exportfence import accepted_summary_export_fence


def accepted_summary_export_receipt():
    export, closure, replay, prune, archive, ack, fence = accepted_summary_export_fence()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SummaryExportReceiptClass.EXPORT_FENCE,
        SummaryExportReceiptClass.RECIPIENT_ACK,
        SummaryExportReceiptClass.CHANNEL_POLICY,
        SummaryExportReceiptClass.REDACTION_MEMORY,
        SummaryExportReceiptClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_export_receipt_marker(
            receipt_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_export_fence_report=export,
            recipient_kind="garden",
            family_id=f"receipt-{seq}",
            path_family_id=f"receipt-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_export_receipt(summary_export_fence_report=export, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryExportReceiptDecisionKind.ACCEPT_SUMMARY_EXPORT_RECEIPTED
    return report, export, closure, replay, prune, archive, ack, fence


def accepted_summary_import_gate():
    receipt, export, closure, replay, prune, archive, ack, fence = accepted_summary_export_receipt()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SummaryImportClass.EXPORT_RECEIPT,
        SummaryImportClass.EXPORT_FENCE,
        SummaryImportClass.IMPORT_SCOPE,
        SummaryImportClass.REDACTION_MEMORY,
        SummaryImportClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_import_marker(
            import_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_export_receipt_report=receipt,
            summary_export_fence_report=export,
            importer_kind="local_operator",
            family_id=f"import-{seq}",
            path_family_id=f"import-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_import_gate(summary_export_receipt_report=receipt, summary_export_fence_report=export, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryImportDecisionKind.ACCEPT_SUMMARY_IMPORT_GATED
    return report, receipt, export, closure, replay, prune, archive, ack, fence


def accepted_export_retention_audit():
    import_gate, receipt, export, closure, replay, prune, archive, ack, fence = accepted_summary_import_gate()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        ExportRetentionClass.EXPORT_RECEIPT,
        ExportRetentionClass.IMPORT_GATE,
        ExportRetentionClass.EXPORT_FENCE,
        ExportRetentionClass.RETENTION_POLICY,
        ExportRetentionClass.REDACTION_MEMORY,
        ExportRetentionClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_export_retention_marker(
            retention_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_export_receipt_report=receipt,
            summary_import_gate_report=import_gate,
            summary_export_fence_report=export,
            family_id=f"retention-{seq}",
            path_family_id=f"retention-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_export_retention_audit(summary_export_receipt_report=receipt, summary_import_gate_report=import_gate, summary_export_fence_report=export, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is ExportRetentionDecisionKind.ACCEPT_EXPORT_RETENTION_AUDITED
    return report, import_gate, receipt, export, closure, replay, prune, archive, ack, fence


def test_summary_export_receipt_import_retention_happy_path() -> None:
    receipt, *_ = accepted_summary_export_receipt()
    import_gate, *_ = accepted_summary_import_gate()
    retention, *_ = accepted_export_retention_audit()
    assert receipt.summary_export_receipted and receipt.recipient_acknowledged and receipt.redacted
    assert import_gate.summary_import_gated and import_gate.import_ready and import_gate.contradiction_preserved
    assert retention.export_retention_audited and retention.retention_safe and retention.redaction_carried


def test_summary_export_receipt_holds_on_recipient_refusal() -> None:
    export, *_ = accepted_summary_export_fence()
    marker = make_summary_export_receipt_marker(
        receipt_class=SummaryExportReceiptClass.RECIPIENT_ACK,
        sequence=1,
        summary_export_fence_report=export,
        receipt_kind="refused",
        family_id="receipt-a",
        path_family_id="receipt-path-a",
    )
    report = assess_summary_export_receipt(summary_export_fence_report=export, markers=(marker,), required_classes=(SummaryExportReceiptClass.RECIPIENT_ACK,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryExportReceiptDecisionKind.HOLD_RECIPIENT_REFUSED


def test_summary_export_receipt_quarantines_raw_leak() -> None:
    export, *_ = accepted_summary_export_fence()
    marker = make_summary_export_receipt_marker(
        receipt_class=SummaryExportReceiptClass.RECIPIENT_ACK,
        sequence=1,
        summary_export_fence_report=export,
        raw_payload_exposed=True,
        family_id="receipt-a",
        path_family_id="receipt-path-a",
    )
    report = assess_summary_export_receipt(summary_export_fence_report=export, markers=(marker,), required_classes=(SummaryExportReceiptClass.RECIPIENT_ACK,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryExportReceiptDecisionKind.QUARANTINE_RAW_LEAK


def test_summary_import_gate_quarantines_digest_drift() -> None:
    receipt, export, *_ = accepted_summary_export_receipt()
    marker = make_summary_import_marker(
        import_class=SummaryImportClass.EXPORT_RECEIPT,
        sequence=1,
        summary_export_receipt_report=receipt,
        summary_export_fence_report=export,
        family_id="import-a",
        path_family_id="import-path-a",
    )
    bad = replace(marker, summary_export_receipt_digest=ZERO_DIGEST)
    report = assess_summary_import_gate(summary_export_receipt_report=receipt, summary_export_fence_report=export, markers=(bad,), required_classes=(SummaryImportClass.EXPORT_RECEIPT,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryImportDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_summary_import_gate_holds_when_import_not_permitted() -> None:
    receipt, export, *_ = accepted_summary_export_receipt()
    marker = make_summary_import_marker(
        import_class=SummaryImportClass.IMPORT_SCOPE,
        sequence=1,
        summary_export_receipt_report=receipt,
        summary_export_fence_report=export,
        import_permitted=False,
        family_id="import-a",
        path_family_id="import-path-a",
    )
    report = assess_summary_import_gate(summary_export_receipt_report=receipt, summary_export_fence_report=export, markers=(marker,), required_classes=(SummaryImportClass.IMPORT_SCOPE,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryImportDecisionKind.HOLD_IMPORT_NOT_PERMITTED


def test_export_retention_audit_quarantines_contradiction_drop() -> None:
    import_gate, receipt, export, *_ = accepted_summary_import_gate()
    marker = make_export_retention_marker(
        retention_class=ExportRetentionClass.CONTRADICTION_MEMORY,
        sequence=1,
        summary_export_receipt_report=receipt,
        summary_import_gate_report=import_gate,
        summary_export_fence_report=export,
        contradiction_carried=False,
        family_id="retention-a",
        path_family_id="retention-path-a",
    )
    report = assess_export_retention_audit(summary_export_receipt_report=receipt, summary_import_gate_report=import_gate, summary_export_fence_report=export, markers=(marker,), required_classes=(ExportRetentionClass.CONTRADICTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ExportRetentionDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_export_retention_audit_quarantines_redaction_drop() -> None:
    import_gate, receipt, export, *_ = accepted_summary_import_gate()
    marker = make_export_retention_marker(
        retention_class=ExportRetentionClass.REDACTION_MEMORY,
        sequence=1,
        summary_export_receipt_report=receipt,
        summary_import_gate_report=import_gate,
        summary_export_fence_report=export,
        redaction_carried=False,
        family_id="retention-a",
        path_family_id="retention-path-a",
    )
    report = assess_export_retention_audit(summary_export_receipt_report=receipt, summary_import_gate_report=import_gate, summary_export_fence_report=export, markers=(marker,), required_classes=(ExportRetentionClass.REDACTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ExportRetentionDecisionKind.QUARANTINE_REDACTION_DROPPED


def test_summary_export_receipt_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_export_receipt_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
