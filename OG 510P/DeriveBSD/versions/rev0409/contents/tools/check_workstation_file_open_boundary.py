#!/usr/bin/env python3
"""Guardrail for the workstation file-open import / bounded-document-role boundary."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": [
        "import-shaped first, route-shaped second",
        "document_viewing",
        "document_editing",
        "import_receipt_digest",
        "host-open",
    ],
    "adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md": [
        "import-shaped first, route-shaped second",
        "document_viewing",
        "document_editing",
        "import_receipt_digest",
        "open with…",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
        "import_receipt_digest",
        "document open/view/edit",
    ],
    "docs/179-portals-and-powerbox.md": [
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
        "document open/view/edit",
        "role-bound second",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "document_viewing",
        "document_editing",
        "import_receipt_digest",
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "document_viewing",
        "document_editing",
        "import_receipt_digest",
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
    ],
    "docs/539-workstation-intent-routed-uri-opening-floor.md": [
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
        "file-open floor",
    ],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
        "document_viewing",
        "document_editing",
    ],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
        "document_viewing",
        "document_editing",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0195",
        "document_viewing",
        "document_editing",
        "import_receipt_digest",
    ],
    "docs/99-llm-runbook.md": [
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
        "check_workstation_file_open_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_file_open_boundary.py",
        "workstation file-open/import boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Imported documents should route through bounded roles, not host-open fallback",
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
    ],
    "README.md": [
        "docs/605-workstation-file-open-import-and-bounded-document-roles.md",
        "document_viewing",
        "document_editing",
        "giant app-taxonomy",
    ],
    "spec/intent.route.receipt.schema.json": [
        '"import_receipt_digest"',
    ],
    "spec/intent.role.binding.schema.json": [
        '"document_viewing"',
        '"document_editing"',
    ],
    "spec/examples/intent.role.binding.json": [
        '"document_viewing"',
        '"document_editing"',
    ],
    "spec/examples/intent.request.document-view.json": [
        '"action": "view"',
        '"type": "file"',
    ],
    "spec/examples/intent.route.receipt.document-view.json": [
        '"import_receipt_digest"',
        '"target_role": "document_viewing"',
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
    print("Workstation file-open boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
