#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0064"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/closure_vs_counter.py",
    "src/muc5/threat_closure.py",
    "tests/test_rev0064_closure_vs_counter.py",
    "scripts/run_rev0064_closure_vs_counter.py",
    "scripts/run_rev0064_artifact_audit.py",
    "docs/closure_vs_counter_audit_rev0064.md",
    "docs/refactor_audit_rev0064.md",
    "docs/simulator_rev0064.md",
    "data/rev0064_closure_vs_counter_summary.json",
    "data/rev0064_closure_vs_counter_games.csv",
    "data/rev0064_closure_vs_counter_aggregate.csv",
    "data/rev0064_closure_vs_counter_arm_summary.csv",
    "data/rev0064_closure_vs_counter_mechanisms.csv",
    "data/rev0064_closure_vs_counter_life_rollup.csv",
    "data/rev0064_closure_vs_counter_comparisons.csv",
    "data/rev0064_closure_vs_counter_cpp_transition_sample.csv",
    "data/rev0064_closure_vs_counter_replay_traces.jsonl",
    "data/rev0064_closure_vs_counter_replay_results.json",
    "data/rev0064_closure_vs_counter_arms.json",
    "data/rev0064_closure_vs_counter_forensics.csv",
    "data/rev0064_closure_vs_counter_forensic_arm_summary.csv",
    "data/rev0064_closure_vs_counter_features.csv",
    "data/rev0064_closure_vs_counter_feature_summary.csv",
    "data/rev0064_closure_vs_counter_feature_comparisons.csv",
    "data/rev0064_closure_vs_counter_legacy_selfdeck_cases.csv",
    "data/rev0064_closure_vs_counter_closure_rescue_cases.csv",
    "data/rev0064_closure_vs_counter_stdout.txt",
    "data/rev0064_test_report.txt",
    "data/rev0064_smoke.txt",
    "data/rev0064_audit_stdout.txt",
    "data/rev0064_inherited_audit_report.json",
    "data/rev0064_artifact_audit.json",
    "data/rev0064_artifact_audit_stdout.txt",
    "data/rev0064_validation_summary.json",
]

MAX_ROWS = {
    "data/rev0064_closure_vs_counter_games.csv": 160,
    "data/rev0064_closure_vs_counter_forensics.csv": 160,
    "data/rev0064_closure_vs_counter_features.csv": 160,
    "data/rev0064_closure_vs_counter_cpp_transition_sample.csv": 260,
    "data/rev0064_closure_vs_counter_legacy_selfdeck_cases.csv": 65,
    "data/rev0064_closure_vs_counter_closure_rescue_cases.csv": 65,
}


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=["data/rev0064*_cpp_transitions.csv", "data/rev0064*_transition_rows.csv"],
        max_csv_rows=MAX_ROWS,
    )
    out = DATA / "rev0064_artifact_audit.json"
    out.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
