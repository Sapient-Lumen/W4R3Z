#!/usr/bin/env python3
"""Guardrail for the workstation URI-opening boundary."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/539-workstation-intent-routed-uri-opening-floor.md": [
        "intent-routing",
        "designated browsing compartment",
        "designated communications compartment",
        "file://",
        "deny-by-default",
    ],
    "adrs/ADR-0129-workstation-intent-routed-uri-opening-floor.md": [
        "intent-routing",
        "designated browsing compartment",
        "file://",
        "deny-by-default",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "docs/539-workstation-intent-routed-uri-opening-floor.md",
        "xdg-open as ambient authority",
        "designated browsing compartment",
    ],
    "docs/179-portals-and-powerbox.md": [
        "docs/539-workstation-intent-routed-uri-opening-floor.md",
        "URI opening / handler routing",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "intent-routed, compartment-preserving",
        "designated browsing compartment",
        "docs/539-workstation-intent-routed-uri-opening-floor.md",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "designated browsing compartment",
        "designated communications compartment",
        "docs/539-workstation-intent-routed-uri-opening-floor.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0129",
        "intent-routed URI opening",
        "trusted host is not the default renderer",
    ],
    "docs/99-llm-runbook.md": [
        "docs/539-workstation-intent-routed-uri-opening-floor.md",
        "check_workstation_uri_open_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_uri_open_boundary.py",
        "URI-opening boundary",
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Workstation URI-opening boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
