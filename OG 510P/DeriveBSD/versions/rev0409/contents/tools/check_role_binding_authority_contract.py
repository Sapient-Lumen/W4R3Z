#!/usr/bin/env python3
"""Guardrail for role-binding authority-lane normalization."""
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

    for example_rel in [
        "spec/examples/intent.role.binding.event.json",
        "spec/examples/intent.role.binding.event.policy-reconcile.json",
        "spec/examples/intent.role.binding.event.support-import.json",
        "spec/examples/intent.role.binding.event.write-denied.precondition.json",
    ]:
        errors.extend(validate("spec/intent.role.binding.event.schema.json", example_rel, reg))

    schema_text = (ROOT / "spec/intent.role.binding.event.schema.json").read_text(encoding="utf-8")
    if '"admin-cli"' in schema_text:
        errors.append("spec/intent.role.binding.event.schema.json must not keep admin-cli in trigger vocabulary")
    for token in ['"trusted-settings-ui"', '"policy-reconcile"', '"support-import"', 'authority/apply lane']:
        if token not in schema_text:
            errors.append(f"spec/intent.role.binding.event.schema.json missing required token: {token}")

    for rel in sorted((ROOT / "spec" / "examples").glob("intent.role.binding.event*.json")):
        text = rel.read_text(encoding="utf-8")
        if '"trigger": "admin-cli"' in text:
            errors.append(f"{rel.relative_to(ROOT)} must not use trigger = admin-cli")

    doc_checks = {
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": ["trigger names the authority lane", "docs/548-role-binding-authority-lanes-not-invocation-surfaces.md"],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": ["source.name` / `source.service_id`", "not a separate trigger vocabulary item"],
        "docs/548-role-binding-authority-lanes-not-invocation-surfaces.md": ["admin-cli", "source.name = derive-rolebind-cli", "trigger = policy-reconcile"],
        "docs/410-desktop-viability-checklist.md": ["authority lanes", "docs/548-role-binding-authority-lanes-not-invocation-surfaces.md"],
        "docs/98-archive-hygiene.md": ["tools/check_role_binding_authority_contract.py", "remove `admin-cli` from `intent.role.binding.event.trigger`"],
        "docs/99-llm-runbook.md": ["docs/548-role-binding-authority-lanes-not-invocation-surfaces.md", "tools/check_role_binding_authority_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Remembered-role triggers should name authority lanes", "policy-csp-applicationdefaults", "Validating Admission Policy"],
        "docs/32-curated-references.md": ["policy-csp-applicationdefaults", "Validating Admission Policy"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0138", "source.*"],
        "README.md": ["docs/548-role-binding-authority-lanes-not-invocation-surfaces.md", "`admin-cli` trigger"],
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
    print("Role-binding authority-lane contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
