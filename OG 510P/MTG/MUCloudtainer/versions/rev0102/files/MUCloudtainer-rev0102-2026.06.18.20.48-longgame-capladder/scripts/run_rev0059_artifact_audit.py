#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0059"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/terminal_decomposition.py",
    "src/muc5/revision_artifacts.py",
    "tests/test_rev0059_decomposition_refactor.py",
    "tests/test_rev0059_revision_artifacts.py",
    "scripts/run_rev0059_seed_disjoint_decomposition.py",
    "scripts/run_rev0059_life20_pilot_stress.py",
    "scripts/run_rev0059_artifact_audit.py",
    "docs/seed_disjoint_decomposition_rev0059.md",
    "docs/life20_pilotstress_rev0059.md",
    "docs/refactor_audit_rev0059.md",
    "docs/priority_reconsideration_rev0059.md",
    "docs/cpp_core_plan_rev0059.md",
    "docs/simulator_rev0059.md",
    "data/rev0059_seed_disjoint_summary.json",
    "data/rev0059_seed_disjoint_games.csv",
    "data/rev0059_seed_disjoint_arm_summary.csv",
    "data/rev0059_seed_disjoint_mechanisms.csv",
    "data/rev0059_seed_disjoint_comparisons.csv",
    "data/rev0059_seed_disjoint_cumulative_comparisons.csv",
    "data/rev0059_seed_disjoint_cpp_transition_sample.csv",
    "data/rev0059_seed_disjoint_cpp_trace_rows.csv",
    "data/rev0059_seed_disjoint_replay_traces.jsonl",
    "data/rev0059_seed_disjoint_replay_results.json",
    "data/rev0059_life20_pilotstress_summary.json",
    "data/rev0059_life20_pilotstress_games.csv",
    "data/rev0059_life20_pilotstress_arm_summary.csv",
    "data/rev0059_life20_pilotstress_ab_delta.csv",
    "data/rev0059_life20_pilotstress_cumulative_delta.csv",
    "data/rev0059_life20_pilotstress_cpp_transition_sample.csv",
    "data/rev0059_life20_pilotstress_cpp_trace_rows.csv",
    "data/rev0059_life20_pilotstress_replay_traces.jsonl",
    "data/rev0059_life20_pilotstress_replay_results.json",
    "data/rev0059_test_report.txt",
    "data/rev0059_smoke.txt",
    "data/rev0059_audit_stdout.txt",
    "data/rev0059_inherited_audit_report.json",
    "data/rev0059_validation_summary.json",
]

MAX_ROWS = {
    "data/rev0059_seed_disjoint_cpp_transition_sample.csv": 240,
    "data/rev0059_life20_pilotstress_cpp_transition_sample.csv": 240,
}


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=["data/rev0059*_cpp_transitions.csv"],
        max_csv_rows=MAX_ROWS,
    )
    out = DATA / "rev0059_artifact_audit.json"
    out.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
