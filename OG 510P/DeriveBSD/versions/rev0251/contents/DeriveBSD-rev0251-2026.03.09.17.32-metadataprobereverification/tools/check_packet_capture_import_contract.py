#!/usr/bin/env python3
"""Guardrail for typed packet-capture strong-artifact intake schemas.

This checker keeps stronger packet-capture artifacts on the generic safe-open
import lane and prevents the archive from drifting back into host-open `.pcap`
folklore or silent promotion of sideband/decryption-bearing originals.
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

    plan_schema = load_json("spec/content.import.packet-capture.plan.schema.json")
    receipt_schema = load_json("spec/content.import.packet-capture.receipt.schema.json")

    def has_ref(schema: dict, ref: str) -> bool:
        return any(isinstance(part, dict) and part.get("$ref") == ref for part in schema.get("allOf") or [])

    if not has_ref(plan_schema, "content.import.plan.schema.json"):
        errors.append("spec/content.import.packet-capture.plan.schema.json must specialize content.import.plan.schema.json")
    if not has_ref(receipt_schema, "content.import.receipt.schema.json"):
        errors.append("spec/content.import.packet-capture.receipt.schema.json must specialize content.import.receipt.schema.json")

    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    reg = build_registry(schema_paths)
    errors.extend(validate("spec/content.import.packet-capture.plan.schema.json", "spec/examples/content.import.packet-capture.plan.json", reg))
    errors.extend(validate("spec/content.import.packet-capture.receipt.schema.json", "spec/examples/content.import.packet-capture.receipt.json", reg))

    plan = load_json("spec/examples/content.import.packet-capture.plan.json")
    receipt = load_json("spec/examples/content.import.packet-capture.receipt.json")

    if plan.get("kind") != "content.import.plan":
        errors.append("packet-capture import plan must keep kind = content.import.plan")
    if receipt.get("kind") != "content.import.receipt":
        errors.append("packet-capture import receipt must keep kind = content.import.receipt")

    required_plan_ops = {
        ("scan", "packet-capture.scan"),
        ("classify", "packet-capture.classify"),
        ("strip-metadata", "packet-capture.normalize"),
    }
    plan_ops = {(op.get("op"), op.get("tool")) for op in plan.get("operations") or []}
    for item in sorted(required_plan_ops):
        if item not in plan_ops:
            errors.append(f"packet-capture import plan missing operation/tool pair: {item[0]} / {item[1]}")

    execution = plan.get("execution") or {}
    if execution != {"isolation": "microvm", "network": "none", "lifetime": "disposable"}:
        errors.append("packet-capture import plan execution must be microvm + none + disposable")

    outputs = receipt.get("outputs") or []
    label_sets = [o.get("labels") or {} for o in outputs]
    if not any(ls.get("class") == "packet-capture-strong-artifact" and ls.get("trust") == "quarantined" for ls in label_sets):
        errors.append("packet-capture import receipt must preserve a quarantined original strong artifact output")
    if not any(ls.get("class") == "packet-capture-normalized" and ls.get("metadata_posture") == "packet-records-only" for ls in label_sets):
        errors.append("packet-capture import receipt must emit a normalized packet-records-only output")
    if not any(ls.get("class") == "packet-capture-summary-preview" for ls in label_sets):
        errors.append("packet-capture import receipt must emit a packet-capture summary preview output")

    metadata = receipt.get("metadata") or {}
    if metadata.get("transport") != "portal-copy":
        errors.append("packet-capture import receipt metadata.transport must be portal-copy")
    if metadata.get("status") not in {"preserved", "rehydrated"}:
        errors.append("packet-capture import receipt metadata.status must be preserved or rehydrated")

    doc_checks = {
        "docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md": [
            "compatibility / imported-artifact states",
            "`docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`",
        ],
        "docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md": [
            "typed specialization of that lane rather than a new subsystem",
            "`kind = content.import.plan`",
            "normalize-before-promotion",
        ],
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "typed safe-open packet-capture import lane",
            "normalized `packet-records-only` derivative",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "safe-open packet-capture intake profile",
            "normalize-before-promotion",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_import_contract.py",
            "typed safe-open import profile",
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

    print("Typed packet-capture strong-artifact import contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
