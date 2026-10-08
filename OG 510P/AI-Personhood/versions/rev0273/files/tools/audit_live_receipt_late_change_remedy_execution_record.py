#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-16T12:58:00Z"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_mod(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


ingress_mod = load_mod("prepare_live_receipt_late_change_ingress_record", "tools/prepare_live_receipt_late_change_ingress_record.py")
notice_mod = load_mod("prepare_live_receipt_late_change_notice_dispatch_record", "tools/prepare_live_receipt_late_change_notice_dispatch_record.py")
resolution_mod = load_mod("prepare_live_receipt_late_change_remedy_resolution_record", "tools/prepare_live_receipt_late_change_remedy_resolution_record.py")
execution_mod = load_mod("prepare_live_receipt_late_change_remedy_execution_record", "tools/prepare_live_receipt_late_change_remedy_execution_record.py")

base_ref = f"examples/live-receipt-publication-rollback-adjudication-{REV}-zero-floor-stayed.json"
base = load(base_ref)
no_signal_resolution_ref = f"examples/live-receipt-late-change-remedy-resolution-record-{REV}-no-signal-monitoring.json"
no_signal_resolution = load(no_signal_resolution_ref)

no_execution = execution_mod.build(
    remedy_resolution=no_signal_resolution,
    remedy_resolution_ref=no_signal_resolution_ref,
    receipt_id=f"{REV}-audit-no-signal-execution",
    created_at=CREATED_AT,
    revision=REV,
)
if no_execution["decision"]["remedy_execution_state"] != "monitoring-no-signal-no-execution-required":
    raise SystemExit("no-signal remedy unexpectedly required execution")
if no_execution["execution_freeze_locks"]["may_increment_live_floor_from_execution"] is not False or no_execution["no_direct_floor_effect"] is not True:
    raise SystemExit("no-signal remedy execution acquired floor effect")

live_ingress = ingress_mod.build(
    publication_adjudication=base,
    publication_adjudication_ref=base_ref,
    receipt_id=f"{REV}-audit-live-revocation-for-execution",
    created_at=CREATED_AT,
    revision=REV,
    signal_type="revocation",
    source_actor_class="counterparty",
    source_identity_ref="org:external-counterparty-a",
    target_ref=base_ref,
    nonhost_retention_ref="nonhost-vault:late-revocation-execution:sha256:" + "3" * 64,
    public_summary_ref="failed-gate-public-summary:late-revocation-execution",
    signal_artifact="counterparty revokes prior receipt and requests public rollback",
    supersedes_or_revokes_refs=[base_ref],
    signature_or_contact_channel_captured=True,
    independent_timestamp_present=True,
)
ready_notice = notice_mod.build(
    late_change_ingress=live_ingress,
    late_change_ingress_ref="embedded:audit-live-revocation-for-execution",
    receipt_id=f"{REV}-audit-ready-execution-notice",
    created_at=CREATED_AT,
    revision=REV,
    affected_party_refs=["counterparty:org:external-counterparty-a", "subject-representative:public-advocate"],
    notice_channels=["counterparty-signed-email", "representative-accessible-portal"],
    public_freeze_notice_ref="failed-gate-public-summary:late-revocation-execution:freeze-notice",
    nonhost_delivery_proof_ref="nonhost-proof:notice-delivery:sha256:" + "4" * 64,
    remedy_or_appeal_window_ref="appeal-window:late-revocation-execution:open-30d",
    accessible_notice_profile_ref="communication-access-profile:public-advocate",
    redaction_boundary_ref="redaction-boundary:late-revocation-execution:public-shell-only",
    dispatch_artifact="freeze notice delivered to counterparty and subject representative",
)
ready_resolution = resolution_mod.build(
    notice_dispatch=ready_notice,
    notice_dispatch_ref="embedded:audit-ready-execution-notice",
    receipt_id=f"{REV}-audit-ready-execution-resolution",
    created_at=CREATED_AT,
    revision=REV,
    remedy_window_status="closed",
    affected_party_submission_refs=["counterparty-submission:sha256:" + "5" * 64, "representative-submission:sha256:" + "6" * 64],
    resolution_authority_ref="remedy-panel:late-change-review:scoped",
    resolution_decision_ref="public-shell:late-change-resolution:sha256:" + "7" * 64,
    resolution_outcome="rollback-required",
    nonhost_resolution_proof_ref="nonhost-proof:resolution-retained:sha256:" + "8" * 64,
    accessible_resolution_notice_ref="public-resolution-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-execution:resolution-public-shell-only",
    resolution_artifact="resolution upholds late revocation and requires rollback/recompute",
)
ready_execution = execution_mod.build(
    remedy_resolution=ready_resolution,
    remedy_resolution_ref="embedded:audit-ready-execution-resolution",
    receipt_id=f"{REV}-audit-ready-execution",
    created_at=CREATED_AT,
    revision=REV,
    execution_status="completed",
    corrective_action_refs=["rollback-ledger:sha256:" + "9" * 64, "public-correction-shell:sha256:" + "a" * 64],
    rollback_completion_ref="rollback-completion:sha256:" + "b" * 64,
    nonhost_execution_proof_ref="nonhost-proof:execution-retained:sha256:" + "c" * 64,
    affected_party_completion_notice_ref="public-remedy-completion-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-execution:execution-public-shell-only",
    execution_artifact="rollback applied to public shell and recompute rerun required",
)
if ready_execution["decision"]["remedy_execution_state"] != "execution-ready-publication-stayed":
    raise SystemExit("complete remedy execution did not become ready")
