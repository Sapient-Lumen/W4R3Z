#!/usr/bin/env python3
"""Check the adopter capture-record validator and fixtures.

This gate makes the rev0869 capture matrix actionable: evidence records now have
a machine-checkable shape, negative fixtures must fail for the expected reason,
and no shipped shape-valid record may authorize public guidance in this synthetic
archive.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
TOOL = ROOT / "tools" / "adopter_capture_record_validator.py"
REPORT = ROOT / "artifacts" / "reports" / "adopter-capture-record-validation-report.json"
FIXTURES = ROOT / "artifacts" / "examples" / "adopter_authority_capture_records"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    if not TOOL.exists():
        errors.append("missing tools/adopter_capture_record_validator.py")
    if not FIXTURES.exists():
        errors.append("missing adopter capture-record fixture directory")
    if not REPORT.exists():
        errors.append("missing adopter-capture-record-validation-report.json")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    proc = subprocess.run(
        [sys.executable, str(TOOL), "--json"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print("ERROR: adopter_capture_record_validator.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return 2
    generated = json.loads(proc.stdout)
    shipped = load_json(REPORT)
    if generated != shipped:
        errors.append("adopter-capture-record-validation-report.json is stale; run tools/adopter_capture_record_validator.py --write")

    if shipped.get("archive_version") != VERSION:
        errors.append("capture-record validation report archive_version does not match VERSION")
    if shipped.get("synthetic_only") is not True:
        errors.append("capture-record validation report must carry synthetic_only=true")
    if int(shipped.get("record_count") or 0) < 6:
        errors.append("expected at least six validator fixtures")
    if int(shipped.get("positive_fixture_count") or 0) < 1:
        errors.append("expected at least one shape-valid non-promoting fixture")
    if int(shipped.get("negative_fixture_count") or 0) < 5:
        errors.append("expected at least five negative capture-record fixtures")
    if int(shipped.get("expectation_failure_count", -1)) != 0:
        errors.append("fixture expectation failures must be zero")
    if int(shipped.get("valid_promotion_allowed_count") or 0) != 0:
        errors.append("no shape-valid shipped capture record may set promotion_allowed=true")
    if int(shipped.get("valid_promotion_requested_count") or 0) != 0:
        errors.append("no shape-valid shipped capture record may request promotion in the synthetic archive")
    if "not current voter instruction" not in str(shipped.get("boundary") or "").lower():
        errors.append("capture-record validation boundary must say not current voter instruction")

    rows = shipped.get("rows") or []
    for row in rows:
        if not isinstance(row, dict):
            errors.append("capture validation row is not an object")
            continue
        path = str(row.get("path") or "")
        if not path.startswith("artifacts/examples/adopter_authority_capture_records/"):
            errors.append(f"unexpected capture record path outside fixture tree: {path}")
        if row.get("expectation_passed") is not True:
            errors.append(f"fixture expectation failed: {path}")
        if row.get("valid") is True and row.get("promotion_allowed") is True:
            errors.append(f"shape-valid fixture must not allow promotion: {path}")
        if row.get("valid") is True and row.get("promotion_requested") is True:
            errors.append(f"shape-valid fixture must not request promotion: {path}")
        if row.get("expected_valid") is False and not row.get("error_codes"):
            errors.append(f"negative fixture has no error_codes: {path}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(
        "PASS: adopter capture-record validator "
        f"({VERSION}, fixtures={shipped['record_count']}, negative={shipped['negative_fixture_count']}, "
        f"valid_promotions={shipped['valid_promotion_allowed_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
