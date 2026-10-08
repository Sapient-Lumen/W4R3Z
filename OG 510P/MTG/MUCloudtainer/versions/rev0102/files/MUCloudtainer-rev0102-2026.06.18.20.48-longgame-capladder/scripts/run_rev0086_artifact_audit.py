#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0086"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_pair_forensics.py",
    "scripts/run_rev0086_mechanism_drift_audit.py",
    "scripts/run_rev0086_artifact_audit.py",
    "tests/test_rev0086_mechanism_drift.py",
    "docs/mechanism_drift_tiecontract_rev0086.md",
    "docs/refactor_audit_rev0086.md",
    "docs/priority_reconsideration_rev0086.md",
    "docs/experiment_matrix_rev0086.md",
    "data/rev0086_mechanism_drift_summary.json",
    "data/rev0086_primary_mechanism_drift.csv",
    "data/rev0086_context_mechanism_drift.csv",
    "data/rev0086_same_score_mechanism_flips.csv",
    "data/rev0086_evidence_tiering_catalog.json",
    "data/rev0086_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0086*_transition_rows.csv",
            "data/rev0086*_cpp_transitions.csv",
            "data/rev0086*_replay_traces.jsonl",
            "data/rev0086*_games.csv",
        ],
        max_csv_rows={
            "data/rev0086_primary_mechanism_drift.csv": 3,
            "data/rev0086_context_mechanism_drift.csv": 48,
            "data/rev0086_same_score_mechanism_flips.csv": 18,
        },
    )
    output = DATA / "rev0086_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
