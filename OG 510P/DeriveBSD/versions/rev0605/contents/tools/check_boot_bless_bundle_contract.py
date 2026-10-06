#!/usr/bin/env python3
"""Guardrail for boot.bless.receipt proof staying wired into incident/support bundles."""
from __future__ import annotations
import json
from pathlib import Path

from cube_digest_lib import file_json_digest, load_json as load_json_strict
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return load_json_strict(ROOT, rel)

def digest(rel: str) -> str:
    return file_json_digest(ROOT, rel)

def main() -> int:
    errors=[]
    incident_schema=load_json("spec/incident.bundle.schema.json")
    include_knobs=((incident_schema.get("$defs") or {}).get("include_knobs") or {}).get("properties") or {}
    includes=(((incident_schema.get("properties") or {}).get("includes") or {}).get("properties") or {})
    if "boot_bless_receipts" not in include_knobs:
        errors.append("spec/incident.bundle.schema.json missing include knob: boot_bless_receipts")
    if "boot_bless_receipt_digests" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes field: boot_bless_receipt_digests")
    bundle_plan_schema=load_json("spec/bundle.plan.schema.json")
    include_ref=((((bundle_plan_schema.get("properties") or {}).get("selection") or {}).get("properties") or {}).get("include") or {}).get("allOf") or []
    if not any(isinstance(item, dict) and item.get("$ref") == "incident.bundle.schema.json#/$defs/include_knobs" for item in include_ref):
        errors.append("spec/bundle.plan.schema.json selection.include must reuse incident.bundle include_knobs")
    incident_example=load_json("spec/examples/incident.bundle.json")
    scope_include=((incident_example.get("scope") or {}).get("include") or {})
    if scope_include.get("boot_bless_receipts") is not True:
        errors.append("spec/examples/incident.bundle.json scope.include.boot_bless_receipts must be true")
    val=(incident_example.get("includes") or {}).get("boot_bless_receipt_digests")
    expected=digest("spec/examples/boot.bless.receipt.json")
    if not val:
        errors.append("spec/examples/incident.bundle.json missing includes.boot_bless_receipt_digests")
    elif val != [expected]:
        errors.append("spec/examples/incident.bundle.json includes.boot_bless_receipt_digests must match computed digest of canonical boot.bless.receipt example")
    bundle_plan_example=load_json("spec/examples/bundle.plan.json")
    if ((bundle_plan_example.get("selection") or {}).get("include") or {}).get("boot_bless_receipts") is not True:
        errors.append("spec/examples/bundle.plan.json selection.include.boot_bless_receipts must be true")
    doc_checks={
        "docs/112-health-gated-updates.md":["`boot_bless_receipt_digests`","official support handoff"],
        "docs/216-incident-snapshots-and-support-bundles.md":["`boot_bless_receipt_digests`","boot-assessment/finalization proof"],
        "docs/229-evidence-spine-overview.md":["`boot_bless_receipt_digests`","boot assessment / finalization decisions"],
        "docs/241-boot-try-counters-and-boot-assessment.md":["`boot_bless_receipt_digests`","health-gated finalization or rollback"],
        "docs/253-bundle-plans-and-deterministic-exports.md":["`boot_bless_receipts` / `boot_bless_receipt_digests`","boot-assessment-shaped incident"],
        "docs/335-boot-assessment-greenboot-and-health-gated-rollback.md":["`boot_bless_receipt_digests`","loader counters or greenboot status text"],
        "docs/472-update-delivery-and-release-posture-by-profile.md":["`boot_bless_receipt_digests`","health-gated finalization proof"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md":["`boot_bless_receipt_digests`","which exact `boot.bless.receipt` participated"],
        "docs/633-incident-bundles-carry-boot-bless-proof-by-digest.md":["`boot_bless_receipts`","`boot_bless_receipt_digests`","greenboot status text"],
        "docs/98-archive-hygiene.md":["check_boot_bless_bundle_contract.py","typed place for `boot.bless.receipt` proof"],
        "docs/99-llm-runbook.md":["check_boot_bless_bundle_contract.py","support handoff can carry `boot_bless_receipt_digests`"],
    }
    for rel, needles in doc_checks.items():
        text=(ROOT/rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Boot-bless bundle contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
