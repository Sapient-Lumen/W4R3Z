from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.outboxsettlement import OutboxSettlementClass, OutboxSettlementDecisionKind, assess_outbox_settlement, make_outbox_settlement_marker
from i2p_dht_lab.summarysendcanary import SummarySendCanaryClass, SummarySendCanaryDecisionKind, assess_summary_send_canary, make_summary_send_canary_marker
from i2p_dht_lab.summarysendfold import audit_summary_send_fold
from test_rev0074_summaryoutbox_redactionarchive_publishfence import accepted_redaction_archive, accepted_summary_outbox, accepted_summary_publish_fence
from test_rev0074_summarysettlement_publicledger_redactiongc import accepted_public_ledger, accepted_redaction_gc, accepted_summary_settlement
from test_rev0073_summarypublish_redactionwitness_importpruneaudit import accepted_import_prune_audit, accepted_redaction_witness, accepted_summary_publish


def accepted_current_components():
    publish = accepted_summary_publish()
    witness = accepted_redaction_witness(publish)
    audit = accepted_import_prune_audit(publish=publish, witness=witness)
    outbox = accepted_summary_outbox(publish, witness, audit)
    archive = accepted_redaction_archive(publish, witness, audit)
    fence = accepted_summary_publish_fence(outbox, archive, audit)
    settlement = accepted_summary_settlement(publish, witness, audit)
    ledger = accepted_public_ledger(settlement)
    gc = accepted_redaction_gc(settlement, ledger)
    return outbox, fence, settlement, ledger, gc


