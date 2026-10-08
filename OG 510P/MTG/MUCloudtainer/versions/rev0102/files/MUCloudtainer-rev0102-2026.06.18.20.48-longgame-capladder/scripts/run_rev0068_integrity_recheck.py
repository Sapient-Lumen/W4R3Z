#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.response_matrix import (
    CLOSURE_THREAT_AXIS,
    PRESSURE_THREAT_AXIS,
    SURGE_THREAT_AXIS,
    compare_response_matrix_by_life,
)


def main() -> None:
    source = ROOT / "data/rev0067_response_matrix_cumulative_arm_summary.csv"
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    comparisons = compare_response_matrix_by_life(rows)
    observed = {
        (str(row["size_axis"]), str(row["threat_policy_axis"]), int(row["starting_life"]))
        for row in rows
    }
    expected = {
        (size, threat, life)
        for size in ("counter40_vs_threat40", "counter60_vs_threat40", "counter60_vs_threat60")
        for threat in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS, SURGE_THREAT_AXIS)
        for life in (20, 40)
    }
    incomplete = [row for row in comparisons if row["provisional_read"] == "incomplete_matrix"]
    payload = {
        "revision": "rev0068",
        "source": source.relative_to(ROOT).as_posix(),
        "expected_cells": len(expected),
        "observed_cells": len(observed & expected),
        "missing_cells": sorted(expected - observed),
        "unexpected_cells": sorted(observed - expected),
        "comparison_cells": len(comparisons),
        "incomplete_comparison_cells": len(incomplete),
        "passed": observed == expected and not incomplete,
        "comparisons": comparisons,
        "note": "This is an integrity recheck of shipped rev0067 aggregates, not a new inference or game run.",
    }
    output = ROOT / "data/rev0068_response_matrix_integrity_recheck.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
