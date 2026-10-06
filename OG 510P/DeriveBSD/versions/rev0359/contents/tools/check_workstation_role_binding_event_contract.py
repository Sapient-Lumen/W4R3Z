#!/usr/bin/env python3
"""Guardrail for the role-binding event evidence surface."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/543-role-binding-event-as-durable-mutation-evidence.md": [
        "intent.role.binding.event",
        "Event Journal",
        "initialized",
        "updated",
        "write-denied",
    ],
    "adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md": [
        "intent.role.binding.event",
        "initialized",
        "updated",
        "write-denied",
    ],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "intent.role.binding.event",
        "snapshot-plus-diff-plus-event",
    ],
    "docs/542-role-binding-diff-as-review-surface.md": [
        "intent.role.binding.event",
        "durable mutation trace",
    ],
    "docs/215-structured-event-log-as-evidence.md": [
        "intent.role.binding.event",
    ],
    "docs/216-incident-snapshots-and-support-bundles.md": [
        "intent.role.binding.event",
    ],
    "docs/229-evidence-spine-overview.md": [
        "intent.role.binding.event",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "intent.role.binding.event",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "intent.role.binding.event",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0133",
        "intent.role.binding.event",
    ],
    "docs/99-llm-runbook.md": [
        "docs/543-role-binding-event-as-durable-mutation-evidence.md",
        "check_workstation_role_binding_event_contract.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_role_binding_event_contract.py",
        "intent.role.binding.event",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Role/default changes need a durable mutation event",
        "docs/543-role-binding-event-as-durable-mutation-evidence.md",
    ],
    "README.md": [
        "docs/543-role-binding-event-as-durable-mutation-evidence.md",
        "intent.role.binding.event",
    ],
    "spec/intent.role.binding.event.schema.json": [
        '"kind":',
        '"intent.role.binding.event"',
        '"initialized"',
        '"updated"',
        '"write-denied"',
    ],
    "spec/examples/intent.role.binding.event.json": [
        '"kind": "intent.role.binding.event"',
        '"action": "updated"',
        '"role-binding-default-changed"',
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
    print("Workstation role-binding event contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
