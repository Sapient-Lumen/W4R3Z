#!/usr/bin/env python3
"""Guardrail for the interactive workstation role-binding consent lane."""
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
    errors.extend(validate("spec/intent.role.binding.consent.request.profile.schema.json", "spec/examples/intent.role.binding.consent.request.profile.json", reg))
    errors.extend(validate("spec/intent.role.binding.consent.receipt.profile.schema.json", "spec/examples/intent.role.binding.consent.receipt.profile.json", reg))
    errors.extend(validate("spec/intent.role.binding.event.schema.json", "spec/examples/intent.role.binding.event.json", reg))

    consent_req = load_json("spec/examples/intent.role.binding.consent.request.profile.json")
    action = consent_req.get("action") or {}
    if action.get("kind") != "change.confirm":
        errors.append("role-binding consent request example must keep action.kind = change.confirm")
    for key in ["plan_digest", "artifact_digest"]:
        if not action.get(key):
            errors.append(f"role-binding consent request example missing action.{key}")
    if consent_req.get("secure_attention_required") is not True:
        errors.append("role-binding consent request example must require secure_attention_required = true")

    consent_receipt = load_json("spec/examples/intent.role.binding.consent.receipt.profile.json")
    if consent_receipt.get("method") == "auto":
        errors.append("role-binding consent receipt example must not use method = auto")
    if consent_receipt.get("outcome") not in {"approved", "denied", "timeout"}:
        errors.append("role-binding consent receipt example must keep outcome on the generic consent lane")

    event = load_json("spec/examples/intent.role.binding.event.json")
    if event.get("trigger") == "trusted-settings-ui" and event.get("action") in {"updated", "write-denied"} and not event.get("consent_receipt_digest"):
        errors.append("trusted-settings-ui role-binding event example must include consent_receipt_digest")

    doc_checks = {
        "docs/256-consent-ux-contract.md": [
            "intent.role.binding.consent.request.profile",
            "intent.role.binding.consent.receipt.profile",
            "method must not be `auto`",
        ],
        "docs/410-desktop-viability-checklist.md": [
            "docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md",
            "non-`auto` approval evidence",
        ],
        "docs/457-workstation-host-ui-and-appvm-boundary.md": [
            "intent.role.binding` consent profiles",
            "ambient write authority",
        ],
        "docs/474-high-risk-approval-posture-by-profile.md": [
            "role-default change",
            "intent.role.binding` consent profiles",
        ],
        "docs/543-role-binding-event-as-durable-mutation-evidence.md": [
            "consent_receipt_digest",
            "generic consent substrate",
        ],
        "docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md": [
            "intent.role.binding.consent.request.profile",
            "intent.role.binding.consent.receipt.profile",
            "consent_receipt_digest",
        ],
        "docs/99-llm-runbook.md": [
            "docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md",
            "tools/check_workstation_role_binding_consent_contract.py",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_workstation_role_binding_consent_contract.py",
            "consent_receipt_digest",
        ],
        "README.md": [
            "docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md",
            "consent.receipt",
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
    print("Workstation role-binding consent contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
