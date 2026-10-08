from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path

from i2p_dht_lab.auditexport import AuditExportAudience, assess_audit_export, make_audit_export_bundle
from i2p_dht_lab.closurehandoff import ClosureHandoffAudience, ClosureHandoffDecisionKind, assess_closure_handoff, make_closure_handoff_packet
from i2p_dht_lab.closureseal import ClosureSealEntryKind, assess_closure_seal, make_closure_seal_entry
from i2p_dht_lab.exporthandofffold import audit_export_handoff_fold
from i2p_dht_lab.exportreceipt import ExportReceiptDecisionKind, ExportReceiptKind, assess_export_receipts, make_export_receipt_entry
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.retentiongc import RetentionGcClass, RetentionGcDecisionKind, assess_retention_gc, make_retention_gc_marker
from i2p_dht_lab.retentionproof import RetentionItemKind, assess_retention_proof, make_retention_item
from i2p_dht_lab.sideeffectjournal import SideEffectAction

ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
PROFILE = "rev0070-profile"
SERVICE = "rev0070-public-edge"
SCOPE = sha256(DOMAIN + b":rev0070:scope")
REQUEST = sha256(DOMAIN + b":rev0070:request")
PAYLOAD = sha256(DOMAIN + b":rev0070:payload")
IDEM = sha256(DOMAIN + b":rev0070:idem")
RETRY_IDEM = sha256(DOMAIN + b":rev0070:retry-idem")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0070:" + label.encode())


