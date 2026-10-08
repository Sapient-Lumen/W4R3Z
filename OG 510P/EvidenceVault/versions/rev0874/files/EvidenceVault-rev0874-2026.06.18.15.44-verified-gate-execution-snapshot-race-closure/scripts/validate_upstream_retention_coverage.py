#!/usr/bin/env python3
"""Validate shipped upstream-retention coverage boundary surfaces."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_upstream_retention_coverage import build, render_markdown  # noqa: E402

AMBIGUOUS_PRESENT_RE = re.compile(r"^- Present in `sources/`: \*\*\d+\*\*$", re.MULTILINE)


def fail(msg: str) -> None:
    print(f"upstream-retention-coverage-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    expected = build(ROOT)
    json_path = ROOT / "AUDIT" / "UPSTREAM_RETENTION_COVERAGE.json"
    md_path = ROOT / "AUDIT" / "UPSTREAM_RETENTION_COVERAGE.md"
    report_path = ROOT / "AUDIT" / "UPSTREAM_DIFF_REPORT.md"
    if not json_path.is_file():
        fail("missing AUDIT/UPSTREAM_RETENTION_COVERAGE.json")
    if not md_path.is_file():
        fail("missing AUDIT/UPSTREAM_RETENTION_COVERAGE.md")
    try:
        actual = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in AUDIT/UPSTREAM_RETENTION_COVERAGE.json: {exc}")
    if actual != expected:
        fail("AUDIT/UPSTREAM_RETENTION_COVERAGE.json does not exactly match current SOURCE_INDEX/report/filesystem boundary")
    expected_md = render_markdown(expected)
    actual_md = md_path.read_text(encoding="utf-8")
    if actual_md != expected_md:
        fail("AUDIT/UPSTREAM_RETENTION_COVERAGE.md does not exactly mirror JSON boundary output")
    report = report_path.read_text(encoding="utf-8")
    if AMBIGUOUS_PRESENT_RE.search(report):
        fail("AUDIT/UPSTREAM_DIFF_REPORT.md contains ambiguous 'Present in `sources/`' claim; qualify it as historical/audit-workspace or use the retention coverage surface")
    drift_projects = expected["summary"]["projects_with_retention_drift"]
    print(
        "upstream-retention-coverage-validate: OK "
        f"({expected['summary']['projects_checked']} projects, "
        f"{len(drift_projects)} drift projects explicitly surfaced)"
    )


if __name__ == "__main__":
    main()
