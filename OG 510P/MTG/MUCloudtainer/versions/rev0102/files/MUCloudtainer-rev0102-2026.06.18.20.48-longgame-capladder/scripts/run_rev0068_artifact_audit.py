#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.revision_artifacts import audit_revision_artifacts

REV = "rev0068"
DATA = ROOT / "data"

EXPECTED_PATHS = [
    "src/muc5/package_contract.py",
    "src/muc5/response_matrix.py",
    "tests/test_rev0068_integrity_contract.py",
    "scripts/audit_package_contract.py",
    "scripts/finalize_package.py",
    "scripts/run_rev0068_cloudtainer_audit.py",
    "scripts/run_rev0068_integrity_recheck.py",
    "scripts/run_rev0068_artifact_audit.py",
    "docs/mission_integrity_audit_rev0068.md",
    "docs/evidence_budget_roadmap_rev0068.md",
    "docs/package_contract_rev0068.md",
    "docs/statistical_design_rev0068.md",
    "docs/refactor_audit_rev0068.md",
    "docs/simulator_rev0068.md",
    "docs/priority_reconsideration_rev0068.md",
    "docs/experiment_matrix_rev0068.md",
    "docs/cpp_core_plan_rev0068.md",
    "docs/current_spec_conformance_plan_rev0068.md",
    "docs/muc5_spec.md",
    "data/rev0068_cloudtainer_audit_summary.json",
    "data/rev0068_uploaded_rev0067_inventory.csv",
    "data/rev0068_cloudtainer_audit_stdout.txt",
    "data/rev0068_claim_registry.json",
    "data/rev0068_research_anchors.json",
    "data/rev0068_question_bank.json",
    "data/rev0068_validation_summary.json",
    "data/rev0068_inherited_audit_report.json",
    "data/rev0068_package_contract_semantic_audit.json",
    "data/rev0068_response_matrix_integrity_recheck.json",
    "data/rev0068_response_matrix_integrity_recheck_stdout.txt",
    "data/rev0068_test_report.txt",
    "data/rev0068_smoke.txt",
    "data/rev0068_audit_stdout.txt",
    "environment.json",
    "requirements.txt",
    ".mucignore",
    "README.md",
    "manifest.json",
]


def main() -> None:
    report = audit_revision_artifacts(
        ROOT,
        revision=REV,
        expected_paths=EXPECTED_PATHS,
        forbidden_globs=[
            "data/rev0068*_cpp_transitions.csv",
            "data/rev0068*_transition_rows.csv",
            "data/rev0068*_replay_traces.jsonl",
        ],
        max_csv_rows={"data/rev0068_uploaded_rev0067_inventory.csv": 2000},
    )
    output = DATA / "rev0068_artifact_audit.json"
    output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
