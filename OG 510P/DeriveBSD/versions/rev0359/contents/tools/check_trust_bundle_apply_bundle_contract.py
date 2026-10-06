#!/usr/bin/env python3
"""Guardrail for trust-bundle apply proof staying wired into incident/support bundles."""
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

    if "pki_trust_bundle_apply_receipts" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: pki_trust_bundle_apply_receipts")
    if "pki_trust_bundle_apply_receipt_digests" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: pki_trust_bundle_apply_receipt_digests")
    if "pki_trust_bundle_digest" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: pki_trust_bundle_digest")

    bundle_plan_schema = load_json("spec/bundle.plan.schema.json")
    include_ref = ((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")

    incident_example = load_json("spec/examples/incident.bundle.json")
    scope_include = ((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("pki_trust_bundle") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.pki_trust_bundle must be true")
    if scope_include.get("pki_trust_bundle_apply_receipts") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.pki_trust_bundle_apply_receipts must be true")

    ex_includes = incident_example.get("includes") or {}
    expected_bundle = digest("spec/examples/pki.trust.bundle.json")
    if ex_includes.get("pki_trust_bundle_digest") != expected_bundle:
        errors.append("spec/examples/incident.bundle.json includes.pki_trust_bundle_digest must match computed digest of canonical trust-bundle example")

    vals = ex_includes.get("pki_trust_bundle_apply_receipt_digests") or []
    expected_apply = digest("spec/examples/pki.trust.bundle.apply.receipt.json")
    if not vals:
        errors.append("spec/examples/incident.bundle.json missing includes.pki_trust_bundle_apply_receipt_digests")
    elif vals[0] != expected_apply:
        errors.append("spec/examples/incident.bundle.json includes.pki_trust_bundle_apply_receipt_digests[0] must match computed digest of canonical apply-receipt example")

    doc_checks = {
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "`pki.trust.bundle.apply.receipt` digests",
            "what exact trust view was actually served",
        ],
        "docs/228-pki-and-identity-lifecycle-as-evidence.md": [
            "`pki_trust_bundle_digest`",
            "`pki_trust_bundle_apply_receipt_digests`",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "`pki_trust_bundle_apply_receipts`",
            "renderer-specific trust dumps",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "`pki_trust_bundle_apply_receipt_digests`",
            "exact served trust-view proof",
        ],
        "docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md": [
            "`pki_trust_bundle_apply_receipt_digests`",
            "docs/624-incident-bundles-carry-trust-bundle-apply-proof-by-digest.md",
        ],
        "docs/624-incident-bundles-carry-trust-bundle-apply-proof-by-digest.md": [
            "`pki_trust_bundle_apply_receipts`",
            "`pki_trust_bundle_apply_receipt_digests`",
            "renderer-private dumps remain stronger/debugging evidence",
        ],
        "docs/98-archive-hygiene.md": [
            "check_trust_bundle_apply_bundle_contract.py",
            "renderer-specific trust dumps",
        ],
        "docs/99-llm-runbook.md": [
            "check_trust_bundle_apply_bundle_contract.py",
            "support handoff carries `pki_trust_bundle_digest` plus `pki_trust_bundle_apply_receipt_digests`",
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

    print("Trust-bundle apply bundle contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
