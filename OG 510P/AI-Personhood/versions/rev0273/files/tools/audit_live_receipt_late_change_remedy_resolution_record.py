#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-16T12:16:00Z"

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

base_ref = f"examples/live-receipt-publication-rollback-adjudication-{REV}-zero-floor-stayed.json"
base = load(base_ref)
no_signal_notice_ref = f"examples/live-receipt-late-change-notice-dispatch-record-{REV}-no-signal-monitoring.json"
no_signal_notice = load(no_signal_notice_ref)

no_remedy = resolution_mod.build(
    notice_dispatch=no_signal_notice,
    notice_dispatch_ref=no_signal_notice_ref,
    receipt_id=f"{REV}-audit-no-signal-resolution",
    created_at=CREATED_AT,
    revision=REV,
)
if no_remedy["decision"]["remedy_resolution_state"] != "monitoring-no-signal-no-remedy-required":
    raise SystemExit("no-signal notice unexpectedly required remedy resolution")
if no_remedy["resolution_freeze_locks"]["may_increment_live_floor_from_resolution"] is not False or no_remedy["no_direct_floor_effect"] is not True:
    raise SystemExit("no-signal remedy resolution acquired floor effect")

live_ingress = ingress_mod.build(
    publication_adjudication=base,
    publication_adjudication_ref=base_ref,
    receipt_id=f"{REV}-audit-live-revocation-for-resolution",
    created_at=CREATED_AT,
    revision=REV,
    signal_type="revocation",
    source_actor_class="counterparty",
    source_identity_ref="org:external-counterparty-a",
    target_ref=base_ref,
    nonhost_retention_ref="nonhost-vault:late-revocation-resolution:sha256:" + "3" * 64,
    public_summary_ref="failed-gate-public-summary:late-revocation-resolution",
    signal_artifact="counterparty revokes prior receipt and requests public correction",
    supersedes_or_revokes_refs=[base_ref],
    signature_or_contact_channel_captured=True,
    independent_timestamp_present=True,
)
ready_notice = notice_mod.build(
    late_change_ingress=live_ingress,
    late_change_ingress_ref="embedded:audit-live-revocation-for-resolution",
    receipt_id=f"{REV}-audit-ready-resolution-notice",
    created_at=CREATED_AT,
    revision=REV,
    affected_party_refs=["counterparty:org:external-counterparty-a", "subject-representative:public-advocate"],
    notice_channels=["counterparty-signed-email", "representative-accessible-portal"],
    public_freeze_notice_ref="failed-gate-public-summary:late-revocation-resolution:freeze-notice",
    nonhost_delivery_proof_ref="nonhost-proof:notice-delivery:sha256:" + "4" * 64,
    remedy_or_appeal_window_ref="appeal-window:late-revocation-resolution:open-30d",
    accessible_notice_profile_ref="communication-access-profile:public-advocate",
    redaction_boundary_ref="redaction-boundary:late-revocation-resolution:public-shell-only",
    dispatch_artifact="freeze notice delivered to counterparty and subject representative",
)
ready_resolution = resolution_mod.build(
    notice_dispatch=ready_notice,
    notice_dispatch_ref="embedded:audit-ready-resolution-notice",
    receipt_id=f"{REV}-audit-ready-resolution",
    created_at=CREATED_AT,
    revision=REV,
    remedy_window_status="closed",
    affected_party_submission_refs=["counterparty-submission:sha256:" + "5" * 64, "representative-submission:sha256:" + "6" * 64],
    resolution_authority_ref="remedy-panel:late-change-review:scoped",
    resolution_decision_ref="public-shell:late-change-resolution:sha256:" + "7" * 64,
    resolution_outcome="rollback-required",
    nonhost_resolution_proof_ref="nonhost-proof:resolution-retained:sha256:" + "8" * 64,
    accessible_resolution_notice_ref="public-resolution-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-resolution:resolution-public-shell-only",
    resolution_artifact="resolution upholds late revocation and requires rollback/recompute",
)
if ready_resolution["decision"]["remedy_resolution_state"] != "resolution-ready-publication-stayed":
    raise SystemExit("complete remedy resolution did not become ready")
if ready_resolution["decision"]["may_publish_or_continue_snapshot"] is not False:
    raise SystemExit("remedy resolution allowed publication continuation")
if ready_resolution["resolution_freeze_locks"]["remedy_silence_counts_as_waiver"] is not False:
    raise SystemExit("remedy silence was treated as waiver")

