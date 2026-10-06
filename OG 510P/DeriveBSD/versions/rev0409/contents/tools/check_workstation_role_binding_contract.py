#!/usr/bin/env python3
"""Guardrail for workstation role-binding typed-state boundary."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "intent.role.binding",
        "persistent-compartment",
        "disposable-template",
        "role_binding_digest",
    ],
    "adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "intent.role.binding",
        "role_binding_digest",
        "persistent-compartment",
        "disposable-template",
    ],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md",
        "typed state",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "role_binding_digest",
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md",
    ],
    "docs/179-portals-and-powerbox.md": [
        "intent.role.binding",
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "intent.role.binding",
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "intent.role.binding",
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0131",
        "typed `intent.role.binding`",
    ],
    "docs/99-llm-runbook.md": [
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md",
        "check_workstation_role_binding_contract.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_role_binding_contract.py",
        "role_binding_digest",
    ],
    "docs/110-juicy-os-lessons.md": [
        "typed role-binding object",
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md",
    ],
    "README.md": [
        "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md",
        "intent.role.binding",
    ],
    "spec/intent.role.binding.schema.json": [
        '"kind":',
        '"intent.role.binding"',
        '"persistent-compartment"',
        '"disposable-template"',
    ],
    "spec/examples/intent.role.binding.json": [
        '"kind": "intent.role.binding"',
        '"target_kind": "persistent-compartment"',
        '"target_kind": "disposable-template"',
    ],
    "spec/intent.route.receipt.schema.json": [
        '"role_binding_digest"',
    ],
    "spec/examples/intent.route.receipt.json": [
        '"role_binding_digest":',
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
    print("Workstation role-binding contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
