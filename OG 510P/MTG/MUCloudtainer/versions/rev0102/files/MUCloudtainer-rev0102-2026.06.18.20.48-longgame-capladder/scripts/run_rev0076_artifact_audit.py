#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0076"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_score_audit.py",
    "src/muc5/terminal_mechanisms.py",
    "src/muc5/threat_response.py",
    "scripts/run_rev0076_score_orientation_audit.py",
    "scripts/run_rev0076_artifact_audit.py",
    "tests/test_rev0076_score_orientation.py",
    "docs/score_orientation_audit_rev0076.md",
    "docs/refactor_audit_rev0076.md",
    "docs/priority_reconsideration_rev0076.md",
    "docs/experiment_matrix_rev0076.md",
    "data/rev0076_score_orientation_summary.json",
    "data/rev0076_score_orientation_by_source.csv",
    "data/rev0076_score_orientation_mismatches.csv",
    "data/rev0076_evidence_tiering_catalog.json",
    "data/rev0076_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0076*_cpp_transitions.csv",
            "data/rev0076*_transition_rows.csv",
            "data/rev0076*_replay_traces.jsonl",
            "data/rev0076*_games.csv",
        ],
        max_csv_rows={
            "data/rev0076_score_orientation_by_source.csv": 3,
            "data/rev0076_score_orientation_mismatches.csv": 0,
        },
    )
    output = DATA / "rev0076_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
