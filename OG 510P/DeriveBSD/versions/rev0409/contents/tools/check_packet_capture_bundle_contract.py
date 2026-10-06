#!/usr/bin/env python3
"""Guardrail for packet-capture evidence joins in incident/support bundles.

This checker keeps the packet-capture lane wired into the official bundle
contract so support workflows do not drift back into raw `.pcapng` payload
folklore or hide packet evidence in `extra`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(rel: str) -> str:
    return "sha256:" + hashlib.sha256(jcs_bytes(load_json(rel))).hexdigest()


def main() -> int:
    errors: list[str] = []

    incident_schema = load_json("spec/incident.bundle.schema.json")
    include_knobs = ((incident_schema.get("$defs") or {}).get("include_knobs") or {}).get("properties") or {}
    includes = (((incident_schema.get("properties") or {}).get("includes") or {}).get("properties") or {})

    for key in (
        "packet_capture_sessions",
        "packet_capture_summaries",
        "packet_capture_import_receipts",
        "packet_capture_redaction_receipts",
    ):
        if key not in include_knobs:
            errors.append(f"spec/incident.bundle.schema.json missing include knob: {key}")

    for key in (
        "packet_capture_session_digests",
        "packet_capture_summary_digests",
        "packet_capture_import_receipt_digests",
        "packet_capture_redaction_receipt_digests",
    ):
        if key not in includes:
            errors.append(f"spec/incident.bundle.schema.json missing includes field: {key}")

    bundle_plan_schema = load_json("spec/bundle.plan.schema.json")
    include_ref = ((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")

    incident_example = load_json("spec/examples/incident.bundle.json")
    scope_include = (((incident_example.get("scope") or {}).get("include") or {}))
    expected_true = {
        "packet_capture_sessions",
        "packet_capture_summaries",
        "packet_capture_import_receipts",
        "packet_capture_redaction_receipts",
    }
    for key in expected_true:
        if scope_include.get(key) is not True:
            errors.append(f"spec/examples/incident.bundle.json scope.include.{key} must be true")

    ex_includes = incident_example.get("includes") or {}
    expected_digests = {
        "packet_capture_session_digests": digest("spec/examples/packet.capture.session.json"),
        "packet_capture_summary_digests": digest("spec/examples/packet.capture.summary.json"),
        "packet_capture_import_receipt_digests": digest("spec/examples/content.import.packet-capture.receipt.json"),
        "packet_capture_redaction_receipt_digests": digest("spec/examples/redaction.receipt.packet-capture.json"),
    }
    for key, expected in expected_digests.items():
        vals = ex_includes.get(key) or []
        if not vals:
            errors.append(f"spec/examples/incident.bundle.json missing includes.{key}")
        elif vals[0] != expected:
            errors.append(f"spec/examples/incident.bundle.json includes.{key}[0] must match computed digest of canonical example")

    doc_checks = {
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "`packet.capture.session` digests",
            "`packet.capture.summary` digests",
            "import + redaction receipt digests",
            "`docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "packet_capture_sessions",
            "packet_capture_summaries",
            "raw packet blobs as default support-bundle members",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "`packet.capture.session` / `packet.capture.summary` digests",
            "Raw packet bytes remain a stronger separate export action",
        ],
        "docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md": [
            "`packet_capture_sessions`",
            "`packet_capture_summary_digests`",
            "raw packet bytes remain out of the default payload",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_bundle_contract.py",
            "packet_capture_sessions",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_packet_capture_bundle_contract.py",
            "summary-first for packet capture",
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

    print("Packet-capture bundle contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