def accepted_outbox_settlement():
    outbox, fence, settlement, ledger, gc = accepted_current_components()
    markers = []
    prev = ZERO_DIGEST
    classes = (OutboxSettlementClass.SUMMARY_OUTBOX, OutboxSettlementClass.PUBLISH_FENCE, OutboxSettlementClass.SUMMARY_SETTLEMENT, OutboxSettlementClass.PUBLIC_LEDGER, OutboxSettlementClass.REDACTION_GC, OutboxSettlementClass.CONTRADICTION_MEMORY)
    for seq, cls in enumerate(classes, start=1):
        marker = make_outbox_settlement_marker(settlement_class=cls, sequence=seq, previous_digest=prev, summary_outbox_report=outbox, publish_fence_report=fence, summary_settlement_report=settlement, public_ledger_report=ledger, redaction_gc_report=gc, family_id=f"settle-join-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_outbox_settlement(summary_outbox_report=outbox, publish_fence_report=fence, summary_settlement_report=settlement, public_ledger_report=ledger, redaction_gc_report=gc, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is OutboxSettlementDecisionKind.ACCEPT_OUTBOX_SETTLED
    return report, outbox, fence, settlement, ledger, gc


def accepted_summary_send_canary():
    settlement_report, _outbox, fence, _settlement, ledger, gc = accepted_outbox_settlement()
    markers = []
    prev = ZERO_DIGEST
    classes = (SummarySendCanaryClass.OUTBOX_SETTLEMENT, SummarySendCanaryClass.PUBLISH_FENCE, SummarySendCanaryClass.PUBLIC_LEDGER, SummarySendCanaryClass.REDACTION_GC, SummarySendCanaryClass.REDACTION_OK, SummarySendCanaryClass.CONTRADICTION_MEMORY)
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_send_canary_marker(canary_class=cls, sequence=seq, previous_digest=prev, outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, family_id=f"canary-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_send_canary(outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummarySendCanaryDecisionKind.ACCEPT_SUMMARY_SEND_CANARY
    return report


def test_summary_send_canary_happy_path() -> None:
    settlement_report, _outbox, _fence, _settlement, _ledger, _gc = accepted_outbox_settlement()
    canary = accepted_summary_send_canary()
    assert settlement_report.outbox_settled and settlement_report.contradiction_preserved
    assert canary.send_canary_ready and canary.contradiction_preserved and canary.redacted


def test_outbox_settlement_rejects_publish_fence_outbox_digest_drift() -> None:
    outbox, fence, settlement, ledger, gc = accepted_current_components()
    object.__setattr__(fence, "summary_outbox_digest", ZERO_DIGEST)
    marker = make_outbox_settlement_marker(settlement_class=OutboxSettlementClass.SUMMARY_OUTBOX, sequence=1, summary_outbox_report=outbox, publish_fence_report=fence, summary_settlement_report=settlement, public_ledger_report=ledger, redaction_gc_report=gc, family_id="join-a", path_family_id="path-a")
    report = assess_outbox_settlement(summary_outbox_report=outbox, publish_fence_report=fence, summary_settlement_report=settlement, public_ledger_report=ledger, redaction_gc_report=gc, markers=(marker,), required_classes=(OutboxSettlementClass.SUMMARY_OUTBOX,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is OutboxSettlementDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_outbox_settlement_rejects_contradiction_drop() -> None:
    outbox, fence, settlement, ledger, gc = accepted_current_components()
    marker = make_outbox_settlement_marker(settlement_class=OutboxSettlementClass.CONTRADICTION_MEMORY, sequence=1, summary_outbox_report=outbox, publish_fence_report=fence, summary_settlement_report=settlement, public_ledger_report=ledger, redaction_gc_report=gc, contradiction_carried=False, family_id="join-a", path_family_id="path-a")
    report = assess_outbox_settlement(summary_outbox_report=outbox, publish_fence_report=fence, summary_settlement_report=settlement, public_ledger_report=ledger, redaction_gc_report=gc, markers=(marker,), required_classes=(OutboxSettlementClass.CONTRADICTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is OutboxSettlementDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_summary_send_canary_rejects_raw_payload_leak() -> None:
    settlement_report, _outbox, fence, _settlement, ledger, gc = accepted_outbox_settlement()
    marker = make_summary_send_canary_marker(canary_class=SummarySendCanaryClass.OUTBOX_SETTLEMENT, sequence=1, outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, raw_payload_exposed=True, family_id="canary-a", path_family_id="path-a")
    report = assess_summary_send_canary(outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, markers=(marker,), required_classes=(SummarySendCanaryClass.OUTBOX_SETTLEMENT,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummarySendCanaryDecisionKind.QUARANTINE_RAW_LEAK


def test_summary_send_canary_rejects_public_ledger_digest_drift() -> None:
    settlement_report, _outbox, fence, _settlement, ledger, gc = accepted_outbox_settlement()
    object.__setattr__(settlement_report, "public_ledger_digest", ZERO_DIGEST)
    marker = make_summary_send_canary_marker(canary_class=SummarySendCanaryClass.PUBLIC_LEDGER, sequence=1, outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, family_id="canary-a", path_family_id="path-a")
    report = assess_summary_send_canary(outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, markers=(marker,), required_classes=(SummarySendCanaryClass.PUBLIC_LEDGER,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummarySendCanaryDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_summary_send_canary_rejects_previous_link_mismatch() -> None:
    settlement_report, _outbox, fence, _settlement, ledger, gc = accepted_outbox_settlement()
    m1 = make_summary_send_canary_marker(canary_class=SummarySendCanaryClass.OUTBOX_SETTLEMENT, sequence=1, outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, family_id="canary-a", path_family_id="path-a")
    m2 = make_summary_send_canary_marker(canary_class=SummarySendCanaryClass.PUBLIC_LEDGER, sequence=2, previous_digest=ZERO_DIGEST, outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, family_id="canary-b", path_family_id="path-b")
    report = assess_summary_send_canary(outbox_settlement_report=settlement_report, publish_fence_report=fence, public_ledger_report=ledger, redaction_gc_report=gc, markers=(m1, m2), required_classes=(SummarySendCanaryClass.OUTBOX_SETTLEMENT, SummarySendCanaryClass.PUBLIC_LEDGER), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummarySendCanaryDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_summary_send_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_send_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
