#!/usr/bin/env python3
"""Guardrail for packet-capture export proof-chain posture.

This checker keeps stronger packet-capture raw-byte exports on the generic
export lane while requiring typed proof joins back to the bounded
session/summary/import/redaction chain.
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

    export_receipt_schema = load_json("spec/export.receipt.schema.json")
    props = export_receipt_schema.get("properties") or {}
    supporting = props.get("supporting_evidence") or {}
    if supporting.get("type") != "array":
        errors.append("spec/export.receipt.schema.json must expose supporting_evidence[] for proof-bound stronger exports")

    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    reg = build_registry(schema_paths)
    errors.extend(validate("spec/packet.capture.export.policy.profile.schema.json", "spec/examples/packet.capture.export.policy.profile.json", reg))
    errors.extend(validate("spec/packet.capture.export.receipt.profile.schema.json", "spec/examples/packet.capture.export.receipt.profile.json", reg))

    policy = load_json("spec/examples/packet.capture.export.policy.profile.json")
    rules = {r.get("artifact_kind"): r for r in policy.get("rules") or []}
    summary_rule = rules.get("packet.capture.summary")
    normalized_rule = rules.get("packet.capture.normalized")
    if not summary_rule:
        errors.append("packet-capture export policy profile must include packet.capture.summary")
    elif summary_rule.get("allow_raw_blobs") is not False:
        errors.append("packet.capture.summary rule must keep allow_raw_blobs = false")
    if not normalized_rule:
        errors.append("packet-capture export policy profile must include packet.capture.normalized")
    else:
        if normalized_rule.get("allow_raw_blobs") is not True:
            errors.append("packet.capture.normalized rule must keep allow_raw_blobs = true")
        if not normalized_rule.get("redaction_transform_digest"):
            errors.append("packet.capture.normalized rule must require a redaction_transform_digest")

    receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")
    if (receipt.get("artifact") or {}).get("kind") != "packet.capture.normalized":
        errors.append("packet-capture export receipt example must demonstrate stronger normalized raw-byte export")
    roles = {item.get("role") for item in receipt.get("supporting_evidence") or []}
    for role in {"session", "summary", "import-receipt", "redaction-receipt"}:
        if role not in roles:
            errors.append(f"packet-capture export receipt example missing supporting evidence role: {role}")

    doc_checks = {
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "packet.capture.normalized",
            "supporting_evidence",
            "packet-capture export receipt profile",
        ],
        "docs/229-evidence-spine-overview.md": [
            "supporting_evidence",
            "packet.capture.normalized",
            "docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md",
        ],
        "docs/466-export-boundary-posture-by-profile.md": [
            "compiled consequence",
            "packet.capture.summary",
            "packet.capture.normalized",
        ],
        "docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md": [
            "packet.capture.normalized",
            "supporting_evidence",
            "compiled consequence",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_export_contract.py",
            "packet.capture.normalized",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_packet_capture_export_contract.py",
            "supporting_evidence",
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

    print("Packet-capture export proof-chain contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
