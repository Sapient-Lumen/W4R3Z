from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.summarysendcanary import (
    SummarySendCanaryClass,
    SummarySendCanaryDecisionKind,
    assess_summary_send_canary,
    make_summary_send_canary_marker,
)
from i2p_dht_lab.redactiongcjoin import (
    RedactionGCClass,
    RedactionGCDecisionKind,
    assess_redaction_gc_join,
    make_redaction_gc_marker,
)
from i2p_dht_lab.outboxsettlement import (
    OutboxSettlementClass,
    OutboxSettlementDecisionKind,
    assess_outbox_settlement,
    make_outbox_settlement_marker,
)
from i2p_dht_lab.summarydeliveryreceipt import (
    SummaryDeliveryDecisionKind,
    SummaryDeliveryReceiptKind,
    assess_summary_delivery_receipts,
    make_summary_delivery_receipt,
)
from i2p_dht_lab.summarysendfold import audit_summary_send_fold
from test_rev0074_summaryoutbox_redactionarchive_publishfence import (
    accepted_import_prune_audit,
    accepted_redaction_archive,
    accepted_redaction_witness,
    accepted_summary_outbox,
    accepted_summary_publish,
    accepted_summary_publish_fence,
)


def accepted_summary_send_canary(publish=None, witness=None, audit=None, outbox=None, archive=None, fence=None):
    publish = publish or accepted_summary_publish()
    witness = witness or accepted_redaction_witness(publish)
    audit = audit or accepted_import_prune_audit(publish=publish, witness=witness)
    outbox = outbox or accepted_summary_outbox(publish, witness, audit)
    archive = archive or accepted_redaction_archive(publish, witness, audit)
    fence = fence or accepted_summary_publish_fence(outbox, archive, audit)
    classes = (
        SummarySendCanaryClass.PUBLISH_FENCE,
        SummarySendCanaryClass.SUMMARY_OUTBOX,
        SummarySendCanaryClass.REDACTION_ARCHIVE,
        SummarySendCanaryClass.IMPORT_PRUNE_AUDIT,
        SummarySendCanaryClass.CONTRADICTION_MEMORY,
    )
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_send_canary_marker(
            canary_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_publish_fence_report=fence,
            summary_outbox_report=outbox,
            redaction_archive_report=archive,
            import_prune_audit_report=audit,
            family_id=f"canary-{seq}",
            path_family_id=f"path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_send_canary(
        summary_publish_fence_report=fence,
        summary_outbox_report=outbox,
        redaction_archive_report=archive,
        import_prune_audit_report=audit,
        markers=tuple(markers),
        previous_digest=ZERO_DIGEST,
    )
    assert report.decision_kind is SummarySendCanaryDecisionKind.ACCEPT_SUMMARY_SEND_CANARY_READY
    return report, (publish, witness, audit, outbox, archive, fence)


def accepted_redaction_gc_join(publish=None, witness=None, audit=None, outbox=None, archive=None, fence=None, canary=None):
    if canary is None:
        canary, parts = accepted_summary_send_canary(publish, witness, audit, outbox, archive, fence)
        publish, witness, audit, outbox, archive, fence = parts
    classes = (
        RedactionGCClass.SUMMARY_OUTBOX,
        RedactionGCClass.REDACTION_ARCHIVE,
        RedactionGCClass.PUBLISH_FENCE,
        RedactionGCClass.SEND_CANARY,
        RedactionGCClass.CONTRADICTION_MEMORY,
    )
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        marker = make_redaction_gc_marker(
            gc_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_outbox_report=outbox,
            redaction_archive_report=archive,
            publish_fence_report=fence,
            send_canary_report=canary,
            soft_bytes_reclaimed=64 * seq,
            family_id=f"gc-{seq}",
            path_family_id=f"path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_redaction_gc_join(
        summary_outbox_report=outbox,
        redaction_archive_report=archive,
        publish_fence_report=fence,
        send_canary_report=canary,
        markers=tuple(markers),
        previous_digest=ZERO_DIGEST,
    )
    assert report.decision_kind is RedactionGCDecisionKind.ACCEPT_REDACTION_GC_JOINED
    return report, (publish, witness, audit, outbox, archive, fence, canary)


def accepted_outbox_settlement(publish=None, witness=None, audit=None, outbox=None, archive=None, fence=None, canary=None, gc=None):
    if gc is None:
        gc, parts = accepted_redaction_gc_join(publish, witness, audit, outbox, archive, fence, canary)
        publish, witness, audit, outbox, archive, fence, canary = parts
    classes = (
        OutboxSettlementClass.SUMMARY_OUTBOX,
        OutboxSettlementClass.SUMMARY_SEND_CANARY,
        OutboxSettlementClass.REDACTION_GC,
        OutboxSettlementClass.PUBLISH_FENCE,
        OutboxSettlementClass.CONTRADICTION_MEMORY,
    )
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate(classes, start=1):
        marker = make_outbox_settlement_marker(
            settlement_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_outbox_report=outbox,
            summary_send_canary_report=canary,
            redaction_gc_report=gc,
            publish_fence_report=fence,
            family_id=f"settle-{seq}",
            path_family_id=f"path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_outbox_settlement(
        summary_outbox_report=outbox,
        summary_send_canary_report=canary,
        redaction_gc_report=gc,
        publish_fence_report=fence,
        markers=tuple(markers),
        previous_digest=ZERO_DIGEST,
    )
    assert report.decision_kind is OutboxSettlementDecisionKind.ACCEPT_OUTBOX_SETTLED_READY
    return report, (publish, witness, audit, outbox, archive, fence, canary, gc)


