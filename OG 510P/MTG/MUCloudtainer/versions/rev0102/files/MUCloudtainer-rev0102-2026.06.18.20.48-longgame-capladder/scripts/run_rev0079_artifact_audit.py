#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0079"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_frontier.py",
    "scripts/run_rev0079_hierarchical_gate_audit.py",
    "scripts/run_rev0079_artifact_audit.py",
    "tests/test_rev0079_hierarchical_gate.py",
    "docs/hierarchical_gate_rev0079.md",
    "docs/refactor_audit_rev0079.md",
    "docs/priority_reconsideration_rev0079.md",
    "docs/experiment_matrix_rev0079.md",
    "data/rev0079_hierarchical_gate_summary.json",
    "data/rev0079_hierarchical_familywise_gate.csv",
    "data/rev0079_hierarchical_gate_layer_summary.csv",
    "data/rev0079_solver_diagnostic.csv",
    "data/rev0079_evidence_tiering_catalog.json",
    "data/rev0079_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0079*_games.csv",
            "data/rev0079*_cpp_transitions.csv",
            "data/rev0079*_transition_rows.csv",
            "data/rev0079*_replay_traces.jsonl",
        ],
        max_csv_rows={
            "data/rev0079_hierarchical_familywise_gate.csv": 12,
            "data/rev0079_hierarchical_gate_layer_summary.csv": 4,
            "data/rev0079_solver_diagnostic.csv": 2,
        },
    )
    output = DATA / "rev0079_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
