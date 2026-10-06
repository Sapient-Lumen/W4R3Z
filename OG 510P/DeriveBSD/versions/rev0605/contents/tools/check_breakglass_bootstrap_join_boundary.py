#!/usr/bin/env python3
"""Guardrail for exact pre-session breakglass bootstrap receipt joins."""
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
    joins = props.get("bootstrap_receipt_joins") or {}
    posture = props.get("bootstrap_join_posture") or {}

    join_items = joins.get("items") or {}
    kind = (join_items.get("properties") or {}).get("kind") or {}
    if kind.get("enum") != ["boot.override.receipt", "reset.receipt"]:
        errors.append("spec/breakglass.receipt.schema.json bootstrap_receipt_joins kind enum must be ['boot.override.receipt', 'reset.receipt']")
    jdesc = joins.get("description") or ""
    for needle in ["pre-session recovery-path receipts", "boot override", "reset/reprovision", "not for post-entry repair receipts"]:
        if needle not in jdesc:
            errors.append(f"spec/breakglass.receipt.schema.json bootstrap_receipt_joins description missing required token: {needle}")
    if posture.get("enum") != ["pre-session-recovery-path-only"]:
        errors.append("spec/breakglass.receipt.schema.json bootstrap_join_posture enum must be ['pre-session-recovery-path-only']")
    pdesc = posture.get("description") or ""
    for needle in ["before the breakglass session opened", "repair_outcome.authoritative_receipt_digests"]:
        if needle not in pdesc:
            errors.append(f"spec/breakglass.receipt.schema.json bootstrap_join_posture description missing required token: {needle}")

    all_of = receipt.get("allOf") or []
    if not any(
        (((entry.get("if") or {}).get("properties") or {}).get("evidence") or {}).get("required") == ["bootstrap_receipt_joins"]
        and ((((entry.get("then") or {}).get("properties") or {}).get("evidence") or {}).get("required") == ["bootstrap_join_posture"])
        for entry in all_of
    ):
        errors.append("spec/breakglass.receipt.schema.json must require bootstrap_join_posture when bootstrap_receipt_joins are present")

    ex = load_json("spec/examples/breakglass.receipt.json")
    evidence_ex = ex.get("evidence") or {}
    joins_ex = evidence_ex.get("bootstrap_receipt_joins") or []
    if not joins_ex:
        errors.append("spec/examples/breakglass.receipt.json must exercise bootstrap_receipt_joins")
    else:
        if joins_ex[0].get("kind") != "boot.override.receipt":
            errors.append("spec/examples/breakglass.receipt.json bootstrap_receipt_joins should demonstrate boot.override.receipt in the canonical example")
    if evidence_ex.get("bootstrap_join_posture") != "pre-session-recovery-path-only":
        errors.append("spec/examples/breakglass.receipt.json must set bootstrap_join_posture to pre-session-recovery-path-only")

    doc_checks = {
        "adrs/ADR-0297-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md": [
            "bootstrap_receipt_joins[]", "boot.override.receipt", "reset.receipt", "pre-session only", "virtual-media"
        ],
        "docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md": [
            "bootstrap_receipt_joins[]", "bootstrap_join_posture", "boot.override.receipt", "reset.receipt", "pre-session-recovery-path-only"
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "bootstrap_receipt_joins", "boot.override.receipt", "pre-session-recovery-path-only"
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "bootstrap_receipt_joins[]", "boot.override.receipt` / `reset.receipt`", "pre-session-recovery-path-only"
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "bootstrap_receipt_joins[]", "boot.override.receipt` / `reset.receipt`", "BMC breadcrumbs"
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0297", "boot.override.receipt` / `reset.receipt` digests"
        ],
        "docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md": [
            "docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md"
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_bootstrap_join_boundary.py", "pre-session-recovery-path-only"
        ],
        "docs/99-llm-runbook.md": [
            "docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md", "tools/check_breakglass_bootstrap_join_boundary.py"
        ],
        "docs/00-index.md": [
            "docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md", "tools/check_breakglass_bootstrap_join_boundary.py"
        ],
        "docs/110-juicy-os-lessons.md": [
            "bootstrap_receipt_joins[]", "pre-session-recovery-path-only"
        ],
        "docs/32-curated-references.md": [
            "DMTF Redfish Resource and Schema Guide (`ComputerSystem.BootSourceOverrideTarget`, manager `SerialInterfaces`)"
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
    print("Breakglass bootstrap join boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
