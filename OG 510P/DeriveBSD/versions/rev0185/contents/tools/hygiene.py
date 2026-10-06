#!/usr/bin/env python3
"""Run all lightweight archive hygiene checks.

This is a convenience wrapper so CI or humans can run a single command.

Usage:
  python3 tools/hygiene.py

Exit codes:
  0: all checks passed
  1: at least one check failed
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    [sys.executable, str(ROOT / "tools" / "check_consistency.py")],
    [sys.executable, str(ROOT / "tools" / "lint_spec_schemas.py")],
    [sys.executable, str(ROOT / "tools" / "check_schema_kind_matches_filename.py")],
    [sys.executable, str(ROOT / "tools" / "validate_spec_examples.py")],
    [sys.executable, str(ROOT / "tools" / "check_discovery.py")],
    [sys.executable, str(ROOT / "tools" / "check_meta_doc_discoverability.py")],
    [sys.executable, str(ROOT / "tools" / "check_changelog_format.py")],
    [sys.executable, str(ROOT / "tools" / "check_changelog_artifact_mentions.py")],
    [sys.executable, str(ROOT / "tools" / "check_release_last_updated.py")],
    [sys.executable, str(ROOT / "tools" / "check_must_read_set.py")],
    [sys.executable, str(ROOT / "tools" / "check_doc_metadata.py")],
    [sys.executable, str(ROOT / "tools" / "check_doc_patterns.py")],
    [sys.executable, str(ROOT / "tools" / "check_diff_surface_registry.py")],
    [sys.executable, str(ROOT / "tools" / "check_diff_surface_registry_wiring.py")],
    [sys.executable, str(ROOT / "tools" / "check_diff_review_docs.py")],
    [sys.executable, str(ROOT / "tools" / "check_diff_wiring_risk_flags.py")],
    [sys.executable, str(ROOT / "tools" / "check_juicy_lesson_references.py")],
    [sys.executable, str(ROOT / "tools" / "check_risk_flag_registry.py")],
    [sys.executable, str(ROOT / "tools" / "check_risk_flag_typical_sources.py")],


    [sys.executable, str(ROOT / "tools" / "check_curated_references.py")],
    [sys.executable, str(ROOT / "tools" / "check_release_curated_references.py")],
    [sys.executable, str(ROOT / "tools" / "check_generated_docs.py")],
    [sys.executable, str(ROOT / "tools" / "check_risk_register.py")],
    [sys.executable, str(ROOT / "tools" / "check_open_questions_decisions.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_example_plan_digests.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_receipt_reason_requirements.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_reason_code_registry.py")],



    [sys.executable, str(ROOT / "tools" / "check_spec_example_coverage.py")],
    [sys.executable, str(ROOT / "tools" / "check_version.py")],
]



def run(cmd: list[str]) -> int:
    print(f"==> {' '.join(cmd)}")
    p = subprocess.run(cmd, cwd=ROOT)
    return int(p.returncode)


def main() -> int:
    rc = 0
    for cmd in CHECKS:
        r = run(cmd)
        if r != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
