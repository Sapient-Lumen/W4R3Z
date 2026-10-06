#!/usr/bin/env python3
"""Guardrail for role-binding policy apply windows and single-apply consumption semantics."""
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

    schema_text = (ROOT / "spec/intent.role.binding.policy.profile.schema.json").read_text(encoding="utf-8")
    for token in [
        '"must_apply_before"',
        '"max_successful_events"',
        'single-apply',
    ]:
        if token not in schema_text:
            errors.append(f"spec/intent.role.binding.policy.profile.schema.json missing required token: {token}")

    example = load_json("spec/examples/intent.role.binding.policy.profile.json")
    apply = example.get("effective_constraints", {}).get("intent_role_binding_apply", {})
    if not apply.get("must_apply_before"):
        errors.append("role-binding policy profile example must include must_apply_before")
    if apply.get("max_successful_events") != 1:
        errors.append("role-binding policy profile example must keep max_successful_events = 1")

    doc_checks = {
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": [
            "docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md",
            "short-lived single-apply",
        ],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": [
            "docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md",
            "must_apply_before",
            "max_successful_events = 1",
        ],
        "docs/549-role-binding-policy-decisions-bind-exact-mutation.md": [
            "docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md",
            "short-lived single-apply",
        ],
        "docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md": [
            "must_apply_before",
            "max_successful_events",
            "policy_decision_digest",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "short-lived single-apply",
            "must_apply_before",
        ],
        "docs/229-evidence-spine-overview.md": [
            "short-lived single-apply",
            "max_successful_events = 1",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_role_binding_policy_apply_window_contract.py",
            "single-apply remembered-role policy decisions",
        ],
        "docs/99-llm-runbook.md": [
            "docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md",
            "tools/check_role_binding_policy_apply_window_contract.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "Remembered-role non-interactive policy decisions should be short-lived and single-apply",
            "Response wrapping",
            "Temporary security credentials in IAM",
        ],
        "docs/32-curated-references.md": [
            "Vault response wrapping",
            "Temporary security credentials in IAM",
            "kube-apiserver Admission (v1)",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0140",
            "must_apply_before",
        ],
        "README.md": [
            "docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md",
            "short-lived single-apply",
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
    print("Role-binding policy apply-window contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
