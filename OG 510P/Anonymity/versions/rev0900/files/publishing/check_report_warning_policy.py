#!/usr/bin/env python3
"""Fail closed when a passing machine report carries warning debt.

A status=pass report should not hide operator-relevant findings in a warning
array.  When a checker wants to allow a non-failing condition, it should encode
that condition explicitly in summary fields with a policy explanation rather
than emitting top-level warnings.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

ALLOWED_POSITIVE_WARNING_COUNT_FIELDS = {
    "reports/queue_compile_smoke.json": {
        "summary.unresolved_warning_hits_total",
        "summary.rerun_warning_hits_total",
    }
}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def count_top_level_warnings(data: dict[str, Any]) -> int:
    warnings = data.get("warnings", [])
    if isinstance(warnings, list):
        return len(warnings)
    if warnings:
        return 1
    return 0


def numeric_warning_counts(data: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for container_name in ["", "summary"]:
        container = data if not container_name else data.get(container_name, {})
        if not isinstance(container, dict):
            continue
        for key, value in container.items():
            if "warning" in str(key).lower() and "warnings_are" not in str(key).lower():
                if isinstance(value, int):
                    counts[(container_name + "." if container_name else "") + str(key)] = value
    return counts


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for path in sorted((root / "reports").glob("*.json"), key=lambda p: p.name):
        rel = path.relative_to(root).as_posix()
        data = load_json(path)
        self_report_previous_copy = rel == "reports/report_warning_policy.json"
        warning_array_count = 0 if self_report_previous_copy else (count_top_level_warnings(data) if isinstance(data, dict) else 0)
        warning_counts = {} if self_report_previous_copy else (numeric_warning_counts(data) if isinstance(data, dict) else {})
        allowed_positive = ALLOWED_POSITIVE_WARNING_COUNT_FIELDS.get(rel, set())
        positive_counts = {key: value for key, value in warning_counts.items() if value > 0 and key not in allowed_positive}
        status = "pass" if warning_array_count == 0 and not positive_counts else "fail"
        row = {
            "path": rel,
            "status": status,
            "report_status": data.get("status") if isinstance(data, dict) else "non_object",
            "top_level_warning_count": warning_array_count,
            "positive_warning_counts": positive_counts,
            "allowed_positive_warning_counts": {key: value for key, value in warning_counts.items() if value > 0 and key in allowed_positive},
            "self_report_previous_copy_ignored": self_report_previous_copy,
        }
        rows.append(row)
        if status != "pass":
            failures.append(row)

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "warning_policy": {
            "passing_reports_must_have_zero_top_level_warnings": True,
            "positive_warning_count_fields_are_failures": True,
            "allowed_positive_warning_count_fields": {key: sorted(value) for key, value in ALLOWED_POSITIVE_WARNING_COUNT_FIELDS.items()},
            "allowed_warning_count": 0,
            "self_report_previous_copy_ignored": True,
        },
        "rows": rows,
        "failures": failures[:100],
        "summary": {
            "checks_failed": len(failures),
            "report_json_count": len(rows),
            "reports_with_warnings": len(failures),
            "total_top_level_warning_count": sum(row["top_level_warning_count"] for row in rows),
            "positive_warning_count_field_count": sum(len(row["positive_warning_counts"]) for row in rows),
        },
        "fail_closed_rule": "If any report carries non-zero warning debt, default to no publication and either repair the condition or make the policy explicit without warnings. The previous on-disk copy of this self-report is ignored to avoid a fixed-point trap.",
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
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
