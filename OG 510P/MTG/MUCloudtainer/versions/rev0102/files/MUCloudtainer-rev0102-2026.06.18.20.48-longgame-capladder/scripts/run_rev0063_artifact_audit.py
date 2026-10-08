#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0063"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/threat_closure.py",
    "src/muc5/public_agents.py",
    "tests/test_rev0063_threat_closure.py",
    "scripts/run_rev0063_threat_closure_audit.py",
    "scripts/run_rev0063_artifact_audit.py",
    "docs/threat_closure_audit_rev0063.md",
    "docs/refactor_audit_rev0063.md",
    "docs/simulator_rev0063.md",
    "data/rev0063_threat_closure_summary.json",
    "data/rev0063_threat_closure_games.csv",
    "data/rev0063_threat_closure_aggregate.csv",
    "data/rev0063_threat_closure_arm_summary.csv",
    "data/rev0063_threat_closure_mechanisms.csv",
    "data/rev0063_threat_closure_life_rollup.csv",
    "data/rev0063_threat_closure_cpp_transition_sample.csv",
    "data/rev0063_threat_closure_replay_traces.jsonl",
    "data/rev0063_threat_closure_replay_results.json",
    "data/rev0063_threat_closure_arms.json",
    "data/rev0063_threat_closure_forensics.csv",
    "data/rev0063_threat_closure_forensic_arm_summary.csv",
    "data/rev0063_threat_closure_features.csv",
    "data/rev0063_threat_closure_feature_summary.csv",
    "data/rev0063_threat_closure_feature_comparisons.csv",
    "data/rev0063_threat_closure_legacy_life40_selfdeck_cases.csv",
    "data/rev0063_threat_closure_guarded_life40_win_cases.csv",
    "data/rev0063_threat_closure_stdout.txt",
    "data/rev0063_test_report.txt",
    "data/rev0063_smoke.txt",
    "data/rev0063_audit_stdout.txt",
    "data/rev0063_inherited_audit_report.json",
    "data/rev0063_artifact_audit.json",
    "data/rev0063_artifact_audit_stdout.txt",
    "data/rev0063_validation_summary.json",
]

MAX_ROWS = {
    "data/rev0063_threat_closure_games.csv": 160,
    "data/rev0063_threat_closure_forensics.csv": 160,
    "data/rev0063_threat_closure_features.csv": 160,
    "data/rev0063_threat_closure_cpp_transition_sample.csv": 260,
    "data/rev0063_threat_closure_legacy_life40_selfdeck_cases.csv": 65,
    "data/rev0063_threat_closure_guarded_life40_win_cases.csv": 65,
}


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=["data/rev0063*_cpp_transitions.csv", "data/rev0063*_transition_rows.csv"],
        max_csv_rows=MAX_ROWS,
    )
    out = DATA / "rev0063_artifact_audit.json"
    out.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
