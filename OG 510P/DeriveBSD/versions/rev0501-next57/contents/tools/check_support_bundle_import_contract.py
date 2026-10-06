#!/usr/bin/env python3
"""Guardrail for typed support-bundle intake specialization schemas.

This checker keeps the archive's official foreign support-bundle intake path
from drifting into either example-only folklore or a second import subsystem.
"""
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

    plan_schema = load_json("spec/content.import.support-bundle.plan.schema.json")
    receipt_schema = load_json("spec/content.import.support-bundle.receipt.schema.json")

    def has_ref(schema: dict, ref: str) -> bool:
        return any(isinstance(part, dict) and part.get("$ref") == ref for part in schema.get("allOf") or [])

    if not has_ref(plan_schema, "content.import.plan.schema.json"):
        errors.append("spec/content.import.support-bundle.plan.schema.json must specialize content.import.plan.schema.json")
    if not has_ref(receipt_schema, "content.import.receipt.schema.json"):
        errors.append("spec/content.import.support-bundle.receipt.schema.json must specialize content.import.receipt.schema.json")

    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    reg = build_registry(schema_paths)
    errors.extend(validate("spec/content.import.support-bundle.plan.schema.json", "spec/examples/content.import.support-bundle.plan.json", reg))
    errors.extend(validate("spec/content.import.support-bundle.receipt.schema.json", "spec/examples/content.import.support-bundle.receipt.json", reg))

    plan = load_json("spec/examples/content.import.support-bundle.plan.json")
    receipt = load_json("spec/examples/content.import.support-bundle.receipt.json")

    if plan.get("kind") != "content.import.plan":
        errors.append("support-bundle intake plan must keep kind = content.import.plan")
    if receipt.get("kind") != "content.import.receipt":
        errors.append("support-bundle intake receipt must keep kind = content.import.receipt")

    prefer = []
    for op in plan.get("operations") or []:
        if op.get("op") == "classify" and op.get("tool") == "bundle.preview":
            prefer = (op.get("params") or {}).get("prefer_members") or []
            break
    for member in [
        "meta/incident.timeline.json",
        "meta/incident.bundle.json",
        "meta/bundle.payload.manifest.json",
    ]:
        if member not in prefer:
            errors.append(f"support-bundle plan missing preview member {member}")

    metadata = receipt.get("metadata") or {}
    if metadata.get("transport") != "bundle-rehydration":
        errors.append("support-bundle receipt metadata.transport must be bundle-rehydration")
    if metadata.get("status") not in {"preserved", "rehydrated"}:
        errors.append("support-bundle receipt metadata.status must be preserved or rehydrated")

    doc_checks = {
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "typed support-bundle intake shapes",
            "generic `content.import.*` lane",
            "`zip` remains a compatibility adapter",
        ],
        "docs/498-safe-open-support-bundle-intake-and-repro-boundary.md": [
            "typed support-bundle plan / receipt profiles",
            "not a new import authority kind",
            "canonical `tar.zst` handoff",
        ],
        "docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md": [
            "typed profiles",
            "do **not** introduce new `kind` values",
            "generic `content.import.*` lane",
            "`zip` still exists as a compatibility adapter",
        ],
        "docs/99-llm-runbook.md": [
            "typed specialization of the generic import lane",
            "tools/check_support_bundle_import_contract.py",
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

    print("Typed support-bundle intake contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