def test_summary_send_canary_gc_settlement_happy_path() -> None:
    canary, parts = accepted_summary_send_canary()
    gc, parts2 = accepted_redaction_gc_join(canary=canary, publish=parts[0], witness=parts[1], audit=parts[2], outbox=parts[3], archive=parts[4], fence=parts[5])
    settlement, _ = accepted_outbox_settlement(publish=parts2[0], witness=parts2[1], audit=parts2[2], outbox=parts2[3], archive=parts2[4], fence=parts2[5], canary=parts2[6], gc=gc)
    assert canary.canary_ready and canary.contradiction_carried
    assert gc.redaction_gc_joined and gc.contradiction_preserved and gc.soft_bytes_reclaimed > 0
    assert settlement.outbox_settled and settlement.contradiction_preserved


def test_summary_send_canary_rejects_raw_payload_leak() -> None:
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    outbox = accepted_summary_outbox(publish, witness, audit)
    archive = accepted_redaction_archive(publish, witness, audit)
    fence = accepted_summary_publish_fence(outbox, archive, audit)
    marker = make_summary_send_canary_marker(canary_class=SummarySendCanaryClass.PUBLISH_FENCE, sequence=1, summary_publish_fence_report=fence, summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, raw_payload_exposed=True, family_id="canary-a", path_family_id="path-a")
    report = assess_summary_send_canary(summary_publish_fence_report=fence, summary_outbox_report=outbox, redaction_archive_report=archive, import_prune_audit_report=audit, markers=(marker,), required_classes=(SummarySendCanaryClass.PUBLISH_FENCE,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummarySendCanaryDecisionKind.QUARANTINE_RAW_LEAK


def test_redaction_gc_join_rejects_contradiction_drop() -> None:
    canary, parts = accepted_summary_send_canary()
    publish, witness, audit, outbox, archive, fence = parts
    marker = make_redaction_gc_marker(gc_class=RedactionGCClass.CONTRADICTION_MEMORY, sequence=1, summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, send_canary_report=canary, contradiction_carried=False, family_id="gc-a", path_family_id="path-a")
    report = assess_redaction_gc_join(summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, send_canary_report=canary, markers=(marker,), required_classes=(RedactionGCClass.CONTRADICTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionGCDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_redaction_gc_join_rejects_canary_digest_drift() -> None:
    canary, parts = accepted_summary_send_canary()
    publish, witness, audit, outbox, archive, fence = parts
    marker = make_redaction_gc_marker(gc_class=RedactionGCClass.SEND_CANARY, sequence=1, summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, send_canary_report=canary, family_id="gc-a", path_family_id="path-a")
    object.__setattr__(marker, "send_canary_digest", ZERO_DIGEST)
    report = assess_redaction_gc_join(summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, send_canary_report=canary, markers=(marker,), required_classes=(RedactionGCClass.SEND_CANARY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionGCDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_outbox_settlement_holds_missing_required_class() -> None:
    gc, parts = accepted_redaction_gc_join()
    publish, witness, audit, outbox, archive, fence, canary = parts
    marker = make_outbox_settlement_marker(settlement_class=OutboxSettlementClass.SUMMARY_OUTBOX, sequence=1, summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, family_id="settle-a", path_family_id="path-a")
    report = assess_outbox_settlement(summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, markers=(marker,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is OutboxSettlementDecisionKind.HOLD_MISSING_REQUIRED_CLASS


def test_outbox_settlement_rejects_previous_link_mismatch() -> None:
    gc, parts = accepted_redaction_gc_join()
    publish, witness, audit, outbox, archive, fence, canary = parts
    m1 = make_outbox_settlement_marker(settlement_class=OutboxSettlementClass.SUMMARY_OUTBOX, sequence=1, summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, family_id="settle-a", path_family_id="path-a")
    m2 = make_outbox_settlement_marker(settlement_class=OutboxSettlementClass.SUMMARY_SEND_CANARY, sequence=2, previous_digest=ZERO_DIGEST, summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, family_id="settle-b", path_family_id="path-b")
    report = assess_outbox_settlement(summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, markers=(m1, m2), required_classes=(OutboxSettlementClass.SUMMARY_OUTBOX, OutboxSettlementClass.SUMMARY_SEND_CANARY), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is OutboxSettlementDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_summary_delivery_receipt_refusal_is_watch_not_success() -> None:
    canary, _ = accepted_summary_send_canary()
    r1 = make_summary_delivery_receipt(receipt_kind=SummaryDeliveryReceiptKind.REFUSAL, sequence=1, summary_send_canary_report=canary, family_id="delivery-a", path_family_id="path-a")
    r2 = make_summary_delivery_receipt(receipt_kind=SummaryDeliveryReceiptKind.REFUSAL, sequence=2, previous_digest=r1.receipt_digest, summary_send_canary_report=canary, family_id="delivery-b", path_family_id="path-b")
    report = assess_summary_delivery_receipts(summary_send_canary_report=canary, receipts=(r1, r2), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryDeliveryDecisionKind.ACCEPT_REFUSAL_WATCH
    assert report.watch and not report.delivered


def test_summary_send_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_send_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
