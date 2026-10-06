#!/usr/bin/env python3
"""Guardrail for stronger packet-capture export recipient digest confirmation.

This checker keeps stronger packet-capture recipient acceptance about the same
normalized bytes on the remote side, not just the same recipient tuple.
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
        ("spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json"),
        ("spec/packet.capture.export.receipt.profile.schema.json", "spec/examples/packet.capture.export.receipt.profile.json"),
    ]:
        errors.extend(validate(schema_rel, example_rel, reg))

    acceptance_receipt = load_json("spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json")
    export_receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")

    acceptance_receipt_d = canonical_digest(acceptance_receipt)
    artifact = acceptance_receipt.get("artifact") or {}
    acceptance = acceptance_receipt.get("acceptance") or {}
    normalized_digest = artifact.get("digest")

    if artifact.get("kind") != "packet.capture.normalized":
        errors.append("packet-capture export transport acceptance receipt example must bind artifact.kind = packet.capture.normalized")
    if not acceptance.get("remote_reference"):
        errors.append("packet-capture export transport acceptance receipt example must include acceptance.remote_reference")
    if acceptance.get("remote_artifact_digest") != normalized_digest:
        errors.append("packet-capture export transport acceptance receipt example must keep acceptance.remote_artifact_digest on the same normalized digest as artifact.digest")
    if export_receipt.get("transport_acceptance_receipt_digest") != acceptance_receipt_d:
        errors.append("packet-capture export receipt example must join the computed transport acceptance receipt digest after remote digest confirmation")
    if (export_receipt.get("artifact") or {}).get("digest") != normalized_digest:
        errors.append("packet-capture export receipt example must stay on the same normalized digest confirmed by recipient acceptance")

    doc_checks = {
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "acceptance.remote_artifact_digest",
            "same normalized digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/255-policy-constrained-transports.md": [
            "remote_artifact_digest",
            "same normalized digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/229-evidence-spine-overview.md": [
            "remote_artifact_digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/466-export-boundary-posture-by-profile.md": [
            "remote_artifact_digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "remote_artifact_digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/517-packet-capture-strong-export-digest-stability-boundary.md": [
            "acceptance.remote_artifact_digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md": [
            "acceptance.remote_artifact_digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md": [
            "remote_artifact_digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md": [
            "acceptance.remote_artifact_digest",
            "same normalized digest",
            "AS2 signed receipts",
        ],
        "docs/98-archive-hygiene.md": [
            "check_packet_capture_export_recipient_digest_contract.py",
            "remote_artifact_digest",
        ],
        "docs/99-llm-runbook.md": [
            "check_packet_capture_export_recipient_digest_contract.py",
            "remote_artifact_digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/110-juicy-os-lessons.md": [
            "remote_artifact_digest",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "remote_artifact_digest",
            "ADR-0110",
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
        ],
        "README.md": [
            "docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md",
            "remote_artifact_digest",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        print("Packet-capture export recipient digest confirmation contract: FAILED")
        for err in errors:
            print("-", err)
        return 1

    print("Packet-capture export recipient digest confirmation contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
