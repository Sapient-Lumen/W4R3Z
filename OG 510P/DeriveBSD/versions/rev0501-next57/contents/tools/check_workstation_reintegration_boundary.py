#!/usr/bin/env python3
"""Guardrail for workstation working-copy reintegration staying explicit and new-version-shaped."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md": ["content.reintegrate.plan", "content.reintegrate.receipt", "local-successor-candidate", "register-successor-candidate", "replace_in_place = forbidden", "upstream_finalize = separate-adapter-required"],
    "adrs/ADR-0199-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md": ["content.reintegrate.plan", "content.reintegrate.receipt", "same-authoritative-origin", "register-successor-candidate", "replace_in_place = forbidden"],
    "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "local successor candidate"],
    "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "content.reintegrate.receipt"],
    "docs/606-workstation-imported-foreign-documents-stay-view-first.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "successor candidate"],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "successor candidate"],
    "docs/179-portals-and-powerbox.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md"],
    "docs/199-intent-routing-and-plumbing.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "successor candidate"],
    "docs/410-desktop-viability-checklist.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "content.reintegrate.receipt"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "content.reintegrate.receipt"],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md"],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "successor candidate"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0199", "content.reintegrate.plan"],
    "docs/99-llm-runbook.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "check_workstation_reintegration_boundary.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_reintegration_boundary.py", "working-copy reintegration / successor-candidate boundary"],
    "docs/110-juicy-os-lessons.md": ["Explicit reintegration should register a successor candidate, not replace in place", "docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md"],
    "README.md": ["docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md", "content.reintegrate.plan", "local-successor-candidate"],
    "spec/content.reintegrate.plan.schema.json": ['"content.reintegrate.plan"', '"same-authoritative-origin"', '"local-successor-candidate"', '"replace_in_place"', '"upstream_finalize"', '"register-successor-candidate"'],
    "spec/content.reintegrate.receipt.schema.json": ['"content.reintegrate.receipt"', '"successor-candidate-of"', '"local-successor-candidate"'],
    "spec/examples/content.reintegrate.plan.json": ['"kind": "content.reintegrate.plan"', '"scope": "same-authoritative-origin"', '"action": "register-successor-candidate"'],
    "spec/examples/content.reintegrate.receipt.json": ['"kind": "content.reintegrate.receipt"', '"relationship": "successor-candidate-of"', '"status": "ok"'],
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
    print("Workstation reintegration boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
