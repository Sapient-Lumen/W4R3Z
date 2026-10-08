#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0075"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_stratum_challenge.py",
    "src/muc5/population_frontier.py",
    "src/muc5/cpp_rollout.py",
    "scripts/run_rev0075_stratum_challenge.py",
    "scripts/run_rev0075_artifact_audit.py",
    "tests/test_rev0075_stratum_challenge.py",
    "docs/stratum_challenge_rev0075.md",
    "docs/refactor_audit_rev0075.md",
    "docs/priority_reconsideration_rev0075.md",
    "docs/experiment_matrix_rev0075.md",
    "data/rev0075_stratum_challenge_summary.json",
    "data/rev0075_stratum_challenge_games.csv",
    "data/rev0075_stratum_challenge_arm_summary.csv",
    "data/rev0075_stratum_challenge_pre_gate.csv",
    "data/rev0075_stratum_challenge_post_gate.csv",
    "data/rev0075_stratum_challenge_comparison.csv",
    "data/rev0075_stratum_challenge_cpp_transition_sample.csv",
    "data/rev0075_stratum_challenge_selected_cells.json",
    "data/rev0075_evidence_tiering_catalog.json",
    "data/rev0075_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0075*_cpp_transitions.csv",
            "data/rev0075*_transition_rows.csv",
            "data/rev0075*_replay_traces.jsonl",
        ],
        max_csv_rows={
            "data/rev0075_stratum_challenge_games.csv": 300,
            "data/rev0075_stratum_challenge_cpp_transition_sample.csv": 400,
        },
    )
    output = DATA / "rev0075_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
