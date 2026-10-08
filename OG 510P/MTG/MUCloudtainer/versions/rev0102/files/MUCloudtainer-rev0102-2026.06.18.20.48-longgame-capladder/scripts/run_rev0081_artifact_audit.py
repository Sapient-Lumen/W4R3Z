#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0081"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_frontier.py",
    "scripts/run_rev0081_opponent_frontier_audit.py",
    "scripts/run_rev0081_artifact_audit.py",
    "tests/test_rev0081_opponent_frontier.py",
    "docs/opponent_frontier_rev0081.md",
    "docs/refactor_audit_rev0081.md",
    "docs/priority_reconsideration_rev0081.md",
    "docs/experiment_matrix_rev0081.md",
    "data/rev0081_opponent_frontier_summary.json",
    "data/rev0081_opponent_frontier_familywise.csv",
    "data/rev0081_opponent_frontier_layer_summary.csv",
    "data/rev0081_opponent_frontier_hierarchical_gate_reference.csv",
    "data/rev0081_sampling_frame_summary.csv",
    "data/rev0081_evidence_tiering_catalog.json",
    "data/rev0081_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0081*_transition_rows.csv",
            "data/rev0081*_cpp_transitions.csv",
            "data/rev0081*_replay_traces.jsonl",
            "data/rev0081*_games.csv",
        ],
        max_csv_rows={
            "data/rev0081_opponent_frontier_familywise.csv": 36,
            "data/rev0081_opponent_frontier_layer_summary.csv": 4,
            "data/rev0081_opponent_frontier_hierarchical_gate_reference.csv": 12,
            "data/rev0081_sampling_frame_summary.csv": 4,
        },
    )
    output = DATA / "rev0081_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
