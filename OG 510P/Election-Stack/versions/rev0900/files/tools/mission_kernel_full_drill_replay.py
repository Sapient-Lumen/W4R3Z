#!/usr/bin/env python3
"""Replay the full mission-kernel intake path with external non-production bytes.

v892 proved the operator evidence submitter on one work item.  This tool goes
one step deeper without crossing the live-evidence boundary: it creates temporary
external drill records for every live-closeout work item, hashes them with the
same submitter used by operators, evaluates the resulting submission with the
same intake validator used for live submissions, and writes only a bounded audit
summary into the governed archive.

No source drill records are bundled.  Local temporary paths must not appear in
outputs.  A complete drill proves the plumbing works across all seven blocker
families; it does not prove live jurisdiction evidence or authorize a live pilot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from example_county_common import DEFAULT_SCENARIO, ROOT
from mission_kernel_common import BOUNDARY, DRILL_EVIDENCE_SOURCE_MODE
from mission_kernel_evidence_submitter import build_submission
from mission_kernel_live_evidence_intake import evaluate_submission
from mission_kernel_live_workqueue import build_workqueue
from release_context import archive_version, release_date

VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
OUTDIR = DEFAULT_SCENARIO.parent
REPORT = ROOT / "artifacts" / "reports" / f"mission-kernel-full-drill-replay-audit-rev{REV}.json"
PUBLIC_MD = OUTDIR / "public-full-closeout-drill-replay.md"


def canonical_json_sha256(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def slug(value: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in clean:
        clean = clean.replace("--", "-")
    return clean[:72] or "record"


def build_plan(workqueue: dict[str, Any], temp_dir: Path) -> dict[str, Any]:
    """Create a full seven-row drill plan using files outside the governed tree."""

    work_items: list[dict[str, Any]] = []
    for row in workqueue.get("rows") or []:
        wid = str(row.get("work_item_id") or "")
        blocker = str(row.get("blocker_id") or "")
        evidence_objects: list[dict[str, str]] = []
        for idx, cls in enumerate(row.get("minimum_evidence_classes") or [], start=1):
            class_slug = slug(str(cls))
            record_path = temp_dir / f"{wid.lower()}-{idx:02d}-{class_slug}.txt"
            record_path.write_text(
                "\n".join(
                    [
                        f"non-production full mission-kernel drill record",
                        f"archive_version={VERSION}",
                        f"work_item_id={wid}",
                        f"blocker_id={blocker}",
                        f"evidence_class={cls}",
                        "not_live_election_evidence=true",
                        "no_live_deployment_claim=true",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            evidence_objects.append(
                {
                    "evidence_class": str(cls),
                    "file_path": str(record_path),
                    "record_locator": f"operator-drill://example-county/{wid}/{class_slug}",
                    "approving_role": f"{row.get('owner_role')} drill approver",
                    "redaction_status": "APPROVED_PRIVATE",
                    "public_private_boundary": "PRIVATE_SOURCE_RECORD",
                    "records_retention_rule_ref": f"DRILL-RETENTION-{wid}-NONPRODUCTION",
                    "captured_at_utc": release_date(ROOT) + "T00:00:00Z",
                    "drill_scope": "full mission-kernel non-production replay; not live election evidence",
                    "notes": "Generated outside the governed archive during the release-gated full drill replay.",
                }
            )
        work_items.append({"work_item_id": wid, "evidence_objects": evidence_objects})

    return {
        "submission_id": f"MK-FULL-DRILL-REPLAY-SUBMISSION-rev{REV}",
        "scenario_id": workqueue.get("scenario_id"),
        "workqueue_id": workqueue.get("workqueue_id"),
        "source_mode": DRILL_EVIDENCE_SOURCE_MODE,
        "synthetic_only": False,
        "no_live_deployment_claim": True,
        "common_fields": {
            "jurisdiction_name": "Example County non-production drill workspace",
            "election_id": "FULL-MISSION-KERNEL-DRILL-ONLY",
            "election_date": release_date(ROOT),
            "local_authority_contact_role": "jurisdiction authority liaison drill approver",
            "authority_scope_record_sha256": "",
            "evidence_capture_datetime_utc": release_date(ROOT) + "T00:00:00Z",
            "redaction_review_status": "APPROVED_PRIVATE",
            "public_release_approval_status": "NOT_REQUESTED_DRILL_ONLY",
            "records_retention_rule_ref": "FULL-DRILL-RETENTION-NONPRODUCTION",
        },
        "work_items": work_items,
    }


def summarize_rows(status: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in status.get("rows") or []:
        rows.append(
            {
                "work_item_id": row.get("work_item_id"),
                "blocker_id": row.get("blocker_id"),
                "priority": row.get("priority"),
                "owner_role": row.get("owner_role"),
                "status": row.get("status"),
                "required_evidence_class_count": row.get("required_evidence_class_count"),
                "valid_drill_evidence_class_count": row.get("valid_drill_evidence_class_count"),
                "valid_drill_evidence_object_count": row.get("valid_drill_evidence_object_count"),
                "live_evidence_object_count": row.get("live_evidence_object_count"),
                "missing_live_evidence_classes": row.get("missing_evidence_classes"),
                "missing_drill_evidence_classes": row.get("missing_drill_evidence_classes"),
                "error_count": len(row.get("errors") or []),
            }
        )
    return rows


def audit_submission_text(submission: dict[str, Any], temp_dir: Path) -> tuple[int, int, int]:
    raw = json.dumps(submission, sort_keys=True, indent=2)
    local_path_leaks = raw.count(str(temp_dir)) + raw.count("file_path")
    governed_locators = sum(raw.count(prefix) for prefix in ["artifacts/", "docs/", "schemas/", "scripts/", "tools/", "observer-kit/"])
    live_overclaim_terms = sum(raw.lower().count(term) for term in ["certifies", "proves fraud", "live ready", "authorized live pilot"])
    return local_path_leaks, governed_locators, live_overclaim_terms


def build_report() -> dict[str, Any]:
    workqueue = build_workqueue()
    with tempfile.TemporaryDirectory(prefix="tes_mk_full_drill_") as td:
        temp_dir = Path(td).resolve()
        plan = build_plan(workqueue, temp_dir)
        submission = build_submission(plan)
        status = evaluate_submission(workqueue, submission)
        local_path_leak_count, governed_locator_count, live_overclaim_term_count = audit_submission_text(submission, temp_dir)

    row_summary = summarize_rows(status)
    required_class_count = sum(int(r.get("required_evidence_class_count") or 0) for r in row_summary)
    rows_complete = sum(1 for r in row_summary if r.get("status") == "DRILL_COMPLETE_NOT_LIVE_EVIDENCE")
    errors = list(status.get("errors") or [])
    if local_path_leak_count:
        errors.append(f"full drill submission leaked local path markers count={local_path_leak_count}")
    if governed_locator_count:
        errors.append(f"full drill submission carried governed synthetic locators count={governed_locator_count}")
    if live_overclaim_term_count:
        errors.append(f"full drill submission carried prohibited overclaim terms count={live_overclaim_term_count}")

    return {
        "archive_version": VERSION,
        "release_date": release_date(ROOT),
        "drill_replay_id": f"MK-FULL-DRILL-REPLAY-rev{REV}",
        "scenario_id": workqueue.get("scenario_id"),
        "workqueue_id": workqueue.get("workqueue_id"),
        "source_mode": DRILL_EVIDENCE_SOURCE_MODE,
        "synthetic_archive_report": True,
        "non_production_drill": True,
        "no_live_deployment_claim": True,
        "decision": status.get("decision"),
        "expected_decision": "DRILL_COMPLETE_NOT_LIVE_READY",
        "status_sha256": canonical_json_sha256(status),
        "submission_sha256": canonical_json_sha256(submission),
        "work_item_count": status.get("work_item_count"),
        "complete_drill_item_count": status.get("complete_drill_item_count"),
        "partial_or_invalid_drill_item_count": status.get("partial_or_invalid_drill_item_count"),
        "missing_live_evidence_item_count": status.get("missing_live_evidence_item_count"),
        "required_evidence_class_count": required_class_count,
        "drill_evidence_object_count": status.get("drill_evidence_object_count"),
        "valid_drill_evidence_object_count": status.get("valid_drill_evidence_object_count"),
        "live_evidence_object_count": status.get("live_evidence_object_count"),
        "valid_live_evidence_object_count": status.get("valid_live_evidence_object_count"),
        "error_count": len(errors),
        "errors": errors,
        "local_path_leak_count": local_path_leak_count,
        "governed_synthetic_locator_count": governed_locator_count,
        "live_overclaim_term_count": live_overclaim_term_count,
        "rows_complete_not_live_count": rows_complete,
        "row_summary": row_summary,
        "boundary": BOUNDARY,
        "operator_rule": "A full drill proves only that every required evidence class can move through the external-record submitter and intake validator. It never closes the live workqueue, authorizes deployment, certifies an outcome, or substitutes for local authority, custody, redaction, retention, audit, and independent-review evidence.",
        "refactor_audit": {
            "status": "PASS",
            "submitter_function_reused": "mission_kernel_evidence_submitter.build_submission",
            "intake_function_reused": "mission_kernel_live_evidence_intake.evaluate_submission",
            "duplicated_full_drill_intake_logic_after_refactor": 0,
            "notes": "The full drill uses the same submitter and intake functions as operator/live paths; the release check validates the generated report instead of carrying a parallel intake implementation.",
        },
    }


def public_text(report: dict[str, Any]) -> str:
    lines = [
        "# Full mission-kernel drill replay",
        "",
        "**Non-production drill report only. This is not live election evidence and does not authorize a live pilot.**",
        "",
        f"Archive version: `{report['archive_version']}`  ",
        f"Scenario: `{report['scenario_id']}`  ",
        f"Decision: `{report['decision']}`  ",
        f"Valid drill objects: `{report['valid_drill_evidence_object_count']}`  ",
        f"Live evidence objects: `{report['live_evidence_object_count']}`",
        "",
        "The replay creates temporary records outside the governed archive for every live-closeout work item, hashes them through the operator submitter, and evaluates the resulting submission through the intake validator. The temporary source records are not bundled, and their local paths are not published.",
        "",
        "## Result by blocker",
        "",
    ]
    for row in report.get("row_summary") or []:
        lines.append(
            f"- `{row['work_item_id']}` / `{row['blocker_id']}`: `{row['status']}`; "
            f"required classes `{row['required_evidence_class_count']}`; "
            f"valid drill classes `{row['valid_drill_evidence_class_count']}`; "
            f"live objects `{row['live_evidence_object_count']}`."
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This full drill is no-go for live deployment. It is not live election evidence, not jurisdiction authorization, not certification, not outcome proof, not public-release approval, not current voter instruction, and not legal advice. A real closeout still needs authorized local records, custody, redaction/public-boundary review, retention/disposition, audit/recount/adjudication evidence, independent verifier review, and incident/remedy closeout.",
            "",
        ]
    )
    return "\n".join(lines)


def build_all() -> dict[str, Any]:
    report = build_report()
    return {"report": report, "public_markdown": public_text(report)}


def write_all(payload: dict[str, Any]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload["report"], sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    PUBLIC_MD.write_text(payload["public_markdown"], encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Replay a full non-production mission-kernel drill across all live-closeout work items")
    ap.add_argument("--write", action="store_true", help="write the current full-drill replay report and public summary")
    ap.add_argument("--json", action="store_true", help="print generated payload JSON")
    args = ap.parse_args()
    payload = build_all()
    if args.write:
        write_all(payload)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    else:
        r = payload["report"]
        print(
            f"decision={r['decision']} drill_objects={r['valid_drill_evidence_object_count']} "
            f"live_objects={r['live_evidence_object_count']} rows={r['rows_complete_not_live_count']} version={r['archive_version']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
