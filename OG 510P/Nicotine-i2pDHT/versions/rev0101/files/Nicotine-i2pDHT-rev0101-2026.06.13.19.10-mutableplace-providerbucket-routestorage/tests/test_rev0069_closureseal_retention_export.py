from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.auditexport import AuditExportAudience, AuditExportDecisionKind, assess_audit_export, make_audit_export_bundle
from i2p_dht_lab.closureseal import ClosureSealDecisionKind, ClosureSealEntryKind, assess_closure_seal, make_closure_seal_entry
from i2p_dht_lab.closuresealfold import audit_closure_seal_fold
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.retentionproof import RetentionItemKind, RetentionProofDecisionKind, assess_retention_proof, make_retention_item
from i2p_dht_lab.sideeffectjournal import SideEffectAction


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0069-test:" + label.encode())


ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
PROFILE = "rev0069-profile"
SERVICE = "rev0069-public-edge"
SCOPE = d("scope")
REQUEST = d("request")
PAYLOAD = d("payload")
IDEM = d("idempotency")
RETRY_IDEM = d("retry-idempotency")


def component(label: str, **kw):
    base = dict(
        report_digest=d(label),
        accepted_marker_digest=d(label + ":marker"),
        accepted_entry_digest=d(label + ":entry"),
        accepted_observation_digest=d(label + ":obs"),
        accept=True,
        watch=False,
        quarantined=False,
        action=ACTION,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        retry_idempotency_key=RETRY_IDEM,
        restart_generation=4,
        hard_negative_count=0,
        family_count=2,
        path_family_count=2,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def accepted_closure_inputs():
    closure_audit = component("closure-audit", closure_audited=True, contradiction_preserved=True, archive_journal_digest=d("archive-journal"), prune_replay_digest=d("prune-replay"))
    archive_journal = component("archive-journal", contradiction_preserved=True, prune_memory_preserved=True)
    prune_replay = component("prune-replay", replay_stable=True, contradiction_preserved=True, prune_marker_preserved=True)
    return closure_audit, archive_journal, prune_replay


def accepted_closure_seal():
    closure_audit, archive_journal, prune_replay = accepted_closure_inputs()
    s1 = make_closure_seal_entry(kind=ClosureSealEntryKind.CLOSURE_AUDIT_SEALED, sequence=1, closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, family_id="seal-a", path_family_id="path-a")
    s2 = make_closure_seal_entry(kind=ClosureSealEntryKind.CONTRADICTION_MEMORY_SEALED, sequence=2, previous_digest=s1.entry_digest, closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, family_id="seal-b", path_family_id="path-b")
    s3 = make_closure_seal_entry(kind=ClosureSealEntryKind.EXPORT_BOUNDARY_SEALED, sequence=3, previous_digest=s2.entry_digest, closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, family_id="seal-c", path_family_id="path-c")
    seal = assess_closure_seal(closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, entries=(s1, s2, s3), previous_digest=s1.previous_digest)
    assert seal.decision_kind is ClosureSealDecisionKind.ACCEPT_CLOSURE_SEALED
    return seal, closure_audit, archive_journal, prune_replay


def accepted_retention(seal=None):
    if seal is None:
        seal, *_ = accepted_closure_seal()
    i1 = make_retention_item(kind=RetentionItemKind.CLOSURE_SEAL, sequence=1, closure_seal_report=seal, family_id="ret-a", path_family_id="path-a")
    i2 = make_retention_item(kind=RetentionItemKind.CLOSURE_AUDIT, sequence=2, previous_digest=i1.item_digest, closure_seal_report=seal, family_id="ret-b", path_family_id="path-b")
    i3 = make_retention_item(kind=RetentionItemKind.ARCHIVE_JOURNAL, sequence=3, previous_digest=i2.item_digest, closure_seal_report=seal, family_id="ret-c", path_family_id="path-c")
    i4 = make_retention_item(kind=RetentionItemKind.PRUNE_REPLAY, sequence=4, previous_digest=i3.item_digest, closure_seal_report=seal, family_id="ret-d", path_family_id="path-d")
    i5 = make_retention_item(kind=RetentionItemKind.CONTRADICTION_MEMORY, sequence=5, previous_digest=i4.item_digest, closure_seal_report=seal, family_id="ret-e", path_family_id="path-e")
    i6 = make_retention_item(kind=RetentionItemKind.REDACTED_OPERATOR_SUMMARY, sequence=6, previous_digest=i5.item_digest, closure_seal_report=seal, family_id="ret-f", path_family_id="path-f")
    retention = assess_retention_proof(closure_seal_report=seal, items=(i1, i2, i3, i4, i5, i6), previous_digest=i1.previous_digest)
    assert retention.decision_kind is RetentionProofDecisionKind.ACCEPT_RETENTION_PROVED
    return retention


def accepted_export(seal=None, retention=None):
    if seal is None:
        seal, *_ = accepted_closure_seal()
    if retention is None:
        retention = accepted_retention(seal)
    e1 = make_audit_export_bundle(audience=AuditExportAudience.LOCAL_OPERATOR, sequence=1, closure_seal_report=seal, retention_proof_report=retention, family_id="export-a", path_family_id="path-a")
    e2 = make_audit_export_bundle(audience=AuditExportAudience.GARDEN_WITNESS, sequence=2, previous_digest=e1.bundle_digest, closure_seal_report=seal, retention_proof_report=retention, family_id="export-b", path_family_id="path-b")
    export = assess_audit_export(closure_seal_report=seal, retention_proof_report=retention, bundles=(e1, e2), previous_digest=e1.previous_digest)
    assert export.decision_kind is AuditExportDecisionKind.ACCEPT_EXPORT_PREPARED
    return export


def test_closure_seal_retention_and_export_happy_path() -> None:
    seal, *_ = accepted_closure_seal()
    retention = accepted_retention(seal)
    export = accepted_export(seal, retention)
    assert seal.accept and seal.contradiction_sealed and seal.export_boundary_sealed
    assert retention.accept and retention.retention_proved and retention.contradiction_preserved
    assert export.accept and export.export_prepared and export.redacted


def test_closure_seal_quarantines_contradiction_drop() -> None:
    closure_audit, archive_journal, prune_replay = accepted_closure_inputs()
    s1 = make_closure_seal_entry(kind=ClosureSealEntryKind.CLOSURE_AUDIT_SEALED, sequence=1, closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, contradiction_sealed=False, family_id="seal-a", path_family_id="path-a")
    s2 = make_closure_seal_entry(kind=ClosureSealEntryKind.EXPORT_BOUNDARY_SEALED, sequence=2, previous_digest=s1.entry_digest, closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, contradiction_sealed=False, family_id="seal-b", path_family_id="path-b")
    report = assess_closure_seal(closure_audit_report=closure_audit, archive_journal_report=archive_journal, prune_replay_report=prune_replay, entries=(s1, s2), previous_digest=s1.previous_digest)
    assert report.decision_kind is ClosureSealDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_retention_proof_rejects_missing_contradiction_class() -> None:
    seal, *_ = accepted_closure_seal()
    i1 = make_retention_item(kind=RetentionItemKind.CLOSURE_SEAL, sequence=1, closure_seal_report=seal, family_id="ret-a", path_family_id="path-a")
    i2 = make_retention_item(kind=RetentionItemKind.CLOSURE_AUDIT, sequence=2, previous_digest=i1.item_digest, closure_seal_report=seal, family_id="ret-b", path_family_id="path-b")
    i3 = make_retention_item(kind=RetentionItemKind.ARCHIVE_JOURNAL, sequence=3, previous_digest=i2.item_digest, closure_seal_report=seal, family_id="ret-c", path_family_id="path-c")
    i4 = make_retention_item(kind=RetentionItemKind.PRUNE_REPLAY, sequence=4, previous_digest=i3.item_digest, closure_seal_report=seal, family_id="ret-d", path_family_id="path-d")
    i5 = make_retention_item(kind=RetentionItemKind.REDACTED_OPERATOR_SUMMARY, sequence=5, previous_digest=i4.item_digest, closure_seal_report=seal, family_id="ret-e", path_family_id="path-e")
    report = assess_retention_proof(closure_seal_report=seal, items=(i1, i2, i3, i4, i5), previous_digest=i1.previous_digest)
    assert report.decision_kind is RetentionProofDecisionKind.HOLD_MISSING_REQUIRED_CLASS


def test_retention_proof_quarantines_hard_negative_drop() -> None:
    seal, *_ = accepted_closure_seal()
    hard_seal = SimpleNamespace(**{**seal.__dict__, "hard_negative_count": 1})
    i1 = make_retention_item(kind=RetentionItemKind.CLOSURE_SEAL, sequence=1, closure_seal_report=hard_seal, family_id="ret-a", path_family_id="path-a")
    i2 = make_retention_item(kind=RetentionItemKind.CLOSURE_AUDIT, sequence=2, previous_digest=i1.item_digest, closure_seal_report=hard_seal, family_id="ret-b", path_family_id="path-b")
    i3 = make_retention_item(kind=RetentionItemKind.ARCHIVE_JOURNAL, sequence=3, previous_digest=i2.item_digest, closure_seal_report=hard_seal, family_id="ret-c", path_family_id="path-c")
    i4 = make_retention_item(kind=RetentionItemKind.PRUNE_REPLAY, sequence=4, previous_digest=i3.item_digest, closure_seal_report=hard_seal, family_id="ret-d", path_family_id="path-d")
    i5 = make_retention_item(kind=RetentionItemKind.CONTRADICTION_MEMORY, sequence=5, previous_digest=i4.item_digest, closure_seal_report=hard_seal, family_id="ret-e", path_family_id="path-e")
    i6 = make_retention_item(kind=RetentionItemKind.REDACTED_OPERATOR_SUMMARY, sequence=6, previous_digest=i5.item_digest, closure_seal_report=hard_seal, family_id="ret-f", path_family_id="path-f")
    report = assess_retention_proof(closure_seal_report=hard_seal, items=(i1, i2, i3, i4, i5, i6), previous_digest=i1.previous_digest)
    assert report.decision_kind is RetentionProofDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED


def test_audit_export_rejects_raw_boundary_exposure() -> None:
    seal, *_ = accepted_closure_seal()
    retention = accepted_retention(seal)
    e1 = make_audit_export_bundle(audience=AuditExportAudience.PUBLIC_REDACTED, sequence=1, closure_seal_report=seal, retention_proof_report=retention, raw_boundary_exposed=True, family_id="export-a", path_family_id="path-a")
    report = assess_audit_export(closure_seal_report=seal, retention_proof_report=retention, bundles=(e1,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is AuditExportDecisionKind.QUARANTINE_RAW_BOUNDARY_EXPOSURE


def test_audit_export_quarantines_boundary_drift() -> None:
    seal, *_ = accepted_closure_seal()
    retention = accepted_retention(seal)
    drifted = SimpleNamespace(**{**retention.__dict__, "request_digest": d("different-request")})
    e1 = make_audit_export_bundle(audience=AuditExportAudience.LOCAL_OPERATOR, sequence=1, closure_seal_report=seal, retention_proof_report=retention, family_id="export-a", path_family_id="path-a")
    report = assess_audit_export(closure_seal_report=seal, retention_proof_report=drifted, bundles=(e1,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is AuditExportDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_closuresealfold_audit_passes() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    report = audit_closure_seal_fold(root, revision="rev0069", artifact_stem=root.name)
    assert report.status == "pass"
