#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0080"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_power.py",
    "src/muc5/population_sampling.py",
    "scripts/run_rev0080_size_ladder_power_audit.py",
    "scripts/run_rev0080_artifact_audit.py",
    "tests/test_rev0080_size_ladder_power.py",
    "docs/size_ladder_power_rev0080.md",
    "docs/refactor_audit_rev0080.md",
    "docs/priority_reconsideration_rev0080.md",
    "docs/experiment_matrix_rev0080.md",
    "data/rev0080_size_ladder_power_summary.json",
    "data/rev0080_size_ladder_games.csv",
    "data/rev0080_size_ladder_arm_summary.csv",
    "data/rev0080_size_ladder_mechanisms.csv",
    "data/rev0080_size_ladder_cpp_transition_sample.csv",
    "data/rev0080_pre_power_ladder.csv",
    "data/rev0080_post_power_ladder.csv",
    "data/rev0080_post_hierarchical_familywise_gate.csv",
    "data/rev0080_sampling_frame_summary.csv",
    "data/rev0080_post_pooled_size_summary.csv",
    "data/rev0080_post_pooled_fine_summary.csv",
    "data/rev0080_evidence_tiering_catalog.json",
    "data/rev0080_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0080*_transition_rows.csv",
            "data/rev0080*_cpp_transitions.csv",
            "data/rev0080*_replay_traces.jsonl",
        ],
        max_csv_rows={
            "data/rev0080_size_ladder_games.csv": 720,
            "data/rev0080_size_ladder_arm_summary.csv": 36,
            "data/rev0080_size_ladder_mechanisms.csv": 144,
            "data/rev0080_size_ladder_cpp_transition_sample.csv": 180,
            "data/rev0080_pre_power_ladder.csv": 12,
            "data/rev0080_post_power_ladder.csv": 12,
            "data/rev0080_post_hierarchical_familywise_gate.csv": 12,
            "data/rev0080_sampling_frame_summary.csv": 4,
            "data/rev0080_post_pooled_size_summary.csv": 18,
            "data/rev0080_post_pooled_fine_summary.csv": 36,
        },
    )
    output = DATA / "rev0080_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
