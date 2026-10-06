#!/usr/bin/env python3
"""Guardrail for stronger packet-capture export remote-locator continuity.

This checker keeps stronger packet-capture export about one stable recipient-side
locator across transport, recipient acceptance, and final export evidence.
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
    for schema_rel, example_rel in [
        ("spec/packet.capture.export.transport.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.receipt.profile.json"),
        ("spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json"),
        ("spec/packet.capture.export.receipt.profile.schema.json", "spec/examples/packet.capture.export.receipt.profile.json"),
    ]:
        errors.extend(validate(schema_rel, example_rel, reg))

    transport_receipt = load_json("spec/examples/packet.capture.export.transport.receipt.profile.json")
    acceptance_receipt = load_json("spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json")
    export_receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")

    transport_locator = ((transport_receipt.get("result") or {}).get("remote_locator"))
    acceptance_locator = ((acceptance_receipt.get("acceptance") or {}).get("remote_locator"))
    export_locator = ((export_receipt.get("adapter") or {}).get("remote_locator"))

    if not transport_locator:
        errors.append("packet-capture export transport receipt example must include result.remote_locator for canonical stronger export")
    if not acceptance_locator:
        errors.append("packet-capture export transport acceptance receipt example must include acceptance.remote_locator for canonical stronger export")
    if not export_locator:
        errors.append("packet-capture export receipt example must include adapter.remote_locator for canonical stronger export")
    if transport_locator and acceptance_locator and transport_locator != acceptance_locator:
        errors.append("packet-capture stronger export must keep transport.result.remote_locator aligned with acceptance.remote_locator")
    if transport_locator and export_locator and transport_locator != export_locator:
        errors.append("packet-capture stronger export must keep transport.result.remote_locator aligned with export.adapter.remote_locator")

    doc_checks = {
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "remote_locator",
            "same remote locator",
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
        ],
        "docs/255-policy-constrained-transports.md": [
            "remote_locator",
            "same remote locator",
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
        ],
        "docs/229-evidence-spine-overview.md": [
            "remote_locator",
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
        ],
        "docs/466-export-boundary-posture-by-profile.md": [
            "remote locator",
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "remote locator",
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
        ],
        "docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md": [
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
            "portal folklore",
        ],
        "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md": [
            "transport.receipt.result.remote_locator",
            "acceptance.remote_locator",
            "export.receipt.adapter.remote_locator",
            "same remote locator",
        ],
        "docs/98-archive-hygiene.md": [
            "check_packet_capture_export_remote_locator_contract.py",
            "remote_locator",
        ],
        "docs/99-llm-runbook.md": [
            "check_packet_capture_export_remote_locator_contract.py",
            "remote_locator",
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
        ],
        "docs/110-juicy-os-lessons.md": [
            "remote locator",
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "remote_locator",
            "ADR-0114",
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
        ],
        "README.md": [
            "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md",
            "remote_locator",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        print("Packet-capture export remote-locator continuity contract: FAILED")
        for err in errors:
            print("-", err)
        return 1

    print("Packet-capture export remote-locator continuity contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
