#!/usr/bin/env python3
"""Guardrail for the role-binding diff review surface."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/542-role-binding-diff-as-review-surface.md": [
        "intent.role.binding.diff",
        "Registry→Diff→Gate",
        "role-binding-default-changed",
        "role-binding-target-enrolled",
        "role-binding-target-removed",
    ],
    "adrs/ADR-0132-role-binding-diff-as-review-surface.md": [
        "intent.role.binding.diff",
        "drift.bundle",
        "role-binding-default-changed",
    ],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "intent.role.binding.diff",
        "snapshot-plus-diff",
    ],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "intent.role.binding.diff",
        "trusted settings/admin UX",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "intent.role.binding.diff",
        "snapshot-plus-diff",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "intent.role.binding.diff",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "intent.role.binding.diff",
    ],
    "docs/430-diff-surface-registry.md": [
        "intent.role.binding.diff",
        "docs/542-role-binding-diff-as-review-surface.md",
    ],
    "docs/395-drift-bundles-and-review-summaries.md": [
        "intent.role.binding.diff",
    ],
    "docs/229-evidence-spine-overview.md": [
        "intent.role.binding.diff",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0132",
        "intent.role.binding.diff",
    ],
    "docs/99-llm-runbook.md": [
        "docs/542-role-binding-diff-as-review-surface.md",
        "check_workstation_role_binding_diff_contract.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_role_binding_diff_contract.py",
        "intent.role.binding.diff",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Role/default changes need a compact diff surface",
        "docs/542-role-binding-diff-as-review-surface.md",
    ],
    "README.md": [
        "docs/542-role-binding-diff-as-review-surface.md",
        "intent.role.binding.diff",
    ],
    "spec/intent.role.binding.diff.schema.json": [
        '"kind":',
        '"intent.role.binding.diff"',
        '"default-target"',
        '"target-enrolled"',
        '"target-removed"',
    ],
    "spec/examples/intent.role.binding.diff.json": [
        '"kind": "intent.role.binding.diff"',
        '"role-binding-default-changed"',
        '"role-binding-target-enrolled"',
        '"role-binding-target-removed"',
    ],
    "spec/examples/risk.flag.registry.json": [
        '"id": "role-binding-default-changed"',
        '"id": "role-binding-target-enrolled"',
        '"id": "role-binding-target-removed"',
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
    print("Workstation role-binding diff contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
