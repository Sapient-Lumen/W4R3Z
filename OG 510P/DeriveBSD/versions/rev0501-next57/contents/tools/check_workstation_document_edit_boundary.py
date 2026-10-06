#!/usr/bin/env python3
"""Guardrail for the workstation imported-document view-first / working-copy boundary."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/606-workstation-imported-foreign-documents-stay-view-first.md": [
        "view-first",
        "working copy",
        "document_viewing",
        "document_editing",
        "save back over the imported original",
    ],
    "adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md": [
        "view-first",
        "working copy",
        "document_editing",
        "save back over the imported original",
    ],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": [
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
        "view-first",
    ],
    "docs/179-portals-and-powerbox.md": [
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
        "view-first",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
        "working-copy",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "view-first",
        "work on a copy",
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "view-first",
        "work on a copy",
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
    ],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
        "document_editing",
    ],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
        "document_editing",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0196",
        "view-first",
        "working-copy",
    ],
    "docs/99-llm-runbook.md": [
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
        "check_workstation_document_edit_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_document_edit_boundary.py",
        "view-first / working-copy boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Imported foreign documents should stay view-first and become editable only via an explicit working copy",
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
    ],
    "README.md": [
        "docs/606-workstation-imported-foreign-documents-stay-view-first.md",
        "view-first",
        "work on a copy",
    ],
    "spec/intent.request.document-edit.schema.json": [
        '"action": {"const": "edit"}',
    ],
    "spec/intent.route.receipt.document-edit-deny.schema.json": [
        '"decision": {"const": "deny"}',
        '"import_receipt_digest"',
    ],
    "spec/examples/intent.request.document-edit.json": [
        '"action": "edit"',
        '"type": "file"',
    ],
    "spec/examples/intent.route.receipt.document-edit-deny.json": [
        '"decision": "deny"',
        '"import_receipt_digest"',
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
    print("Workstation document-edit boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
