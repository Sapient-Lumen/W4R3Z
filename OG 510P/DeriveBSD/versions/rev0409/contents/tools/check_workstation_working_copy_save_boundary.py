#!/usr/bin/env python3
"""Guardrail for workstation working-copy save scope and no implicit source write-back."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md": [
        "default_save_target = working-copy-output",
        "source_writeback = separate-act-required",
        "ordinary save",
    ],
    "adrs/ADR-0198-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md": [
        "default_save_target = working-copy-output",
        "source_writeback = separate-act-required",
        "ordinary “Save” mean",
    ],
    "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "default_save_target",
        "source_writeback",
    ],
    "docs/606-workstation-imported-foreign-documents-stay-view-first.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "source write-back",
    ],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "source write-back",
    ],
    "docs/179-portals-and-powerbox.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "ordinary save",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "working-copy output",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "working-copy output",
    ],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
    ],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "default_save_target",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0198",
        "source write-back",
    ],
    "docs/99-llm-runbook.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "check_workstation_working_copy_save_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_working_copy_save_boundary.py",
        "working-copy save-scope / no-implicit-writeback boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Imported-document authoring should not inherit save-back folklore",
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
    ],
    "README.md": [
        "docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md",
        "default_save_target",
        "source_writeback",
    ],
    "spec/content.working-copy.plan.schema.json": [
        '"boundary": {',
        '"default_save_target": {"type": "string", "const": "working-copy-output"}',
        '"source_writeback": {"type": "string", "const": "separate-act-required"}',
    ],
    "spec/content.working-copy.receipt.schema.json": [
        '"boundary": {',
        '"default_save_target": {"type": "string", "const": "working-copy-output"}',
        '"source_writeback": {"type": "string", "const": "separate-act-required"}',
    ],
    "spec/examples/content.working-copy.plan.json": [
        '"default_save_target": "working-copy-output"',
        '"source_writeback": "separate-act-required"',
    ],
    "spec/examples/content.working-copy.receipt.json": [
        '"default_save_target": "working-copy-output"',
        '"source_writeback": "separate-act-required"',
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Workstation working-copy save boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
