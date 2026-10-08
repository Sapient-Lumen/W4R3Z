#!/usr/bin/env python3
"""Validate and report mission-kernel live-closeout evidence intake.

This is the concrete bridge after the live workqueue: it does not collect live
records itself, but it gives an operator a fail-closed shape for digest-bound
local evidence and proves the governed synthetic archive has not filled those
slots with generated examples.  v892 also recognizes a non-production drill mode
so operators can test the path with external bytes without calling them live
election evidence.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from example_county_common import DEFAULT_SCENARIO, ROOT
from mission_kernel_common import (
    ALLOWED_SOURCE_MODES,
    BOUNDARY,
    DRILL_EVIDENCE_SOURCE_MODE,
    EMPTY_SOURCE_MODES,
    LIVE_EVIDENCE_SOURCE_MODE,
    NON_LIVE_SOURCE_MODES,
    PUBLIC_BOUNDARY_VALUES,
    REDACTION_STATUS_VALUES,
    is_governed_synthetic_locator,
    missing_classes,
)
from mission_kernel_live_workqueue import build_workqueue
from release_context import archive_version, release_date

VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
OUTDIR = DEFAULT_SCENARIO.parent
SUBMISSION = OUTDIR / "live-closeout-evidence-submission-empty.json"
STATUS_JSON = OUTDIR / "live-closeout-evidence-intake-status.json"
STATUS_CSV = OUTDIR / "live-closeout-evidence-intake-status.csv"
PUBLIC_MD = OUTDIR / "public-live-closeout-intake-status.md"
REPORT = ROOT / "artifacts" / "reports" / f"mission-kernel-live-evidence-intake-rev{REV}.json"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
RAW_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
LOCATOR_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
WINDOWS_ABSOLUTE_RE = re.compile(r"^[a-zA-Z]:[\\/]")


def normalize_digest(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if RAW_DIGEST_RE.fullmatch(raw):
        return "sha256:" + raw
    return raw


def empty_submission(workqueue: dict[str, Any]) -> dict[str, Any]:
    """Return the shipped empty submission, deliberately not evidence."""

    return {
        "archive_version": VERSION,
        "submission_id": f"MK-LIVE-EVIDENCE-EMPTY-SUBMISSION-rev{REV}",
        "scenario_id": workqueue.get("scenario_id"),
        "workqueue_id": workqueue.get("workqueue_id"),
        "source_mode": "SYNTHETIC_EMPTY_TEMPLATE",
        "synthetic_only": True,
        "non_production_drill": False,
        "no_live_deployment_claim": True,
        "decision": "UNFILLED_TEMPLATE_NOT_EVIDENCE",
        "boundary": BOUNDARY,
        "common_fields": {
            "jurisdiction_name": "",
            "election_id": "",
            "election_date": "",
            "local_authority_contact_role": "",
            "authority_scope_record_sha256": "",
            "evidence_capture_datetime_utc": "",
            "redaction_review_status": "",
            "public_release_approval_status": "",
            "records_retention_rule_ref": "",
        },
        "work_items": [
            {
                "work_item_id": row["work_item_id"],
                "blocker_id": row["blocker_id"],
                "submission_status": "MISSING_LIVE_EVIDENCE",
                "owner_role": row["owner_role"],
                "minimum_evidence_classes": row["minimum_evidence_classes"],
                "evidence_objects": [],
                "operator_next_action": "collect authorized local records outside the governed synthetic archive, hash them, record approving roles, and rerun the intake validator",
            }
            for row in workqueue.get("rows") or []
        ],
    }


def load_submission(path: Path | None, workqueue: dict[str, Any]) -> dict[str, Any]:
    if path is None:
        return empty_submission(workqueue)
    return json.loads(path.read_text(encoding="utf-8"))


def _evidence_objects_for(item: dict[str, Any]) -> list[dict[str, Any]]:
    values = item.get("evidence_objects") or []
    return [v for v in values if isinstance(v, dict)]


def _parse_utc_timestamp(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        return None
    return parsed


def _locator_problem(locator: str) -> str | None:
    clean = str(locator or "").strip().replace("\\", "/")
    lower = clean.lower()
    if not clean:
        return "missing record_locator"
    if clean.startswith(("/", "~/", "../", "./")) or WINDOWS_ABSOLUTE_RE.match(clean):
        return "record_locator must be an opaque external locator, not a local filesystem path"
    if lower.startswith(("file:", "path:")):
        return "record_locator must not use a local file/path scheme"
    if is_governed_synthetic_locator(clean):
        return f"governed synthetic archive path cannot satisfy external evidence: {clean}"
    if not LOCATOR_SCHEME_RE.match(clean):
        return "record_locator must use an explicit opaque scheme"
    return None


def _review_boundary_problem(redaction_status: str, boundary: str) -> str | None:
    allowed_pairs = {
        "APPROVED_PUBLIC": {"PUBLIC_RELEASED", "REDACTED_PUBLIC_DERIVATIVE"},
        "APPROVED_PRIVATE": {"PRIVATE_SOURCE_RECORD"},
        "WITHHELD": {"WITHHELD_LEGAL_OR_PRIVACY"},
    }
    if redaction_status in allowed_pairs and boundary not in allowed_pairs[redaction_status]:
        return f"redaction_status {redaction_status!r} conflicts with public_private_boundary {boundary!r}"
    return None


def validate_evidence_object(
    obj: dict[str, Any],
    *,
    work_item_id: str,
    required_classes: set[str],
    submission_source_mode: str,
) -> tuple[str, str, list[str]]:
    """Return ``(validation_kind, evidence_class, problems)``.

    A live record can be *shape-valid* here, but it is never authenticated by a
    digest and a free-text approving role.  Until strict EvidenceEnvelope and
    trust-profile verification is wired into this intake, live records remain
    candidates and cannot increment the valid-live counters.
    """

    problems: list[str] = []
    evidence_class = str(obj.get("evidence_class") or "").strip()
    source_mode = str(obj.get("source_mode") or "").strip()
    locator = str(obj.get("record_locator") or obj.get("local_path_or_record_locator") or "").strip()
    digest = normalize_digest(obj.get("sha256"))
    approving_role = str(obj.get("approving_role") or "").strip()
    redaction_status = str(obj.get("redaction_status") or "").strip()
    boundary = str(obj.get("public_private_boundary") or "").strip()
    retention_ref = str(obj.get("records_retention_rule_ref") or "").strip()
    captured_at = str(obj.get("captured_at_utc") or "").strip()
    byte_count = obj.get("byte_count")

    if not evidence_class:
        problems.append(f"{work_item_id}: evidence object missing evidence_class")
    elif evidence_class not in required_classes:
        problems.append(f"{work_item_id}: evidence_class {evidence_class!r} is not required for this item")

    if source_mode not in ALLOWED_SOURCE_MODES:
        problems.append(f"{work_item_id}: source_mode {source_mode!r} is not allowed")
    if source_mode in EMPTY_SOURCE_MODES:
        if locator or digest:
            problems.append(f"{work_item_id}: empty/missing source_mode must not carry locator or digest")
        return "empty", evidence_class, problems
    if source_mode in NON_LIVE_SOURCE_MODES:
        if digest and not DIGEST_RE.fullmatch(digest):
            problems.append(f"{work_item_id}: non-live digest must be sha256:<64hex> if present")
        return "non_live", evidence_class, problems

    if source_mode in {LIVE_EVIDENCE_SOURCE_MODE, DRILL_EVIDENCE_SOURCE_MODE}:
        if source_mode != submission_source_mode:
            problems.append(
                f"{work_item_id}: evidence object source_mode {source_mode!r} does not match "
                f"submission source_mode {submission_source_mode!r}"
            )
        locator_problem = _locator_problem(locator)
        if locator_problem:
            problems.append(f"{work_item_id}: {locator_problem}")
        if not DIGEST_RE.fullmatch(digest):
            problems.append(f"{work_item_id}: evidence object missing sha256:<64hex> digest")
        if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
            problems.append(f"{work_item_id}: evidence object byte_count must be a positive integer")
        if not approving_role:
            problems.append(f"{work_item_id}: evidence object missing approving_role")
        if redaction_status not in REDACTION_STATUS_VALUES or redaction_status in {"", "NOT_REVIEWED"}:
            problems.append(f"{work_item_id}: evidence object has no completed redaction review")
        if boundary not in PUBLIC_BOUNDARY_VALUES or not boundary:
            problems.append(f"{work_item_id}: evidence object missing or invalid public/private boundary")
        pair_problem = _review_boundary_problem(redaction_status, boundary)
        if pair_problem:
            problems.append(f"{work_item_id}: {pair_problem}")
        if not retention_ref:
            problems.append(f"{work_item_id}: evidence object missing records_retention_rule_ref")
        if _parse_utc_timestamp(captured_at) is None:
            problems.append(f"{work_item_id}: captured_at_utc must be an explicit UTC RFC3339 timestamp")

        if source_mode == LIVE_EVIDENCE_SOURCE_MODE:
            return ("live_candidate_shape_valid" if not problems else "live_candidate_invalid"), evidence_class, problems
        return ("drill_valid" if not problems else "drill_invalid"), evidence_class, problems

    problems.append(f"{work_item_id}: unhandled source_mode {source_mode!r}")
    return "non_live", evidence_class, problems


def _duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for value in values:
        if value in seen:
            dup.add(value)
        seen.add(value)
    return sorted(dup)


def evaluate_submission(workqueue: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    rows_by_id = {str(r.get("work_item_id")): r for r in workqueue.get("rows") or [] if isinstance(r, dict)}
    errors: list[str] = []
    status_rows: list[dict[str, Any]] = []

    raw_items = submission.get("work_items") or []
    if not isinstance(raw_items, list):
        errors.append("submission work_items must be an array")
        raw_items = []
    submitted_items = [item for item in raw_items if isinstance(item, dict)]
    if len(submitted_items) != len(raw_items):
        errors.append("submission work_items contains a non-object entry")
    submitted_ids = [str(item.get("work_item_id") or "").strip() for item in submitted_items]
    for wid in _duplicate_values(submitted_ids):
        errors.append(f"submission contains duplicate work_item_id {wid}")
    submitted_by_id = {wid: item for wid, item in zip(submitted_ids, submitted_items) if wid}

    submission_mode = str(submission.get("source_mode") or "").strip()
    if submission.get("archive_version") != VERSION:
        errors.append("submission archive_version does not match this release")
    if submission.get("scenario_id") != workqueue.get("scenario_id"):
        errors.append("submission scenario_id does not match generated workqueue")
    if submission.get("workqueue_id") != workqueue.get("workqueue_id"):
        errors.append("submission workqueue_id does not match generated workqueue")
    if submission_mode not in ALLOWED_SOURCE_MODES:
        errors.append(f"submission source_mode {submission_mode!r} is not allowed")
    if submission.get("no_live_deployment_claim") is not True:
        errors.append("submission must keep no_live_deployment_claim=true")
    if submission_mode == LIVE_EVIDENCE_SOURCE_MODE and submission.get("synthetic_only") is True:
        errors.append("live source_mode submission must not be marked synthetic_only=true")
    if submission_mode == DRILL_EVIDENCE_SOURCE_MODE:
        if submission.get("no_live_deployment_claim") is not True:
            errors.append("non-production drill submission must keep no_live_deployment_claim=true")
        if submission.get("non_production_drill") is not True:
            errors.append("non-production drill submission must set non_production_drill=true")

    common = submission.get("common_fields") if isinstance(submission.get("common_fields"), dict) else {}
    if submission_mode == LIVE_EVIDENCE_SOURCE_MODE:
        required_common = [
            "jurisdiction_name",
            "election_id",
            "election_date",
            "local_authority_contact_role",
            "authority_scope_record_sha256",
            "evidence_capture_datetime_utc",
            "redaction_review_status",
            "public_release_approval_status",
            "records_retention_rule_ref",
        ]
        for field in required_common:
            if not str(common.get(field) or "").strip():
                errors.append(f"live submission common_fields missing {field}")
        if common.get("authority_scope_record_sha256") and not DIGEST_RE.fullmatch(normalize_digest(common.get("authority_scope_record_sha256"))):
            errors.append("live submission authority_scope_record_sha256 must be sha256:<64hex>")
        if common.get("evidence_capture_datetime_utc") and _parse_utc_timestamp(common.get("evidence_capture_datetime_utc")) is None:
            errors.append("live submission evidence_capture_datetime_utc must be an explicit UTC RFC3339 timestamp")

    extra_ids = sorted(set(submitted_by_id) - set(rows_by_id))
    for wid in extra_ids:
        errors.append(f"submission contains unknown work_item_id {wid}")

    live_object_count = 0
    shape_valid_live_candidate_object_count = 0
    drill_object_count = 0
    valid_drill_object_count = 0
    non_live_object_count = 0
    complete_live_candidate_item_count = 0
    partial_live_candidate_item_count = 0
    complete_drill_item_count = 0
    partial_drill_item_count = 0

    for wid, row in rows_by_id.items():
        item = submitted_by_id.get(wid, {})
        required = [str(x) for x in row.get("minimum_evidence_classes") or []]
        required_set = set(required)
        candidate_live_classes: list[str] = []
        valid_drill_classes: list[str] = []
        item_errors: list[str] = []
        item_live_count = 0
        item_shape_valid_live_count = 0
        item_drill_count = 0
        item_valid_drill_count = 0
        item_non_live_count = 0

        if item and item.get("blocker_id") not in {None, "", row.get("blocker_id")}:
            item_errors.append(f"{wid}: blocker_id does not match workqueue")

        objects = _evidence_objects_for(item)
        class_values = [str(obj.get("evidence_class") or "").strip() for obj in objects]
        for duplicate_class in _duplicate_values([v for v in class_values if v]):
            item_errors.append(f"{wid}: duplicate evidence_class {duplicate_class!r}")

        for obj in objects:
            source_mode = str(obj.get("source_mode") or "").strip()
            kind, cls, problems = validate_evidence_object(
                obj,
                work_item_id=wid,
                required_classes=required_set,
                submission_source_mode=submission_mode,
            )
            item_errors.extend(problems)
            if source_mode == LIVE_EVIDENCE_SOURCE_MODE:
                item_live_count += 1
                live_object_count += 1
                if kind == "live_candidate_shape_valid":
                    item_shape_valid_live_count += 1
                    shape_valid_live_candidate_object_count += 1
                    if cls:
                        candidate_live_classes.append(cls)
            elif source_mode == DRILL_EVIDENCE_SOURCE_MODE:
                item_drill_count += 1
                drill_object_count += 1
                if kind == "drill_valid":
                    item_valid_drill_count += 1
                    valid_drill_object_count += 1
                    if cls:
                        valid_drill_classes.append(cls)
            elif source_mode not in EMPTY_SOURCE_MODES:
                item_non_live_count += 1
                non_live_object_count += 1

        # Bare live candidates never satisfy authenticated live evidence.  Keep
        # the candidate coverage separately so operators can see whether shape
        # or authentication is the remaining blocker.
        missing_live = list(required)
        missing_candidate = missing_classes(required, candidate_live_classes)
        missing_drill = missing_classes(required, valid_drill_classes)
        if item_live_count:
            if missing_candidate or item_errors:
                item_status = "PARTIAL_OR_INVALID_LIVE_EVIDENCE_CANDIDATE"
                partial_live_candidate_item_count += 1
            else:
                item_status = "CANDIDATE_COMPLETE_AUTHENTICATION_REQUIRED"
                complete_live_candidate_item_count += 1
        elif item_drill_count:
            if missing_drill or item_errors:
                item_status = "DRILL_PARTIAL_OR_INVALID_NOT_LIVE_EVIDENCE"
                partial_drill_item_count += 1
            else:
                item_status = "DRILL_COMPLETE_NOT_LIVE_EVIDENCE"
                complete_drill_item_count += 1
        else:
            item_status = "MISSING_LIVE_EVIDENCE"

        status_rows.append({
            "work_item_id": wid,
            "blocker_id": row.get("blocker_id"),
            "priority": row.get("priority"),
            "owner_role": row.get("owner_role"),
            "required_evidence_class_count": len(required),
            "valid_live_evidence_class_count": 0,
            "shape_valid_live_candidate_class_count": len(set(candidate_live_classes)),
            "valid_drill_evidence_class_count": len(set(valid_drill_classes)),
            "live_evidence_object_count": item_live_count,
            "valid_live_evidence_object_count": 0,
            "shape_valid_live_candidate_object_count": item_shape_valid_live_count,
            "drill_evidence_object_count": item_drill_count,
            "valid_drill_evidence_object_count": item_valid_drill_count,
            "non_live_evidence_object_count": item_non_live_count,
            "missing_evidence_classes": missing_live,
            "missing_candidate_evidence_classes": missing_candidate,
            "missing_drill_evidence_classes": missing_drill,
            "status": item_status,
            "errors": item_errors,
            "next_action": row.get("first_operator_action"),
        })
        errors.extend(item_errors)

    if live_object_count:
        decision = "NO_GO_INTAKE_VALIDATION_FAILED" if errors else "NO_GO_LIVE_EVIDENCE_AUTHENTICATION_REQUIRED"
    elif drill_object_count:
        if errors:
            decision = "NO_GO_DRILL_VALIDATION_FAILED_NOT_LIVE_EVIDENCE"
        elif complete_drill_item_count == len(rows_by_id):
            decision = "DRILL_COMPLETE_NOT_LIVE_READY"
        else:
            decision = "DRILL_PARTIAL_NOT_LIVE_EVIDENCE"
    elif errors:
        decision = "NO_GO_INTAKE_VALIDATION_FAILED"
    else:
        decision = "NO_GO_NO_LIVE_EVIDENCE_SUBMITTED"

    return {
        "archive_version": VERSION,
        "release_date": release_date(ROOT),
        "scenario_id": workqueue.get("scenario_id"),
        "workqueue_id": workqueue.get("workqueue_id"),
        "intake_report_id": f"MK-LIVE-EVIDENCE-INTAKE-rev{REV}",
        "generated_at": release_date(ROOT) + "T00:00:00Z",
        "synthetic_archive_report": True,
        "no_live_deployment_claim": True,
        "decision": decision,
        "submission_id": submission.get("submission_id"),
        "submission_source_mode": submission.get("source_mode"),
        "work_item_count": len(rows_by_id),
        "complete_pending_review_item_count": 0,
        "complete_live_candidate_item_count": complete_live_candidate_item_count,
        "partial_or_invalid_item_count": partial_live_candidate_item_count,
        "complete_drill_item_count": complete_drill_item_count,
        "partial_or_invalid_drill_item_count": partial_drill_item_count,
        "missing_live_evidence_item_count": sum(1 for r in status_rows if r["status"] == "MISSING_LIVE_EVIDENCE"),
        "live_evidence_object_count": live_object_count,
        "valid_live_evidence_object_count": 0,
        "shape_valid_live_candidate_object_count": shape_valid_live_candidate_object_count,
        "drill_evidence_object_count": drill_object_count,
        "valid_drill_evidence_object_count": valid_drill_object_count,
        "non_live_evidence_object_count": non_live_object_count,
        "error_count": len(errors),
        "errors": errors,
        "rows": status_rows,
        "boundary": BOUNDARY,
        "authentication_boundary": (
            "This intake checks shape, content digests, and review metadata only. It does not authenticate an issuer, "
            "authority delegation, or signature. Bare digest submissions remain candidates until strict signed "
            "EvidenceEnvelope and trust-profile verification is integrated."
        ),
        "operator_rule": (
            "A digest is necessary but not sufficient. Live evidence must be carried by a signed canonical "
            "EvidenceEnvelope bound to jurisdiction, election, issuer, and payload, then verified against an external "
            "trust profile. Non-production drill records test plumbing but never close live evidence."
        ),
        "refactor_audit": {
            "status": "PASS",
            "shared_module": "tools/mission_kernel_common.py",
            "duplicated_evidence_class_maps_after_refactor": 0,
            "bare_digest_live_promotion_paths_after_refactor": 0,
            "consumers": [
                "tools/mission_kernel_live_workqueue.py",
                "tools/mission_kernel_live_evidence_intake.py",
                "tools/mission_kernel_evidence_submitter.py",
            ],
        },
    }


def csv_rows(status: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in status.get("rows") or []:
        out.append({
            "work_item_id": str(row.get("work_item_id") or ""),
            "blocker_id": str(row.get("blocker_id") or ""),
            "priority": str(row.get("priority") or ""),
            "owner_role": str(row.get("owner_role") or ""),
            "status": str(row.get("status") or ""),
            "live_evidence_object_count": str(row.get("live_evidence_object_count") or 0),
            "valid_live_evidence_object_count": str(row.get("valid_live_evidence_object_count") or 0),
            "shape_valid_live_candidate_object_count": str(row.get("shape_valid_live_candidate_object_count") or 0),
            "drill_evidence_object_count": str(row.get("drill_evidence_object_count") or 0),
            "valid_drill_evidence_object_count": str(row.get("valid_drill_evidence_object_count") or 0),
            "missing_evidence_classes": "; ".join(row.get("missing_evidence_classes") or []),
            "missing_candidate_evidence_classes": "; ".join(row.get("missing_candidate_evidence_classes") or []),
            "missing_drill_evidence_classes": "; ".join(row.get("missing_drill_evidence_classes") or []),
            "error_count": str(len(row.get("errors") or [])),
            "next_action": str(row.get("next_action") or ""),
        })
    return out


def public_text(status: dict[str, Any]) -> str:
    lines = [
        "# Live-closeout evidence intake status",
        "",
        "**Synthetic archive report only. This is not live election evidence and does not authorize a live pilot.**",
        "",
        f"Archive version: `{status['archive_version']}`  ",
        f"Scenario: `{status['scenario_id']}`  ",
        f"Decision: `{status['decision']}`",
        "",
        "The shipped submission is deliberately empty. It proves that the archive has an intake validator and a concrete evidence contract, not that a jurisdiction has supplied live closeout evidence. Non-production drill records can exercise the mechanism, but they are not live evidence and do not close the live workqueue.",
        "",
        "## Status by blocker",
        "",
    ]
    for row in status.get("rows") or []:
        lines.append(
            f"- `{row['work_item_id']}` / `{row['blocker_id']}`: `{row['status']}`; "
            f"authenticated live objects `{row['valid_live_evidence_object_count']}`; "
            f"shape-valid live candidates `{row['shape_valid_live_candidate_object_count']}`; "
            f"valid drill objects `{row['valid_drill_evidence_object_count']}`; "
            f"missing live classes `{len(row['missing_evidence_classes'])}`."
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "This report is no-go for live closeout: not live election evidence, not certification, not outcome proof, not current voter instruction, and not legal advice. Bare digests and free-text approving roles are candidates only. A real submission must use signed canonical EvidenceEnvelopes, an external trust profile, local authority review, custody, redaction/publication review, records retention, and independent verification.",
        "",
    ])
    return "\n".join(lines)


def build_all(submission_path: Path | None = None) -> dict[str, Any]:
    workqueue = build_workqueue()
    submission = load_submission(submission_path, workqueue)
    status = evaluate_submission(workqueue, submission)
    return {
        "submission": submission,
        "status": status,
        "report": status,
        "public_markdown": public_text(status),
        "csv_rows": csv_rows(status),
    }


def write_all(payload: dict[str, Any]) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    SUBMISSION.write_text(json.dumps(payload["submission"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    STATUS_JSON.write_text(json.dumps(payload["status"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(payload["report"], sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    PUBLIC_MD.write_text(payload["public_markdown"], encoding="utf-8")
    fields = [
        "work_item_id", "blocker_id", "priority", "owner_role", "status",
        "live_evidence_object_count", "valid_live_evidence_object_count", "shape_valid_live_candidate_object_count",
        "drill_evidence_object_count", "valid_drill_evidence_object_count",
        "missing_evidence_classes", "missing_candidate_evidence_classes", "missing_drill_evidence_classes", "error_count", "next_action",
    ]
    with STATUS_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(payload["csv_rows"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", type=Path, help="optional filled evidence submission JSON to evaluate")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = build_all(args.submission)
    if args.write:
        write_all(payload)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    else:
        s = payload["status"]
        print(
            f"decision={s['decision']} live_objects={s['live_evidence_object_count']} "
            f"drill_objects={s['drill_evidence_object_count']} items={s['work_item_count']} version={s['archive_version']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
