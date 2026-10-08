#!/usr/bin/env python3
"""Compute a conservative rule-implementation progress estimate from the ledger.

This is deliberately humble. It does not claim the official Comprehensive Rules have
N equal-sized pieces; it gives both a coarse ledger percentage and a tiny conservative
full-rules proxy so each revision can track direction without overclaiming.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from collections import Counter
from typing import Any

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "rules" / "coverage" / "rules_ledger.json"
REPORT_DIR = ROOT / "reports" / "rules"

# These weights are for MTGSim's own ledger rows, not the official CR. They express
# how executable each tracked row is today.
LEDGER_WEIGHTS = {
    "inventory": 0.00,
    "roadmap": 0.00,
    "design": 0.05,
    "scaffold": 0.20,
    "implemented": 0.70,
    "tested": 1.00,
}

# A rough denominator for "complete game-engine rule units". We intentionally choose
# a large denominator because Magic's official numbered rules plus object/card-specific
# interactions are much more granular than our current top-level ledger buckets.
DEFAULT_FULL_RULE_UNIT_PROXY = 2500.0


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def append_jsonl(path: pathlib.Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def compute_progress(ledger_path: pathlib.Path = LEDGER, full_rule_unit_proxy: float = DEFAULT_FULL_RULE_UNIT_PROXY) -> dict[str, Any]:
    started = time.perf_counter()
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    rules = ledger.get("rules", [])
    status_counts: Counter[str] = Counter(str(row.get("status", "")) for row in rules)
    weighted_units = sum(LEDGER_WEIGHTS.get(str(row.get("status", "")), 0.0) for row in rules)
    total_rows = len(rules)
    ledger_weighted_pct = (weighted_units / total_rows * 100.0) if total_rows else 0.0
    full_rules_conservative_pct = min(100.0, weighted_units / max(full_rule_unit_proxy, 1.0) * 100.0)

    executable_rows = sum(status_counts[s] for s in ("scaffold", "implemented", "tested"))
    tested_rows = status_counts["tested"]
    tests_linked = sum(len(row.get("tests", [])) for row in rules)

    report = {
        "schema": "mtgsim.rules_progress.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "duration_sec": time.perf_counter() - started,
        "ledger": rel(ledger_path),
        "ledger_revision": ledger.get("revision"),
        "source_effective_date": ledger.get("source_effective_date"),
        "method": {
            "ledger_weights": LEDGER_WEIGHTS,
            "full_rule_unit_proxy": full_rule_unit_proxy,
            "warning": "Full-rules percentage is a conservative proxy for trend tracking, not a formal proof of Comprehensive Rules coverage.",
        },
        "summary": {
            "total_rows": total_rows,
            "status_counts": dict(sorted(status_counts.items())),
            "executable_rows": executable_rows,
            "tested_rows": tested_rows,
            "tests_linked": tests_linked,
            "weighted_units": round(weighted_units, 3),
            "ledger_weighted_pct": round(ledger_weighted_pct, 3),
            "full_rules_conservative_pct": round(full_rules_conservative_pct, 3),
        },
    }
    return report


def record_sqlite(report: dict[str, Any], report_path: pathlib.Path) -> None:
    try:
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        import metrics_db  # type: ignore
        metrics_db.record_rules_progress(report, report_path)
    except Exception as exc:  # pragma: no cover
        print(f"warning: unable to record rules progress in sqlite: {exc}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=pathlib.Path, default=LEDGER)
    parser.add_argument("--full-rule-unit-proxy", type=float, default=DEFAULT_FULL_RULE_UNIT_PROXY)
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_DIR / "rules_progress_latest.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = compute_progress(args.ledger, args.full_rule_unit_proxy)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(REPORT_DIR / "rules_progress_history.jsonl", report)
    record_sqlite(report, args.report)

    summary = report["summary"]
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "rules progress: "
            f"full_rules_conservative={summary['full_rules_conservative_pct']:.3f}% "
            f"ledger_weighted={summary['ledger_weighted_pct']:.3f}% "
            f"tested_rows={summary['tested_rows']}/{summary['total_rows']} "
            f"report={args.report.relative_to(ROOT)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
