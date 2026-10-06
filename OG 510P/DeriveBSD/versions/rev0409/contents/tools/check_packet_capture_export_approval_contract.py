#!/usr/bin/env python3
"""Guardrail for stronger packet-capture export approval evidence.

This checker keeps stronger packet-capture raw-byte export on the generic
consent lane while requiring explicit non-auto approval evidence.
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
    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    reg = build_registry(schema_paths)
    errors.extend(validate("spec/packet.capture.export.consent.request.profile.schema.json", "spec/examples/packet.capture.export.consent.request.profile.json", reg))
    errors.extend(validate("spec/packet.capture.export.consent.receipt.profile.schema.json", "spec/examples/packet.capture.export.consent.receipt.profile.json", reg))
    errors.extend(validate("spec/packet.capture.export.receipt.profile.schema.json", "spec/examples/packet.capture.export.receipt.profile.json", reg))

    consent_req = load_json("spec/examples/packet.capture.export.consent.request.profile.json")
    action = consent_req.get("action") or {}
    if action.get("kind") != "export":
        errors.append("packet-capture export consent request example must keep action.kind = export")
    for key in ["policy_digest", "artifact_digest", "lease_id"]:
        if not action.get(key):
            errors.append(f"packet-capture export consent request example missing action.{key}")
    if consent_req.get("secure_attention_required") is not True:
        errors.append("packet-capture export consent request example must require secure_attention_required = true")

    consent_receipt = load_json("spec/examples/packet.capture.export.consent.receipt.profile.json")
    if consent_receipt.get("outcome") != "approved":
        errors.append("packet-capture export consent receipt example must be approved")
    if consent_receipt.get("method") == "auto":
        errors.append("packet-capture export consent receipt example must not use method = auto")

    export_receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")
    if (export_receipt.get("artifact") or {}).get("kind") == "packet.capture.normalized" and not export_receipt.get("consent_receipt_digest"):
        errors.append("packet-capture normalized export receipt example must include consent_receipt_digest")

    doc_checks = {
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "packet.capture.export.consent.request.profile.schema.json",
            "packet.capture.export.consent.receipt.profile.schema.json",
            "method = auto",
        ],
        "docs/256-consent-ux-contract.md": [
            "packet.capture.normalized",
            "method = auto",
            "docs/515-packet-capture-strong-export-approval-evidence-boundary.md",
        ],
        "docs/474-high-risk-approval-posture-by-profile.md": [
            "packet.capture.normalized",
            "non-auto",
            "docs/515-packet-capture-strong-export-approval-evidence-boundary.md",
        ],
        "docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md": [
            "consent_receipt_digest",
            "docs/515-packet-capture-strong-export-approval-evidence-boundary.md",
        ],
        "docs/515-packet-capture-strong-export-approval-evidence-boundary.md": [
            "packet.capture.export.consent.request.profile.schema.json",
            "packet.capture.export.consent.receipt.profile.schema.json",
            "method = auto",
            "consent_receipt_digest",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_export_approval_contract.py",
            "packet.capture.export.consent.request.profile.schema.json",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_packet_capture_export_approval_contract.py",
            "consent_receipt_digest",
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

    print("Packet-capture export approval evidence contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
