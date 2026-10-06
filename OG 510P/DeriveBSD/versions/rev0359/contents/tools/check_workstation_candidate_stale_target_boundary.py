#!/usr/bin/env python3
"""Guardrail for workstation candidate supersession staying head-exact and stale-target fail-closed."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md": ["supersession_target_posture = current-unsuperseded-candidate-only", "stale_target_handling = fail-closed", "retarget to a newer candidate", "current unsuperseded candidate"],
    "adrs/ADR-0203-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md": ["supersession_target_posture = current-unsuperseded-candidate-only", "stale_target_handling = fail-closed", "compare-and-swap", "current unsuperseded candidate"],
    "docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md": ["docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md", "current unsuperseded candidate"],
    "docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md": ["docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md"],
    "docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md": ["docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md", "stale-target rebinding"],
    "docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md": ["docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md", "stale supersession attempts fail closed"],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": ["docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md", "current-head exact"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0203", "supersession_target_posture = current-unsuperseded-candidate-only", "stale_target_handling = fail-closed"],
    "docs/99-llm-runbook.md": ["docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md", "check_workstation_candidate_stale_target_boundary.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_candidate_stale_target_boundary.py", "stale supersession attempts fail closed"],
    "docs/110-juicy-os-lessons.md": ["Candidate supersession should be current-head exact, not stale-target rebinding", "docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md"],
    "README.md": ["docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md", "supersession_target_posture", "stale_target_handling"],
    "spec/content.reintegrate.plan.schema.json": ['"supersession_target_posture"', '"current-unsuperseded-candidate-only"', '"stale_target_handling"', '"fail-closed"'],
    "spec/content.reintegrate.receipt.schema.json": ['"supersession_target_posture"', '"current-unsuperseded-candidate-only"', '"stale_target_handling"', '"fail-closed"'],
    "spec/examples/content.reintegrate.plan.json": ['"supersession_target_posture": "current-unsuperseded-candidate-only"', '"stale_target_handling": "fail-closed"'],
    "spec/examples/content.reintegrate.receipt.json": ['"supersession_target_posture": "current-unsuperseded-candidate-only"', '"stale_target_handling": "fail-closed"'],
}

def main() -> int:
    errors = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Workstation candidate stale-target boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
