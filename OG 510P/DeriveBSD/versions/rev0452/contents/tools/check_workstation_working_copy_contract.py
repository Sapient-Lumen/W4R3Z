#!/usr/bin/env python3
"""Guardrail for workstation working-copy receipts and edit-route joins."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md": [
        "content.working-copy.plan",
        "content.working-copy.receipt",
        "working_copy_receipt_digest",
        "document_editing",
    ],
    "adrs/ADR-0197-workstation-working-copy-receipts-and-edit-route-joins.md": [
        "content.working-copy.plan",
        "content.working-copy.receipt",
        "working_copy_receipt_digest",
        "intent.request.context",
    ],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "working_copy_receipt_digest",
    ],
    "docs/606-workstation-imported-foreign-documents-stay-view-first.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "content.working-copy.plan",
        "working_copy_receipt_digest",
    ],
    "docs/179-portals-and-powerbox.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "working_copy_receipt_digest",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "content.working-copy.receipt",
        "working_copy_receipt_digest",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "working_copy_receipt_digest",
        "content.working-copy.receipt",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "working_copy_receipt_digest",
        "content.working-copy.receipt",
    ],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "working_copy_receipt_digest",
    ],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "working_copy_receipt_digest",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0197",
        "working_copy_receipt_digest",
    ],
    "docs/99-llm-runbook.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "check_workstation_working_copy_contract.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_working_copy_contract.py",
        "working-copy receipt / edit-route join boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Typed working-copy receipts keep edit routes honest",
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
    ],
    "README.md": [
        "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md",
        "content.working-copy.plan",
        "working_copy_receipt_digest",
    ],
    "spec/content.working-copy.plan.schema.json": [
        '"kind": {"const": "content.working-copy.plan"}',
        '"source_output_digest"',
    ],
    "spec/content.working-copy.receipt.schema.json": [
        '"kind": {"const": "content.working-copy.receipt"}',
        '"relationship": {"type": "string", "const": "working-copy-of"}',
    ],
    "spec/intent.request.schema.json": [
        '"working_copy_receipt_digest"',
    ],
    "spec/intent.route.receipt.schema.json": [
        '"working_copy_receipt_digest"',
    ],
    "spec/intent.route.receipt.document-edit-allow.schema.json": [
        '"target_role": {"const": "document_editing"}',
        '"working_copy_receipt_digest"',
    ],
    "spec/examples/content.working-copy.plan.json": [
        '"kind": "content.working-copy.plan"',
        '"source_output_digest"',
    ],
    "spec/examples/content.working-copy.receipt.json": [
        '"kind": "content.working-copy.receipt"',
        '"relationship": "working-copy-of"',
    ],
    "spec/examples/intent.request.document-edit.json": [
        '"working_copy_receipt_digest"',
    ],
    "spec/examples/intent.route.receipt.document-edit-allow.json": [
        '"target_role": "document_editing"',
        '"working_copy_receipt_digest"',
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
    print("Workstation working-copy contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
