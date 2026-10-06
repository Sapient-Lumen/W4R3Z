#!/usr/bin/env python3
"""Guardrail for remembered-role policy-consumed denials carrying the consuming binding digest."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from cube_digest_lib import canonical_digest

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
    errors.extend(validate("spec/intent.role.binding.event.schema.json", "spec/examples/intent.role.binding.event.policy-consume-success.json", reg))
    errors.extend(validate("spec/intent.role.binding.event.write-denied.policy-window.schema.json", "spec/examples/intent.role.binding.event.write-denied.policy-window.json", reg))

    schema_text = (ROOT / "spec/intent.role.binding.event.schema.json").read_text(encoding="utf-8")
    for token in ['"consumed_binding_digest"', 'resulting binding.digest from the earlier successful consuming event', 'evidence-only summary data']:
        if token not in schema_text:
            errors.append(f"spec/intent.role.binding.event.schema.json missing required token: {token}")

    denial = load_json("spec/examples/intent.role.binding.event.write-denied.policy-window.json")
    winner = load_json("spec/examples/intent.role.binding.event.policy-consume-success.json")
    if denial.get("reason_code") != "policy-consumed":
        errors.append("policy-window denial example must keep reason_code = policy-consumed")
    if denial.get("consumed_by_event_id") != winner.get("event_id"):
        errors.append("policy-window denial example consumed_by_event_id must point at the consuming-success example event_id")
    expected_event_digest = canonical_digest(winner)
    if denial.get("consumed_by_event_digest") != expected_event_digest:
        errors.append("policy-window denial example consumed_by_event_digest must equal the canonical digest of the consuming-success example")
    winner_binding = ((winner.get("binding") or {}).get("digest"))
    if denial.get("consumed_binding_digest") != winner_binding:
        errors.append("policy-window denial example consumed_binding_digest must equal the consuming-success example binding.digest")
    if denial.get("recovery_interpretation") == "already-applied" and denial.get("consumed_binding_digest") != winner_binding:
        errors.append("already-applied denial example must keep consumed_binding_digest aligned with the consuming-success binding.digest")
    notes = str(denial.get("notes") or "")
    for needle in ['consumed_binding_digest carries the resulting binding.digest', 'evidence-only summary data']:
        if needle not in notes:
            errors.append(f"spec/examples/intent.role.binding.event.write-denied.policy-window.json missing note text: {needle}")

    doc_checks = {
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": ["docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md", "consumed_binding_digest"],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": ["docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md", "consumed_binding_digest"],
        "docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md": ["docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md", "consumed_binding_digest"],
        "docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md": ["docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md", "consumed_binding_digest"],
        "docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md": ["docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md", "consumed_binding_digest"],
        "docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md": ["consumed_binding_digest", "evidence-only summary data", "Stripe idempotent requests"],
        "docs/216-incident-snapshots-and-support-bundles.md": ["consumed_binding_digest", "docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md"],
        "docs/229-evidence-spine-overview.md": ["consumed_binding_digest", "docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md"],
        "docs/98-archive-hygiene.md": ["tools/check_role_binding_policy_consumption_binding_digest_contract.py", "consumed_binding_digest"],
        "docs/99-llm-runbook.md": ["docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md", "tools/check_role_binding_policy_consumption_binding_digest_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Remembered-role policy-consumed denials should carry the consuming binding digest", "docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0148", "consumed_binding_digest"],
        "README.md": ["docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md", "consumed_binding_digest"],
        "docs/00-index.md": ["docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md", "consumed_binding_digest"],
        "CHANGELOG.md": ["ADR-0148", "consumed_binding_digest"],
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
    print("Role-binding policy-consumed binding-digest contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