if ready_execution["decision"]["may_publish_or_continue_snapshot"] is not False:
    raise SystemExit("remedy execution allowed publication continuation")
if ready_execution["execution_freeze_locks"]["execution_silence_counts_as_completion"] is not False:
    raise SystemExit("execution silence was treated as completion")

pending_execution = execution_mod.build(
    remedy_resolution=ready_resolution,
    remedy_resolution_ref="embedded:audit-ready-execution-resolution",
    receipt_id=f"{REV}-audit-pending-execution",
    created_at=CREATED_AT,
    revision=REV,
    execution_status="pending",
    corrective_action_refs=["rollback-ledger:sha256:" + "d" * 64],
    rollback_completion_ref="rollback-completion:sha256:" + "e" * 64,
    nonhost_execution_proof_ref="nonhost-proof:execution-retained:sha256:" + "f" * 64,
    affected_party_completion_notice_ref="public-remedy-completion-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-execution:execution-public-shell-only",
)
if pending_execution["decision"]["remedy_execution_state"] != "blocked-execution-pending":
    raise SystemExit("pending remedy execution did not block")

missing_rollback = execution_mod.build(
    remedy_resolution=ready_resolution,
    remedy_resolution_ref="embedded:audit-ready-execution-resolution",
    receipt_id=f"{REV}-audit-missing-rollback-execution",
    created_at=CREATED_AT,
    revision=REV,
    execution_status="completed",
    corrective_action_refs=["public-correction-shell:sha256:" + "0" * 64],
    nonhost_execution_proof_ref="nonhost-proof:execution-retained:sha256:" + "1" * 64,
    affected_party_completion_notice_ref="public-remedy-completion-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-execution:execution-public-shell-only",
)
if missing_rollback["decision"]["remedy_execution_state"] != "blocked-corrective-actions-incomplete":
    raise SystemExit("missing rollback completion did not block")

private_leak = execution_mod.build(
    remedy_resolution=ready_resolution,
    remedy_resolution_ref="embedded:audit-ready-execution-resolution",
    receipt_id=f"{REV}-audit-private-execution-leak",
    created_at=CREATED_AT,
    revision=REV,
    execution_status="completed",
    corrective_action_refs=["private-vault://sealed-rollback-ledger"],
    rollback_completion_ref="rollback-completion:sha256:" + "2" * 64,
    nonhost_execution_proof_ref="nonhost-proof:execution-retained:sha256:" + "3" * 64,
    affected_party_completion_notice_ref="public-remedy-completion-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-execution:execution-public-shell-only",
    private_locator_leak=True,
)
if private_leak["decision"]["remedy_execution_state"] != "blocked-private-material-in-public-execution":
    raise SystemExit("private material in remedy execution did not block")

if Draft202012Validator is not None:
    schema = load("schemas/live-receipt-late-change-remedy-execution-record.schema.json")
    Draft202012Validator.check_schema(schema)
    for label, obj in [
        ("no_execution", no_execution),
        ("ready_execution", ready_execution),
        ("pending_execution", pending_execution),
        ("missing_rollback", missing_rollback),
        ("private_leak", private_leak),
    ]:
        errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{label} remedy execution fails schema: {errors[0].message}")

print("audit_live_receipt_late_change_remedy_execution_record: OK")
