#!/usr/bin/env python3
"""Guardrail for breakglass accepted case-object metadata-only reverification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
BASE_URI = "https://derivebsd.local/spec/"


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def digest_obj(obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


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
        ("spec/export.receipt.schema.json", "spec/examples/export.receipt.breakglass.accepted-case-object.json"),
        ("spec/transport.receipt.schema.json", "spec/examples/transport.receipt.breakglass.accepted-case-object.json"),
        ("spec/transport.acceptance.receipt.schema.json", "spec/examples/transport.acceptance.receipt.breakglass.accepted-case-object.json"),
        ("spec/transport.reverification.receipt.schema.json", "spec/examples/transport.reverification.receipt.breakglass.accepted-case-object.json"),
    ]:
        errors.extend(validate(schema_rel, example_rel, reg))

    export_receipt = load_json("spec/examples/export.receipt.breakglass.accepted-case-object.json")
    transport_receipt = load_json("spec/examples/transport.receipt.breakglass.accepted-case-object.json")
    acceptance_receipt = load_json("spec/examples/transport.acceptance.receipt.breakglass.accepted-case-object.json")
    reverification_receipt = load_json("spec/examples/transport.reverification.receipt.breakglass.accepted-case-object.json")
    incident_bundle = load_json("spec/examples/incident.bundle.json")

    transport_d = digest_obj(transport_receipt)
    acceptance_d = digest_obj(acceptance_receipt)
    export_d = digest_obj(export_receipt)

    artifact = export_receipt.get("artifact") or {}
    acceptance = acceptance_receipt.get("acceptance") or {}
    reverification = reverification_receipt.get("reverification") or {}

    if export_receipt.get("transport_receipt_digest") != transport_d:
        errors.append("breakglass accepted-case-object export receipt example must join the computed transport receipt digest")
    if export_receipt.get("transport_acceptance_receipt_digest") != acceptance_d:
        errors.append("breakglass accepted-case-object export receipt example must join the computed transport acceptance receipt digest")
    if acceptance_receipt.get("transport_receipt_digest") != transport_d:
        errors.append("breakglass accepted-case-object acceptance receipt example must join the computed transport receipt digest")
    if reverification_receipt.get("export_receipt_digest") != export_d:
        errors.append("breakglass accepted-case-object reverification receipt example must join the computed export receipt digest")
    if reverification_receipt.get("transport_acceptance_receipt_digest") != acceptance_d:
        errors.append("breakglass accepted-case-object reverification receipt example must join the computed transport acceptance receipt digest")
    if (reverification_receipt.get("artifact") or {}).get("digest") != artifact.get("digest"):
        errors.append("breakglass accepted-case-object reverification receipt example must stay on the same artifact digest as the export receipt example")
    if reverification.get("body_downloaded") is not False:
        errors.append("breakglass accepted-case-object reverification receipt example must keep reverification.body_downloaded = false")
    if reverification.get("status") != "match":
        errors.append("breakglass accepted-case-object reverification receipt example must keep reverification.status = match")
    if reverification.get("remote_reference") != acceptance.get("remote_reference"):
        errors.append("breakglass accepted-case-object reverification must keep reverification.remote_reference aligned with acceptance.remote_reference")
    if reverification.get("remote_validator") != acceptance.get("remote_validator"):
        errors.append("breakglass accepted-case-object reverification must keep reverification.remote_validator aligned with acceptance.remote_validator")
    if reverification.get("remote_protection") != acceptance.get("remote_protection"):
        errors.append("breakglass accepted-case-object reverification must keep reverification.remote_protection aligned with acceptance.remote_protection")
    if reverification.get("remote_locator") != acceptance.get("remote_locator"):
        errors.append("breakglass accepted case-object reverification must keep reverification.remote_locator aligned with acceptance.remote_locator")
    if not any("reverification" in item for item in ((incident_bundle.get("includes") or {}).get("extra") or [])):
        errors.append("spec/examples/incident.bundle.json includes.extra missing metadata-only reverification example")

    schema = load_json("spec/incident.bundle.schema.json")
    includes = ((schema.get("properties") or {}).get("includes") or {}).get("properties") or {}
    for field in ["extra", "breakglass_receipt_digests"]:
        desc = (includes.get(field) or {}).get("description") or ""
        for needle in ["transport.reverification.receipt", "metadata-only reverification", "body_downloaded = false"]:
            if needle not in desc:
                errors.append(f"spec/incident.bundle.schema.json includes.{field} description missing required token: {needle}")

    doc_checks = {
        "adrs/ADR-0311-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md": ["metadata-only reverification when visible", "transport.reverification.receipt", "body_downloaded = false"],
        "docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md": ["metadata-only reverification when visible", "transport.reverification.receipt", "body_downloaded = false", "tools/check_breakglass_adapter_case_object_reverification_boundary.py"],
        "docs/216-incident-snapshots-and-support-bundles.md": ["metadata-only reverification too when visible", "transport.reverification.receipt"],
        "docs/236-breakglass-and-recovery-mode.md": ["metadata-only reverification too when visible", "transport.reverification.receipt"],
        "docs/250-breakglass-and-recovery-workflows.md": ["metadata-only reverification too when visible", "body_downloaded = false"],
        "docs/253-bundle-plans-and-deterministic-exports.md": ["metadata-only reverification when visible too", "transport.reverification.receipt"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": ["metadata-only reverification when visible too", "body_downloaded = false"],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": ["metadata-only reverification too when visible", "transport.reverification.receipt"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0311", "metadata-only reverification"],
        "docs/98-archive-hygiene.md": ["check_breakglass_adapter_case_object_reverification_boundary.py", "metadata-only reverification"],
        "docs/99-llm-runbook.md": ["docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md", "tools/check_breakglass_adapter_case_object_reverification_boundary.py"],
        "docs/00-index.md": ["docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md", "tools/check_breakglass_adapter_case_object_reverification_boundary.py"],
        "docs/110-juicy-os-lessons.md": ["accepted case-object anchors should gain metadata-only reverification when visible", "docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        print("Breakglass accepted case-object reverification boundary: FAILED")
        for err in errors:
            print("-", err)
        return 1

    print("Breakglass accepted case-object reverification boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
