#!/usr/bin/env python3
"""Ensure current-release pre-pilot evidence ledgers are not stale.

Historical rows may remain, but every release that claims pilot readiness must
carry current-version placeholder/status rows for ledgers that would otherwise be
mistaken for live evidence.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REG = ROOT / "artifacts" / "registries"

REQUIREMENTS = [
    ("drill-runs.csv", "archive_version", "status", {"pre_pilot_empty"}),
    ("external-review-log.csv", "archive_version", "surface", {"pre-pilot surface inventory", "pre-pilot output pack inventory"}),
    ("mapt-evaluations.csv", "archive_version", "result", {"not_run"}),
    ("witness-health-log.csv", "archive_version", "liveness_score", {"not_measured"}),
    ("adopter-path-smoke-tests.csv", "archive_version", "result", {"synthetic_pass", "manual_pass"}),
    ("pilot-data-ledger.csv", "archive_version", "status", {"pre_pilot_empty"}),
    ("pilot-data-ledger.csv", "archive_version", "status", {"synthetic_smoke_harness"}),
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def main() -> int:
    errors: list[str] = []
    for filename, version_col, status_col, allowed_statuses in REQUIREMENTS:
        path = REG / filename
        if not path.exists():
            errors.append(f"missing registry: artifacts/registries/{filename}")
            continue
        try:
            rows = read_rows(path)
        except Exception as exc:
            errors.append(f"cannot read {filename}: {exc}")
            continue
        current = [r for r in rows if r.get(version_col) == VERSION]
        if not current:
            errors.append(f"{filename} has no row for current VERSION {VERSION}")
            continue
        if not any((r.get(status_col) in allowed_statuses) for r in current):
            errors.append(
                f"{filename} has {VERSION} row(s) but none with {status_col} in {sorted(allowed_statuses)}"
            )
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: current-version pre-pilot ledgers ({VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
