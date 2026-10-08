from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.readiness import run_rules_scenarios



def main() -> None:
    checks = [c.as_dict() for c in run_rules_scenarios()]
    out_csv = ROOT / "data" / "rev0010_rules_scenarios.csv"
    out_json = ROOT / "data" / "rev0010_rules_scenarios_summary.json"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "passed", "focus", "details_json"])
        writer.writeheader()
        for row in checks:
            writer.writerow({
                "name": row["name"],
                "passed": row["passed"],
                "focus": row["focus"],
                "details_json": json.dumps(row["details"], sort_keys=True),
            })
    summary = {
        "revision": "rev0010",
        "scenario_count": len(checks),
        "passed": sum(1 for c in checks if c["passed"]),
        "failed": sum(1 for c in checks if not c["passed"]),
        "all_passed": all(c["passed"] for c in checks),
        "scenarios": checks,
    }
    out_json.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
