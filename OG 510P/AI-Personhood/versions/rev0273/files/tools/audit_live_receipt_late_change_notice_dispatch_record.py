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

base_ref = f"examples/live-receipt-publication-rollback-adjudication-{REV}-zero-floor-stayed.json"
base = load(base_ref)
no_signal_ref = f"examples/live-receipt-late-change-ingress-record-{REV}-no-signal-monitoring.json"
no_signal_ingress = load(no_signal_ref)

no_notice = notice_mod.build(
    late_change_ingress=no_signal_ingress,
    late_change_ingress_ref=no_signal_ref,
    receipt_id=f"{REV}-audit-no-signal-notice",
    created_at=CREATED_AT,
    revision=REV,
)
if no_notice["decision"]["notice_dispatch_state"] != "monitoring-no-signal-no-notice-required":
    raise SystemExit("no-signal ingress unexpectedly required notice dispatch")
if no_notice["notice_freeze_locks"]["may_increment_live_floor_from_notice"] is not False or no_notice["no_direct_floor_effect"] is not True:
    raise SystemExit("no-signal notice dispatch acquired floor effect")

live_ingress = ingress_mod.build(
    publication_adjudication=base,
    publication_adjudication_ref=base_ref,
    receipt_id=f"{REV}-audit-live-revocation-for-notice",
    created_at=CREATED_AT,
    revision=REV,
    signal_type="revocation",
    source_actor_class="counterparty",
    source_identity_ref="org:external-counterparty-a",
    target_ref=base_ref,
    nonhost_retention_ref="nonhost-vault:late-revocation-a:sha256:" + "d" * 64,
    public_summary_ref="failed-gate-public-summary:late-revocation-a",
    signal_artifact="counterparty revokes prior receipt and requests public correction",
    supersedes_or_revokes_refs=[base_ref],
    signature_or_contact_channel_captured=True,
    independent_timestamp_present=True,
)
ready_dispatch = notice_mod.build(
    late_change_ingress=live_ingress,
    late_change_ingress_ref="embedded:audit-live-revocation-for-notice",
    receipt_id=f"{REV}-audit-ready-dispatch",
    created_at=CREATED_AT,
    revision=REV,
    affected_party_refs=["counterparty:org:external-counterparty-a", "subject-representative:public-advocate"],
    notice_channels=["counterparty-signed-email", "representative-accessible-portal"],
    public_freeze_notice_ref="failed-gate-public-summary:late-revocation-a:freeze-notice",
    nonhost_delivery_proof_ref="nonhost-proof:notice-delivery:sha256:" + "e" * 64,
    remedy_or_appeal_window_ref="appeal-window:late-revocation-a:open-30d",
    accessible_notice_profile_ref="communication-access-profile:public-advocate",
    redaction_boundary_ref="redaction-boundary:late-revocation-a:public-shell-only",
    dispatch_artifact="freeze notice delivered to counterparty and subject representative",
)
if ready_dispatch["decision"]["notice_dispatch_state"] != "dispatch-ready-publication-stayed":
    raise SystemExit("complete live-signal notice dispatch did not become ready")
if ready_dispatch["decision"]["may_publish_or_continue_snapshot"] is not False:
    raise SystemExit("notice dispatch allowed publication continuation")
if ready_dispatch["notice_freeze_locks"]["notice_silence_counts_as_waiver"] is not False:
    raise SystemExit("notice silence was treated as waiver")

missing_notice = notice_mod.build(
    late_change_ingress=live_ingress,
    late_change_ingress_ref="embedded:audit-live-revocation-for-notice",
    receipt_id=f"{REV}-audit-missing-party-notice",
    created_at=CREATED_AT,
    revision=REV,
    affected_party_refs=["counterparty:org:external-counterparty-a"],
    notice_channels=["counterparty-signed-email"],
    public_freeze_notice_ref="failed-gate-public-summary:late-revocation-a:freeze-notice",
    nonhost_delivery_proof_ref="nonhost-proof:notice-delivery:sha256:" + "f" * 64,
    remedy_or_appeal_window_ref="appeal-window:late-revocation-a:open-30d",
    accessible_notice_profile_ref="communication-access-profile:counterparty",
    redaction_boundary_ref="redaction-boundary:late-revocation-a:public-shell-only",
)
if missing_notice["decision"]["notice_dispatch_state"] != "blocked-affected-party-notice-missing":
    raise SystemExit("missing subject/representative notice did not block")

missing_remedy = notice_mod.build(
    late_change_ingress=live_ingress,
    late_change_ingress_ref="embedded:audit-live-revocation-for-notice",
    receipt_id=f"{REV}-audit-missing-remedy",
    created_at=CREATED_AT,
    revision=REV,
    affected_party_refs=["counterparty:org:external-counterparty-a", "subject-representative:public-advocate"],
    notice_channels=["counterparty-signed-email", "representative-accessible-portal"],
    public_freeze_notice_ref="failed-gate-public-summary:late-revocation-a:freeze-notice",
    nonhost_delivery_proof_ref="nonhost-proof:notice-delivery:sha256:" + "1" * 64,
    accessible_notice_profile_ref="communication-access-profile:public-advocate",
    redaction_boundary_ref="redaction-boundary:late-revocation-a:public-shell-only",
)
if missing_remedy["decision"]["notice_dispatch_state"] != "blocked-remedy-window-missing":
    raise SystemExit("missing remedy window did not block")

private_leak = notice_mod.build(
    late_change_ingress=live_ingress,
    late_change_ingress_ref="embedded:audit-live-revocation-for-notice",
    receipt_id=f"{REV}-audit-private-leak-notice",
    created_at=CREATED_AT,
    revision=REV,
    affected_party_refs=["counterparty:org:external-counterparty-a", "subject-representative:public-advocate"],
    notice_channels=["counterparty-signed-email", "representative-accessible-portal"],
    public_freeze_notice_ref="private-vault://raw-late-signal-notice",
    nonhost_delivery_proof_ref="nonhost-proof:notice-delivery:sha256:" + "2" * 64,
    remedy_or_appeal_window_ref="appeal-window:late-revocation-a:open-30d",
    accessible_notice_profile_ref="communication-access-profile:public-advocate",
    redaction_boundary_ref="redaction-boundary:late-revocation-a:public-shell-only",
    private_locator_leak=True,
)
if private_leak["decision"]["notice_dispatch_state"] != "blocked-private-material-in-public-notice":
    raise SystemExit("private material in notice did not block")

if Draft202012Validator is not None:
    schema = load("schemas/live-receipt-late-change-notice-dispatch-record.schema.json")
    Draft202012Validator.check_schema(schema)
    for label, obj in [
        ("no_notice", no_notice),
        ("ready_dispatch", ready_dispatch),
        ("missing_notice", missing_notice),
        ("missing_remedy", missing_remedy),
        ("private_leak", private_leak),
    ]:
        errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{label} notice dispatch fails schema: {errors[0].message}")

print("audit_live_receipt_late_change_notice_dispatch_record: OK")
