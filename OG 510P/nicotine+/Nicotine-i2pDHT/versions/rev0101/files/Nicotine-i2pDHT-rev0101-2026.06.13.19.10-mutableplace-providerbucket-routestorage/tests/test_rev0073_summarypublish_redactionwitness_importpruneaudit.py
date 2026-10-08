from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.importpruneaudit import ImportPruneAuditClass, ImportPruneAuditDecisionKind, assess_import_prune_audit, make_import_prune_audit_marker
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.redactionwitness import RedactionWitnessClass, RedactionWitnessDecisionKind, assess_redaction_witnesses, make_redaction_witness_receipt
from i2p_dht_lab.summarypublish import SummaryPublishChannel, SummaryPublishDecisionKind, assess_summary_publication, make_summary_publish_intent
from i2p_dht_lab.summarypublishfold import audit_summary_publish_fold
from test_rev0072_summaryreceipt_importarchive_lineageprune import accepted_import_archive, accepted_lineage_prune, accepted_summary_receipt


def accepted_summary_publish(receipt=None, archive=None, prune=None):
    receipt = receipt or accepted_summary_receipt()
    archive = archive or accepted_import_archive(receipt)
    prune = prune or accepted_lineage_prune(receipt, archive)
    p1 = make_summary_publish_intent(channel=SummaryPublishChannel.OPERATOR_NOTE, sequence=1, summary_receipt_report=receipt, import_archive_report=archive, lineage_prune_report=prune, family_id="pub-a", path_family_id="path-a")
    p2 = make_summary_publish_intent(channel=SummaryPublishChannel.GARDEN_SUMMARY, sequence=2, previous_digest=p1.intent_digest, summary_receipt_report=receipt, import_archive_report=archive, lineage_prune_report=prune, family_id="pub-b", path_family_id="path-b")
    report = assess_summary_publication(summary_receipt_report=receipt, import_archive_report=archive, lineage_prune_report=prune, intents=(p1, p2), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryPublishDecisionKind.ACCEPT_SUMMARY_PUBLICATION_READY
    return report


def accepted_redaction_witness(publish=None):
    publish = publish or accepted_summary_publish()
    classes = [
        RedactionWitnessClass.BOUNDARY_REDACTED,
        RedactionWitnessClass.PAYLOAD_REDACTED,
        RedactionWitnessClass.DIGEST_BOUND,
        RedactionWitnessClass.CONTRADICTION_CARRIED,
    ]
    receipts = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        receipt = make_redaction_witness_receipt(witness_class=cls, sequence=seq, previous_digest=prev, summary_publish_report=publish, family_id=f"redact-{seq}", path_family_id=f"path-{seq}")
        receipts.append(receipt)
        prev = receipt.receipt_digest
    report = assess_redaction_witnesses(summary_publish_report=publish, receipts=tuple(receipts), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is RedactionWitnessDecisionKind.ACCEPT_REDACTION_WITNESSED
    return report


def accepted_import_prune_audit(publish=None, witness=None, archive=None, prune=None):
    receipt = accepted_summary_receipt()
    archive = archive or accepted_import_archive(receipt)
    prune = prune or accepted_lineage_prune(receipt, archive)
    publish = publish or accepted_summary_publish(receipt, archive, prune)
    witness = witness or accepted_redaction_witness(publish)
    classes = [
        ImportPruneAuditClass.SUMMARY_PUBLICATION,
        ImportPruneAuditClass.REDACTION_WITNESS,
        ImportPruneAuditClass.IMPORT_ARCHIVE,
        ImportPruneAuditClass.LINEAGE_PRUNE,
        ImportPruneAuditClass.CONTRADICTION_MEMORY,
    ]
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        marker = make_import_prune_audit_marker(audit_class=cls, sequence=seq, previous_digest=prev, summary_publish_report=publish, redaction_witness_report=witness, import_archive_report=archive, lineage_prune_report=prune, family_id=f"audit-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_import_prune_audit(summary_publish_report=publish, redaction_witness_report=witness, import_archive_report=archive, lineage_prune_report=prune, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is ImportPruneAuditDecisionKind.ACCEPT_IMPORT_PRUNE_AUDITED
    return report


def test_summary_publish_redaction_audit_happy_path() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    assert publish.publication_ready and publish.contradiction_carried
    assert witness.redaction_witnessed and witness.contradiction_carried
    assert audit.import_prune_audited and audit.contradiction_preserved


def test_summary_publish_rejects_raw_public_payload_leak() -> None:
    receipt = accepted_summary_receipt()
    archive = accepted_import_archive(receipt)
    prune = accepted_lineage_prune(receipt, archive)
    p1 = make_summary_publish_intent(channel=SummaryPublishChannel.OPERATOR_NOTE, sequence=1, summary_receipt_report=receipt, import_archive_report=archive, lineage_prune_report=prune, raw_payload_exposed=True, family_id="pub-a", path_family_id="path-a")
    p2 = make_summary_publish_intent(channel=SummaryPublishChannel.GARDEN_SUMMARY, sequence=2, previous_digest=p1.intent_digest, summary_receipt_report=receipt, import_archive_report=archive, lineage_prune_report=prune, family_id="pub-b", path_family_id="path-b")
    report = assess_summary_publication(summary_receipt_report=receipt, import_archive_report=archive, lineage_prune_report=prune, intents=(p1, p2))
    assert report.decision_kind is SummaryPublishDecisionKind.QUARANTINE_RAW_LEAK


def test_redaction_witness_holds_missing_required_class() -> None:
    publish = accepted_summary_publish()
    r1 = make_redaction_witness_receipt(witness_class=RedactionWitnessClass.BOUNDARY_REDACTED, sequence=1, summary_publish_report=publish, family_id="redact-a", path_family_id="path-a")
    r2 = make_redaction_witness_receipt(witness_class=RedactionWitnessClass.PAYLOAD_REDACTED, sequence=2, previous_digest=r1.receipt_digest, summary_publish_report=publish, family_id="redact-b", path_family_id="path-b")
    report = assess_redaction_witnesses(summary_publish_report=publish, receipts=(r1, r2), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionWitnessDecisionKind.HOLD_MISSING_REQUIRED_CLASS


def test_redaction_witness_rejects_digest_drift() -> None:
    publish = accepted_summary_publish()
    receipts = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((RedactionWitnessClass.BOUNDARY_REDACTED, RedactionWitnessClass.PAYLOAD_REDACTED, RedactionWitnessClass.DIGEST_BOUND, RedactionWitnessClass.CONTRADICTION_CARRIED), start=1):
        receipt = make_redaction_witness_receipt(witness_class=cls, sequence=seq, previous_digest=prev, summary_publish_report=publish, family_id=f"redact-{seq}", path_family_id=f"path-{seq}")
        receipts.append(receipt)
        prev = receipt.receipt_digest
    object.__setattr__(receipts[-1], "accepted_intent_digest", ZERO_DIGEST)
    report = assess_redaction_witnesses(summary_publish_report=publish, receipts=tuple(receipts), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionWitnessDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_import_prune_audit_rejects_contradiction_drop() -> None:
    receipt = accepted_summary_receipt()
    archive = accepted_import_archive(receipt)
    prune = accepted_lineage_prune(receipt, archive)
    publish = accepted_summary_publish(receipt, archive, prune)
    witness = accepted_redaction_witness(publish)
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((ImportPruneAuditClass.SUMMARY_PUBLICATION, ImportPruneAuditClass.REDACTION_WITNESS, ImportPruneAuditClass.IMPORT_ARCHIVE, ImportPruneAuditClass.LINEAGE_PRUNE, ImportPruneAuditClass.CONTRADICTION_MEMORY), start=1):
        marker = make_import_prune_audit_marker(audit_class=cls, sequence=seq, previous_digest=prev, summary_publish_report=publish, redaction_witness_report=witness, import_archive_report=archive, lineage_prune_report=prune, contradiction_carried=False, family_id=f"audit-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_import_prune_audit(summary_publish_report=publish, redaction_witness_report=witness, import_archive_report=archive, lineage_prune_report=prune, markers=tuple(markers), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ImportPruneAuditDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_import_prune_audit_rejects_boundary_drift() -> None:
    receipt = accepted_summary_receipt()
    archive = accepted_import_archive(receipt)
    prune = accepted_lineage_prune(receipt, archive)
    publish = accepted_summary_publish(receipt, archive, prune)
    witness = accepted_redaction_witness(publish)
    marker = make_import_prune_audit_marker(audit_class=ImportPruneAuditClass.SUMMARY_PUBLICATION, sequence=1, summary_publish_report=publish, redaction_witness_report=witness, import_archive_report=archive, lineage_prune_report=prune, family_id="audit-a", path_family_id="path-a")
    object.__setattr__(marker, "request_digest", ZERO_DIGEST)
    report = assess_import_prune_audit(summary_publish_report=publish, redaction_witness_report=witness, import_archive_report=archive, lineage_prune_report=prune, markers=(marker,), min_family_count=1, min_path_family_count=1, required_classes=(ImportPruneAuditClass.SUMMARY_PUBLICATION,))
    assert report.decision_kind is ImportPruneAuditDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_summary_publish_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_publish_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
