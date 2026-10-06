#!/usr/bin/env python3
"""Guardrail for unique issuance identity on remembered-role policy decisions."""
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

    errors.extend(validate("spec/intent.role.binding.policy.profile.schema.json", "spec/examples/intent.role.binding.policy.profile.json", reg))
    errors.extend(validate("spec/policy.decision.schema.json", "spec/examples/intent.role.binding.policy.profile.json", reg))

    schema_text = (ROOT / "spec/intent.role.binding.policy.profile.schema.json").read_text(encoding="utf-8")
    for token in [
        '"decision_instance_id"',
        'independently issuable',
        'same digest',
    ]:
        if token not in schema_text:
            errors.append(f"spec/intent.role.binding.policy.profile.schema.json missing required token: {token}")

    example = load_json("spec/examples/intent.role.binding.policy.profile.json")
    if not example.get("decision_instance_id"):
        errors.append("role-binding policy profile example must include decision_instance_id")

    doc_checks = {
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": [
            "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md",
            "decision_instance_id",
        ],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": [
            "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md",
            "decision_instance_id",
        ],
        "docs/549-role-binding-policy-decisions-bind-exact-mutation.md": [
            "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md",
            "decision_instance_id",
        ],
        "docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md": [
            "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md",
            "decision_instance_id",
        ],
        "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md": [
            "decision_instance_id",
            "policy_decision_digest",
            "same exact mutation tuple",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "decision_instance_id",
            "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md",
        ],
        "docs/229-evidence-spine-overview.md": [
            "decision_instance_id",
            "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_role_binding_policy_instance_identity_contract.py",
            "unique issuance identity",
        ],
        "docs/99-llm-runbook.md": [
            "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md",
            "tools/check_role_binding_policy_instance_identity_contract.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "Remembered-role policy decisions need unique instance identity",
            "kube-apiserver Admission (v1)",
            "Vault response wrapping",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0141",
            "decision_instance_id",
        ],
        "README.md": [
            "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md",
            "decision_instance_id",
        ],
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
    print("Role-binding policy instance-identity contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
