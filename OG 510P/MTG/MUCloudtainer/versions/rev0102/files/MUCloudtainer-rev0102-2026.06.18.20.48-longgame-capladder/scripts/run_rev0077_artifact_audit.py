#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0077"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_sampling.py",
    "scripts/run_rev0077_adaptive_pooling_guard.py",
    "scripts/run_rev0077_artifact_audit.py",
    "tests/test_rev0077_adaptive_pooling.py",
    "docs/adaptive_pooling_guard_rev0077.md",
    "docs/refactor_audit_rev0077.md",
    "docs/priority_reconsideration_rev0077.md",
    "docs/experiment_matrix_rev0077.md",
    "data/rev0077_adaptive_pooling_guard_summary.json",
    "data/rev0077_sampling_frame_summary.csv",
    "data/rev0077_population_pool_eligible_arm_summary.csv",
    "data/rev0077_population_pool_eligible_gate.csv",
    "data/rev0077_population_pool_naive_adaptive_gate.csv",
    "data/rev0077_population_pool_life_gate_comparison.csv",
    "data/rev0077_population_pool_guard_comparison.csv",
    "data/rev0077_evidence_tiering_catalog.json",
    "data/rev0077_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0077*_games.csv",
            "data/rev0077*_cpp_transitions.csv",
            "data/rev0077*_transition_rows.csv",
            "data/rev0077*_replay_traces.jsonl",
        ],
        max_csv_rows={
            "data/rev0077_sampling_frame_summary.csv": 3,
            "data/rev0077_population_pool_eligible_arm_summary.csv": 6,
            "data/rev0077_population_pool_eligible_gate.csv": 1,
            "data/rev0077_population_pool_naive_adaptive_gate.csv": 1,
            "data/rev0077_population_pool_life_gate_comparison.csv": 4,
            "data/rev0077_population_pool_guard_comparison.csv": 4,
        },
    )
    output = DATA / "rev0077_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
