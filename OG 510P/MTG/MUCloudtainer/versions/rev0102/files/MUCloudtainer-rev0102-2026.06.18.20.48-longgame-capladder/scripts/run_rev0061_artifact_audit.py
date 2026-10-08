#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0061"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/mechanism_ablation.py",
    "src/muc5/trajectory_forensics.py",
    "tests/test_rev0061_mechanism_ablation.py",
    "tests/test_rev0060_trajectory_forensics.py",
    "scripts/run_rev0061_mechanism_ablation.py",
    "scripts/run_rev0061_artifact_audit.py",
    "docs/mechanism_ablation_rev0061.md",
    "docs/refactor_audit_rev0061.md",
    "docs/simulator_rev0061.md",
    "data/rev0061_mechanism_ablation_summary.json",
    "data/rev0061_mechanism_ablation_games.csv",
    "data/rev0061_mechanism_ablation_aggregate.csv",
    "data/rev0061_mechanism_ablation_arm_summary.csv",
    "data/rev0061_mechanism_ablation_mechanisms.csv",
    "data/rev0061_mechanism_ablation_life_rollup.csv",
    "data/rev0061_mechanism_ablation_comparisons.csv",
    "data/rev0061_mechanism_ablation_cpp_transition_sample.csv",
    "data/rev0061_mechanism_ablation_replay_traces.jsonl",
    "data/rev0061_mechanism_ablation_replay_results.json",
    "data/rev0061_mechanism_ablation_arms.json",
    "data/rev0061_mechanism_ablation_forensics.csv",
    "data/rev0061_mechanism_ablation_forensic_arm_summary.csv",
    "data/rev0061_mechanism_ablation_forensic_result_summary.csv",
    "data/rev0061_mechanism_ablation_forensic_feature_comparisons.csv",
    "data/rev0061_mechanism_ablation_nojace_win_cases.csv",
    "data/rev0061_mechanism_ablation_nocounter_loss_cases.csv",
    "data/rev0061_mechanism_ablation_stdout.txt",
    "data/rev0061_test_report.txt",
    "data/rev0061_smoke.txt",
    "data/rev0061_audit_stdout.txt",
    "data/rev0061_inherited_audit_report.json",
    "data/rev0061_artifact_audit.json",
    "data/rev0061_artifact_audit_stdout.txt",
    "data/rev0061_validation_summary.json",
]

MAX_ROWS = {
    "data/rev0061_mechanism_ablation_games.csv": 260,
    "data/rev0061_mechanism_ablation_forensics.csv": 260,
    "data/rev0061_mechanism_ablation_cpp_transition_sample.csv": 260,
    "data/rev0061_mechanism_ablation_nojace_win_cases.csv": 40,
    "data/rev0061_mechanism_ablation_nocounter_loss_cases.csv": 40,
}


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=["data/rev0061*_cpp_transitions.csv", "data/rev0061*_transition_rows.csv"],
        max_csv_rows=MAX_ROWS,
    )
    out = DATA / "rev0061_artifact_audit.json"
    out.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
