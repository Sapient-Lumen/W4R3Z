#!/usr/bin/env python3
"""Guardrail for remembered-role policy-consumed denials carrying a stable recovery_interpretation summary."""
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
    errors.extend(validate("spec/intent.role.binding.event.schema.json", "spec/examples/intent.role.binding.event.write-denied.policy-window.json", reg))
    errors.extend(validate("spec/intent.role.binding.event.write-denied.policy-window.schema.json", "spec/examples/intent.role.binding.event.write-denied.policy-window.json", reg))

    schema_text = (ROOT / "spec/intent.role.binding.event.schema.json").read_text(encoding="utf-8")
    for token in ['"recovery_interpretation"', 'already-applied', 'evidence-only retry/reporting summary']:
        if token not in schema_text:
            errors.append(f"spec/intent.role.binding.event.schema.json missing required token: {token}")

    ex = load_json("spec/examples/intent.role.binding.event.write-denied.policy-window.json")
    if ex.get("reason_code") != "policy-consumed":
        errors.append("policy-window denial example must keep reason_code = policy-consumed")
    if ex.get("recovery_interpretation") != "already-applied":
        errors.append("policy-window denial example must set recovery_interpretation = already-applied")
    notes = str(ex.get("notes") or "")
    for needle in ['recovery_interpretation = already-applied', 'evidence-only', 'same exact mutation retry may be surfaced as already-applied']:
        if needle not in notes:
            errors.append(f"spec/examples/intent.role.binding.event.write-denied.policy-window.json missing note text: {needle}")

    doc_checks = {
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": ["docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md", "recovery_interpretation"],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": ["docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md", "recovery_interpretation"],
        "docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md": ["docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md", "recovery_interpretation"],
        "docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md": ["docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md", "recovery_interpretation"],
        "docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md": ["recovery_interpretation", "already-applied", "evidence-only"],
        "docs/216-incident-snapshots-and-support-bundles.md": ["recovery_interpretation", "docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md"],
        "docs/229-evidence-spine-overview.md": ["recovery_interpretation", "docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md"],
        "docs/98-archive-hygiene.md": ["tools/check_role_binding_policy_recovery_interpretation_contract.py", "recovery_interpretation"],
        "docs/99-llm-runbook.md": ["docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md", "tools/check_role_binding_policy_recovery_interpretation_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Remembered-role retries need a stable recovery interpretation field", "docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0146", "recovery_interpretation"],
        "docs/32-curated-references.md": ["AWS Well-Architected REL04-BP04", "https://docs.aws.amazon.com/wellarchitected/2023-04-10/framework/rel_prevent_interaction_failure_idempotent.html"],
        "README.md": ["docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md", "recovery_interpretation"],
        "docs/00-index.md": ["docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md", "recovery_interpretation"],
        "CHANGELOG.md": ["ADR-0146", "recovery_interpretation"],
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
    print("Role-binding recovery interpretation contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
