#!/usr/bin/env python3
"""Guardrail for the official support-bundle handoff contract.

This checker keeps the archive's timeline-first support-handoff contract wired:
- incident.bundle carries incident_timeline_digest
- bundle.build.receipt can bind incident_timeline_digest
- canonical examples use tar.zst by default
- the payload manifest example includes the incident timeline member
- key docs mention the contract pieces so discovery doesn't drift
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    incident_schema = load_json("spec/incident.bundle.schema.json")
    includes = incident_schema["properties"]["includes"]["properties"]
    if "incident_timeline_digest" not in includes:
        errors.append("spec/incident.bundle.schema.json missing includes.incident_timeline_digest")

    build_schema = load_json("spec/bundle.build.receipt.schema.json")
    output = build_schema["properties"]["output"]["properties"]
    if "incident_timeline_digest" not in output:
        errors.append("spec/bundle.build.receipt.schema.json missing output.incident_timeline_digest")

    incident_example = load_json("spec/examples/incident.bundle.json")
    if not (incident_example.get("includes") or {}).get("incident_timeline_digest"):
        errors.append("spec/examples/incident.bundle.json missing includes.incident_timeline_digest")

    build_example = load_json("spec/examples/bundle.build.receipt.json")
    if (build_example.get("output") or {}).get("format") != "tar.zst":
        errors.append("spec/examples/bundle.build.receipt.json output.format must default to 'tar.zst'")
    if not (build_example.get("output") or {}).get("incident_timeline_digest"):
        errors.append("spec/examples/bundle.build.receipt.json missing output.incident_timeline_digest")

    plan_example = load_json("spec/examples/bundle.plan.json")
    if (plan_example.get("output") or {}).get("format") != "tar.zst":
        errors.append("spec/examples/bundle.plan.json output.format must default to 'tar.zst'")

    manifest_example = load_json("spec/examples/bundle.payload.manifest.json")
    payload = manifest_example.get("payload") or {}
    if payload.get("format") != "tar.zst":
        errors.append("spec/examples/bundle.payload.manifest.json payload.format must default to 'tar.zst'")
    entries = manifest_example.get("entries") or []
    timeline_entries = [
        e for e in entries
        if (e.get("source") or {}).get("kind") == "incident-timeline"
    ]
    if not timeline_entries:
        errors.append("spec/examples/bundle.payload.manifest.json missing incident-timeline entry")
    elif timeline_entries[0].get("path") != "meta/incident.timeline.json":
        errors.append("incident-timeline entry in bundle.payload.manifest example must use path meta/incident.timeline.json")

    doc_checks = {
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "`incident.timeline`",
            "`bundle.plan`",
            "`bundle.payload.manifest`",
            "`bundle.build.receipt`",
            "**`tar.zst`**",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "`incident.timeline`",
            "`bundle.build.receipt`",
            "**`tar.zst`**",
        ],
        "docs/419-incident-timelines-as-derived-artifacts.md": [
            "official support bundle",
            "`incident.bundle`",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "`incident.timeline`",
            "`incident.bundle`",
            "`bundle.plan`",
            "`bundle.payload.manifest`",
            "`bundle.build.receipt`",
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

    print("Support-bundle contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