open_window = resolution_mod.build(
    notice_dispatch=ready_notice,
    notice_dispatch_ref="embedded:audit-ready-resolution-notice",
    receipt_id=f"{REV}-audit-open-remedy-window",
    created_at=CREATED_AT,
    revision=REV,
    remedy_window_status="open",
    affected_party_submission_refs=["counterparty-submission:sha256:" + "9" * 64, "representative-submission:sha256:" + "a" * 64],
    resolution_authority_ref="remedy-panel:late-change-review:scoped",
    resolution_decision_ref="public-shell:late-change-resolution:sha256:" + "b" * 64,
    resolution_outcome="rollback-required",
    nonhost_resolution_proof_ref="nonhost-proof:resolution-retained:sha256:" + "c" * 64,
    accessible_resolution_notice_ref="public-resolution-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-resolution:resolution-public-shell-only",
)
if open_window["decision"]["remedy_resolution_state"] != "blocked-remedy-window-still-open":
    raise SystemExit("open remedy window did not block resolution")

missing_submissions = resolution_mod.build(
    notice_dispatch=ready_notice,
    notice_dispatch_ref="embedded:audit-ready-resolution-notice",
    receipt_id=f"{REV}-audit-missing-submissions",
    created_at=CREATED_AT,
    revision=REV,
    remedy_window_status="closed",
    affected_party_submission_refs=["counterparty-submission:sha256:" + "d" * 64],
    resolution_authority_ref="remedy-panel:late-change-review:scoped",
    resolution_decision_ref="public-shell:late-change-resolution:sha256:" + "e" * 64,
    resolution_outcome="rollback-required",
    nonhost_resolution_proof_ref="nonhost-proof:resolution-retained:sha256:" + "f" * 64,
    accessible_resolution_notice_ref="public-resolution-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-resolution:resolution-public-shell-only",
)
if missing_submissions["decision"]["remedy_resolution_state"] != "blocked-remedy-submissions-unretained":
    raise SystemExit("missing affected-party submissions did not block")

missing_authority = resolution_mod.build(
    notice_dispatch=ready_notice,
    notice_dispatch_ref="embedded:audit-ready-resolution-notice",
    receipt_id=f"{REV}-audit-missing-resolution-authority",
    created_at=CREATED_AT,
    revision=REV,
    remedy_window_status="closed",
    affected_party_submission_refs=["counterparty-submission:sha256:" + "0" * 64, "representative-submission:sha256:" + "1" * 64],
    resolution_decision_ref="public-shell:late-change-resolution:sha256:" + "2" * 64,
    resolution_outcome="rollback-required",
    nonhost_resolution_proof_ref="nonhost-proof:resolution-retained:sha256:" + "3" * 64,
    accessible_resolution_notice_ref="public-resolution-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-resolution:resolution-public-shell-only",
)
if missing_authority["decision"]["remedy_resolution_state"] != "blocked-resolution-authority-missing":
    raise SystemExit("missing resolution authority did not block")

private_leak = resolution_mod.build(
    notice_dispatch=ready_notice,
    notice_dispatch_ref="embedded:audit-ready-resolution-notice",
    receipt_id=f"{REV}-audit-private-resolution-leak",
    created_at=CREATED_AT,
    revision=REV,
    remedy_window_status="closed",
    affected_party_submission_refs=["counterparty-submission:sha256:" + "4" * 64, "representative-submission:sha256:" + "5" * 64],
    resolution_authority_ref="remedy-panel:late-change-review:scoped",
    resolution_decision_ref="private-vault://sealed-resolution-decision",
    resolution_outcome="rollback-required",
    nonhost_resolution_proof_ref="nonhost-proof:resolution-retained:sha256:" + "6" * 64,
    accessible_resolution_notice_ref="public-resolution-notice:accessible-shell",
    redaction_boundary_ref="redaction-boundary:late-revocation-resolution:resolution-public-shell-only",
    private_locator_leak=True,
)
if private_leak["decision"]["remedy_resolution_state"] != "blocked-private-material-in-public-resolution":
    raise SystemExit("private material in remedy resolution did not block")

if Draft202012Validator is not None:
    schema = load("schemas/live-receipt-late-change-remedy-resolution-record.schema.json")
    Draft202012Validator.check_schema(schema)
    for label, obj in [
        ("no_remedy", no_remedy),
        ("ready_resolution", ready_resolution),
        ("open_window", open_window),
        ("missing_submissions", missing_submissions),
        ("missing_authority", missing_authority),
        ("private_leak", private_leak),
    ]:
        errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{label} remedy resolution fails schema: {errors[0].message}")

print("audit_live_receipt_late_change_remedy_resolution_record: OK")
