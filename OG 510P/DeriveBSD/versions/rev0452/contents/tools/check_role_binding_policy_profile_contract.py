#!/usr/bin/env python3
"""Guardrail for exact-mutation role-binding policy decisions."""
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
        '"intent_role_binding_request"',
        '"intent_role_binding_apply"',
        '"requested_binding_digest"',
        '"binding_digest"',
        '"require_event_trigger"',
        '"diff_digest"',
    ]:
        if token not in schema_text:
            errors.append(f"spec/intent.role.binding.policy.profile.schema.json missing required token: {token}")

    example = load_json("spec/examples/intent.role.binding.policy.profile.json")
    req = example.get("inputs", {}).get("intent_role_binding_request", {})
    apply = example.get("effective_constraints", {}).get("intent_role_binding_apply", {})
    if req.get("trigger") != "policy-reconcile":
        errors.append("role-binding policy profile example must keep trigger = policy-reconcile")
    if req.get("requested_action") != "updated":
        errors.append("role-binding policy profile example must keep requested_action = updated")
    if not req.get("requested_binding_digest"):
        errors.append("role-binding policy profile example must include requested_binding_digest")
    if not req.get("from_binding_digest"):
        errors.append("role-binding policy profile example must include from_binding_digest for updated requests")
    if apply.get("require_event_trigger") != "policy-reconcile":
        errors.append("role-binding policy profile example must keep require_event_trigger = policy-reconcile")
    if apply.get("apply_mode") != "updated":
        errors.append("role-binding policy profile example must keep apply_mode = updated")
    if not apply.get("binding_digest"):
        errors.append("role-binding policy profile example must include binding_digest")
    if not apply.get("diff_digest"):
        errors.append("role-binding policy profile example must include diff_digest for updated applies")

    doc_checks = {
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": [
            "docs/549-role-binding-policy-decisions-bind-exact-mutation.md",
            "spec/intent.role.binding.policy.profile.schema.json",
        ],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": [
            "docs/549-role-binding-policy-decisions-bind-exact-mutation.md",
            "exact mutation tuple",
        ],
        "docs/549-role-binding-policy-decisions-bind-exact-mutation.md": [
            "inputs.intent_role_binding_request",
            "effective_constraints.intent_role_binding_apply",
            "spec/intent.role.binding.policy.profile.schema.json",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "intent.role.binding.policy.profile",
            "policy_decision_digest",
        ],
        "docs/229-evidence-spine-overview.md": [
            "exact-mutation `intent.role.binding.policy.profile`",
            "policy_decision_digest",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_role_binding_policy_profile_contract.py",
            "exact-mutation role-binding policy profile",
        ],
        "docs/99-llm-runbook.md": [
            "docs/549-role-binding-policy-decisions-bind-exact-mutation.md",
            "tools/check_role_binding_policy_profile_contract.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "Remembered-role policy decisions should bind the exact mutation",
            "Mutating Admission Policy",
            "export-or-import-default-application-associations",
        ],
        "docs/32-curated-references.md": [
            "Mutating Admission Policy",
            "export-or-import-default-application-associations",
            "apiserver-admission.v1",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0139",
            "exact mutation tuple",
        ],
        "README.md": [
            "docs/549-role-binding-policy-decisions-bind-exact-mutation.md",
            "exact-mutation `policy.decision` profile",
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
    print("Role-binding policy exact-mutation profile contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
