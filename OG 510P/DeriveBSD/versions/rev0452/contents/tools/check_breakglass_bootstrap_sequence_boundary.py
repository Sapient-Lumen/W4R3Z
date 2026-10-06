#!/usr/bin/env python3
"""Guardrail for enabling-only ordered breakglass bootstrap receipt joins."""
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
    posture = props.get("bootstrap_join_sequence_posture") or {}

    if posture.get("enum") != ["earliest-to-latest-pre-session-enabling-only"]:
        errors.append("spec/breakglass.receipt.schema.json bootstrap_join_sequence_posture enum must be ['earliest-to-latest-pre-session-enabling-only']")
    pdesc = posture.get("description") or ""
    for needle in ["materially enabled the actual emergency session", "earliest-to-latest causal order", "denied attempts", "failed dead ends"]:
        if needle not in pdesc:
            errors.append(f"spec/breakglass.receipt.schema.json bootstrap_join_sequence_posture description missing required token: {needle}")

    jdesc = joins.get("description") or ""
    for needle in ["materially enabled this breakglass session", "earliest-to-latest order", "denied attempts", "failed dead ends"]:
        if needle not in jdesc:
            errors.append(f"spec/breakglass.receipt.schema.json bootstrap_receipt_joins description missing required token: {needle}")

    all_of = receipt.get("allOf") or []
    if not any(
        (((entry.get("if") or {}).get("properties") or {}).get("evidence") or {}).get("required") == ["bootstrap_receipt_joins"]
        and "bootstrap_join_sequence_posture" in ((((entry.get("then") or {}).get("properties") or {}).get("evidence") or {}).get("required") or [])
        for entry in all_of
    ):
        errors.append("spec/breakglass.receipt.schema.json must require bootstrap_join_sequence_posture when bootstrap_receipt_joins are present")

    ex = load_json("spec/examples/breakglass.receipt.json")
    evidence_ex = ex.get("evidence") or {}
    joins_ex = evidence_ex.get("bootstrap_receipt_joins") or []
    if len(joins_ex) < 2:
        errors.append("spec/examples/breakglass.receipt.json must exercise ordered plural bootstrap_receipt_joins")
    else:
        ordered_kinds = [j.get("kind") for j in joins_ex]
        if ordered_kinds != ["boot.override.receipt", "reset.receipt"]:
            errors.append("spec/examples/breakglass.receipt.json bootstrap_receipt_joins should demonstrate earliest-to-latest order with boot.override.receipt before reset.receipt in the paired one-time-boot case")
    if evidence_ex.get("bootstrap_join_sequence_posture") != "earliest-to-latest-pre-session-enabling-only":
        errors.append("spec/examples/breakglass.receipt.json must set bootstrap_join_sequence_posture to earliest-to-latest-pre-session-enabling-only")

    doc_checks = {
        "adrs/ADR-0298-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md": [
            "enabling-only", "earliest-to-latest", "denied attempts", "failed dead ends"
        ],
        "docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md": [
            "bootstrap_join_sequence_posture", "earliest-to-latest-pre-session-enabling-only", "enabling-only", "denied attempts"
        ],
        "docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md": [
            "docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md", "earliest-to-latest"
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "bootstrap_join_sequence_posture", "earliest-to-latest-pre-session-enabling-only"
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "bootstrap_join_sequence_posture", "earliest-to-latest-pre-session-enabling-only", "denied attempts", "boot.override.receipt` before the later `reset.receipt`"
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "bootstrap_join_sequence_posture", "earliest-to-latest-pre-session-enabling-only"
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0298", "earliest-to-latest-pre-session-enabling-only"
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_bootstrap_sequence_boundary.py", "earliest-to-latest-pre-session-enabling-only"
        ],
        "docs/99-llm-runbook.md": [
            "docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md", "tools/check_breakglass_bootstrap_sequence_boundary.py", "docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md"
        ],
        "docs/00-index.md": [
            "docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md", "tools/check_breakglass_bootstrap_sequence_boundary.py", "docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md"
        ],
        "docs/110-juicy-os-lessons.md": [
            "earliest-to-latest-pre-session-enabling-only", "denied attempts", "boot.override.receipt` before the later `reset.receipt`"
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
    print("Breakglass bootstrap sequence boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
