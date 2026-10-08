#!/usr/bin/env python3
"""Drift firewall for CSV registries and tables.

Checks all release-scope CSV files under artifacts/ for:
- stable row width (no silent comma-split corruption)
- duplicate primary IDs for common ID columns

This intentionally does not validate domain semantics. It catches the class of
registry damage that makes later proof, risk, and release ledgers unreliable.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"

PRIMARY_ID_COLUMNS = {
    "ID",
    "id",
    "ClaimID",
    "HazardID",
    "ProofObligationID",
    "issue_id",
    "run_id",
    "session_id",
    "eval_id",
    "promotion_id",
    "ttr_eval_id",
    "record_id",
    "ledger_id",
    "control_id",
    "jurisdiction_id",
    "catastrophe_class_id",
}


def primary_column(header: list[str]) -> str | None:
    for h in header:
        if h in PRIMARY_ID_COLUMNS:
            return h
    for h in header:
        if h.lower().endswith("_id") and h not in {"kind"}:
            return h
    return None


def main() -> int:
    failures: list[str] = []
    for path in sorted(ARTIFACTS.rglob("*.csv")):
        rel = path.relative_to(ROOT)
        try:
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
        except Exception as e:
            failures.append(f"{rel}: CSV parse failed: {e}")
            continue
        if not rows:
            failures.append(f"{rel}: empty CSV")
            continue
        header = rows[0]
        width = len(header)
        if width == 0:
            failures.append(f"{rel}: empty header")
            continue
        for line_no, row in enumerate(rows[1:], start=2):
            if len(row) != width:
                failures.append(f"{rel}:{line_no}: row has {len(row)} columns; header has {width}")
        pc = primary_column(header)
        if not pc:
            continue
        try:
            with path.open("r", encoding="utf-8", newline="") as f:
                drows = list(csv.DictReader(f))
        except Exception:
            continue
        seen: dict[str, int] = {}
        duplicates: defaultdict[str, list[int]] = defaultdict(list)
        for line_no, row in enumerate(drows, start=2):
            value = (row.get(pc) or "").strip()
            if not value:
                failures.append(f"{rel}:{line_no}: empty primary id column {pc}")
                continue
            if value in seen:
                duplicates[value].append(line_no)
            else:
                seen[value] = line_no
        for value, lines in sorted(duplicates.items()):
            failures.append(f"{rel}: duplicate {pc}={value!r} at lines {seen[value]} and {', '.join(map(str, lines))}")

    if failures:
        for failure in failures:
            print("ERROR:", failure, file=sys.stderr)
        return 2
    print("PASS: CSV registry/table integrity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
