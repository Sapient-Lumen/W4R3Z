#!/usr/bin/env python3
"""Guardrail for the workstation role-bound intent-target / chooser boundary."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "trusted host-managed target roles",
        "browsing",
        "communications",
        "trusted-chooser",
        "first-open prompts do **not** rewrite global defaults",
    ],
    "adrs/ADR-0130-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "trusted host-managed target roles",
        "browsing",
        "communications",
        "role-default",
        "trusted-chooser",
        "policy-pinned",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md",
        "target_role",
        "resolution_mode",
        "trusted-chooser",
    ],
    "docs/179-portals-and-powerbox.md": [
        "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md",
        'trusted host-managed role slots',
    ],
    "docs/410-desktop-viability-checklist.md": [
        "trusted host-managed role slots",
        "first-open default rewrites",
        "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "trusted host-managed role slots",
        "arbitrary handler discovery",
        "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md",
    ],
    "docs/539-workstation-intent-routed-uri-opening-floor.md": [
        "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0130",
        "chooser/default-app behavior onto trusted host-managed role slots",
    ],
    "docs/99-llm-runbook.md": [
        "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md",
        "check_workstation_intent_role_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_intent_role_boundary.py",
        "trusted host-managed roles",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Default handlers are safer as host-managed roles",
        "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md",
    ],
    "README.md": [
        "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md",
        "open with…",
    ],
    "spec/intent.route.receipt.schema.json": [
        '"target_role"',
        '"resolution_mode"',
        '"role-default"',
        '"trusted-chooser"',
        '"policy-pinned"',
    ],
    "spec/examples/intent.route.receipt.json": [
        '"target_role": "browsing"',
        '"resolution_mode": "role-default"',
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
    print("Workstation intent-role boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
