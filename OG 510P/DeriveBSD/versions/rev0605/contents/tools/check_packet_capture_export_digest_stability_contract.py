#!/usr/bin/env python3
"""Guardrail for stronger packet-capture export digest stability.

This checker keeps the stronger packet-capture export chain about the same
normalized bytes across redaction, approval, transport, and export.
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


def _supporting_digest(receipt: dict, role: str) -> str | None:
    for item in receipt.get("supporting_evidence") or []:
        if item.get("role") == role:
            return item.get("digest")
    return None


def main() -> int:
    errors: list[str] = []
    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    reg = build_registry(schema_paths)
    for schema_rel, example_rel in [
        ("spec/redaction.receipt.packet-capture.schema.json", "spec/examples/redaction.receipt.packet-capture.json"),
        ("spec/content.import.packet-capture.receipt.schema.json", "spec/examples/content.import.packet-capture.receipt.json"),
        ("spec/packet.capture.export.consent.request.profile.schema.json", "spec/examples/packet.capture.export.consent.request.profile.json"),
        ("spec/packet.capture.export.consent.receipt.profile.schema.json", "spec/examples/packet.capture.export.consent.receipt.profile.json"),
        ("spec/packet.capture.export.transport.receipt.profile.schema.json", "spec/examples/packet.capture.export.transport.receipt.profile.json"),
        ("spec/packet.capture.export.receipt.profile.schema.json", "spec/examples/packet.capture.export.receipt.profile.json"),
    ]:
        errors.extend(validate(schema_rel, example_rel, reg))

    session = load_json("spec/examples/packet.capture.session.json")
    summary = load_json("spec/examples/packet.capture.summary.json")
    redaction_transform = load_json("spec/examples/redaction.transform.packet-capture.json")
    redaction_receipt = load_json("spec/examples/redaction.receipt.packet-capture.json")
    import_receipt = load_json("spec/examples/content.import.packet-capture.receipt.json")
    export_policy = load_json("spec/examples/packet.capture.export.policy.profile.json")
    consent_request = load_json("spec/examples/packet.capture.export.consent.request.profile.json")
    consent_receipt = load_json("spec/examples/packet.capture.export.consent.receipt.profile.json")
    transport_policy = load_json("spec/examples/transport.policy.json")
    transport_receipt = load_json("spec/examples/packet.capture.export.transport.receipt.profile.json")
    export_receipt = load_json("spec/examples/packet.capture.export.receipt.profile.json")

    session_d = canonical_digest(session)
    summary_d = canonical_digest(summary)
    redaction_transform_d = canonical_digest(redaction_transform)
    redaction_receipt_d = canonical_digest(redaction_receipt)
    import_receipt_d = canonical_digest(import_receipt)
    export_policy_d = canonical_digest(export_policy)
    consent_request_d = canonical_digest(consent_request)
    consent_receipt_d = canonical_digest(consent_receipt)
    transport_policy_d = canonical_digest(transport_policy)
    transport_receipt_d = canonical_digest(transport_receipt)

    normalized_digest = redaction_receipt.get("output_digest")
    if not normalized_digest:
        errors.append("redaction receipt example must expose output_digest for normalized artifact")
    if redaction_receipt.get("transform_digest") != redaction_transform_d:
        errors.append("redaction receipt example transform_digest must equal computed digest of redaction transform example")
    if ((redaction_receipt.get("summary") or {}).get("summary_digest")) != summary_d:
        errors.append("redaction receipt example summary.summary_digest must equal computed digest of packet.capture.summary example")

    outputs = import_receipt.get("outputs") or []
    normalized_output = next((o for o in outputs if (o.get("labels") or {}).get("class") == "packet-capture-normalized"), None)
    summary_output = next((o for o in outputs if (o.get("labels") or {}).get("class") == "packet-capture-summary-preview"), None)
    if not normalized_output:
        errors.append("packet-capture import receipt example must include normalized output")
    else:
        labels = normalized_output.get("labels") or {}
        if normalized_output.get("digest") != normalized_digest:
            errors.append("packet-capture import receipt normalized output digest must equal redaction receipt output_digest")
        if labels.get("redaction_transform_digest") != redaction_transform_d:
            errors.append("packet-capture import receipt normalized output must carry computed redaction transform digest")
        if labels.get("redaction_receipt_digest") != redaction_receipt_d:
            errors.append("packet-capture import receipt normalized output must carry computed redaction receipt digest")
    if not summary_output:
        errors.append("packet-capture import receipt example must include summary preview output")
    elif summary_output.get("digest") != summary_d:
        errors.append("packet-capture import receipt summary preview digest must equal computed packet.capture.summary digest")

    action = consent_request.get("action") or {}
    if action.get("policy_digest") != export_policy_d:
        errors.append("packet-capture export consent request action.policy_digest must equal computed digest of packet-capture export policy example")
    if action.get("artifact_digest") != normalized_digest:
        errors.append("packet-capture export consent request action.artifact_digest must equal normalized packet-capture digest")
    if consent_receipt.get("request_digest") != consent_request_d:
        errors.append("packet-capture export consent receipt request_digest must equal computed digest of consent request example")

    t_artifact = transport_receipt.get("artifact") or {}
    if transport_receipt.get("transport_policy_digest") != transport_policy_d:
        errors.append("packet-capture export transport receipt transport_policy_digest must equal computed digest of transport policy example")
    if t_artifact.get("kind") != "packet.capture.normalized":
        errors.append("packet-capture export transport receipt artifact.kind must equal packet.capture.normalized")
    if t_artifact.get("digest") != normalized_digest:
        errors.append("packet-capture export transport receipt artifact.digest must equal normalized packet-capture digest")

    e_artifact = export_receipt.get("artifact") or {}
    if e_artifact.get("kind") != "packet.capture.normalized":
        errors.append("packet-capture export receipt artifact.kind must equal packet.capture.normalized")
    if e_artifact.get("digest") != normalized_digest:
        errors.append("packet-capture export receipt artifact.digest must equal normalized packet-capture digest")
    if export_receipt.get("policy_digest") != export_policy_d:
        errors.append("packet-capture export receipt policy_digest must equal computed digest of packet-capture export policy example")
    red = export_receipt.get("redaction") or {}
    if red.get("transform_digest") != redaction_transform_d:
        errors.append("packet-capture export receipt redaction.transform_digest must equal computed digest of packet-capture redaction transform example")
    if red.get("receipt_digest") != redaction_receipt_d:
        errors.append("packet-capture export receipt redaction.receipt_digest must equal computed digest of packet-capture redaction receipt example")
    expected_supporting = {
        "session": session_d,
        "summary": summary_d,
        "import-receipt": import_receipt_d,
        "redaction-receipt": redaction_receipt_d,
    }
    for role, want in expected_supporting.items():
        got = _supporting_digest(export_receipt, role)
        if got != want:
            errors.append(f"packet-capture export receipt supporting_evidence role {role!r} must carry computed digest {want}")
    if export_receipt.get("consent_receipt_digest") != consent_receipt_d:
        errors.append("packet-capture export receipt consent_receipt_digest must equal computed digest of consent receipt example")
    if export_receipt.get("transport_receipt_digest") != transport_receipt_d:
        errors.append("packet-capture export receipt transport_receipt_digest must equal computed digest of transport receipt example")
    if (export_receipt.get("destination") or {}).get("ticket_id") != (transport_receipt.get("destination") or {}).get("ticket_id"):
        errors.append("packet-capture export receipt destination.ticket_id must match transport receipt destination.ticket_id")
    if (export_receipt.get("destination") or {}).get("recipient") != (transport_receipt.get("destination") or {}).get("recipient"):
        errors.append("packet-capture export receipt destination.recipient must match transport receipt destination.recipient")

    doc_checks = {
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "digest-stable",
            "consent.request.action.artifact_digest",
            "transport.receipt.artifact.digest",
            "docs/517-packet-capture-strong-export-digest-stability-boundary.md",
        ],
        "docs/255-policy-constrained-transports.md": [
            "Content-Digest",
            "RFC 9530",
            "same bytes",
            "docs/517-packet-capture-strong-export-digest-stability-boundary.md",
        ],
        "docs/229-evidence-spine-overview.md": [
            "digest-stable",
            "consent.request.action.artifact_digest",
            "docs/517-packet-capture-strong-export-digest-stability-boundary.md",
        ],
        "docs/466-export-boundary-posture-by-profile.md": [
            "digest-stable",
            "same normalized digest",
            "docs/517-packet-capture-strong-export-digest-stability-boundary.md",
        ],
        "docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md": [
            "digest-stable",
            "same normalized digest",
            "docs/517-packet-capture-strong-export-digest-stability-boundary.md",
        ],
        "docs/515-packet-capture-strong-export-approval-evidence-boundary.md": [
            "same bytes",
            "consent.request.action.artifact_digest",
            "docs/517-packet-capture-strong-export-digest-stability-boundary.md",
        ],
        "docs/516-packet-capture-strong-export-transport-boundary.md": [
            "digest-stable",
            "transport.receipt.artifact.digest",
            "docs/517-packet-capture-strong-export-digest-stability-boundary.md",
        ],
        "docs/517-packet-capture-strong-export-digest-stability-boundary.md": [
            "digest-stable",
            "consent.request.action.artifact_digest",
            "transport.receipt.artifact.digest",
            "export.receipt.artifact.digest",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_export_digest_stability_contract.py",
            "digest-stable",
            "same normalized digest",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_packet_capture_export_digest_stability_contract.py",
            "digest-stable",
            "same normalized digest",
        ],
        "README.md": [
            "docs/517-packet-capture-strong-export-digest-stability-boundary.md",
            "same normalized digest",
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

    print("Packet-capture export digest stability contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
