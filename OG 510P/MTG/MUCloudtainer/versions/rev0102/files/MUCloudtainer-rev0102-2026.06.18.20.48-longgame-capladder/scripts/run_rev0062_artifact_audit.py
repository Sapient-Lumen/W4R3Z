#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0062"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/library_buffer_sweep.py",
    "src/muc5/trajectory_forensics.py",
    "tests/test_rev0062_library_buffer_sweep.py",
    "scripts/run_rev0062_library_buffer_sweep.py",
    "scripts/run_rev0062_artifact_audit.py",
    "docs/library_buffer_sweep_rev0062.md",
    "docs/refactor_audit_rev0062.md",
    "docs/simulator_rev0062.md",
    "data/rev0062_library_buffer_sweep_summary.json",
    "data/rev0062_library_buffer_sweep_games.csv",
    "data/rev0062_library_buffer_sweep_aggregate.csv",
    "data/rev0062_library_buffer_sweep_arm_summary.csv",
    "data/rev0062_library_buffer_sweep_mechanisms.csv",
    "data/rev0062_library_buffer_sweep_life_rollup.csv",
    "data/rev0062_library_buffer_sweep_size_rollup.csv",
    "data/rev0062_library_buffer_sweep_comparisons.csv",
    "data/rev0062_library_buffer_sweep_cpp_transition_sample.csv",
    "data/rev0062_library_buffer_sweep_replay_traces.jsonl",
    "data/rev0062_library_buffer_sweep_replay_results.json",
    "data/rev0062_library_buffer_sweep_arms.json",
    "data/rev0062_library_buffer_sweep_forensics.csv",
    "data/rev0062_library_buffer_sweep_forensic_arm_summary.csv",
    "data/rev0062_library_buffer_sweep_forensic_size_summary.csv",
    "data/rev0062_library_buffer_sweep_forensic_result_summary.csv",
    "data/rev0062_library_buffer_sweep_forensic_feature_comparisons.csv",
    "data/rev0062_library_buffer_sweep_buffer60_win_cases.csv",
    "data/rev0062_library_buffer_sweep_equalized_buffer_loss_cases.csv",
    "data/rev0062_library_buffer_sweep_stdout.txt",
    "data/rev0062_test_report.txt",
    "data/rev0062_smoke.txt",
    "data/rev0062_audit_stdout.txt",
    "data/rev0062_inherited_audit_report.json",
    "data/rev0062_artifact_audit.json",
    "data/rev0062_artifact_audit_stdout.txt",
    "data/rev0062_validation_summary.json",
]

MAX_ROWS = {
    "data/rev0062_library_buffer_sweep_games.csv": 180,
    "data/rev0062_library_buffer_sweep_forensics.csv": 180,
    "data/rev0062_library_buffer_sweep_cpp_transition_sample.csv": 260,
    "data/rev0062_library_buffer_sweep_buffer60_win_cases.csv": 45,
    "data/rev0062_library_buffer_sweep_equalized_buffer_loss_cases.csv": 45,
}


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=["data/rev0062*_cpp_transitions.csv", "data/rev0062*_transition_rows.csv"],
        max_csv_rows=MAX_ROWS,
    )
    out = DATA / "rev0062_artifact_audit.json"
    out.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
