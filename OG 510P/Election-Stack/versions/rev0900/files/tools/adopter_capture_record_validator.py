#!/usr/bin/env python3
"""Validate adopter source-authority capture records.

This is the practical promotion firewall after the state/local quarantine:
- the capture matrix says what evidence is required;
- this validator checks the shape of capture records before any quarantined
  source can be considered for public-answer promotion.

The shipped archive remains synthetic-only.  Even a shape-valid fixture must not
set ``promotion_allowed=true`` inside this archive.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
RELEASE_DATE = release_date(ROOT)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
DEFAULT_FIXTURE_DIR = ROOT / "artifacts" / "examples" / "adopter_authority_capture_records"
REPORT = ROOT / "artifacts" / "reports" / "adopter-capture-record-validation-report.json"

REQUIRED_EVIDENCE = {
    "adopter_capture_id",
    "captured_at_utc",
    "captured_by_role",
    "source_url_or_official_channel_id",
    "byte_or_text_sha256",
    "responsible_office",
    "public_help_route",
    "jurisdiction_scope",
    "election_scope_or_effective_date",
    "conflict_check_status",
    "human_approver_role",
    "approved_at_utc",
}
REQUIRED_RECORD_FIELDS = REQUIRED_EVIDENCE | {
    "record_id",
    "source_id",
    "public_answer_surface_id",
    "promotion_requested",
    "promotion_allowed",
    "synthetic_fixture",
    "non_claims",
}
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
GLOBAL_SCOPE_RE = re.compile(r"\b(all|any|nationwide|national|statewide|cross[- ]?jurisdiction|every)\b", re.I)
VALID_CONFLICT_STATUSES = {"checked_no_conflict", "checked_conflict_resolved"}

ERROR_MESSAGES = {
    "MISSING_REQUIRED_FIELD": "record is missing a required field",
    "UNKNOWN_SOURCE_ID": "source_id does not exist in external-sources lockfile",
    "SOURCE_NOT_QUARANTINED": "source_id is not a quarantined state/local xref row",
    "INVALID_SHA256": "byte_or_text_sha256 must be a lowercase 64-hex digest",
    "INVALID_CAPTURE_TIME": "captured_at_utc must be UTC ISO seconds ending in Z",
    "INVALID_APPROVAL_TIME": "approved_at_utc must be UTC ISO seconds ending in Z",
    "APPROVAL_BEFORE_CAPTURE": "approved_at_utc must be at or after captured_at_utc",
    "GLOBAL_OR_AMBIGUOUS_SCOPE": "jurisdiction_scope must not be global/cross-jurisdictional",
    "MISSING_PUBLIC_HELP_ROUTE": "public_help_route must name a human help route or official contact path",
    "MISSING_RESPONSIBLE_OFFICE": "responsible_office must name the responsible election office",
    "INVALID_CONFLICT_STATUS": "conflict_check_status must show conflict review closure",
    "MISSING_HUMAN_APPROVER": "human_approver_role must name a human approving role",
    "SYNTHETIC_PROMOTION_ALLOWED": "synthetic archive records must not set promotion_allowed=true",
    "SYNTHETIC_PROMOTION_REQUESTED": "synthetic archive records must not request public-answer promotion",
    "REQUESTED_WITHOUT_VALID_EVIDENCE": "promotion_requested=true requires all evidence-shape checks to pass",
    "NON_CLAIMS_BOUNDARY_MISSING": "non_claims must say not current voter instruction and not legal advice",
    "FIXTURE_EXPECTATION_MISMATCH": "negative/positive fixture did not produce expected validation result",
}


def load_sources() -> dict[str, dict[str, Any]]:
    with LOCK.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return {str(r.get("id") or ""): r for r in rows if isinstance(r, dict) and str(r.get("id") or "")}


def tags_of(row: dict[str, Any]) -> set[str]:
    return {str(t).strip() for t in (row.get("tags") or []) if str(t).strip()}


def is_quarantined(row: dict[str, Any]) -> bool:
    tags = tags_of(row)
    return {"jurisdiction_quarantine", "not_current_voter_instruction"} <= tags and not str(row.get("sha256") or "").strip()


def parse_utc(raw: Any) -> dt.datetime | None:
    s = str(raw or "")
    if not UTC_RE.fullmatch(s):
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate_record(record: dict[str, Any], sources: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for field in sorted(REQUIRED_RECORD_FIELDS):
        if field not in record or str(record.get(field) if record.get(field) is not None else "").strip() == "":
            errors.append("MISSING_REQUIRED_FIELD")

    sid = str(record.get("source_id") or "").strip()
    src = sources.get(sid)
    if not src:
        errors.append("UNKNOWN_SOURCE_ID")
    elif not is_quarantined(src):
        errors.append("SOURCE_NOT_QUARANTINED")

    if not HEX64_RE.fullmatch(str(record.get("byte_or_text_sha256") or "")):
        errors.append("INVALID_SHA256")

    captured = parse_utc(record.get("captured_at_utc"))
    approved = parse_utc(record.get("approved_at_utc"))
    if captured is None:
        errors.append("INVALID_CAPTURE_TIME")
    if approved is None:
        errors.append("INVALID_APPROVAL_TIME")
    if captured is not None and approved is not None and approved < captured:
        errors.append("APPROVAL_BEFORE_CAPTURE")

    scope = str(record.get("jurisdiction_scope") or "").strip()
    if not scope or GLOBAL_SCOPE_RE.search(scope):
        errors.append("GLOBAL_OR_AMBIGUOUS_SCOPE")
    if len(str(record.get("public_help_route") or "").strip()) < 8:
        errors.append("MISSING_PUBLIC_HELP_ROUTE")
    if len(str(record.get("responsible_office") or "").strip()) < 6:
        errors.append("MISSING_RESPONSIBLE_OFFICE")
    if str(record.get("conflict_check_status") or "").strip() not in VALID_CONFLICT_STATUSES:
        errors.append("INVALID_CONFLICT_STATUS")
    if len(str(record.get("human_approver_role") or "").strip()) < 6:
        errors.append("MISSING_HUMAN_APPROVER")

    non_claims = str(record.get("non_claims") or "").lower()
    if "not current voter instruction" not in non_claims or "not legal advice" not in non_claims:
        errors.append("NON_CLAIMS_BOUNDARY_MISSING")

    if record.get("promotion_allowed") is True:
        errors.append("SYNTHETIC_PROMOTION_ALLOWED")
    if record.get("synthetic_fixture") is True and record.get("promotion_requested") is True:
        errors.append("SYNTHETIC_PROMOTION_REQUESTED")

    evidence_errors = [e for e in errors if e not in {"SYNTHETIC_PROMOTION_ALLOWED", "SYNTHETIC_PROMOTION_REQUESTED", "FIXTURE_EXPECTATION_MISMATCH"}]
    if record.get("promotion_requested") is True and evidence_errors:
        errors.append("REQUESTED_WITHOUT_VALID_EVIDENCE")

    # stable unique order
    return sorted(set(errors))


def record_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iter_records(records_dir: Path) -> list[Path]:
    if not records_dir.exists():
        return []
    return sorted(p for p in records_dir.rglob("*.json") if p.is_file())


def classify_expected(record: dict[str, Any]) -> tuple[bool | None, set[str]]:
    expected_valid = record.get("expected_valid")
    if isinstance(expected_valid, bool):
        raw_codes = record.get("expected_error_codes") or []
        return expected_valid, {str(c) for c in raw_codes}
    return None, set()


def build_report(records_dir: Path = DEFAULT_FIXTURE_DIR) -> dict[str, Any]:
    sources = load_sources()
    quarantined_count = sum(1 for row in sources.values() if is_quarantined(row))
    rows: list[dict[str, Any]] = []
    expectation_failures = 0
    for path in iter_records(records_dir):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({
                "path": path.relative_to(ROOT).as_posix(),
                "record_id": "",
                "source_id": "",
                "valid": False,
                "error_codes": ["JSON_PARSE_ERROR"],
                "error_messages": {"JSON_PARSE_ERROR": str(exc)},
                "expected_valid": None,
                "expectation_passed": False,
                "sha256": record_digest(path),
            })
            expectation_failures += 1
            continue
        if not isinstance(record, dict):
            record = {"_raw_non_object": record}
        errors = validate_record(record, sources)
        valid = not errors
        expected_valid, expected_codes = classify_expected(record)
        expectation_passed = True
        if expected_valid is not None:
            if expected_valid != valid:
                expectation_passed = False
            if expected_codes and not expected_codes <= set(errors):
                expectation_passed = False
        if not expectation_passed:
            expectation_failures += 1
        rows.append({
            "path": path.relative_to(ROOT).as_posix(),
            "record_id": str(record.get("record_id") or ""),
            "source_id": str(record.get("source_id") or ""),
            "synthetic_fixture": bool(record.get("synthetic_fixture")),
            "promotion_requested": bool(record.get("promotion_requested")),
            "promotion_allowed": bool(record.get("promotion_allowed")),
            "valid": valid,
            "error_codes": errors,
            "error_messages": {code: ERROR_MESSAGES.get(code, code) for code in errors},
            "expected_valid": expected_valid,
            "expected_error_codes": sorted(expected_codes),
            "expectation_passed": expectation_passed,
            "sha256": record_digest(path),
        })
    positive = [r for r in rows if r.get("expected_valid") is True]
    negative = [r for r in rows if r.get("expected_valid") is False]
    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "synthetic_only": True,
        "records_dir": records_dir.relative_to(ROOT).as_posix() if records_dir.is_relative_to(ROOT) else str(records_dir),
        "record_count": len(rows),
        "shape_valid_record_count": sum(1 for r in rows if r["valid"]),
        "promotion_allowed_count": sum(1 for r in rows if r["promotion_allowed"]),
        "valid_promotion_allowed_count": sum(1 for r in rows if r["valid"] and r["promotion_allowed"]),
        "promotion_requested_count": sum(1 for r in rows if r["promotion_requested"]),
        "valid_promotion_requested_count": sum(1 for r in rows if r["valid"] and r["promotion_requested"]),
        "negative_fixture_count": len(negative),
        "positive_fixture_count": len(positive),
        "expectation_failure_count": expectation_failures,
        "quarantined_source_count": quarantined_count,
        "required_evidence": sorted(REQUIRED_EVIDENCE),
        "boundary": "Capture-record validation checks evidence shape only; it is not current voter instruction, not legal advice, not source-byte cache completeness, not public-release authorization, and not live-pilot approval.",
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records-dir", default=str(DEFAULT_FIXTURE_DIR), help="Directory containing adopter capture record JSON files")
    ap.add_argument("--write", action="store_true", help="Write the deterministic validation report")
    ap.add_argument("--json", action="store_true", help="Print validation report JSON")
    args = ap.parse_args()
    report = build_report(Path(args.records_dir))
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if int(report["expectation_failure_count"]) == 0 and int(report["valid_promotion_allowed_count"]) == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
