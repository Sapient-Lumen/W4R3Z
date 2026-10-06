#!/usr/bin/env python3
"""Guardrail for role-binding support-import provenance joins and subtype schemas."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
BASE_URI = "https://derivebsd.local/spec/"


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def build_registry(schema_paths: list[Path]) -> Registry:
    reg: Registry = Registry()
    for p in schema_paths:
        schema = json.loads(p.read_text(encoding="utf-8"))
        uri = BASE_URI + p.name
        if isinstance(schema, dict) and "$id" not in schema:
            schema = dict(schema)
            schema["$id"] = uri
        reg = reg.with_resource(uri, Resource.from_contents(schema, default_specification=DRAFT202012))
    return reg


def validate(schema_rel: str, example_rel: str, reg: Registry) -> list[str]:
    schema = load_json(schema_rel)
    if "$id" not in schema:
        schema = dict(schema)
        schema["$id"] = BASE_URI + Path(schema_rel).name
    instance = load_json(example_rel)
    errs = sorted(Draft202012Validator(schema, registry=reg).iter_errors(instance), key=lambda e: list(e.absolute_path))
    out: list[str] = []
    for e in errs[:20]:
        path = "/".join(str(x) for x in e.absolute_path) or "<root>"
        out.append(f"{example_rel} invalid at {path}: {e.message}")
    if len(errs) > 20:
        out.append(f"{example_rel} invalid with {len(errs) - 20} additional errors")
    return out


def main() -> int:
    errors: list[str] = []
    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    reg = build_registry(schema_paths)

    pairs = [
        ("spec/intent.role.binding.event.schema.json", "spec/examples/intent.role.binding.event.support-import.json"),
        ("spec/intent.role.binding.event.support-import.schema.json", "spec/examples/intent.role.binding.event.support-import.json"),
        ("spec/intent.role.binding.event.policy-reconcile.schema.json", "spec/examples/intent.role.binding.event.policy-reconcile.json"),
        ("spec/intent.role.binding.event.write-denied.precondition.schema.json", "spec/examples/intent.role.binding.event.write-denied.precondition.json"),
    ]
    for schema_rel, example_rel in pairs:
        errors.extend(validate(schema_rel, example_rel, reg))

    support = load_json("spec/examples/intent.role.binding.event.support-import.json")
    if support.get("trigger") != "support-import":
        errors.append("support-import role-binding event example must keep trigger = support-import")
    if not support.get("import_receipt_digest"):
        errors.append("support-import role-binding event example must include import_receipt_digest")
    if support.get("consent_receipt_digest"):
        errors.append("support-import role-binding event example must not rely on consent_receipt_digest")

    doc_checks = {
        "docs/216-incident-snapshots-and-support-bundles.md": ["import_receipt_digest", "intent.role.binding.event"],
        "docs/229-evidence-spine-overview.md": ["import_receipt_digest", "intent.role.binding.event"],
        "docs/410-desktop-viability-checklist.md": ["import_receipt_digest", "support-import"],
        "docs/457-workstation-host-ui-and-appvm-boundary.md": ["import_receipt_digest", "support-import"],
        "docs/498-safe-open-support-bundle-intake-and-repro-boundary.md": ["content.import.receipt"],
        "docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md": ["content.import.receipt"],
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": ["import_receipt_digest", "support-import"],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": ["import_receipt_digest", "support-import"],
        "docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md": ["import_receipt_digest", "support-import"],
        "docs/547-role-binding-support-import-join-via-content-import-receipt.md": ["import_receipt_digest", "content.import.receipt"],
        "docs/98-archive-hygiene.md": ["tools/check_role_binding_import_contract.py", "import_receipt_digest"],
        "docs/99-llm-runbook.md": ["docs/547-role-binding-support-import-join-via-content-import-receipt.md", "tools/check_role_binding_import_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Imported remembered-role changes need an import-receipt join", "docs/547-role-binding-support-import-join-via-content-import-receipt.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0137", "import_receipt_digest"],
        "docs/32-curated-references.md": ["Qubes OS backup/restore guide (explicit restore workflow and verify-only restore path)"],
        "README.md": ["docs/547-role-binding-support-import-join-via-content-import-receipt.md", "import_receipt_digest"],
        "spec/intent.role.binding.event.schema.json": ['"import_receipt_digest"', '"support-import"'],
        "spec/intent.role.binding.event.support-import.schema.json": ['"support-import"', '"import_receipt_digest"'],
        "spec/examples/intent.role.binding.event.support-import.json": ['"trigger": "support-import"', '"import_receipt_digest"'],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Role-binding support-import contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
