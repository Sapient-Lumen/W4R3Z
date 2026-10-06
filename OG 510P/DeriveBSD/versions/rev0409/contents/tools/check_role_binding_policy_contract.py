#!/usr/bin/env python3
"""Guardrail for the non-interactive role-binding policy-decision join."""
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
        uri = BASE_URI + p.name
        schema = json.loads(p.read_text(encoding="utf-8"))
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
    errors.extend(validate("spec/intent.role.binding.event.schema.json", "spec/examples/intent.role.binding.event.json", reg))
    errors.extend(validate("spec/intent.role.binding.event.schema.json", "spec/examples/intent.role.binding.event.policy-reconcile.json", reg))

    event = load_json("spec/examples/intent.role.binding.event.policy-reconcile.json")
    if event.get("trigger") != "policy-reconcile":
        errors.append("policy role-binding event example must keep trigger = policy-reconcile")
    if not event.get("policy_decision_digest"):
        errors.append("policy role-binding event example must include policy_decision_digest")
    if event.get("consent_receipt_digest"):
        errors.append("policy role-binding event example must not rely on consent_receipt_digest")

    doc_checks = {
        "docs/93-policy-decision-records.md": [
            "policy decision record",
            "policy_decision_digest",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "policy_decision_digest",
            "intent.role.binding.event",
        ],
        "docs/229-evidence-spine-overview.md": [
            "policy_decision_digest",
            "intent.role.binding.event",
        ],
        "docs/474-high-risk-approval-posture-by-profile.md": [
            "explicit admin lane",
            "user-consent prompts and organizational quorum prompts are related but not interchangeable surfaces",
        ],
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": [
            "policy_decision_digest",
            "policy-reconcile",
        ],
        "docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md": [
            "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md",
            "policy_decision_digest",
        ],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": [
            "policy_decision_digest",
            "trigger = policy-reconcile",
        ],
        "docs/99-llm-runbook.md": [
            "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md",
            "tools/check_role_binding_policy_contract.py",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_role_binding_policy_contract.py",
            "policy_decision_digest",
        ],
        "README.md": [
            "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md",
            "policy.decision",
        ],
        "spec/intent.role.binding.event.schema.json": [
            '"policy_decision_digest"',
            '"policy-reconcile"',
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
    print("Role-binding policy-decision contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
