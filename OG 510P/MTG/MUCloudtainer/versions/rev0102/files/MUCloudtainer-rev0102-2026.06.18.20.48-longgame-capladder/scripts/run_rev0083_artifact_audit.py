#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0083"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/public_agents.py",
    "src/muc5/population_counterprobe.py",
    "scripts/run_rev0083_deficient_cell_counterprobe.py",
    "scripts/run_rev0083_artifact_audit.py",
    "tests/test_rev0083_deficient_cell_counterprobe.py",
    "docs/deficient_cell_counterprobe_rev0083.md",
    "docs/refactor_audit_rev0083.md",
    "docs/priority_reconsideration_rev0083.md",
    "docs/experiment_matrix_rev0083.md",
    "data/rev0083_deficient_cell_counterprobe_summary.json",
    "data/rev0083_deficient_cell_counterprobe_games.csv",
    "data/rev0083_deficient_cell_counterprobe_arm_summary.csv",
    "data/rev0083_deficient_cell_counterprobe_policy_deltas.csv",
    "data/rev0083_deficient_cell_counterprobe_frontier.csv",
    "data/rev0083_deficient_cell_counterprobe_rescue.csv",
    "data/rev0083_deficient_cell_counterprobe_seed_balance.csv",
    "data/rev0083_deficient_cell_counterprobe_paired_outcome_delta.csv",
    "data/rev0083_deficient_cell_counterprobe_cpp_transition_sample.csv",
    "data/rev0083_evidence_tiering_catalog.json",
    "data/rev0083_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0083*_transition_rows.csv",
            "data/rev0083*_cpp_transitions.csv",
            "data/rev0083*_replay_traces.jsonl",
        ],
        max_csv_rows={
            "data/rev0083_deficient_cell_counterprobe_games.csv": 192,
            "data/rev0083_deficient_cell_counterprobe_arm_summary.csv": 3,
            "data/rev0083_deficient_cell_counterprobe_policy_deltas.csv": 3,
            "data/rev0083_deficient_cell_counterprobe_frontier.csv": 1,
            "data/rev0083_deficient_cell_counterprobe_rescue.csv": 1,
            "data/rev0083_deficient_cell_counterprobe_seed_balance.csv": 64,
            "data/rev0083_deficient_cell_counterprobe_paired_outcome_delta.csv": 64,
            "data/rev0083_deficient_cell_counterprobe_cpp_transition_sample.csv": 180,
        },
    )
    output = DATA / "rev0083_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
