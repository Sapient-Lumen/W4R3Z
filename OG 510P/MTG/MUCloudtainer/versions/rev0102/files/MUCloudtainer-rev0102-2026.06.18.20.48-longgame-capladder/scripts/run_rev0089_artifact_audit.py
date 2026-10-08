#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0089"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/population_replay_guard.py",
    "scripts/run_rev0089_policy_replay_drift_guard.py",
    "scripts/run_rev0089_artifact_audit.py",
    "tests/test_rev0089_policy_replay_guard.py",
    "docs/policyreplay_driftguard_rev0089.md",
    "docs/refactor_audit_rev0089.md",
    "docs/priority_reconsideration_rev0089.md",
    "docs/experiment_matrix_rev0089.md",
    "data/rev0089_policy_replay_summary.json",
    "data/rev0089_policy_runtime_identity.json",
    "data/rev0089_policy_replay_sample_rows.csv",
    "data/rev0089_policy_replay_check_rows.csv",
    "data/rev0089_policy_identity_coverage.csv",
    "data/rev0089_evidence_tiering_catalog.json",
    "data/rev0089_evidence_bundle_audit.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0089*_transition_rows.csv",
            "data/rev0089*_cpp_transitions.csv",
            "data/rev0089*_replay_traces.jsonl",
            "data/rev0089*_games.csv",
            "data/rev0089*_paired_deltas.csv",
        ],
        max_csv_rows={
            "data/rev0089_policy_replay_sample_rows.csv": 64,
            "data/rev0089_policy_replay_check_rows.csv": 64,
            "data/rev0089_policy_identity_coverage.csv": 4,
        },
    )
    output = DATA / "rev0089_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
