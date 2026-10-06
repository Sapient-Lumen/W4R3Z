#!/usr/bin/env python3
"""Guardrail for the workstation remoted session-surface boundary."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/537-workstation-remoted-session-surface-boundary.md": [
        "remoted session surface",
        "small-role or single-app AppVMs",
        "seamless host-native per-window guest integration",
    ],
    "adrs/ADR-0127-workstation-remoted-session-surface-boundary.md": [
        "remoted session surface",
        "seamless per-window remoting",
        "small-role or single-app AppVMs",
    ],
    "docs/536-workstation-display-composition-and-gpu-boundary.md": [
        "docs/537-workstation-remoted-session-surface-boundary.md",
        "session-surface-first",
        "future bounded adapter lane",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "remoted session surface",
        "small-role or single-app AppVMs",
        "docs/537-workstation-remoted-session-surface-boundary.md",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "session-surface-first",
        "not seamless per-window host-native windows",
        "docs/537-workstation-remoted-session-surface-boundary.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0127",
        "session-surface-first",
        "seamless per-window host-native integration",
    ],
    "docs/99-llm-runbook.md": [
        "docs/537-workstation-remoted-session-surface-boundary.md",
        "check_workstation_session_surface_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_session_surface_boundary.py",
        "session-surface boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "docs/537-workstation-remoted-session-surface-boundary.md",
        "session-surface-first",
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
    print("Workstation session-surface boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
