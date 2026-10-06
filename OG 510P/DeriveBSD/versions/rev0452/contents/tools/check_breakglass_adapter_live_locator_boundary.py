#!/usr/bin/env python3
"""Guardrail for keeping portable supplementary breakglass adapter/runtime evidence off live control locators."""
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

    extra_desc = (includes.get("extra") or {}).get("description") or ""
    for needle in [
        "Portable supplementary breakglass adapter/runtime evidence carried here must stay artifactized",
        "ConsoleEntryCommand",
        "WebSocketEndpoint",
        "session ids/tokens",
    ]:
        if needle not in extra_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.extra description missing required token: {needle}")

    breakglass_desc = (includes.get("breakglass_receipt_digests") or {}).get("description") or ""
    for needle in [
        "Keep live control locators",
        "copied console-entry commands",
        "exported artifacts and typed handling receipts are the portable surface instead",
    ]:
        if needle not in breakglass_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.breakglass_receipt_digests description missing required token: {needle}")

    doc_checks = {
        "adrs/ADR-0304-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md": [
            "artifactized evidence",
            "ConsoleEntryCommand",
            "WebSocketEndpoint",
            "live control locators",
        ],
        "docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md": [
            "artifactized",
            "`extra[]` is not a place for live control surfaces",
            "tools/check_breakglass_adapter_live_locator_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "keep supplementary breakglass adapter/runtime evidence artifactized",
            "WebSocketEndpoint",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "artifactized rather than live-locator-shaped",
            "ConsoleEntryCommand",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "must also stay artifactized",
            "WebSocketEndpoint",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "Keep the portable story artifactized too",
            "session tokens",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "artifactized rather than live-locator-shaped",
            "docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "same portable story must stay artifactized too",
            "ConsoleEntryCommand",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0304",
            "artifactized",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_live_locator_boundary.py",
            "portable supplementary breakglass adapter/runtime evidence artifactized",
        ],
        "docs/99-llm-runbook.md": [
            "docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md",
            "tools/check_breakglass_adapter_live_locator_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md",
            "tools/check_breakglass_adapter_live_locator_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "Portable breakglass side evidence should not carry live console entrypoints",
            "docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md",
        ],
        "docs/32-curated-references.md": [
            "WebSocketEndpoint",
            "intel-server-obmc-redfish-interface.pdf",
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
    print("Breakglass adapter live-locator boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
