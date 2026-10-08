from pathlib import Path

from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.outboxsettlement import OutboxSettlementClass, OutboxSettlementDecisionKind, assess_outbox_settlement, make_outbox_settlement_marker
from i2p_dht_lab.redactiongc import RedactionGCClass, RedactionGCDecisionKind, assess_redaction_gc, make_redaction_gc_marker
from i2p_dht_lab.summarysendcanary import SummarySendCanaryDecisionKind, SummarySendCanaryTarget, assess_summary_send_canary, make_summary_send_canary_probe
from i2p_dht_lab.summarysendfold import audit_summary_send_fold
from test_rev0074_summaryoutbox_redactionarchive_publishfence import accepted_redaction_archive, accepted_summary_outbox, accepted_summary_publish_fence


def accepted_summary_send_canary(outbox=None, archive=None, fence=None):
    outbox = outbox or accepted_summary_outbox()
    archive = archive or accepted_redaction_archive()
    fence = fence or accepted_summary_publish_fence(outbox=outbox, archive=archive)
    c1 = make_summary_send_canary_probe(target=SummarySendCanaryTarget.OPERATOR, sequence=1, summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, family_id="canary-a", path_family_id="path-a")
    c2 = make_summary_send_canary_probe(target=SummarySendCanaryTarget.PUBLIC, sequence=2, previous_digest=c1.probe_digest, summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, family_id="canary-b", path_family_id="path-b")
    report = assess_summary_send_canary(summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, probes=(c1, c2), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummarySendCanaryDecisionKind.ACCEPT_SUMMARY_SEND_CANARY_READY
    return report


def accepted_redaction_gc(canary=None, archive=None, fence=None):
    outbox = accepted_summary_outbox()
    archive = archive or accepted_redaction_archive()
    fence = fence or accepted_summary_publish_fence(outbox=outbox, archive=archive)
    canary = canary or accepted_summary_send_canary(outbox, archive, fence)
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((RedactionGCClass.SUMMARY_SEND_CANARY, RedactionGCClass.REDACTION_ARCHIVE, RedactionGCClass.PUBLISH_FENCE, RedactionGCClass.CONTRADICTION_MEMORY, RedactionGCClass.REDACTED_SUMMARY_MEMORY), start=1):
        marker = make_redaction_gc_marker(gc_class=cls, sequence=seq, previous_digest=prev, summary_send_canary_report=canary, redaction_archive_report=archive, publish_fence_report=fence, family_id=f"gc-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_redaction_gc(summary_send_canary_report=canary, redaction_archive_report=archive, publish_fence_report=fence, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is RedactionGCDecisionKind.ACCEPT_REDACTION_GC_READY
    return report


def accepted_outbox_settlement(outbox=None, canary=None, gc=None, fence=None):
    outbox = outbox or accepted_summary_outbox()
    archive = accepted_redaction_archive()
    fence = fence or accepted_summary_publish_fence(outbox=outbox, archive=archive)
    canary = canary or accepted_summary_send_canary(outbox, archive, fence)
    gc = gc or accepted_redaction_gc(canary, archive, fence)
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((OutboxSettlementClass.SUMMARY_OUTBOX, OutboxSettlementClass.SUMMARY_SEND_CANARY, OutboxSettlementClass.REDACTION_GC, OutboxSettlementClass.PUBLISH_FENCE, OutboxSettlementClass.CONTRADICTION_MEMORY), start=1):
        marker = make_outbox_settlement_marker(settlement_class=cls, sequence=seq, previous_digest=prev, summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, family_id=f"settle-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_outbox_settlement(summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is OutboxSettlementDecisionKind.ACCEPT_OUTBOX_SETTLED_READY
    return report


def test_summary_send_redaction_gc_settlement_happy_path() -> None:
    outbox = accepted_summary_outbox()
    archive = accepted_redaction_archive()
    fence = accepted_summary_publish_fence(outbox=outbox, archive=archive)
    canary = accepted_summary_send_canary(outbox, archive, fence)
    gc = accepted_redaction_gc(canary, archive, fence)
    settlement = accepted_outbox_settlement(outbox, canary, gc, fence)
    assert canary.canary_ready and canary.contradiction_carried
    assert gc.redaction_gc_ready and gc.redacted_summary_preserved
    assert settlement.outbox_settled and settlement.contradiction_preserved


def test_summary_canary_rejects_raw_payload_leak() -> None:
    outbox = accepted_summary_outbox()
    archive = accepted_redaction_archive()
    fence = accepted_summary_publish_fence(outbox=outbox, archive=archive)
    c1 = make_summary_send_canary_probe(target=SummarySendCanaryTarget.PUBLIC, sequence=1, summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, raw_payload_exposed=True, family_id="canary-a", path_family_id="path-a")
    report = assess_summary_send_canary(summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, probes=(c1,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummarySendCanaryDecisionKind.QUARANTINE_RAW_LEAK


def test_summary_canary_rejects_boundary_drift() -> None:
    outbox = accepted_summary_outbox()
    archive = accepted_redaction_archive()
    fence = accepted_summary_publish_fence(outbox=outbox, archive=archive)
    c1 = make_summary_send_canary_probe(target=SummarySendCanaryTarget.PUBLIC, sequence=1, summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, family_id="canary-a", path_family_id="path-a")
    object.__setattr__(c1, "request_digest", sha256(DOMAIN + b":rev0075:drift"))
    report = assess_summary_send_canary(summary_outbox_report=outbox, redaction_archive_report=archive, publish_fence_report=fence, probes=(c1,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummarySendCanaryDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_redaction_gc_rejects_contradiction_drop() -> None:
    outbox = accepted_summary_outbox()
    archive = accepted_redaction_archive()
    fence = accepted_summary_publish_fence(outbox=outbox, archive=archive)
    canary = accepted_summary_send_canary(outbox, archive, fence)
    marker = make_redaction_gc_marker(gc_class=RedactionGCClass.CONTRADICTION_MEMORY, sequence=1, summary_send_canary_report=canary, redaction_archive_report=archive, publish_fence_report=fence, contradiction_carried=False, family_id="gc-a", path_family_id="path-a")
    report = assess_redaction_gc(summary_send_canary_report=canary, redaction_archive_report=archive, publish_fence_report=fence, markers=(marker,), required_classes=(RedactionGCClass.CONTRADICTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionGCDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_redaction_gc_rejects_previous_mismatch() -> None:
    outbox = accepted_summary_outbox()
    archive = accepted_redaction_archive()
    fence = accepted_summary_publish_fence(outbox=outbox, archive=archive)
    canary = accepted_summary_send_canary(outbox, archive, fence)
    m1 = make_redaction_gc_marker(gc_class=RedactionGCClass.SUMMARY_SEND_CANARY, sequence=1, summary_send_canary_report=canary, redaction_archive_report=archive, publish_fence_report=fence, family_id="gc-a", path_family_id="path-a")
    m2 = make_redaction_gc_marker(gc_class=RedactionGCClass.REDACTION_ARCHIVE, sequence=2, previous_digest=ZERO_DIGEST, summary_send_canary_report=canary, redaction_archive_report=archive, publish_fence_report=fence, family_id="gc-b", path_family_id="path-b")
    report = assess_redaction_gc(summary_send_canary_report=canary, redaction_archive_report=archive, publish_fence_report=fence, markers=(m1, m2), required_classes=(RedactionGCClass.SUMMARY_SEND_CANARY, RedactionGCClass.REDACTION_ARCHIVE), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is RedactionGCDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_outbox_settlement_rejects_digest_drift() -> None:
    outbox = accepted_summary_outbox()
    archive = accepted_redaction_archive()
    fence = accepted_summary_publish_fence(outbox=outbox, archive=archive)
    canary = accepted_summary_send_canary(outbox, archive, fence)
    gc = accepted_redaction_gc(canary, archive, fence)
    marker = make_outbox_settlement_marker(settlement_class=OutboxSettlementClass.REDACTION_GC, sequence=1, summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, family_id="settle-a", path_family_id="path-a")
    object.__setattr__(marker, "redaction_gc_digest", ZERO_DIGEST)
    report = assess_outbox_settlement(summary_outbox_report=outbox, summary_send_canary_report=canary, redaction_gc_report=gc, publish_fence_report=fence, markers=(marker,), required_classes=(OutboxSettlementClass.REDACTION_GC,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is OutboxSettlementDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_summary_send_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_send_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
