#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0078"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_frontier.py",
    "scripts/run_rev0078_familywise_gate_audit.py",
    "scripts/run_rev0078_artifact_audit.py",
    "tests/test_rev0078_familywise_gate.py",
    "docs/familywise_gate_rev0078.md",
    "docs/refactor_audit_rev0078.md",
    "docs/priority_reconsideration_rev0078.md",
    "docs/experiment_matrix_rev0078.md",
    "data/rev0078_familywise_gate_summary.json",
    "data/rev0078_familywise_global_gate.csv",
    "data/rev0078_familywise_life_gate.csv",
    "data/rev0078_familywise_naive_adaptive_gate.csv",
    "data/rev0078_familywise_gate_comparison.csv",
    "data/rev0078_familywise_gate_stdout.txt",
    "data/rev0078_evidence_tiering_catalog.json",
    "data/rev0078_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0078*_games.csv",
            "data/rev0078*_cpp_transitions.csv",
            "data/rev0078*_transition_rows.csv",
            "data/rev0078*_replay_traces.jsonl",
        ],
        max_csv_rows={
            "data/rev0078_familywise_global_gate.csv": 1,
            "data/rev0078_familywise_life_gate.csv": 2,
            "data/rev0078_familywise_naive_adaptive_gate.csv": 1,
            "data/rev0078_familywise_gate_comparison.csv": 4,
        },
    )
    output = DATA / "rev0078_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
