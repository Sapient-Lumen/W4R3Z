#!/usr/bin/env python3
"""Guardrail for workstation candidate supersession staying explicit and no-latest-wins."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md": ["candidate_ordering = explicit-supersession-only", "recency_precedence = forbidden", "supersedes_receipt_digest", "latest-wins-shaped"],
    "adrs/ADR-0201-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md": ["candidate_ordering = explicit-supersession-only", "recency_precedence = forbidden", "supersedes_receipt_digest"],
    "docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md", "explicit supersession"],
    "docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md", "supersedes_receipt_digest"],
    "docs/179-portals-and-powerbox.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md"],
    "docs/199-intent-routing-and-plumbing.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md", "explicit supersession"],
    "docs/410-desktop-viability-checklist.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md", "recency alone"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md", "supersedes_receipt_digest"],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md"],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md", "explicit supersession"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0201", "candidate_ordering = explicit-supersession-only"],
    "docs/99-llm-runbook.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md", "check_workstation_candidate_supersession_boundary.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_candidate_supersession_boundary.py", "explicit-candidate-supersession / no-latest-wins boundary"],
    "docs/110-juicy-os-lessons.md": ["Candidate supersession should be explicit, not newest-wins folklore", "docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md"],
    "README.md": ["docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md", "candidate_ordering", "recency_precedence"],
    "spec/content.reintegrate.plan.schema.json": ['"candidate_ordering"', '"explicit-supersession-only"', '"recency_precedence"', '"forbidden"', '"supersedes_receipt_digest"'],
    "spec/content.reintegrate.receipt.schema.json": ['"candidate_ordering"', '"explicit-supersession-only"', '"recency_precedence"', '"forbidden"', '"supersedes_receipt_digest"'],
    "spec/examples/content.reintegrate.plan.json": ['"candidate_ordering": "explicit-supersession-only"', '"recency_precedence": "forbidden"', '"supersedes_receipt_digest"'],
    "spec/examples/content.reintegrate.receipt.json": ['"candidate_ordering": "explicit-supersession-only"', '"recency_precedence": "forbidden"', '"supersedes_receipt_digest"'],
}

def main() -> int:
    errors=[]
    for rel, needles in DOCS.items():
        text=(ROOT/rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for e in errors: print(f"ERROR: {e}")
        return 1
    print("Workstation candidate supersession boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
