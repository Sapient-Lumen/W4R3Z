from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.importarchiveledger import ImportArchiveClass, ImportArchiveDecisionKind, assess_import_archive, make_import_archive_marker
from i2p_dht_lab.importretentionseal import ImportRetentionSealClass, ImportRetentionSealDecisionKind, assess_import_retention_seal, make_import_retention_seal_marker
from i2p_dht_lab.importsettlementfold import audit_import_settlement_fold
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.summaryimportsettlement import SummaryImportSettlementClass, SummaryImportSettlementDecisionKind, assess_summary_import_settlement, make_summary_import_settlement_marker
from test_rev0079_summaryexportreceipt_importgate_retentionaudit import accepted_export_retention_audit, accepted_summary_import_gate


def accepted_summary_import_settlement():
    retention, import_gate, receipt, export, *_ = accepted_export_retention_audit()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SummaryImportSettlementClass.EXPORT_RECEIPT,
        SummaryImportSettlementClass.IMPORT_GATE,
        SummaryImportSettlementClass.RETENTION_AUDIT,
        SummaryImportSettlementClass.IMPORT_STATE,
        SummaryImportSettlementClass.REDACTION_MEMORY,
        SummaryImportSettlementClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_import_settlement_marker(
            settlement_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_export_receipt_report=receipt,
            summary_import_gate_report=import_gate,
            export_retention_audit_report=retention,
            family_id=f"settlement-{seq}",
            path_family_id=f"settlement-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_import_settlement(summary_export_receipt_report=receipt, summary_import_gate_report=import_gate, export_retention_audit_report=retention, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryImportSettlementDecisionKind.ACCEPT_SUMMARY_IMPORT_SETTLED
    return report, retention, import_gate, receipt, export


def accepted_import_archive():
    settlement, retention, import_gate, receipt, export = accepted_summary_import_settlement()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        ImportArchiveClass.IMPORT_SETTLEMENT,
        ImportArchiveClass.RETENTION_AUDIT,
        ImportArchiveClass.IMPORT_GATE,
        ImportArchiveClass.ARCHIVE_STATE,
        ImportArchiveClass.REDACTION_MEMORY,
        ImportArchiveClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_import_archive_marker(
            archive_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_import_settlement_report=settlement,
            export_retention_audit_report=retention,
            summary_import_gate_report=import_gate,
            family_id=f"archive-{seq}",
            path_family_id=f"archive-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_import_archive(summary_import_settlement_report=settlement, export_retention_audit_report=retention, summary_import_gate_report=import_gate, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is ImportArchiveDecisionKind.ACCEPT_IMPORT_ARCHIVED
    return report, settlement, retention, import_gate, receipt, export


def accepted_import_retention_seal():
    archive, settlement, retention, import_gate, receipt, export = accepted_import_archive()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        ImportRetentionSealClass.IMPORT_SETTLEMENT,
        ImportRetentionSealClass.IMPORT_ARCHIVE,
        ImportRetentionSealClass.RETENTION_AUDIT,
        ImportRetentionSealClass.RETENTION_POLICY,
        ImportRetentionSealClass.REDACTION_MEMORY,
        ImportRetentionSealClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_import_retention_seal_marker(
            seal_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_import_settlement_report=settlement,
            import_archive_report=archive,
            export_retention_audit_report=retention,
            family_id=f"seal-{seq}",
            path_family_id=f"seal-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_import_retention_seal(summary_import_settlement_report=settlement, import_archive_report=archive, export_retention_audit_report=retention, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is ImportRetentionSealDecisionKind.ACCEPT_IMPORT_RETENTION_SEALED
    return report, archive, settlement, retention, import_gate, receipt, export


def test_import_settlement_archive_retention_seal_happy_path() -> None:
    settlement, *_ = accepted_summary_import_settlement()
    archive, *_ = accepted_import_archive()
    seal, *_ = accepted_import_retention_seal()
    assert settlement.summary_import_settled and settlement.import_terminal and settlement.contradiction_preserved
    assert archive.import_archived and archive.archive_restart_sticky and archive.redacted
    assert seal.import_retention_sealed and seal.cleanup_guarded and seal.contradiction_preserved


def test_import_settlement_quarantines_digest_drift() -> None:
    retention, import_gate, receipt, *_ = accepted_export_retention_audit()
    marker = make_summary_import_settlement_marker(
        settlement_class=SummaryImportSettlementClass.RETENTION_AUDIT,
        sequence=1,
        summary_export_receipt_report=receipt,
        summary_import_gate_report=import_gate,
        export_retention_audit_report=retention,
        family_id="settlement-a",
        path_family_id="settlement-path-a",
    )
    bad = replace(marker, export_retention_audit_digest=ZERO_DIGEST)
    report = assess_summary_import_settlement(summary_export_receipt_report=receipt, summary_import_gate_report=import_gate, export_retention_audit_report=retention, markers=(bad,), required_classes=(SummaryImportSettlementClass.RETENTION_AUDIT,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryImportSettlementDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_import_settlement_holds_when_import_gate_not_ready() -> None:
    import_gate, receipt, export, *_ = accepted_summary_import_gate()
    not_ready = replace(import_gate, import_ready=False, summary_import_gated=True)
    retention, *_ = accepted_export_retention_audit()
    marker = make_summary_import_settlement_marker(
        settlement_class=SummaryImportSettlementClass.IMPORT_STATE,
        sequence=1,
        summary_export_receipt_report=receipt,
        summary_import_gate_report=not_ready,
        export_retention_audit_report=retention,
        family_id="settlement-a",
        path_family_id="settlement-path-a",
    )
    report = assess_summary_import_settlement(summary_export_receipt_report=receipt, summary_import_gate_report=not_ready, export_retention_audit_report=retention, markers=(marker,), required_classes=(SummaryImportSettlementClass.IMPORT_STATE,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryImportSettlementDecisionKind.HOLD_IMPORT_NOT_READY


def test_import_archive_quarantines_redaction_drop() -> None:
    settlement, retention, import_gate, *_ = accepted_summary_import_settlement()
    marker = make_import_archive_marker(
        archive_class=ImportArchiveClass.REDACTION_MEMORY,
        sequence=1,
        summary_import_settlement_report=settlement,
        export_retention_audit_report=retention,
        summary_import_gate_report=import_gate,
        redaction_carried=False,
        family_id="archive-a",
        path_family_id="archive-path-a",
    )
    report = assess_import_archive(summary_import_settlement_report=settlement, export_retention_audit_report=retention, summary_import_gate_report=import_gate, markers=(marker,), required_classes=(ImportArchiveClass.REDACTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ImportArchiveDecisionKind.QUARANTINE_REDACTION_DROPPED


def test_import_archive_holds_missing_archive_state_class() -> None:
    settlement, retention, import_gate, *_ = accepted_summary_import_settlement()
    marker = make_import_archive_marker(
        archive_class=ImportArchiveClass.IMPORT_SETTLEMENT,
        sequence=1,
        summary_import_settlement_report=settlement,
        export_retention_audit_report=retention,
        summary_import_gate_report=import_gate,
        family_id="archive-a",
        path_family_id="archive-path-a",
    )
    report = assess_import_archive(summary_import_settlement_report=settlement, export_retention_audit_report=retention, summary_import_gate_report=import_gate, markers=(marker,), required_classes=(ImportArchiveClass.ARCHIVE_STATE,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ImportArchiveDecisionKind.HOLD_MISSING_REQUIRED_CLASS


def test_import_retention_seal_quarantines_contradiction_drop() -> None:
    archive, settlement, retention, *_ = accepted_import_archive()
    marker = make_import_retention_seal_marker(
        seal_class=ImportRetentionSealClass.CONTRADICTION_MEMORY,
        sequence=1,
        summary_import_settlement_report=settlement,
        import_archive_report=archive,
        export_retention_audit_report=retention,
        contradiction_carried=False,
        family_id="seal-a",
        path_family_id="seal-path-a",
    )
    report = assess_import_retention_seal(summary_import_settlement_report=settlement, import_archive_report=archive, export_retention_audit_report=retention, markers=(marker,), required_classes=(ImportRetentionSealClass.CONTRADICTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ImportRetentionSealDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_import_retention_seal_quarantines_archive_digest_drift() -> None:
    archive, settlement, retention, *_ = accepted_import_archive()
    marker = make_import_retention_seal_marker(
        seal_class=ImportRetentionSealClass.IMPORT_ARCHIVE,
        sequence=1,
        summary_import_settlement_report=settlement,
        import_archive_report=archive,
        export_retention_audit_report=retention,
        family_id="seal-a",
        path_family_id="seal-path-a",
    )
    bad = replace(marker, import_archive_digest=ZERO_DIGEST)
    report = assess_import_retention_seal(summary_import_settlement_report=settlement, import_archive_report=archive, export_retention_audit_report=retention, markers=(bad,), required_classes=(ImportRetentionSealClass.IMPORT_ARCHIVE,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ImportRetentionSealDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_import_settlement_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_import_settlement_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
