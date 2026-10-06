#!/usr/bin/env python3
"""Guardrail for workstation candidate supersession staying same-origin and self-describing."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md": ["supersession_scope = same-authoritative-origin-only", "superseded_candidate_digest", "superseded_authoritative_origin_digest", "silently downgrade to `mode = none`"],
    "adrs/ADR-0202-workstation-candidate-supersession-stays-same-origin-and-self-describing.md": ["supersession_scope = same-authoritative-origin-only", "superseded_candidate_digest", "superseded_authoritative_origin_digest", "same authoritative origin"],
    "docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "same-authoritative-origin-only"],
    "docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "same-origin"],
    "docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "same authoritative origin"],
    "docs/179-portals-and-powerbox.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md"],
    "docs/199-intent-routing-and-plumbing.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "same-authoritative-origin-only"],
    "docs/410-desktop-viability-checklist.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "superseded_candidate_digest"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "superseded_candidate_digest"],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "same-authoritative-origin-only"],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "cross-origin"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0202", "supersession_scope = same-authoritative-origin-only"],
    "docs/99-llm-runbook.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "check_workstation_candidate_same_origin_boundary.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_candidate_same_origin_boundary.py", "same-origin candidate-supersession boundary"],
    "docs/110-juicy-os-lessons.md": ["Candidate supersession should stay same-origin and self-describing", "docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md"],
    "README.md": ["docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md", "supersession_scope", "superseded_candidate_digest"],
    "spec/content.reintegrate.plan.schema.json": ['"supersession_scope"', '"same-authoritative-origin-only"', '"superseded_candidate_digest"', '"superseded_authoritative_origin_digest"'],
    "spec/content.reintegrate.receipt.schema.json": ['"supersession_scope"', '"same-authoritative-origin-only"', '"superseded_candidate_digest"', '"superseded_authoritative_origin_digest"'],
    "spec/examples/content.reintegrate.plan.json": ['"supersession_scope": "same-authoritative-origin-only"', '"superseded_candidate_digest"', '"superseded_authoritative_origin_digest"'],
    "spec/examples/content.reintegrate.receipt.json": ['"supersession_scope": "same-authoritative-origin-only"', '"superseded_candidate_digest"', '"superseded_authoritative_origin_digest"'],
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
    print("Workstation candidate same-origin supersession boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
