#!/usr/bin/env python3
"""Guardrail for role-binding compare-and-swap preconditions and stale-write denial evidence."""
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

    for example in [
        "spec/examples/intent.role.binding.event.json",
        "spec/examples/intent.role.binding.event.policy-reconcile.json",
        "spec/examples/intent.role.binding.event.write-denied.precondition.json",
    ]:
        errors.extend(validate("spec/intent.role.binding.event.schema.json", example, reg))

    stale = load_json("spec/examples/intent.role.binding.event.write-denied.precondition.json")
    if stale.get("action") != "write-denied":
        errors.append("precondition denial example must keep action = write-denied")
    if stale.get("reason_code") != "precondition-failed":
        errors.append("precondition denial example must keep reason_code = precondition-failed")
    if not stale.get("observed_binding"):
        errors.append("precondition denial example must include observed_binding")
    if not stale.get("diff"):
        errors.append("precondition denial example must include diff")
    if stale.get("trigger") == "trusted-settings-ui" and not stale.get("consent_receipt_digest"):
        errors.append("trusted-settings-ui precondition denial example must include consent_receipt_digest")
    if "role-binding-precondition-failed" not in (stale.get("risk_flags") or []):
        errors.append("precondition denial example must include risk flag role-binding-precondition-failed")

    doc_checks = {
        "docs/410-desktop-viability-checklist.md": ["precondition-failed", "silently rebasing"],
        "docs/457-workstation-host-ui-and-appvm-boundary.md": ["precondition-failed", "compare-and-swap"],
        "docs/474-high-risk-approval-posture-by-profile.md": ["precondition-failed", "auto-merge"],
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": ["diff.from_binding.digest", "compare-and-swap"],
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": ["reason_code", "observed_binding"],
        "docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md": ["precondition-failed", "silently rebasing"],
        "docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md": ["precondition-failed", "silently rebasing"],
        "docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md": ["precondition-failed", "observed_binding", "compare-and-swap"],
        "docs/216-incident-snapshots-and-support-bundles.md": ["precondition-failed", "observed_binding.digest"],
        "docs/229-evidence-spine-overview.md": ["reason_code", "observed_binding"],
        "docs/98-archive-hygiene.md": ["tools/check_role_binding_precondition_contract.py", "diff.from_binding.digest"],
        "docs/99-llm-runbook.md": ["docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md", "tools/check_role_binding_precondition_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Remembered-default writes need stale-write denial", "docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0136", "precondition-failed"],
        "docs/32-curated-references.md": ["RFC 9110 (`If-Match` and strong validators prevent the lost-update problem)", "Kubernetes optimistic concurrency via `resourceVersion` (only one concurrent update succeeds)"],
        "README.md": ["docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md", "precondition-failed"],
        "spec/intent.role.binding.event.schema.json": ['"reason_code"', '"observed_binding"', '"precondition-failed"'],
        "spec/examples/intent.role.binding.event.write-denied.precondition.json": ['"reason_code": "precondition-failed"', '"observed_binding"', '"role-binding-precondition-failed"'],
        "spec/examples/risk.flag.registry.json": ['"id": "role-binding-precondition-failed"'],
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
    print("Role-binding precondition contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