def component(label: str, **kw):
    base = dict(
        report_digest=d(label),
        accepted_marker_digest=d(label + ":marker"),
        accepted_entry_digest=d(label + ":entry"),
        accept=True,
        watch=False,
        closure_audited=True,
        contradiction_preserved=True,
        replay_stable=True,
        prune_memory_preserved=True,
        prune_marker_preserved=True,
        action=ACTION,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        retry_idempotency_key=RETRY_IDEM,
        restart_generation=7,
        family_count=2,
        path_family_count=2,
        hard_negative_count=0,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def accepted_rev0069_export():
    closure_audit = component("closure-audit")
    archive_journal = component("archive-journal")
    prune_replay = component("prune-replay")
    s1 = make_closure_seal_entry(kind=ClosureSealEntryKind.CLOSURE_AUDIT_SEALED, sequence=1, closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, family_id="seal-a", path_family_id="path-a")
    s2 = make_closure_seal_entry(kind=ClosureSealEntryKind.CONTRADICTION_MEMORY_SEALED, sequence=2, previous_digest=s1.entry_digest, closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, family_id="seal-b", path_family_id="path-b")
    s3 = make_closure_seal_entry(kind=ClosureSealEntryKind.EXPORT_BOUNDARY_SEALED, sequence=3, previous_digest=s2.entry_digest, closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, family_id="seal-c", path_family_id="path-c")
    seal = assess_closure_seal(closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, entries=(s1, s2, s3), previous_digest=ZERO_DIGEST)
    assert seal.accept
    items = []
    prev = ZERO_DIGEST
    for seq, (kind, family) in enumerate(((RetentionItemKind.CLOSURE_SEAL, "ret-a"), (RetentionItemKind.CLOSURE_AUDIT, "ret-b"), (RetentionItemKind.ARCHIVE_JOURNAL, "ret-c"), (RetentionItemKind.PRUNE_REPLAY, "ret-d"), (RetentionItemKind.CONTRADICTION_MEMORY, "ret-e"), (RetentionItemKind.REDACTED_OPERATOR_SUMMARY, "ret-f")), start=1):
        item = make_retention_item(kind=kind, sequence=seq, previous_digest=prev, closure_seal_report=seal, family_id=family, path_family_id="path-" + family[-1])
        items.append(item)
        prev = item.item_digest
    retention = assess_retention_proof(closure_seal_report=seal, items=tuple(items), previous_digest=ZERO_DIGEST)
    assert retention.accept
    e1 = make_audit_export_bundle(audience=AuditExportAudience.LOCAL_OPERATOR, sequence=1, closure_seal_report=seal, retention_proof_report=retention, family_id="export-a", path_family_id="path-a")
    e2 = make_audit_export_bundle(audience=AuditExportAudience.GARDEN_WITNESS, sequence=2, previous_digest=e1.bundle_digest, closure_seal_report=seal, retention_proof_report=retention, family_id="export-b", path_family_id="path-b")
    export = assess_audit_export(closure_seal_report=seal, retention_proof_report=retention, bundles=(e1, e2), previous_digest=ZERO_DIGEST)
    assert export.accept
    return seal, retention, export


def accepted_export_receipt(export=None):
    if export is None:
        _, _, export = accepted_rev0069_export()
    r1 = make_export_receipt_entry(kind=ExportReceiptKind.OPERATOR_RECEIPT, sequence=1, audit_export_report=export, family_id="receipt-a", path_family_id="path-a")
    r2 = make_export_receipt_entry(kind=ExportReceiptKind.GARDEN_RECEIPT, sequence=2, previous_digest=r1.entry_digest, audit_export_report=export, audience=AuditExportAudience.GARDEN_WITNESS, family_id="receipt-b", path_family_id="path-b")
    receipt = assess_export_receipts(audit_export_report=export, entries=(r1, r2), previous_digest=ZERO_DIGEST)
    assert receipt.decision_kind is ExportReceiptDecisionKind.ACCEPT_EXPORT_RECEIPTED
    return receipt


def accepted_retention_gc(receipt=None, retention=None):
    if retention is None or receipt is None:
        _, retention, export = accepted_rev0069_export()
        receipt = accepted_export_receipt(export)
    markers = []
    prev = ZERO_DIGEST
    classes = [
        RetentionGcClass.CLOSURE_SEAL_MARKER,
        RetentionGcClass.RETENTION_PROOF_MARKER,
        RetentionGcClass.EXPORT_RECEIPT_MARKER,
        RetentionGcClass.CONTRADICTION_MEMORY,
        RetentionGcClass.REDACTED_EXPORT_SUMMARY,
        RetentionGcClass.SOFT_WORKING_SET,
    ]
    for seq, cls in enumerate(classes, start=1):
        marker = make_retention_gc_marker(gc_class=cls, sequence=seq, previous_digest=prev, export_receipt_report=receipt, retention_proof_report=retention, family_id=f"gc-{seq}", path_family_id=f"path-{seq}", reclaimed_bytes=64 if cls is RetentionGcClass.SOFT_WORKING_SET else 0)
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_retention_gc(export_receipt_report=receipt, retention_proof_report=retention, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is RetentionGcDecisionKind.ACCEPT_RETENTION_GC
    return report


def accepted_handoff(receipt=None, gc=None, retention=None):
    if receipt is None or gc is None or retention is None:
        _, retention, export = accepted_rev0069_export()
        receipt = accepted_export_receipt(export)
        gc = accepted_retention_gc(receipt, retention)
    p1 = make_closure_handoff_packet(audience=ClosureHandoffAudience.LOCAL_OPERATOR, sequence=1, export_receipt_report=receipt, retention_gc_report=gc, family_id="handoff-a", path_family_id="path-a")
    p2 = make_closure_handoff_packet(audience=ClosureHandoffAudience.GARDEN_WITNESS, sequence=2, previous_digest=p1.packet_digest, export_receipt_report=receipt, retention_gc_report=gc, family_id="handoff-b", path_family_id="path-b")
    handoff = assess_closure_handoff(export_receipt_report=receipt, retention_gc_report=gc, packets=(p1, p2), previous_digest=ZERO_DIGEST)
    assert handoff.decision_kind is ClosureHandoffDecisionKind.ACCEPT_CLOSURE_HANDOFF_PREPARED
    return handoff


def test_export_receipt_retention_gc_and_handoff_happy_path() -> None:
    seal, retention, export = accepted_rev0069_export()
    receipt = accepted_export_receipt(export)
    gc = accepted_retention_gc(receipt, retention)
    handoff = accepted_handoff(receipt, gc, retention)
    assert seal.accept and export.accept and receipt.export_receipted
    assert gc.retention_gc_applied and gc.contradiction_preserved
    assert handoff.closure_handoff_prepared and handoff.redacted


def test_export_receipt_rejects_raw_boundary_leak() -> None:
    _, _, export = accepted_rev0069_export()
    r1 = make_export_receipt_entry(kind=ExportReceiptKind.OPERATOR_RECEIPT, sequence=1, audit_export_report=export, raw_boundary_exposed=True, family_id="receipt-a", path_family_id="path-a")
    report = assess_export_receipts(audit_export_report=export, entries=(r1,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ExportReceiptDecisionKind.QUARANTINE_RAW_LEAK


def test_export_receipt_rejects_sequence_fork() -> None:
    _, _, export = accepted_rev0069_export()
    r1 = make_export_receipt_entry(kind=ExportReceiptKind.OPERATOR_RECEIPT, sequence=1, audit_export_report=export, family_id="receipt-a", path_family_id="path-a")
    r2 = make_export_receipt_entry(kind=ExportReceiptKind.GARDEN_RECEIPT, sequence=1, audit_export_report=export, audience=AuditExportAudience.GARDEN_WITNESS, family_id="receipt-b", path_family_id="path-b")
    report = assess_export_receipts(audit_export_report=export, entries=(r1, r2), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ExportReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_retention_gc_quarantines_contradiction_drop() -> None:
    _, retention, export = accepted_rev0069_export()
    receipt = accepted_export_receipt(export)
    markers = []
    prev = ZERO_DIGEST
    classes = [RetentionGcClass.CLOSURE_SEAL_MARKER, RetentionGcClass.RETENTION_PROOF_MARKER, RetentionGcClass.EXPORT_RECEIPT_MARKER, RetentionGcClass.CONTRADICTION_MEMORY, RetentionGcClass.REDACTED_EXPORT_SUMMARY]
    for seq, cls in enumerate(classes, start=1):
        marker = make_retention_gc_marker(gc_class=cls, sequence=seq, previous_digest=prev, export_receipt_report=receipt, retention_proof_report=retention, contradiction_carried=False, family_id=f"gc-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_retention_gc(export_receipt_report=receipt, retention_proof_report=retention, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is RetentionGcDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_retention_gc_quarantines_hard_negative_drop() -> None:
    _, retention, export = accepted_rev0069_export()
    receipt = SimpleNamespace(**{**accepted_export_receipt(export).__dict__, "hard_negative_count": 1})
    markers = []
    prev = ZERO_DIGEST
    for seq, cls in enumerate((RetentionGcClass.CLOSURE_SEAL_MARKER, RetentionGcClass.RETENTION_PROOF_MARKER, RetentionGcClass.EXPORT_RECEIPT_MARKER, RetentionGcClass.CONTRADICTION_MEMORY, RetentionGcClass.REDACTED_EXPORT_SUMMARY), start=1):
        marker = make_retention_gc_marker(gc_class=cls, sequence=seq, previous_digest=prev, export_receipt_report=receipt, retention_proof_report=retention, family_id=f"gc-{seq}", path_family_id=f"path-{seq}")
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_retention_gc(export_receipt_report=receipt, retention_proof_report=retention, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is RetentionGcDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED


def test_closure_handoff_rejects_raw_payload_leak() -> None:
    _, retention, export = accepted_rev0069_export()
    receipt = accepted_export_receipt(export)
    gc = accepted_retention_gc(receipt, retention)
    packet = make_closure_handoff_packet(audience=ClosureHandoffAudience.PUBLIC_SUMMARY, sequence=1, export_receipt_report=receipt, retention_gc_report=gc, raw_payload_exposed=True, family_id="handoff-a", path_family_id="path-a")
    report = assess_closure_handoff(export_receipt_report=receipt, retention_gc_report=gc, packets=(packet,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ClosureHandoffDecisionKind.QUARANTINE_RAW_LEAK


def test_closure_handoff_rejects_boundary_drift() -> None:
    _, retention, export = accepted_rev0069_export()
    receipt = accepted_export_receipt(export)
    gc = SimpleNamespace(**{**accepted_retention_gc(receipt, retention).__dict__, "request_digest": d("different-request")})
    packet = make_closure_handoff_packet(audience=ClosureHandoffAudience.LOCAL_OPERATOR, sequence=1, export_receipt_report=receipt, retention_gc_report=accepted_retention_gc(receipt, retention), family_id="handoff-a", path_family_id="path-a")
    report = assess_closure_handoff(export_receipt_report=receipt, retention_gc_report=gc, packets=(packet,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is ClosureHandoffDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_exporthandofffold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_export_handoff_fold(root, revision="rev0070", artifact_stem=root.name)
    assert report.status == "pass"
