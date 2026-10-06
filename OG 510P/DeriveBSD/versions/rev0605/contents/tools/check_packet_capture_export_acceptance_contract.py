#!/usr/bin/env python3
"""Guardrail for stronger packet-capture export recipient acceptance.

This checker keeps final stronger packet-capture raw-byte export distinct from
mere transport success by requiring typed recipient-acceptance evidence.
"""
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
        ("spec/transport.acceptance.receipt.schema.json", "spec/examples/transport.acceptance.receipt.json"),
        ("spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json"),
        ("spec/packet.capture.export.receipt.profile.schema.json", "spec/examples/packet.capture.export.receipt.profile.json"),
    ]:
        errors.extend(validate(schema_rel, example_rel, reg))

    transport_receipt = load_json("spec/examples/packet.capture.export.transport.receipt.profile.json")
    acceptance_receipt = load_json("spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json")
    export_receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")

    transport_receipt_d = canonical_digest(transport_receipt)
    acceptance_receipt_d = canonical_digest(acceptance_receipt)

    expected_digest = (transport_receipt.get("artifact") or {}).get("digest")
    if (acceptance_receipt.get("artifact") or {}).get("kind") != "packet.capture.normalized":
        errors.append("packet-capture export transport acceptance receipt example must bind artifact.kind = packet.capture.normalized")
    if (acceptance_receipt.get("artifact") or {}).get("digest") != expected_digest:
        errors.append("packet-capture export transport acceptance receipt example must stay on the same artifact digest as the transport receipt example")
    if acceptance_receipt.get("transport_receipt_digest") != transport_receipt_d:
        errors.append("packet-capture export transport acceptance receipt example must join the computed transport receipt digest")
    if acceptance_receipt.get("outcome") != "accepted":
        errors.append("packet-capture export transport acceptance receipt example must keep outcome = accepted")
    if not ((acceptance_receipt.get("acceptance") or {}).get("remote_reference")):
        errors.append("packet-capture export transport acceptance receipt example must include acceptance.remote_reference")

    if (export_receipt.get("artifact") or {}).get("kind") == "packet.capture.normalized":
        if export_receipt.get("delivery_state") != "recipient-accepted":
            errors.append("packet-capture normalized export receipt example must keep delivery_state = recipient-accepted")
        if export_receipt.get("transport_acceptance_receipt_digest") != acceptance_receipt_d:
            errors.append("packet-capture normalized export receipt example must join the computed transport acceptance receipt digest")
        if (export_receipt.get("artifact") or {}).get("digest") != expected_digest:
            errors.append("packet-capture normalized export receipt example must stay on the same artifact digest named by transport and acceptance receipts")

    doc_checks = {
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "transport_acceptance_receipt_digest",
            "delivery_state = recipient-accepted",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
        "docs/255-policy-constrained-transports.md": [
            "transport.acceptance.receipt",
            "recipient-accepted",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
        "docs/466-export-boundary-posture-by-profile.md": [
            "recipient-accepted",
            "transport acceptance receipt",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "recipient-accepted",
            "transport.acceptance.receipt",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
        "docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md": [
            "transport_acceptance_receipt_digest",
            "delivery_state = recipient-accepted",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
        "docs/516-packet-capture-strong-export-transport-boundary.md": [
            "transport.acceptance.receipt",
            "merely transported",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
        "docs/517-packet-capture-strong-export-digest-stability-boundary.md": [
            "transport acceptance receipt",
            "same normalized digest",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
        "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md": [
            "transport.acceptance.receipt",
            "recipient-accepted",
            "transport_acceptance_receipt_digest",
        ],
        "docs/98-archive-hygiene.md": [
            "check_packet_capture_export_acceptance_contract.py",
            "transport acceptance receipt",
        ],
        "docs/99-llm-runbook.md": [
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
            "transport acceptance receipt",
        ],
        "docs/110-juicy-os-lessons.md": [
            "recipient-accepted",
            "transport acceptance receipt",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "recipient-accepted",
            "ADR-0108",
            "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing expected acceptance-boundary reference: {needle}")

    if errors:
        print("Packet-capture export recipient-acceptance contract: FAILED")
        for err in errors:
            print("-", err)
        return 1

    print("Packet-capture export recipient-acceptance contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
