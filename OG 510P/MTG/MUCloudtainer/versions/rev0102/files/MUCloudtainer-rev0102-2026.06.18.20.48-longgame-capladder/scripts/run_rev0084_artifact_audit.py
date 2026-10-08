#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0084"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_candidate_transfer.py",
    "scripts/run_rev0084_candidate_transfer_audit.py",
    "scripts/run_rev0084_artifact_audit.py",
    "tests/test_rev0084_candidate_transfer.py",
    "docs/candidate_transfer_audit_rev0084.md",
    "docs/refactor_audit_rev0084.md",
    "docs/priority_reconsideration_rev0084.md",
    "docs/experiment_matrix_rev0084.md",
    "data/rev0084_candidate_transfer_summary.json",
    "data/rev0084_candidate_transfer_games.csv",
    "data/rev0084_candidate_transfer_arm_summary.csv",
    "data/rev0084_candidate_transfer_paired_deltas.csv",
    "data/rev0084_candidate_transfer_context_summary.csv",
    "data/rev0084_candidate_transfer_axis_summary.csv",
    "data/rev0084_candidate_transfer_cpp_transition_sample.csv",
    "data/rev0084_evidence_tiering_catalog.json",
    "data/rev0084_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0084*_transition_rows.csv",
            "data/rev0084*_cpp_transitions.csv",
            "data/rev0084*_replay_traces.jsonl",
        ],
        max_csv_rows={
            "data/rev0084_candidate_transfer_games.csv": 480,
            "data/rev0084_candidate_transfer_arm_summary.csv": 36,
            "data/rev0084_candidate_transfer_paired_deltas.csv": 240,
            "data/rev0084_candidate_transfer_context_summary.csv": 19,
            "data/rev0084_candidate_transfer_axis_summary.csv": 30,
            "data/rev0084_candidate_transfer_cpp_transition_sample.csv": 180,
        },
    )
    output = DATA / "rev0084_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
