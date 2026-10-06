#!/usr/bin/env python3
"""Guardrail for paired boot-override-then-reset breakglass bootstrap joins."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    receipt = load_json("spec/breakglass.receipt.schema.json")
    evidence = ((receipt.get("properties") or {}).get("evidence") or {})
    props = evidence.get("properties") or {}
    posture_desc = ((props.get("bootstrap_join_sequence_posture") or {}).get("description") or "")
    joins_desc = ((props.get("bootstrap_receipt_joins") or {}).get("description") or "")

    for needle in [
        "boot.override.receipt.applied_at",
        "later `reset.receipt.applied_at`/`finished_at`",
        "override selects the next boot",
        "reset consumes that selection",
    ]:
        if needle not in posture_desc:
            errors.append(f"spec/breakglass.receipt.schema.json bootstrap_join_sequence_posture description missing required token: {needle}")

    for needle in [
        "paired one-time-boot case",
        "`boot.override.receipt` appears before the later `reset.receipt`",
        "next-boot selection",
    ]:
        if needle not in joins_desc:
            errors.append(f"spec/breakglass.receipt.schema.json bootstrap_receipt_joins description missing required token: {needle}")

    ex = load_json("spec/examples/breakglass.receipt.json")
    ordered_kinds = [j.get("kind") for j in ((ex.get("evidence") or {}).get("bootstrap_receipt_joins") or [])]
    if ordered_kinds != ["boot.override.receipt", "reset.receipt"]:
        errors.append("spec/examples/breakglass.receipt.json bootstrap_receipt_joins should demonstrate the paired actuation order: boot.override.receipt before reset.receipt")

    doc_checks = {
        "adrs/ADR-0299-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md": [
            "boot.override.receipt",
            "reset.receipt",
            "select the next boot target",
            "rebooted or reset",
        ],
        "docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md": [
            "boot.override.receipt",
            "reset.receipt",
            "select the *next* boot target",
            "actuated that selection",
            "tools/check_breakglass_bootstrap_actuation_boundary.py",
        ],
        "docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md": [
            "`boot.override.receipt` that selected the next maintenance boot",
            "`reset.receipt` that actuated that selection",
            "docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "boot.override.receipt` comes before the later `reset.receipt`",
            "docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "`boot.override.receipt` first and the later `reset.receipt` second",
            "actuation step rather than the boot-selection step",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "keep `boot.override.receipt` before the later `reset.receipt` that actuated it",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0299",
            "`boot.override.receipt` then `reset.receipt`",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_bootstrap_actuation_boundary.py",
            "boot.override.receipt` before the later `reset.receipt`",
        ],
        "docs/99-llm-runbook.md": [
            "docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md",
            "tools/check_breakglass_bootstrap_actuation_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md",
            "tools/check_breakglass_bootstrap_actuation_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "GUI-order folklore",
            "docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md",
        ],
        "docs/32-curated-references.md": [
            "Dell iDRAC virtual console / next boot menu",
            "HPE iLO one-time boot status",
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
    print("Breakglass bootstrap actuation boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
