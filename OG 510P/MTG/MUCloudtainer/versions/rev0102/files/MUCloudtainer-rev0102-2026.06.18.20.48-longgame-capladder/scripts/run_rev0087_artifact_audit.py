#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0087"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_candidate_gate.py",
    "scripts/run_rev0087_candidate_gate_audit.py",
    "scripts/run_rev0087_artifact_audit.py",
    "tests/test_rev0087_candidate_gate.py",
    "docs/mechanismgate_candidatefirewall_rev0087.md",
    "docs/refactor_audit_rev0087.md",
    "docs/priority_reconsideration_rev0087.md",
    "docs/experiment_matrix_rev0087.md",
    "data/rev0087_candidate_gate_summary.json",
    "data/rev0087_candidate_gate_rows.csv",
    "data/rev0087_candidate_gate_component_rows.csv",
    "data/rev0087_candidate_gate_leak_audit.csv",
    "data/rev0087_evidence_tiering_catalog.json",
    "data/rev0087_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0087*_transition_rows.csv",
            "data/rev0087*_cpp_transitions.csv",
            "data/rev0087*_replay_traces.jsonl",
            "data/rev0087*_games.csv",
            "data/rev0087*_paired_deltas.csv",
        ],
        max_csv_rows={
            "data/rev0087_candidate_gate_rows.csv": 1,
            "data/rev0087_candidate_gate_component_rows.csv": 6,
            "data/rev0087_candidate_gate_leak_audit.csv": 8,
        },
    )
    output = DATA / "rev0087_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
