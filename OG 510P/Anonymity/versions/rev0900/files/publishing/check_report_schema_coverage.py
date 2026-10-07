#!/usr/bin/env python3
"""Ensure every reports/*.json file is visible to surface schema validation."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    schema_report_path = root / "reports" / "surface_schema_validation.json"
    failures: list[dict[str, Any]] = []
    schema_report: dict[str, Any] = {}

    if not schema_report_path.exists():
        failures.append({"category": "surface_schema_validation_report_missing", "path": "reports/surface_schema_validation.json"})
    else:
        schema_report = load_json(schema_report_path)
        if schema_report.get("status") != "pass":
            failures.append({"category": "surface_schema_validation_not_pass", "status": schema_report.get("status")})

    report_paths = sorted(p.relative_to(root).as_posix() for p in (root / "reports").glob("*.json"))
    schema_checks = schema_report.get("checks", []) if isinstance(schema_report.get("checks", []), list) else []
    checked = {str(row.get("target")): row for row in schema_checks if isinstance(row, dict) and row.get("target")}
    missing_reports = sorted(set(report_paths) - set(checked))
    failed_report_targets = sorted(
        str(row.get("target"))
        for row in schema_checks
        if isinstance(row, dict) and str(row.get("target", "")).startswith("reports/") and row.get("status") != "pass"
    )
    generic_report_targets = sorted(
        str(row.get("target"))
        for row in schema_checks
        if isinstance(row, dict) and str(row.get("target", "")).startswith("reports/") and row.get("schema") == "schemas/generic_report.schema.json"
    )
    explicit_report_targets = sorted(
        str(row.get("target"))
        for row in schema_checks
        if isinstance(row, dict) and str(row.get("target", "")).startswith("reports/") and row.get("schema") != "schemas/generic_report.schema.json"
    )

    if missing_reports:
        failures.append({"category": "report_json_missing_schema_validation", "paths": missing_reports[:50], "count": len(missing_reports)})
    if failed_report_targets:
        failures.append({"category": "report_json_schema_validation_failed", "paths": failed_report_targets[:50], "count": len(failed_report_targets)})

    summary = {
        "checks_failed": len(failures),
        "report_json_count": len(report_paths),
        "schema_report_checked_target_count": schema_report.get("checked_targets", 0),
        "report_json_schema_checked_count": len([p for p in report_paths if p in checked]),
        "explicit_report_schema_count": len(explicit_report_targets),
        "generic_report_schema_count": len(generic_report_targets),
        "missing_report_schema_count": len(missing_reports),
        "failed_report_schema_count": len(failed_report_targets),
        "all_report_json_schema_checked": not missing_reports and not failed_report_targets,
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "schema_validation_report": "reports/surface_schema_validation.json",
        "generic_report_schema": "schemas/generic_report.schema.json",
        "explicit_report_targets": explicit_report_targets,
        "generic_report_targets": generic_report_targets,
        "failures": failures[:50],
        "summary": summary,
        "fail_closed_rule": "If any reports/*.json file is absent from schema validation, default to no publication and add an explicit or generic schema binding.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
