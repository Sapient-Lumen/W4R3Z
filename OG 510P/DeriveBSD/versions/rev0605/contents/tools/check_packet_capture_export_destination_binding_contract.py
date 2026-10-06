#!/usr/bin/env python3
"""Guardrail for stronger packet-capture export destination-bound approval.

This checker keeps stronger packet-capture raw-byte export tied to the same
approved recipient/ticket/domain tuple across approval, transport,
recipient acceptance, and final export evidence.
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


def norm_approval_destination(obj: dict) -> dict:
    dest = (((obj.get("action") or {}).get("destination")) or {})
    return {
        "type": dest.get("type"),
        "ticket_id": dest.get("ticket_id"),
        "recipient": dest.get("recipient"),
        "domain": dest.get("domain"),
        "uri_hint": dest.get("uri_hint"),
    }


def norm_transport_destination(obj: dict) -> dict:
    dest = obj.get("destination") or {}
    kind = obj.get("transport_kind")
    type_map = {
        "jira": "ticket-upload",
        "servicenow": "ticket-upload",
        "https-upload": "https-upload",
        "email": "email",
        "removable-media": "removable-media",
        "oob": "oob",
        "custom": None,
        "sftp": None,
    }
    return {
        "type": type_map.get(kind),
        "ticket_id": dest.get("ticket_id"),
        "recipient": dest.get("recipient"),
        "domain": dest.get("domain"),
        "uri_hint": dest.get("uri_hint"),
    }


def norm_acceptance_recipient(obj: dict, approved_type: str | None) -> dict:
    rec = obj.get("recipient") or {}
    return {
        "type": approved_type,
        "ticket_id": rec.get("ticket_id"),
        "recipient": rec.get("recipient"),
        "domain": rec.get("domain"),
        "uri_hint": None,
    }


def norm_export_destination(obj: dict) -> dict:
    dest = obj.get("destination") or {}
    return {
        "type": dest.get("type"),
        "ticket_id": dest.get("ticket_id"),
        "recipient": dest.get("recipient"),
        "domain": dest.get("domain"),
        "uri_hint": dest.get("uri_hint"),
    }


def compare(expected: dict, actual: dict, label: str) -> list[str]:
    errors: list[str] = []
    for key in ["type", "ticket_id", "recipient", "domain"]:
        if expected.get(key) != actual.get(key):
            errors.append(f"{label} must keep approved destination {key} = {expected.get(key)!r}; got {actual.get(key)!r}")
    if expected.get("uri_hint") and actual.get("uri_hint") and expected.get("uri_hint") != actual.get("uri_hint"):
        errors.append(f"{label} must keep approved destination uri_hint = {expected.get('uri_hint')!r}; got {actual.get('uri_hint')!r}")
    return errors


def main() -> int:
    errors: list[str] = []
    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    reg = build_registry(schema_paths)
    for schema_rel, example_rel in [
        ("spec/packet.capture.export.consent.request.profile.schema.json", "spec/examples/packet.capture.export.consent.request.profile.json"),
        ("spec/packet.capture.export.transport.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.receipt.profile.json"),
        ("spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json"),
        ("spec/packet.capture.export.receipt.profile.schema.json", "spec/examples/packet.capture.export.receipt.profile.json"),
    ]:
        errors.extend(validate(schema_rel, example_rel, reg))

    consent_request = load_json("spec/examples/packet.capture.export.consent.request.profile.json")
    consent_receipt = load_json("spec/examples/packet.capture.export.consent.receipt.profile.json")
    transport_receipt = load_json("spec/examples/packet.capture.export.transport.receipt.profile.json")
    acceptance_receipt = load_json("spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json")
    export_receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")

    approved = norm_approval_destination(consent_request)
    if not approved.get("type"):
        errors.append("packet-capture export consent request example must include action.destination.type")
    if approved.get("type") == "file":
        errors.append("packet-capture export consent request example must not approve destination.type = file for stronger export")
    if not approved.get("recipient"):
        errors.append("packet-capture export consent request example must include action.destination.recipient")
    if approved.get("type") == "ticket-upload" and not approved.get("ticket_id"):
        errors.append("packet-capture export consent request example must include action.destination.ticket_id for ticket-upload")

    if consent_receipt.get("request_digest") != canonical_digest(consent_request):
        errors.append("packet-capture export consent receipt example must join the computed consent request digest after destination binding")

    errors.extend(compare(approved, norm_transport_destination(transport_receipt), "packet-capture export transport receipt example"))
    errors.extend(compare(approved, norm_acceptance_recipient(acceptance_receipt, approved.get("type")), "packet-capture export transport acceptance receipt example"))
    errors.extend(compare(approved, norm_export_destination(export_receipt), "packet-capture export receipt example"))

    doc_checks = {
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "action.destination",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
            "same approved destination tuple",
        ],
        "docs/255-policy-constrained-transports.md": [
            "action.destination",
            "transport.acceptance.receipt.recipient",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/229-evidence-spine-overview.md": [
            "consent.request.action.destination",
            "same approved destination tuple",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/466-export-boundary-posture-by-profile.md": [
            "destination-bound",
            "different ticket or recipient",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/474-high-risk-approval-posture-by-profile.md": [
            "destination-bound",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "approved case/recipient tuple",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/515-packet-capture-strong-export-approval-evidence-boundary.md": [
            "action.destination",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md": [
            "same approved recipient identity",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md": [
            "action.destination",
            "transport.receipt.destination",
            "transport.acceptance.receipt.recipient",
            "export.receipt.destination",
        ],
        "docs/256-consent-ux-contract.md": [
            "action.destination",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_packet_capture_export_destination_binding_contract.py",
            "action.destination",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_export_destination_binding_contract.py",
            "action.destination",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/110-juicy-os-lessons.md": [
            "approved destination tuple",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "consent.request.action.destination",
            "ADR-0109",
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
        ],
        "README.md": [
            "docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md",
            "same approved destination tuple",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing expected destination-binding reference: {needle}")

    if errors:
        print("Packet-capture export destination-bound approval contract: FAILED")
        for err in errors:
            print("-", err)
        return 1

    print("Packet-capture export destination-bound approval contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
