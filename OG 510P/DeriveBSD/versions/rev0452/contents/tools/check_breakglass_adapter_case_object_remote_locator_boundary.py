#!/usr/bin/env python3
"""Guardrail for keeping breakglass accepted case-object visible remote locator continuity exact and safe."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def main() -> int:
    errors: list[str] = []
    schema = load_json("spec/incident.bundle.schema.json")
    includes = ((schema.get("properties") or {}).get("includes") or {}).get("properties") or {}
    required = ["remote-locator-continuous", "parent case/ticket/thread/container browse URLs", "Live control locators remain forbidden"]
    for field in ["extra", "breakglass_receipt_digests"]:
        desc = (includes.get(field) or {}).get("description") or ""
        for needle in required:
            if needle not in desc:
                errors.append(f"spec/incident.bundle.schema.json includes.{field} description missing required token: {needle}")
    ex = load_json("spec/examples/incident.bundle.json")
    extra = ((ex.get("includes") or {}).get("extra") or [])
    if not any("remotelocator" in item for item in extra):
        errors.append("spec/examples/incident.bundle.json includes.extra missing remote-locator continuity accepted case-object proof example")
    doc_checks = {
        "adrs/ADR-0310-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md": ["remote-locator-continuous when visible", "parent case, thread, container, bucket, or browse page", "metadata-only reverification"],
        "docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md": ["remote-locator-continuous when visible", "parent case/container browse URLs", "tools/check_breakglass_adapter_case_object_remote_locator_boundary.py"],
        "docs/216-incident-snapshots-and-support-bundles.md": ["remote-locator-continuous too", "parent case/container browse URLs"],
        "docs/236-breakglass-and-recovery-mode.md": ["remote-locator-continuous too", "live control locators remain forbidden"],
        "docs/250-breakglass-and-recovery-workflows.md": ["remote-locator-continuous too", "parent case/container browse URLs"],
        "docs/253-bundle-plans-and-deterministic-exports.md": ["remote-locator-continuous", "parent case/container browse URLs"],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": ["remote-locator-continuous", "parent case/container browse URLs"],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": ["remote-locator-continuous too", "parent case/container browse URLs"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0310", "metadata-only reverification"],
        "docs/98-archive-hygiene.md": ["check_breakglass_adapter_case_object_remote_locator_boundary.py", "parent case/container browse URLs"],
        "docs/99-llm-runbook.md": ["docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md", "tools/check_breakglass_adapter_case_object_remote_locator_boundary.py"],
        "docs/00-index.md": ["docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md", "tools/check_breakglass_adapter_case_object_remote_locator_boundary.py"],
        "docs/110-juicy-os-lessons.md": ["accepted case-object anchors should keep visible remote locators too", "docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md"],
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
    print("Breakglass accepted case-object remote locator continuity boundary: OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
