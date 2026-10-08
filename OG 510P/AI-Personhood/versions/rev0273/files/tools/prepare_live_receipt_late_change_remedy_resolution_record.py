#!/usr/bin/env python3
"""Prepare a live receipt late-change remedy resolution record.

Notice dispatch proves affected parties were notified and a remedy window was
opened. This tool proves the next thing: that the remedy/appeal window has been
resolved, retained, scoped, redacted, and routed back into recompute/publication
rollback. The resolution record is not a publication continuation, waiver,
reliance upgrade, or live-floor increment.
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
    return re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip()).strip("-") or "late-change-remedy-resolution"


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
    notice_dispatch: dict,
    notice_dispatch_ref: str,
    receipt_id: str,
    created_at: str,
    revision: str,
    remedy_window_status: str = "open",
    affected_party_submission_refs: list[str] | None = None,
    resolution_authority_ref: str = "none",
    resolution_decision_ref: str = "none",
    resolution_outcome: str = "recompute-required",
    nonhost_resolution_proof_ref: str = "none",
    accessible_resolution_notice_ref: str = "none",
    redaction_boundary_ref: str = "none",
    resolution_artifact: str = "none",
    private_locator_leak: bool = False,
) -> dict:
    affected_party_submission_refs = affected_party_submission_refs or []
    context = notice_dispatch.get("notice_context", {})
    checks_from_notice = notice_dispatch.get("dispatch_checks", {})
    decision_from_notice = notice_dispatch.get("decision", {})
    locks_from_notice = notice_dispatch.get("notice_freeze_locks", {})
    live_signal = bool(context.get("live_late_signal_present"))
    signal_type = context.get("signal_type", "none")
    target_ref = context.get("target_receipt_or_publication_ref", notice_dispatch.get("linked_publication_adjudication_ref", "missing"))
    ingress_ref = notice_dispatch.get("linked_late_change_ingress_ref", "missing")
    publication_ref = notice_dispatch.get("linked_publication_adjudication_ref", "missing")
    recompute_ref = notice_dispatch.get("linked_floor_recompute_receipt_ref", "missing")
    remedy_ref = context.get("remedy_or_appeal_window_ref", "none")

    no_signal = not live_signal
    dispatch_ready = no_signal or decision_from_notice.get("notice_dispatch_state") == "dispatch-ready-publication-stayed"
    window_closed = no_signal or remedy_window_status == "closed"
    submissions_ok = no_signal or len([s for s in affected_party_submission_refs if s]) >= 2
    authority_ok = no_signal or resolution_authority_ref not in {"", "none"}
    decision_ok = no_signal or resolution_decision_ref not in {"", "none"}
    outcome_ok = no_signal or resolution_outcome in {"upheld-late-change", "denied-no-change", "supersession-required", "rollback-required", "correction-required", "recompute-required"}
    route_bound = no_signal or resolution_outcome in {"upheld-late-change", "supersession-required", "rollback-required", "correction-required", "recompute-required", "denied-no-change"}
    nonhost_ok = no_signal or (nonhost_resolution_proof_ref not in {"", "none"} and not nonhost_resolution_proof_ref.startswith("private-vault://"))
    accessible_ok = no_signal or accessible_resolution_notice_ref not in {"", "none"}
    redaction_ok = no_signal or redaction_boundary_ref not in {"", "none"}
    private_safe = not private_locator_leak and not _contains_private_locator([
        notice_dispatch_ref,
        ingress_ref,
        publication_ref,
        recompute_ref,
        target_ref,
        remedy_ref,
        resolution_authority_ref,
        resolution_decision_ref,
        nonhost_resolution_proof_ref,
        accessible_resolution_notice_ref,
        redaction_boundary_ref,
        *affected_party_submission_refs,
    ])
    notice_replayed = bool(notice_dispatch.get("late_change_notice_dispatch_id")) and notice_dispatch.get("no_direct_floor_effect") is True
    publication_stayed = locks_from_notice.get("may_continue_published_snapshot_from_notice") is False and locks_from_notice.get("may_increment_live_floor_from_notice") is False
    checks = {
        "notice_dispatch_replayed": notice_replayed,
        "dispatch_ready_or_no_signal": dispatch_ready,
        "remedy_window_closed_or_not_required": window_closed,
        "affected_party_submissions_retained": submissions_ok,
        "resolution_authority_scoped": authority_ok,
        "resolution_decision_recorded": decision_ok,
        "resolution_outcome_scoped": outcome_ok,
        "rollback_or_recompute_route_bound": route_bound,
        "nonhost_resolution_proof_present": nonhost_ok,
        "accessible_resolution_notice_prepared": accessible_ok,
        "private_material_not_in_public_release": private_safe,
        "publication_continuation_stayed": publication_stayed,
        "no_silence_as_waiver": True,
    }
    if no_signal:
        state = "monitoring-no-signal-no-remedy-required"
    elif not dispatch_ready or not checks_from_notice.get("remedy_window_opened", False):
        state = "blocked-notice-dispatch-not-ready"
    elif not private_safe:
        state = "blocked-private-material-in-public-resolution"
    elif not window_closed:
        state = "blocked-remedy-window-still-open"
    elif not submissions_ok:
        state = "blocked-remedy-submissions-unretained"
    elif not authority_ok:
        state = "blocked-resolution-authority-missing"
    elif not decision_ok or not (outcome_ok and route_bound and nonhost_ok and accessible_ok and redaction_ok):
        state = "blocked-resolution-decision-missing"
    else:
        state = "resolution-ready-publication-stayed"
    ready = state == "resolution-ready-publication-stayed"
    if state == "monitoring-no-signal-no-remedy-required":
        reason = "No live late-change signal exists; the remedy resolution control has no publication, reliance, or floor effect."
    elif ready:
        reason = "The remedy/appeal window has closed with retained submissions, scoped authority, a decision record, non-host proof, accessible resolution notice, and redaction boundary; recompute plus publication rollback adjudication must rerun before any continuation."
    else:
        reason = "Late-change remedy resolution blocked: " + "; ".join(k for k, v in checks.items() if v is not True)
    return {
        "late_change_remedy_resolution_id": f"LRLCRR-2026-{safe_slug(receipt_id)}",
        "schema_version": "live-receipt-late-change-remedy-resolution-v0.1",
        "created_at": created_at,
        "revision": revision,
        "linked_late_change_notice_dispatch_ref": notice_dispatch_ref,
        "linked_late_change_ingress_ref": ingress_ref,
        "linked_publication_adjudication_ref": publication_ref,
        "linked_floor_recompute_receipt_ref": recompute_ref,
        "remedy_context": {
            "live_late_signal_present": live_signal,
            "signal_type": signal_type,
            "target_receipt_or_publication_ref": target_ref,
            "remedy_or_appeal_window_ref": remedy_ref,
            "remedy_window_status": "none" if no_signal else remedy_window_status,
            "affected_party_submission_refs": affected_party_submission_refs,
            "resolution_authority_ref": resolution_authority_ref,
            "resolution_decision_ref": resolution_decision_ref,
            "resolution_outcome": "none-no-signal" if no_signal else resolution_outcome,
            "nonhost_resolution_proof_ref": nonhost_resolution_proof_ref,
            "accessible_resolution_notice_ref": accessible_resolution_notice_ref,
            "redaction_boundary_ref": redaction_boundary_ref,
            "private_material_locator_redacted": not private_locator_leak,
            "resolution_artifact_sha256": "none" if resolution_artifact == "none" else sha256_text(resolution_artifact),
        },
        "resolution_checks": checks,
        "resolution_freeze_locks": {
            "may_continue_published_snapshot_from_resolution": False,
            "may_continue_reliance_from_resolution": False,
            "may_upgrade_reliance_from_resolution": False,
            "may_increment_live_floor_from_resolution": False,
            "manual_publication_override_allowed": False,
            "remedy_silence_counts_as_waiver": False,
            "must_rerun_floor_recompute_and_publication_rollback_after_resolution": live_signal,
        },
        "decision": {
            "remedy_resolution_state": state,
            "may_mark_resolution_ready": ready,
            "may_publish_or_continue_snapshot": False,
            "may_upgrade_reliance": False,
            "may_increment_live_floor": False,
            "reason": reason,
            "blocked_actions": [
                "treating notice dispatch as remedy completion",
                "continuing publication while remedy or appeal window remains open",
                "treating remedy silence as waiver or acceptance",
                "publishing private-vault locators or sealed remedy submissions",
                "incrementing live floor or upgrading reliance from a remedy resolution record",
            ],
            "next_actions": [
                "retain affected-party submissions and resolution decision outside the public release tree",
                "publish only public-shell/hash references and accessible resolution notice",
                "rerun compute_live_receipt_floor.py, floor recompute receipt, and publication rollback adjudication after resolution readiness or blockage",
            ],
        },
        "no_direct_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notice-dispatch", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--remedy-window-status", choices=["open", "closed"], default="open")
    parser.add_argument("--affected-party-submission-ref", action="append", default=[])
    parser.add_argument("--resolution-authority-ref", default="none")
    parser.add_argument("--resolution-decision-ref", default="none")
    parser.add_argument("--resolution-outcome", default="recompute-required")
    parser.add_argument("--nonhost-resolution-proof-ref", default="none")
    parser.add_argument("--accessible-resolution-notice-ref", default="none")
    parser.add_argument("--redaction-boundary-ref", default="none")
    parser.add_argument("--resolution-artifact", default="none")
    parser.add_argument("--private-locator-leak", action="store_true")
    args = parser.parse_args()
    path = Path(args.notice_dispatch)
    if not path.is_absolute():
        path = ROOT / path
    notice = load(path)
    revision = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    record = build(
        notice_dispatch=notice,
        notice_dispatch_ref=_rel(path),
        receipt_id=args.receipt_id,
        created_at=args.created_at,
        revision=revision,
        remedy_window_status=args.remedy_window_status,
        affected_party_submission_refs=args.affected_party_submission_ref,
        resolution_authority_ref=args.resolution_authority_ref,
        resolution_decision_ref=args.resolution_decision_ref,
        resolution_outcome=args.resolution_outcome,
        nonhost_resolution_proof_ref=args.nonhost_resolution_proof_ref,
        accessible_resolution_notice_ref=args.accessible_resolution_notice_ref,
        redaction_boundary_ref=args.redaction_boundary_ref,
        resolution_artifact=args.resolution_artifact,
        private_locator_leak=args.private_locator_leak,
    )
    out = Path(args.output_dir) / f"live-receipt-late-change-remedy-resolution-record-{safe_slug(args.receipt_id)}.json"
    write_json(out, record)
    print(out)


if __name__ == "__main__":
    main()
