#!/usr/bin/env python3
"""Guardrail for stronger packet-capture export remote reverification.

This checker keeps later stronger packet-evidence re-checks on a typed metadata-only
reverification lane instead of packet re-downloads or portal folklore.
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
        ("spec/transport.reverification.receipt.schema.json", "spec/examples/transport.reverification.receipt.json"),
        ("spec/packet.capture.export.transport.reverification.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.reverification.receipt.profile.json"),
    ]:
        errors.extend(validate(schema_rel, example_rel, reg))

    acceptance_receipt = load_json("spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json")
    export_receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")
    reverification_receipt = load_json("spec/examples/packet.capture.export.transport.reverification.receipt.profile.json")

    acceptance_d = canonical_digest(acceptance_receipt)
    export_d = canonical_digest(export_receipt)

    expected_digest = (export_receipt.get("artifact") or {}).get("digest")
    acceptance_locator = ((acceptance_receipt.get("acceptance") or {}).get("remote_locator"))
    acceptance_validator = ((acceptance_receipt.get("acceptance") or {}).get("remote_validator"))
    acceptance_protection = ((acceptance_receipt.get("acceptance") or {}).get("remote_protection"))
    reverify = reverification_receipt.get("reverification") or {}

    if (reverification_receipt.get("artifact") or {}).get("kind") != "packet.capture.normalized":
        errors.append("packet-capture export transport reverification receipt example must bind artifact.kind = packet.capture.normalized")
    if (reverification_receipt.get("artifact") or {}).get("digest") != expected_digest:
        errors.append("packet-capture export transport reverification receipt example must stay on the same artifact digest as the export receipt example")
    if reverification_receipt.get("export_receipt_digest") != export_d:
        errors.append("packet-capture export transport reverification receipt example must join the computed export receipt digest")
    if reverification_receipt.get("transport_acceptance_receipt_digest") != acceptance_d:
        errors.append("packet-capture export transport reverification receipt example must join the computed transport acceptance receipt digest")
    if reverify.get("body_downloaded") is not False:
        errors.append("packet-capture export transport reverification receipt example must keep reverification.body_downloaded = false")
    if reverify.get("status") != "match":
        errors.append("packet-capture export transport reverification receipt example must keep reverification.status = match")
    if reverify.get("remote_locator") != acceptance_locator:
        errors.append("packet-capture stronger export reverification must keep reverification.remote_locator aligned with acceptance.remote_locator")
    if reverify.get("remote_validator") != acceptance_validator:
        errors.append("packet-capture stronger export reverification must keep reverification.remote_validator aligned with acceptance.remote_validator")
    if reverify.get("remote_protection") != acceptance_protection:
        errors.append("packet-capture stronger export reverification must keep reverification.remote_protection aligned with acceptance.remote_protection")
    if reverify.get("remote_artifact_digest") not in (None, expected_digest):
        errors.append("packet-capture stronger export reverification remote_artifact_digest must either be omitted or match the normalized export artifact digest")

    doc_checks = {
        "docs/229-evidence-spine-overview.md": [
            "transport.reverification.receipt",
            "metadata-only reverification",
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
        ],
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "transport.reverification.receipt",
            "body_downloaded = false",
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
        ],
        "docs/255-policy-constrained-transports.md": [
            "transport.reverification.receipt",
            "body_downloaded = false",
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
        ],
        "docs/466-export-boundary-posture-by-profile.md": [
            "remote reverification",
            "body_downloaded = false",
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "transport.reverification.receipt",
            "metadata-only reverification",
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
        ],
        "docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md": [
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
            "metadata-only reverification",
        ],
        "docs/525-packet-capture-strong-export-remote-reverification-boundary.md": [
            "transport.reverification.receipt",
            "reverification.body_downloaded = false",
            "same accepted remote object",
        ],
        "docs/98-archive-hygiene.md": [
            "check_packet_capture_export_reverification_contract.py",
            "transport.reverification.receipt",
        ],
        "docs/99-llm-runbook.md": [
            "check_packet_capture_export_reverification_contract.py",
            "transport.reverification.receipt",
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
        ],
        "docs/110-juicy-os-lessons.md": [
            "metadata-only reverification",
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "transport.reverification.receipt",
            "ADR-0115",
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
        ],
        "README.md": [
            "docs/525-packet-capture-strong-export-remote-reverification-boundary.md",
            "transport.reverification.receipt",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        print("Packet-capture export remote reverification contract: FAILED")
        for err in errors:
            print("-", err)
        return 1

    print("Packet-capture export remote reverification contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
