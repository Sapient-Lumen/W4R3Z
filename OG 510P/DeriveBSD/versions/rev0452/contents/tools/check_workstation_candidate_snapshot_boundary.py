#!/usr/bin/env python3
"""Guardrail for workstation successor candidates staying immutable snapshots."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md": ["candidate_snapshot = immutable", "later_edits = new-candidate-required", "immutable candidate snapshot"],
    "adrs/ADR-0200-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md": ["candidate_snapshot = immutable", "later_edits = new-candidate-required", "immutable snapshot"],
    "docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "candidate_snapshot"],
    "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "new candidate"],
    "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "new candidate"],
    "docs/606-workstation-imported-foreign-documents-stay-view-first.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "immutable successor candidate"],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "immutable successor candidate"],
    "docs/179-portals-and-powerbox.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md"],
    "docs/199-intent-routing-and-plumbing.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "immutable snapshot"],
    "docs/410-desktop-viability-checklist.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "new candidate"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "immutable snapshot"],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md"],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "new candidate"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0200", "candidate_snapshot = immutable"],
    "docs/99-llm-runbook.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "check_workstation_candidate_snapshot_boundary.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_candidate_snapshot_boundary.py", "immutable-candidate / resnapshot boundary"],
    "docs/110-juicy-os-lessons.md": ["Successor candidates should be immutable snapshots, not moving file pointers", "docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md"],
    "README.md": ["docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md", "candidate_snapshot", "later_edits"],
    "spec/content.reintegrate.plan.schema.json": ['"candidate_snapshot"', '"immutable"', '"later_edits"', '"new-candidate-required"'],
    "spec/content.reintegrate.receipt.schema.json": ['"candidate_snapshot"', '"immutable"', '"later_edits"', '"new-candidate-required"'],
    "spec/examples/content.reintegrate.plan.json": ['"candidate_snapshot": "immutable"', '"later_edits": "new-candidate-required"'],
    "spec/examples/content.reintegrate.receipt.json": ['"candidate_snapshot": "immutable"', '"later_edits": "new-candidate-required"'],
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
    print("Workstation candidate snapshot boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
