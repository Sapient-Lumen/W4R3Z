#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0066"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/public_agents.py",
    "src/muc5/threat_response.py",
    "tests/test_rev0066_threat_response.py",
    "scripts/run_rev0066_threat_response.py",
    "scripts/run_rev0066_artifact_audit.py",
    "docs/threat_response_audit_rev0066.md",
    "docs/refactor_audit_rev0066.md",
    "docs/simulator_rev0066.md",
    "data/rev0066_threat_response_summary.json",
    "data/rev0066_threat_response_games.csv",
    "data/rev0066_threat_response_aggregate.csv",
    "data/rev0066_threat_response_arm_summary.csv",
    "data/rev0066_threat_response_mechanisms.csv",
    "data/rev0066_threat_response_life_rollup.csv",
    "data/rev0066_threat_response_comparisons.csv",
    "data/rev0066_threat_response_cpp_transition_sample.csv",
    "data/rev0066_threat_response_replay_traces.jsonl",
    "data/rev0066_threat_response_replay_results.json",
    "data/rev0066_threat_response_arms.json",
    "data/rev0066_threat_response_forensics.csv",
    "data/rev0066_threat_response_forensic_arm_summary.csv",
    "data/rev0066_threat_response_features.csv",
    "data/rev0066_threat_response_feature_summary.csv",
    "data/rev0066_threat_response_counter_ownership.csv",
    "data/rev0066_threat_response_counter_ownership_summary.csv",
    "data/rev0066_threat_response_pressure_refute_cases.csv",
    "data/rev0066_threat_response_counter_survive_cases.csv",
    "data/rev0066_threat_response_stress_games.csv",
    "data/rev0066_threat_response_stress_aggregate.csv",
    "data/rev0066_threat_response_stress_arm_summary.csv",
    "data/rev0066_threat_response_stress_mechanisms.csv",
    "data/rev0066_threat_response_stress_life_rollup.csv",
    "data/rev0066_threat_response_stress_comparisons.csv",
    "data/rev0066_threat_response_stress_cpp_transition_sample.csv",
    "data/rev0066_threat_response_stress_forensics.csv",
    "data/rev0066_threat_response_stress_forensic_arm_summary.csv",
    "data/rev0066_threat_response_stress_features.csv",
    "data/rev0066_threat_response_stress_feature_summary.csv",
    "data/rev0066_threat_response_stress_counter_ownership.csv",
    "data/rev0066_threat_response_stress_counter_ownership_summary.csv",
    "data/rev0066_threat_response_stress_pressure_refute_cases.csv",
    "data/rev0066_threat_response_stress_counter_survive_cases.csv",
    "data/rev0066_threat_response_stdout.txt",
    "data/rev0066_test_report.txt",
    "data/rev0066_smoke.txt",
    "data/rev0066_audit_stdout.txt",
    "data/rev0066_inherited_audit_report.json",
    "data/rev0066_artifact_audit.json",
    "data/rev0066_artifact_audit_stdout.txt",
    "data/rev0066_validation_summary.json",
]

MAX_ROWS = {
    "data/rev0066_threat_response_games.csv": 160,
    "data/rev0066_threat_response_forensics.csv": 160,
    "data/rev0066_threat_response_features.csv": 160,
    "data/rev0066_threat_response_counter_ownership.csv": 160,
    "data/rev0066_threat_response_cpp_transition_sample.csv": 260,
    "data/rev0066_threat_response_stress_games.csv": 80,
    "data/rev0066_threat_response_stress_forensics.csv": 80,
    "data/rev0066_threat_response_stress_features.csv": 80,
    "data/rev0066_threat_response_stress_counter_ownership.csv": 80,
    "data/rev0066_threat_response_stress_cpp_transition_sample.csv": 260,
    "data/rev0066_threat_response_pressure_refute_cases.csv": 70,
    "data/rev0066_threat_response_counter_survive_cases.csv": 70,
    "data/rev0066_threat_response_stress_pressure_refute_cases.csv": 40,
    "data/rev0066_threat_response_stress_counter_survive_cases.csv": 40,
}


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=["data/rev0066*_cpp_transitions.csv", "data/rev0066*_transition_rows.csv"],
        max_csv_rows=MAX_ROWS,
    )
    out = DATA / "rev0066_artifact_audit.json"
    out.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
