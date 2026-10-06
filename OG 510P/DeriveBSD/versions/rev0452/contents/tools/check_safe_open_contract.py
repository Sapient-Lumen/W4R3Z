#!/usr/bin/env python3
"""Guardrail for the safe-open support-bundle intake boundary."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    for rel in ["spec/content.import.plan.schema.json", "spec/content.import.receipt.schema.json"]:
        schema = load_json(rel)
        execution = (schema.get("properties") or {}).get("execution")
        if not execution:
            errors.append(f"{rel} missing execution object")
            continue
        required = execution.get("required") or []
        for field in ["isolation", "network", "lifetime"]:
            if field not in required:
                errors.append(f"{rel} execution missing required field {field}")
        props = execution.get("properties") or {}
        expected = {
            "isolation": {"host-adapter", "jail", "microvm"},
            "network": {"none", "brokered", "full"},
            "lifetime": {"disposable", "persistent"},
        }
        for field, want in expected.items():
            have = set((props.get(field) or {}).get("enum") or [])
            if have != want:
                errors.append(f"{rel} execution.{field} enum mismatch: {sorted(have)} != {sorted(want)}")

    plan = load_json("spec/examples/content.import.support-bundle.plan.json")
    if (plan.get("execution") or {}).get("network") != "none":
        errors.append("support-bundle import plan must default to execution.network = none")
    if (plan.get("execution") or {}).get("lifetime") != "disposable":
        errors.append("support-bundle import plan must default to execution.lifetime = disposable")
    if (plan.get("execution") or {}).get("isolation") != "microvm":
        errors.append("support-bundle import plan must default to execution.isolation = microvm")
    ops = [op.get("op") for op in plan.get("operations") or []]
    for expected_op in ["scan", "unpack", "classify"]:
        if expected_op not in ops:
            errors.append(f"support-bundle import plan missing operation: {expected_op}")
    if not str((plan.get("subject") or {}).get("filename", "")).endswith(".tar.zst"):
        errors.append("support-bundle import plan subject filename must end with .tar.zst")

    receipt = load_json("spec/examples/content.import.support-bundle.receipt.json")
    if (receipt.get("execution") or {}).get("network") != "none":
        errors.append("support-bundle import receipt must record execution.network = none")
    outputs = receipt.get("outputs") or []
    if not any(o.get("path") == "/var/derive/imports/case-8841/meta/incident.timeline.json" for o in outputs):
        errors.append("support-bundle import receipt must expose timeline-preview path")

    doc_checks = {
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "safe-open intake path",
            "`content.import.plan`",
            "`content.import.receipt`",
            "`incident.timeline`",
        ],
        "docs/220-operational-time-travel-debugging.md": [
            "support bundles stay foreign evidence",
            "disposable workspace",
        ],
        "docs/267-sanitization-portal-and-disposable-sandboxes.md": [
            "support bundle",
            "no-network sandbox",
        ],
        "docs/280-origin-labels-and-quarantine-attributes.md": [
            "support bundles",
            "disposable sandbox",
            "`content.import.receipt`",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "safe-open intake path",
            "timeline-first preview",
            "foreign evidence",
        ],
        "docs/498-safe-open-support-bundle-intake-and-repro-boundary.md": [
            "`content.import.plan.execution`",
            "`content.import.receipt.execution`",
            "`incident.bundle`",
            "`debug.replay.capsule`",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "Guided incident reproduction + safe-open workflows [DECIDED]",
            "ADR-0088",
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

    print("Safe-open support-bundle contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
