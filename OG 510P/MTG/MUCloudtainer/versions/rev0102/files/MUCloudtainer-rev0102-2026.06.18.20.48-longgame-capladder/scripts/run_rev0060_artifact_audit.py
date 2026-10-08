#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0060"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/trajectory_forensics.py",
    "src/muc5/agents.py",
    "src/muc5/cpp_rollout.py",
    "tests/test_rev0060_trajectory_forensics.py",
    "scripts/run_rev0060_life20_forensics.py",
    "scripts/run_rev0060_artifact_audit.py",
    "docs/life20_forensics_rev0060.md",
    "docs/refactor_audit_rev0060.md",
    "docs/simulator_rev0060.md",
    "data/rev0060_life20_forensics_summary.json",
    "data/rev0060_life20_forensics_games.csv",
    "data/rev0060_life20_forensics_arm_summary.csv",
    "data/rev0060_life20_forensics_arm_result_summary.csv",
    "data/rev0060_life20_forensics_source_arm_summary.csv",
    "data/rev0060_life20_forensics_ab_metric_deltas.csv",
    "data/rev0060_life20_forensics_pilotswap_win_cases.csv",
    "data/rev0060_life20_forensics_failure_cases.csv",
    "data/rev0060_life20_forensics_stdout.txt",
    "data/rev0060_test_report.txt",
    "data/rev0060_smoke.txt",
    "data/rev0060_audit_stdout.txt",
    "data/rev0060_inherited_audit_report.json",
    "data/rev0060_validation_summary.json",
]

MAX_ROWS = {
    "data/rev0060_life20_forensics_games.csv": 200,
    "data/rev0060_life20_forensics_pilotswap_win_cases.csv": 30,
    "data/rev0060_life20_forensics_failure_cases.csv": 40,
}


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=["data/rev0060*_cpp_transitions.csv", "data/rev0060*_transition_rows.csv"],
        max_csv_rows=MAX_ROWS,
    )
    out = DATA / "rev0060_artifact_audit.json"
    out.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
