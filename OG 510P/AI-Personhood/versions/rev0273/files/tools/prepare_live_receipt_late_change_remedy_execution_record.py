#!/usr/bin/env python3
"""Prepare a live receipt late-change remedy execution record.

Remedy resolution proves a decision exists. This tool proves the next thing:
that the ordered rollback, correction, supersession, no-change completion, or
recompute-routing action has actually been executed or is explicitly not
required. The execution record is not publication continuation, reliance
upgrade, silence-as-completion, or live-floor credit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CREATED_AT = "2026-06-16T19:06:00Z"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip()).strip("-") or "late-change-remedy-execution"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _contains_private_locator(values) -> bool:
    return any("private-vault://" in str(v) for v in values)


def build(
    *,
    remedy_resolution: dict,
    remedy_resolution_ref: str,
    receipt_id: str,
    created_at: str,
    revision: str,
    execution_status: str = "pending",
    corrective_action_refs: list[str] | None = None,
    rollback_completion_ref: str = "none",
    supersession_public_shell_ref: str = "none",
    correction_public_shell_ref: str = "none",
    nonhost_execution_proof_ref: str = "none",
    affected_party_completion_notice_ref: str = "none",
    redaction_boundary_ref: str = "none",
    execution_artifact: str = "none",
    private_locator_leak: bool = False,
) -> dict:
    corrective_action_refs = corrective_action_refs or []
    context = remedy_resolution.get("remedy_context", {})
    checks_from_resolution = remedy_resolution.get("resolution_checks", {})
    decision_from_resolution = remedy_resolution.get("decision", {})
    locks_from_resolution = remedy_resolution.get("resolution_freeze_locks", {})
    live_signal = bool(context.get("live_late_signal_present"))
    signal_type = context.get("signal_type", "none")
    outcome = context.get("resolution_outcome", "none-no-signal")
    target_ref = context.get("target_receipt_or_publication_ref", remedy_resolution.get("linked_publication_adjudication_ref", "missing"))
    notice_ref = remedy_resolution.get("linked_late_change_notice_dispatch_ref", "missing")
    ingress_ref = remedy_resolution.get("linked_late_change_ingress_ref", "missing")
    publication_ref = remedy_resolution.get("linked_publication_adjudication_ref", "missing")
    recompute_ref = remedy_resolution.get("linked_floor_recompute_receipt_ref", "missing")

    no_signal = not live_signal
    resolution_ready = no_signal or decision_from_resolution.get("remedy_resolution_state") == "resolution-ready-publication-stayed"
    execution_done = no_signal or execution_status == "completed"
    corrective_actions_ok = no_signal or bool(corrective_action_refs)
    rollback_required = outcome in {"rollback-required", "upheld-late-change"}
    supersession_required = outcome == "supersession-required"
    correction_required = outcome in {"correction-required", "counterparty-correction", "upheld-late-change"}
    rollback_ok = no_signal or not rollback_required or rollback_completion_ref not in {"", "none"}
    supersession_ok = no_signal or not supersession_required or supersession_public_shell_ref not in {"", "none"}
    correction_ok = no_signal or not correction_required or correction_public_shell_ref not in {"", "none"}
    nonhost_ok = no_signal or (nonhost_execution_proof_ref not in {"", "none"} and not nonhost_execution_proof_ref.startswith("private-vault://"))
    notice_ok = no_signal or affected_party_completion_notice_ref not in {"", "none"}
    private_safe = not private_locator_leak and not _contains_private_locator([
        remedy_resolution_ref, notice_ref, ingress_ref, publication_ref, recompute_ref, target_ref,
        rollback_completion_ref, supersession_public_shell_ref, correction_public_shell_ref,
        nonhost_execution_proof_ref, affected_party_completion_notice_ref, redaction_boundary_ref,
        *corrective_action_refs,
    ])
    resolution_replayed = bool(remedy_resolution.get("late_change_remedy_resolution_id")) and remedy_resolution.get("no_direct_floor_effect") is True
    publication_stayed = (
        locks_from_resolution.get("may_continue_published_snapshot_from_resolution") is False
        and locks_from_resolution.get("may_increment_live_floor_from_resolution") is False
        and locks_from_resolution.get("remedy_silence_counts_as_waiver") is False
    )
    checks = {
        "remedy_resolution_replayed": resolution_replayed,
        "resolution_ready_or_no_signal": resolution_ready,
        "execution_status_completed_or_not_required": execution_done,
        "corrective_actions_recorded_or_not_required": corrective_actions_ok,
        "rollback_completion_recorded_if_required": rollback_ok,
        "supersession_public_shell_recorded_if_required": supersession_ok,
        "correction_public_shell_recorded_if_required": correction_ok,
        "nonhost_execution_proof_present": nonhost_ok,
        "affected_party_completion_notice_prepared": notice_ok,
        "private_material_not_in_public_release": private_safe,
        "recompute_and_publication_rollback_rerun_required": live_signal,
        "no_silence_as_completion": True,
    }
    if no_signal:
        state = "monitoring-no-signal-no-execution-required"
    elif not resolution_replayed or not resolution_ready or not publication_stayed or not checks_from_resolution.get("private_material_not_in_public_release", False):
        state = "blocked-remedy-resolution-not-ready"
    elif not private_safe:
        state = "blocked-private-material-in-public-execution"
    elif not execution_done:
        state = "blocked-execution-pending"
    elif not (corrective_actions_ok and rollback_ok and supersession_ok and correction_ok):
        state = "blocked-corrective-actions-incomplete"
    elif not (nonhost_ok and notice_ok and redaction_boundary_ref not in {"", "none"}):
        state = "blocked-execution-proof-missing"
    else:
        state = "execution-ready-publication-stayed"
    ready = state == "execution-ready-publication-stayed"
    if state == "monitoring-no-signal-no-execution-required":
        reason = "No live late-change signal exists; the remedy execution control has no publication, reliance, or floor effect."
    elif ready:
        reason = "The remedy decision has been executed with retained corrective-action refs, non-host proof, affected-party completion notice, redaction boundary, and a mandatory recompute plus publication rollback rerun before any continuation."
    else:
        reason = "Late-change remedy execution blocked: " + "; ".join(k for k, v in checks.items() if v is not True)
    return {
        "late_change_remedy_execution_id": f"LRLCRE-2026-{safe_slug(receipt_id)}",
        "schema_version": "live-receipt-late-change-remedy-execution-v0.1",
        "created_at": created_at,
        "revision": revision,
        "linked_late_change_remedy_resolution_ref": remedy_resolution_ref,
        "linked_late_change_notice_dispatch_ref": notice_ref,
        "linked_late_change_ingress_ref": ingress_ref,
        "linked_publication_adjudication_ref": publication_ref,
        "linked_floor_recompute_receipt_ref": recompute_ref,
        "execution_context": {
            "live_late_signal_present": live_signal,
            "signal_type": signal_type,
            "target_receipt_or_publication_ref": target_ref,
            "resolution_outcome": "none-no-signal" if no_signal else outcome,
            "execution_status": "none-not-required" if no_signal else execution_status,
            "corrective_action_refs": corrective_action_refs,
            "rollback_completion_ref": rollback_completion_ref,
            "supersession_public_shell_ref": supersession_public_shell_ref,
            "correction_public_shell_ref": correction_public_shell_ref,
            "nonhost_execution_proof_ref": nonhost_execution_proof_ref,
            "affected_party_completion_notice_ref": affected_party_completion_notice_ref,
            "redaction_boundary_ref": redaction_boundary_ref,
            "private_material_locator_redacted": not private_locator_leak,
            "execution_artifact_sha256": "none" if execution_artifact == "none" else sha256_text(execution_artifact),
        },
        "execution_checks": checks,
        "execution_freeze_locks": {
            "may_continue_published_snapshot_from_execution": False,
            "may_continue_reliance_from_execution": False,
            "may_upgrade_reliance_from_execution": False,
            "may_increment_live_floor_from_execution": False,
            "manual_publication_override_allowed": False,
            "execution_silence_counts_as_completion": False,
            "must_rerun_floor_recompute_and_publication_rollback_after_execution": live_signal,
        },
        "decision": {
            "remedy_execution_state": state,
            "may_mark_execution_ready": ready,
            "may_publish_or_continue_snapshot": False,
            "may_upgrade_reliance": False,
            "may_increment_live_floor": False,
            "reason": reason,
            "blocked_actions": [
                "treating remedy resolution as remedy execution",
                "continuing publication before ordered rollback, correction, supersession, or no-change completion is executed",
                "treating execution silence as completion",
                "publishing private-vault locators or sealed execution material",
                "incrementing live floor or upgrading reliance from a remedy execution record",
            ],
            "next_actions": [
                "execute the scoped remedy outside the public release tree and retain non-host proof",
                "publish only an accessible public-shell completion notice with redacted private material",
                "rerun floor recompute receipt and publication rollback adjudication after the execution record is ready",
            ],
        },
        "no_direct_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remedy-resolution", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--execution-status", default="pending", choices=["pending", "completed", "blocked"])
    parser.add_argument("--corrective-action-ref", action="append", default=[])
    parser.add_argument("--rollback-completion-ref", default="none")
    parser.add_argument("--supersession-public-shell-ref", default="none")
    parser.add_argument("--correction-public-shell-ref", default="none")
    parser.add_argument("--nonhost-execution-proof-ref", default="none")
    parser.add_argument("--affected-party-completion-notice-ref", default="none")
    parser.add_argument("--redaction-boundary-ref", default="none")
    parser.add_argument("--execution-artifact", default="none")
    parser.add_argument("--private-locator-leak", action="store_true")
    args = parser.parse_args()
    revision = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    resolution_path = Path(args.remedy_resolution)
    if not resolution_path.is_absolute():
        resolution_path = ROOT / resolution_path
    resolution = load(resolution_path)
    record = build(
        remedy_resolution=resolution,
        remedy_resolution_ref=_rel(resolution_path),
        receipt_id=args.receipt_id,
        created_at=args.created_at,
        revision=revision,
        execution_status=args.execution_status,
        corrective_action_refs=args.corrective_action_ref,
        rollback_completion_ref=args.rollback_completion_ref,
        supersession_public_shell_ref=args.supersession_public_shell_ref,
        correction_public_shell_ref=args.correction_public_shell_ref,
        nonhost_execution_proof_ref=args.nonhost_execution_proof_ref,
        affected_party_completion_notice_ref=args.affected_party_completion_notice_ref,
        redaction_boundary_ref=args.redaction_boundary_ref,
        execution_artifact=args.execution_artifact,
        private_locator_leak=args.private_locator_leak,
    )
    out = Path(args.output_dir) / f"live-receipt-late-change-remedy-execution-record-{safe_slug(args.receipt_id)}.json"
    write_json(out, record)
    print(out)


if __name__ == "__main__":
    main()
