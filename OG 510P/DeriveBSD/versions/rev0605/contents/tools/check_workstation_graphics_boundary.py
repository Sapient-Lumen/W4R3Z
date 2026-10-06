#!/usr/bin/env python3
"""Guardrail for the workstation display composition / GPU boundary."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/536-workstation-display-composition-and-gpu-boundary.md": [
        "software-first guest rendering",
        "docs/537-workstation-remoted-session-surface-boundary.md",
        "session-surface-first",
        "raw DRM/render nodes",
        "direct PCI GPU passthrough",
    ],
    "adrs/ADR-0126-workstation-display-composition-and-gpu-boundary.md": [
        "software-first guest rendering",
        "raw host X11 access",
        "direct PCI GPU passthrough",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/536-workstation-display-composition-and-gpu-boundary.md",
        "software-rendered or 2D guest output",
        "raw host X11/DRM/render-node access",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/536-workstation-display-composition-and-gpu-boundary.md",
        "docs/537-workstation-remoted-session-surface-boundary.md",
        "remoted session surface",
        "software-rendered or simple 2D guest output",
    ],
    "docs/476-device-authority-posture-by-profile.md": [
        "docs/536-workstation-display-composition-and-gpu-boundary.md",
        "DRM/render-node",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0126",
        "host-owned composition",
        "software-first remoted GUI",
    ],
    "docs/99-llm-runbook.md": [
        "docs/536-workstation-display-composition-and-gpu-boundary.md",
        "check_workstation_graphics_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_graphics_boundary.py",
        "graphics/GUI boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "docs/536-workstation-display-composition-and-gpu-boundary.md",
        "software-first guest rendering",
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
    print("Workstation graphics boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
