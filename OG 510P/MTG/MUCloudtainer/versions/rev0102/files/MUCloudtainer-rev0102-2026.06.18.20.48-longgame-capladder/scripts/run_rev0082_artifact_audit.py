#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0082"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_frontier.py",
    "scripts/run_rev0082_counterset_rescue_audit.py",
    "scripts/run_rev0082_artifact_audit.py",
    "tests/test_rev0082_counterset_rescue.py",
    "docs/counterset_rescue_rev0082.md",
    "docs/refactor_audit_rev0082.md",
    "docs/priority_reconsideration_rev0082.md",
    "docs/experiment_matrix_rev0082.md",
    "data/rev0082_counterset_rescue_summary.json",
    "data/rev0082_counterset_rescue_envelope.csv",
    "data/rev0082_counterset_rescue_layer_summary.csv",
    "data/rev0082_evidence_tiering_catalog.json",
    "data/rev0082_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0082*_transition_rows.csv",
            "data/rev0082*_cpp_transitions.csv",
            "data/rev0082*_replay_traces.jsonl",
            "data/rev0082*_games.csv",
        ],
        max_csv_rows={
            "data/rev0082_counterset_rescue_envelope.csv": 36,
            "data/rev0082_counterset_rescue_layer_summary.csv": 4,
        },
    )
    output = DATA / "rev0082_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
