#!/usr/bin/env python3
"""Audit the post-publication rollback adjudication lock."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from prepare_live_receipt_publication_rollback_adjudication import build, load, sha256_json
from prepare_live_receipt_late_change_ingress_record import build as build_ingress
from prepare_live_receipt_late_change_notice_dispatch_record import build as build_notice
from prepare_live_receipt_late_change_remedy_resolution_record import build as build_resolution
from prepare_live_receipt_late_change_remedy_execution_record import build as build_execution

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

CREATED_AT = "2026-06-16T14:05:00Z"


def main() -> None:
    rev = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    schema = load(ROOT / "schemas/live-receipt-publication-rollback-adjudication.schema.json")
    example_path = ROOT / "examples" / f"live-receipt-publication-rollback-adjudication-{rev}-zero-floor-stayed.json"
    example = load(example_path)
    if Draft202012Validator is not None:
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"current example fails schema: {errors[0].message}")
    if example["decision"]["publication_adjudication_state"] != "eligible-zero-floor-stayed":
        raise SystemExit("current zero-floor adjudication did not stay eligible")
    if example["publication_rollback_locks"]["may_increment_live_floor_from_adjudication"] is not False:
        raise SystemExit("adjudication record allowed a direct floor increment")
    receipt_path = ROOT / "examples" / f"live-receipt-floor-recompute-receipt-{rev}-zero-floor-stayed.json"
    receipt = load(receipt_path)
    snap_path = ROOT / receipt["linked_computed_snapshot_ref"]
    snap = load(snap_path)
    ref = f"examples/{receipt_path.name}"
    base = build(
        recompute_receipt=receipt,
        recompute_receipt_ref=ref,
        snapshot=snap,
        snapshot_ref=receipt["linked_computed_snapshot_ref"],
        snapshot_hash=sha256_json(snap),
        challenges=[],
        challenge_refs=[],
        receipt_id=f"{rev}-audit-base",
        created_at=CREATED_AT,
        revision=rev,
    )
    if base["decision"]["publication_adjudication_state"] != "eligible-zero-floor-stayed":
        raise SystemExit("base adjudication without late challenges did not pass zero/stayed")
    open_challenge = {
        "challenge_record_id": "RICR-2026-audit-open-post-publication",
        "challenge_state": "post-import-challenge",
        "recheck_matrix": {"quorum_recomputed_after_rollback": False, "failed_gate_public_summary_updated": False},
        "decision": {"challenge_upheld": False, "rollback_required": False, "rollback_completed": False, "live_floor_change_allowed": False},
        "public_summary_ref": "FGPS-2026-audit-open",
    }
    blocked = build(
        recompute_receipt=receipt,
        recompute_receipt_ref=ref,
        snapshot=snap,
        snapshot_ref=receipt["linked_computed_snapshot_ref"],
        snapshot_hash=sha256_json(snap),
        challenges=[open_challenge],
        challenge_refs=["embedded:audit-open-challenge"],
        receipt_id=f"{rev}-audit-open",
        created_at=CREATED_AT,
        revision=rev,
    )
    if blocked["decision"]["publication_adjudication_state"] != "blocked-open-challenge":
        raise SystemExit("open challenge did not block publication continuation")
    rollback_needed = json.loads(json.dumps(open_challenge))
    rollback_needed["challenge_state"] = "rollback-required"
    rollback_needed["decision"]["challenge_upheld"] = True
    rollback_needed["decision"]["rollback_required"] = True
    rollback_needed["decision"]["rollback_completed"] = False
    blocked2 = build(
        recompute_receipt=receipt,
        recompute_receipt_ref=ref,
        snapshot=snap,
        snapshot_ref=receipt["linked_computed_snapshot_ref"],
        snapshot_hash=sha256_json(snap),
        challenges=[rollback_needed],
        challenge_refs=["embedded:audit-rollback-needed"],
        receipt_id=f"{rev}-audit-rollback-needed",
        created_at=CREATED_AT,
        revision=rev,
    )
    if blocked2["decision"]["publication_adjudication_state"] not in {"blocked-open-challenge", "blocked-rollback-required"}:
        raise SystemExit("upheld uncompleted rollback did not block")
    tampered_hash = "f" * 64
    blocked3 = build(
        recompute_receipt=receipt,
        recompute_receipt_ref=ref,
        snapshot=snap,
        snapshot_ref=receipt["linked_computed_snapshot_ref"],
        snapshot_hash=tampered_hash,
        challenges=[],
        challenge_refs=[],
        receipt_id=f"{rev}-audit-hash-mismatch",
        created_at=CREATED_AT,
        revision=rev,
    )
    if blocked3["decision"]["publication_adjudication_state"] != "blocked-snapshot-hash-mismatch":
        raise SystemExit("snapshot hash mismatch did not block")

    live_ingress = build_ingress(
        publication_adjudication=base,
        publication_adjudication_ref="embedded:audit-base-adjudication",
        receipt_id=f"{rev}-audit-publication-live-ingress",
        created_at=CREATED_AT,
        revision=rev,
        signal_type="revocation",
        source_actor_class="counterparty",
        source_identity_ref="org:external-counterparty-a",
        target_ref="embedded:audit-base-adjudication",
        nonhost_retention_ref="nonhost-vault:publication-execution:sha256:" + "4" * 64,
        public_summary_ref="failed-gate-public-summary:publication-execution",
        signal_artifact="late revocation requires rollback execution",
        supersedes_or_revokes_refs=["embedded:audit-base-adjudication"],
        signature_or_contact_channel_captured=True,
        independent_timestamp_present=True,
    )
    live_notice = build_notice(
        late_change_ingress=live_ingress,
        late_change_ingress_ref="embedded:audit-publication-live-ingress",
        receipt_id=f"{rev}-audit-publication-live-notice",
        created_at=CREATED_AT,
        revision=rev,
        affected_party_refs=["counterparty:org:external-counterparty-a", "subject-representative:public-advocate"],
        notice_channels=["counterparty-signed-email", "representative-accessible-portal"],
        public_freeze_notice_ref="failed-gate-public-summary:publication-execution:freeze-notice",
        nonhost_delivery_proof_ref="nonhost-proof:notice-delivery:sha256:" + "5" * 64,
        remedy_or_appeal_window_ref="appeal-window:publication-execution:open-30d",
        accessible_notice_profile_ref="communication-access-profile:public-advocate",
        redaction_boundary_ref="redaction-boundary:publication-execution:public-shell-only",
        dispatch_artifact="freeze notice delivered",
    )
    live_resolution = build_resolution(
        notice_dispatch=live_notice,
        notice_dispatch_ref="embedded:audit-publication-live-notice",
        receipt_id=f"{rev}-audit-publication-live-resolution",
        created_at=CREATED_AT,
        revision=rev,
        remedy_window_status="closed",
        affected_party_submission_refs=["counterparty-submission:sha256:" + "6" * 64, "representative-submission:sha256:" + "7" * 64],
        resolution_authority_ref="remedy-panel:late-change-review:scoped",
        resolution_decision_ref="public-shell:late-change-resolution:sha256:" + "8" * 64,
        resolution_outcome="rollback-required",
        nonhost_resolution_proof_ref="nonhost-proof:resolution-retained:sha256:" + "9" * 64,
        accessible_resolution_notice_ref="public-resolution-notice:accessible-shell",
        redaction_boundary_ref="redaction-boundary:publication-execution:resolution-public-shell-only",
    )
    blocked4 = build(
        recompute_receipt=receipt,
        recompute_receipt_ref=ref,
        snapshot=snap,
        snapshot_ref=receipt["linked_computed_snapshot_ref"],
        snapshot_hash=sha256_json(snap),
        challenges=[],
        challenge_refs=[],
        receipt_id=f"{rev}-audit-resolution-unexecuted",
        created_at=CREATED_AT,
        revision=rev,
        remedy_resolutions=[live_resolution],
        remedy_resolution_refs=["embedded:audit-publication-live-resolution"],
    )
    if blocked4["decision"]["publication_adjudication_state"] != "blocked-remedy-resolution-unexecuted":
        raise SystemExit("ready live remedy resolution without execution did not block")
    pending_execution = build_execution(
        remedy_resolution=live_resolution,
        remedy_resolution_ref="embedded:audit-publication-live-resolution",
        receipt_id=f"{rev}-audit-publication-pending-execution",
        created_at=CREATED_AT,
        revision=rev,
        execution_status="pending",
        corrective_action_refs=["rollback-ledger:sha256:" + "a" * 64],
        rollback_completion_ref="rollback-completion:sha256:" + "b" * 64,
        nonhost_execution_proof_ref="nonhost-proof:execution-retained:sha256:" + "c" * 64,
        affected_party_completion_notice_ref="public-remedy-completion-notice:accessible-shell",
        redaction_boundary_ref="redaction-boundary:publication-execution:execution-public-shell-only",
    )
    blocked5 = build(
        recompute_receipt=receipt,
        recompute_receipt_ref=ref,
        snapshot=snap,
        snapshot_ref=receipt["linked_computed_snapshot_ref"],
        snapshot_hash=sha256_json(snap),
        challenges=[],
        challenge_refs=[],
        receipt_id=f"{rev}-audit-execution-open",
        created_at=CREATED_AT,
        revision=rev,
        remedy_resolutions=[live_resolution],
        remedy_resolution_refs=["embedded:audit-publication-live-resolution"],
        remedy_executions=[pending_execution],
        remedy_execution_refs=["embedded:audit-publication-pending-execution"],
    )
    if blocked5["decision"]["publication_adjudication_state"] != "blocked-late-change-remedy-execution-open":
        raise SystemExit("pending remedy execution did not block publication adjudication")
    ready_execution = build_execution(
        remedy_resolution=live_resolution,
        remedy_resolution_ref="embedded:audit-publication-live-resolution",
        receipt_id=f"{rev}-audit-publication-ready-execution",
        created_at=CREATED_AT,
        revision=rev,
        execution_status="completed",
        corrective_action_refs=["rollback-ledger:sha256:" + "d" * 64, "public-correction-shell:sha256:" + "e" * 64],
        rollback_completion_ref="rollback-completion:sha256:" + "f" * 64,
        nonhost_execution_proof_ref="nonhost-proof:execution-retained:sha256:" + "0" * 64,
        affected_party_completion_notice_ref="public-remedy-completion-notice:accessible-shell",
        redaction_boundary_ref="redaction-boundary:publication-execution:execution-public-shell-only",
    )
    passed_execution = build(
        recompute_receipt=receipt,
        recompute_receipt_ref=ref,
        snapshot=snap,
        snapshot_ref=receipt["linked_computed_snapshot_ref"],
        snapshot_hash=sha256_json(snap),
        challenges=[],
        challenge_refs=[],
        receipt_id=f"{rev}-audit-execution-ready",
        created_at=CREATED_AT,
        revision=rev,
        remedy_resolutions=[live_resolution],
        remedy_resolution_refs=["embedded:audit-publication-live-resolution"],
        remedy_executions=[ready_execution],
        remedy_execution_refs=["embedded:audit-publication-ready-execution"],
    )
    if passed_execution["decision"]["publication_adjudication_state"] != "eligible-zero-floor-stayed":
        raise SystemExit("ready remedy execution unexpectedly blocked zero-floor adjudication")
    print("audit_live_receipt_publication_rollback_adjudication: OK")


if __name__ == "__main__":
    main()
