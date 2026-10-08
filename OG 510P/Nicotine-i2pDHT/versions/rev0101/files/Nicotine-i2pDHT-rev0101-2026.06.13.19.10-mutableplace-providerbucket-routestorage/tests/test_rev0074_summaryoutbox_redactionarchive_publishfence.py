from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.publishfence import SummaryPublishFenceClass, SummaryPublishFenceDecisionKind, assess_summary_publish_fence, make_summary_publish_fence_marker
from i2p_dht_lab.redactionarchive import RedactionArchiveClass, RedactionArchiveDecisionKind, assess_redaction_archive, make_redaction_archive_marker
from i2p_dht_lab.summaryoutbox import SummaryOutboxDecisionKind, SummaryOutboxTarget, assess_summary_outbox, make_summary_outbox_entry
from i2p_dht_lab.summaryoutboxfold import audit_summary_outbox_fold
from test_rev0073_summarypublish_redactionwitness_importpruneaudit import accepted_import_prune_audit, accepted_redaction_witness, accepted_summary_publish


def accepted_summary_outbox(publish=None, witness=None, audit=None):
    publish = publish or accepted_summary_publish()
    witness = witness or accepted_redaction_witness(publish)
    audit = audit or accepted_import_prune_audit(publish=publish, witness=witness)
    e1 = make_summary_outbox_entry(target=SummaryOutboxTarget.OPERATOR, sequence=1, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, family_id="outbox-a", path_family_id="path-a")
    e2 = make_summary_outbox_entry(target=SummaryOutboxTarget.PUBLIC, sequence=2, previous_digest=e1.entry_digest, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, family_id="outbox-b", path_family_id="path-b")
    report = assess_summary_outbox(summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, entries=(e1, e2), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryOutboxDecisionKind.ACCEPT_SUMMARY_OUTBOX_STAGED
    return report


def accepted_redaction_archive(publish=None, witness=None, audit=None):
    publish = publish or accepted_summary_publish()
    witness = witness or accepted_redaction_witness(publish)
    audit = audit or accepted_import_prune_audit(publish=publish, witness=witness)
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((RedactionArchiveClass.SUMMARY_PUBLICATION, RedactionArchiveClass.REDACTION_WITNESS, RedactionArchiveClass.IMPORT_PRUNE_AUDIT, RedactionArchiveClass.CONTRADICTION_MEMORY), start=1):
        marker = make_redaction_archive_marker(archive_class=cls, sequence=seq, previous_digest=prev, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, family_id=f"archive-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_redaction_archive(summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is RedactionArchiveDecisionKind.ACCEPT_REDACTION_ARCHIVED
    return report


def accepted_summary_publish_fence(outbox=None, archive=None, audit=None):
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = audit or accepted_import_prune_audit(publish=publish, witness=witness)
    outbox = outbox or accepted_summary_outbox(publish, witness, audit)
    archive = archive or accepted_redaction_archive(publish, witness, audit)
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((SummaryPublishFenceClass.SUMMARY_OUTBOX, SummaryPublishFenceClass.REDACTION_ARCHIVE, SummaryPublishFenceClass.IMPORT_PRUNE_AUDIT, SummaryPublishFenceClass.CONTRADICTION_MEMORY), start=1):
        marker = make_summary_publish_fence_marker(fence_class=cls, sequence=seq, previous_digest=prev, summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, family_id=f"fence-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_publish_fence(summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryPublishFenceDecisionKind.ACCEPT_SUMMARY_PUBLISH_FENCED
    return report


def test_summary_outbox_archive_fence_happy_path() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    outbox = accepted_summary_outbox(publish, witness, audit)
    archive = accepted_redaction_archive(publish, witness, audit)
    fence = accepted_summary_publish_fence(outbox, archive, audit)
    assert outbox.outbox_staged and outbox.contradiction_carried
    assert archive.redaction_archived and archive.contradiction_preserved
    assert fence.summary_publish_fenced and fence.contradiction_preserved


def test_summary_outbox_rejects_public_raw_leak() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    e1 = make_summary_outbox_entry(target=SummaryOutboxTarget.PUBLIC, sequence=1, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, raw_payload_exposed=True, family_id="outbox-a", path_family_id="path-a")
    e2 = make_summary_outbox_entry(target=SummaryOutboxTarget.GARDEN, sequence=2, previous_digest=e1.entry_digest, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, family_id="outbox-b", path_family_id="path-b")
    report = assess_summary_outbox(summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, entries=(e1, e2))
    assert report.decision_kind is SummaryOutboxDecisionKind.QUARANTINE_RAW_LEAK


def test_redaction_archive_rejects_contradiction_drop() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    marker = make_redaction_archive_marker(archive_class=RedactionArchiveClass.CONTRADICTION_MEMORY, sequence=1, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, contradiction_carried=False, family_id="archive-a", path_family_id="path-a")
    report = assess_redaction_archive(summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, markers=(marker,), required_classes=(RedactionArchiveClass.CONTRADICTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionArchiveDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_redaction_archive_rejects_digest_drift() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    marker = make_redaction_archive_marker(archive_class=RedactionArchiveClass.REDACTION_WITNESS, sequence=1, summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, family_id="archive-a", path_family_id="path-a")
    object.__setattr__(marker, "redaction_witness_digest", ZERO_DIGEST)
    report = assess_redaction_archive(summary_publish_report=publish, redaction_witness_report=witness, import_prune_audit_report=audit, markers=(marker,), required_classes=(RedactionArchiveClass.REDACTION_WITNESS,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionArchiveDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_publish_fence_holds_missing_required_class() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    outbox = accepted_summary_outbox(publish, witness, audit)
    archive = accepted_redaction_archive(publish, witness, audit)
    marker = make_summary_publish_fence_marker(fence_class=SummaryPublishFenceClass.SUMMARY_OUTBOX, sequence=1, summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, family_id="fence-a", path_family_id="path-a")
    report = assess_summary_publish_fence(summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, markers=(marker,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryPublishFenceDecisionKind.HOLD_MISSING_REQUIRED_CLASS


def test_publish_fence_rejects_previous_link_mismatch() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    outbox = accepted_summary_outbox(publish, witness, audit)
    archive = accepted_redaction_archive(publish, witness, audit)
    m1 = make_summary_publish_fence_marker(fence_class=SummaryPublishFenceClass.SUMMARY_OUTBOX, sequence=1, summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, family_id="fence-a", path_family_id="path-a")
    m2 = make_summary_publish_fence_marker(fence_class=SummaryPublishFenceClass.REDACTION_ARCHIVE, sequence=2, previous_digest=ZERO_DIGEST, summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, family_id="fence-b", path_family_id="path-b")
    report = assess_summary_publish_fence(summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, markers=(m1, m2), required_classes=(SummaryPublishFenceClass.SUMMARY_OUTBOX, SummaryPublishFenceClass.REDACTION_ARCHIVE), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryPublishFenceDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_summary_outbox_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_outbox_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
