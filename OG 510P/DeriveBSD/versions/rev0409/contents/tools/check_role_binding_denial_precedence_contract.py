#!/usr/bin/env python3
"""Guardrail for remembered-role denial precedence across policy-window checks and compare-and-swap."""
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

    errors.extend(validate("spec/intent.role.binding.event.schema.json", "spec/examples/intent.role.binding.event.write-denied.precondition.json", reg))
    errors.extend(validate("spec/intent.role.binding.event.schema.json", "spec/examples/intent.role.binding.event.write-denied.policy-window.json", reg))
    errors.extend(validate("spec/intent.role.binding.event.write-denied.precondition.schema.json", "spec/examples/intent.role.binding.event.write-denied.precondition.json", reg))
    errors.extend(validate("spec/intent.role.binding.event.write-denied.policy-window.schema.json", "spec/examples/intent.role.binding.event.write-denied.policy-window.json", reg))

    schema_text = (ROOT / "spec/intent.role.binding.event.schema.json").read_text(encoding="utf-8")
    for token in [
        '"policy-denied"',
        '"policy-consumed"',
        '"policy-expired"',
        '"precondition-failed"',
        'precede precondition-failed',
    ]:
        if token not in schema_text:
            errors.append(f"spec/intent.role.binding.event.schema.json missing required token: {token}")

    pre = load_json("spec/examples/intent.role.binding.event.write-denied.precondition.json")
    if pre.get("reason_code") != "precondition-failed":
        errors.append("precondition denial example must keep reason_code = precondition-failed")
    if not pre.get("observed_binding"):
        errors.append("precondition denial example must include observed_binding")

    pol = load_json("spec/examples/intent.role.binding.event.write-denied.policy-window.json")
    if pol.get("reason_code") != "policy-consumed":
        errors.append("policy-window denial example must keep reason_code = policy-consumed to exercise precedence over later expiry")
    if pol.get("observed_binding") is not None:
        errors.append("policy-window denial example must not include observed_binding when policy-window denial wins before compare-and-swap")
    notes = str(pol.get("notes") or "")
    for needle in ["policy-consumed wins before compare-and-swap", "does not later decay into policy-expired"]:
        if needle not in notes:
            errors.append(f"spec/examples/intent.role.binding.event.write-denied.policy-window.json missing note text: {needle}")

    doc_checks = {
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "policy-window reasons win before `precondition-failed`"],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "normal request checks", "precondition-failed"],
        "docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "`precondition-failed` is now the *last* denial"],
        "docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "`policy-consumed` stays the winning denial"],
        "docs/551-role-binding-policy-decisions-need-unique-instance-identity.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "`policy-consumed` rather than decaying into a mere expiry story"],
        "docs/552-role-binding-policy-window-denials-need-typed-reasons.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "`policy-consumed` wins before `policy-expired`", "win before `precondition-failed`"],
        "docs/553-role-binding-denial-precedence-between-policy-and-precondition.md": ["`policy-denied`", "`policy-consumed`", "`policy-expired`", "`precondition-failed`", "normal request checks", "replay evidence"],
        "docs/216-incident-snapshots-and-support-bundles.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "reason_code = precondition-failed"],
        "docs/229-evidence-spine-overview.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "policy-window validity winning before compare-and-swap"],
        "docs/98-archive-hygiene.md": ["tools/check_role_binding_denial_precedence_contract.py", "policy-consumed` / `policy-expired`"],
        "docs/99-llm-runbook.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "tools/check_role_binding_denial_precedence_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Remembered-role denial precedence should be deterministic", "docs/553-role-binding-denial-precedence-between-policy-and-precondition.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0143", "`policy-denied`, then `policy-consumed`, then `policy-expired`, and only then `precondition-failed`"],
        "README.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "policy-window validity wins before compare-and-swap"],
        "docs/00-index.md": ["docs/553-role-binding-denial-precedence-between-policy-and-precondition.md", "policy-consumed"],
        "CHANGELOG.md": ["ADR-0143", "policy-consumed"],
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
    print("Role-binding denial precedence contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
