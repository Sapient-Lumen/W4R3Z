#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0067"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/public_agents.py",
    "src/muc5/response_matrix.py",
    "tests/test_rev0067_response_matrix.py",
    "scripts/run_rev0067_response_matrix.py",
    "scripts/run_rev0067_artifact_audit.py",
    "docs/response_matrix_audit_rev0067.md",
    "docs/refactor_audit_rev0067.md",
    "docs/simulator_rev0067.md",
    "data/rev0067_response_matrix_summary.json",
    "data/rev0067_response_matrix_arms.json",
    "data/rev0067_response_matrix_games.csv",
    "data/rev0067_response_matrix_aggregate.csv",
    "data/rev0067_response_matrix_arm_summary.csv",
    "data/rev0067_response_matrix_mechanisms.csv",
    "data/rev0067_response_matrix_life_rollup.csv",
    "data/rev0067_response_matrix_comparisons.csv",
    "data/rev0067_response_matrix_cpp_transition_sample.csv",
    "data/rev0067_response_matrix_replay_traces.jsonl",
    "data/rev0067_response_matrix_replay_results.json",
    "data/rev0067_response_matrix_forensics.csv",
    "data/rev0067_response_matrix_forensic_arm_summary.csv",
    "data/rev0067_response_matrix_features.csv",
    "data/rev0067_response_matrix_feature_summary.csv",
    "data/rev0067_response_matrix_counter_ownership.csv",
    "data/rev0067_response_matrix_counter_ownership_summary.csv",
    "data/rev0067_response_matrix_surge_refute_cases.csv",
    "data/rev0067_response_matrix_counter_survive_cases.csv",
    "data/rev0067_response_matrix_stress_games.csv",
    "data/rev0067_response_matrix_stress_aggregate.csv",
    "data/rev0067_response_matrix_stress_arm_summary.csv",
    "data/rev0067_response_matrix_stress_mechanisms.csv",
    "data/rev0067_response_matrix_stress_life_rollup.csv",
    "data/rev0067_response_matrix_stress_comparisons.csv",
    "data/rev0067_response_matrix_stress_cpp_transition_sample.csv",
    "data/rev0067_response_matrix_stress_forensics.csv",
    "data/rev0067_response_matrix_stress_forensic_arm_summary.csv",
    "data/rev0067_response_matrix_stress_features.csv",
    "data/rev0067_response_matrix_stress_feature_summary.csv",
    "data/rev0067_response_matrix_stress_counter_ownership.csv",
    "data/rev0067_response_matrix_stress_counter_ownership_summary.csv",
    "data/rev0067_response_matrix_stress_surge_refute_cases.csv",
    "data/rev0067_response_matrix_stress_counter_survive_cases.csv",
    "data/rev0067_response_matrix_deep60_games.csv",
    "data/rev0067_response_matrix_deep60_aggregate.csv",
    "data/rev0067_response_matrix_deep60_arm_summary.csv",
    "data/rev0067_response_matrix_deep60_mechanisms.csv",
    "data/rev0067_response_matrix_deep60_life_rollup.csv",
    "data/rev0067_response_matrix_deep60_comparisons.csv",
    "data/rev0067_response_matrix_deep60_cpp_transition_sample.csv",
    "data/rev0067_response_matrix_deep60_forensics.csv",
    "data/rev0067_response_matrix_deep60_forensic_arm_summary.csv",
    "data/rev0067_response_matrix_deep60_features.csv",
    "data/rev0067_response_matrix_deep60_feature_summary.csv",
    "data/rev0067_response_matrix_deep60_counter_ownership.csv",
    "data/rev0067_response_matrix_deep60_counter_ownership_summary.csv",
    "data/rev0067_response_matrix_deep60_surge_refute_cases.csv",
    "data/rev0067_response_matrix_deep60_counter_survive_cases.csv",
    "data/rev0067_response_matrix_cumulative_arm_summary.csv",
    "data/rev0067_response_matrix_cumulative_mechanisms.csv",
    "data/rev0067_response_matrix_cumulative_life_rollup.csv",
    "data/rev0067_response_matrix_cumulative_comparisons.csv",
    "data/rev0067_response_matrix_stdout.txt",
    "data/rev0067_test_report.txt",
    "data/rev0067_smoke.txt",
    "data/rev0067_audit_stdout.txt",
    "data/rev0067_inherited_audit_report.json",
    "data/rev0067_artifact_audit.json",
    "data/rev0067_artifact_audit_stdout.txt",
    "data/rev0067_validation_summary.json",
]

MAX_ROWS = {
    "data/rev0067_response_matrix_games.csv": 160,
    "data/rev0067_response_matrix_forensics.csv": 160,
    "data/rev0067_response_matrix_features.csv": 160,
    "data/rev0067_response_matrix_counter_ownership.csv": 160,
    "data/rev0067_response_matrix_cpp_transition_sample.csv": 260,
    "data/rev0067_response_matrix_stress_games.csv": 120,
    "data/rev0067_response_matrix_stress_forensics.csv": 120,
    "data/rev0067_response_matrix_stress_features.csv": 120,
    "data/rev0067_response_matrix_stress_counter_ownership.csv": 120,
    "data/rev0067_response_matrix_stress_cpp_transition_sample.csv": 260,
    "data/rev0067_response_matrix_deep60_games.csv": 110,
    "data/rev0067_response_matrix_deep60_forensics.csv": 110,
    "data/rev0067_response_matrix_deep60_features.csv": 110,
    "data/rev0067_response_matrix_deep60_counter_ownership.csv": 110,
    "data/rev0067_response_matrix_deep60_cpp_transition_sample.csv": 260,
    "data/rev0067_response_matrix_surge_refute_cases.csv": 70,
    "data/rev0067_response_matrix_counter_survive_cases.csv": 70,
    "data/rev0067_response_matrix_stress_surge_refute_cases.csv": 70,
    "data/rev0067_response_matrix_stress_counter_survive_cases.csv": 70,
    "data/rev0067_response_matrix_deep60_surge_refute_cases.csv": 70,
    "data/rev0067_response_matrix_deep60_counter_survive_cases.csv": 70,
}


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=["data/rev0067*_cpp_transitions.csv", "data/rev0067*_transition_rows.csv"],
        max_csv_rows=MAX_ROWS,
    )
    out = DATA / "rev0067_artifact_audit.json"
    out.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
