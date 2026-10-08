#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0085"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_pair_forensics.py",
    "scripts/run_rev0085_pair_integrity_tie_forensics.py",
    "scripts/run_rev0085_artifact_audit.py",
    "tests/test_rev0085_pair_integrity.py",
    "docs/pair_integrity_tie_forensics_rev0085.md",
    "docs/refactor_audit_rev0085.md",
    "docs/priority_reconsideration_rev0085.md",
    "docs/experiment_matrix_rev0085.md",
    "data/rev0085_pair_integrity_summary.json",
    "data/rev0085_pair_integrity_rows.csv",
    "data/rev0085_primary_sign_tests.csv",
    "data/rev0085_context_sign_tests.csv",
    "data/rev0085_tie_mechanism_forensics.csv",
    "data/rev0085_evidence_tiering_catalog.json",
    "data/rev0085_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0085*_transition_rows.csv",
            "data/rev0085*_cpp_transitions.csv",
            "data/rev0085*_replay_traces.jsonl",
            "data/rev0085*_games.csv",
        ],
        max_csv_rows={
            "data/rev0085_pair_integrity_rows.csv": 240,
            "data/rev0085_primary_sign_tests.csv": 3,
            "data/rev0085_context_sign_tests.csv": 48,
            "data/rev0085_tie_mechanism_forensics.csv": 51,
        },
    )
    output = DATA / "rev0085_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
