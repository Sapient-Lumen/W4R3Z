#!/usr/bin/env python3
"""Guardrail for stronger packet-capture export transport completion.

This checker keeps completed stronger packet-capture raw-byte export on the
generic transport lane while rejecting local-file completion folklore.
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
    errors.extend(validate("spec/packet.capture.export.transport.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.receipt.profile.json", reg))
    errors.extend(validate("spec/packet.capture.export.receipt.profile.schema.json", "spec/examples/packet.capture.export.receipt.profile.json", reg))

    export_receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")
    artifact = export_receipt.get("artifact") or {}
    destination = export_receipt.get("destination") or {}
    if artifact.get("kind") == "packet.capture.normalized":
        if not export_receipt.get("transport_receipt_digest"):
            errors.append("packet-capture normalized export receipt example must include transport_receipt_digest")
        if destination.get("type") == "file":
            errors.append("packet-capture normalized export receipt example must not use destination.type = file")

    transport_receipt = load_json("spec/examples/packet.capture.export.transport.receipt.profile.json")
    if (transport_receipt.get("artifact") or {}).get("kind") != "packet.capture.normalized":
        errors.append("packet-capture export transport receipt example must bind artifact.kind = packet.capture.normalized")
    if ((transport_receipt.get("result") or {}).get("status")) != "ok":
        errors.append("packet-capture export transport receipt example must keep result.status = ok")
    if not ((transport_receipt.get("destination") or {}).get("recipient")):
        errors.append("packet-capture export transport receipt example must include destination.recipient")
    if transport_receipt.get("transport_kind") in {"jira", "servicenow"} and not ((transport_receipt.get("destination") or {}).get("ticket_id")):
        errors.append("ticketed packet-capture export transport receipt example must include destination.ticket_id")

    doc_checks = {
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "transport_receipt_digest",
            "destination.type = file",
            "packet.capture.export.transport.receipt.profile.schema.json",
        ],
        "docs/255-policy-constrained-transports.md": [
            "transport_receipt_digest",
            "artifact.kind = packet.capture.normalized",
            "docs/516-packet-capture-strong-export-transport-boundary.md",
        ],
        "docs/466-export-boundary-posture-by-profile.md": [
            "transport-bound",
            "transport_receipt_digest",
            "docs/516-packet-capture-strong-export-transport-boundary.md",
        ],
        "docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md": [
            "transport_receipt_digest",
            "destination.type = file",
            "docs/516-packet-capture-strong-export-transport-boundary.md",
        ],
        "docs/515-packet-capture-strong-export-approval-evidence-boundary.md": [
            "transport receipt",
            "completed stronger export",
            "docs/516-packet-capture-strong-export-transport-boundary.md",
        ],
        "docs/516-packet-capture-strong-export-transport-boundary.md": [
            "transport_receipt_digest",
            "destination.type = file",
            "packet.capture.export.transport.receipt.profile.schema.json",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_export_transport_contract.py",
            "transport_receipt_digest",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_packet_capture_export_transport_contract.py",
            "destination.type = file",
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

    print("Packet-capture export transport contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
