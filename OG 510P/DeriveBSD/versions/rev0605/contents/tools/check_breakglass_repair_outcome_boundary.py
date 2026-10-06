#!/usr/bin/env python3
"""Guardrail for typed breakglass closeout and exact repair-receipt joins."""
from __future__ import annotations
import json
from pathlib import Path

from cube_digest_lib import file_json_digest, load_json as load_json_strict
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return load_json_strict(ROOT, rel)

def digest(rel: str) -> str:
    return file_json_digest(ROOT, rel)

def main() -> int:
    errors = []
    schema = load_json("spec/breakglass.receipt.schema.json")
    repair = (schema.get("properties") or {}).get("repair_outcome") or {}
    rprops = repair.get("properties") or {}
    if repair.get("required") != ["status"]:
        errors.append("spec/breakglass.receipt.schema.json repair_outcome must require status")
    if (rprops.get("status") or {}).get("enum") != ["observation-only", "repair-pending-confirmation", "repair-confirmed", "repair-rolled-back", "repair-failed"]:
        errors.append("spec/breakglass.receipt.schema.json repair_outcome.status enum mismatch")
    if "authoritative_receipt_digests" not in rprops:
        errors.append("spec/breakglass.receipt.schema.json missing repair_outcome.authoritative_receipt_digests")
    allof_txt = json.dumps(schema.get("allOf", []), sort_keys=True)
    if "repair-pending-confirmation" not in allof_txt or "authoritative_receipt_digests" not in allof_txt:
        errors.append("spec/breakglass.receipt.schema.json must require authoritative_receipt_digests for non-observation repair_outcome statuses")

    accepted = load_json("spec/examples/breakglass.receipt.json")
    aout = accepted.get("repair_outcome") or {}
    if aout.get("status") != "repair-pending-confirmation":
        errors.append("spec/examples/breakglass.receipt.json repair_outcome.status must be repair-pending-confirmation")
    expected_cfg = digest("spec/examples/config.receipt.json")
    if (aout.get("authoritative_receipt_digests") or [None])[0] != expected_cfg:
        errors.append("spec/examples/breakglass.receipt.json repair_outcome.authoritative_receipt_digests[0] must match computed digest of spec/examples/config.receipt.json")

    rejected = load_json("spec/examples/breakglass.receipt.rejected.json")
    rout = rejected.get("repair_outcome") or {}
    if rout.get("status") != "observation-only":
        errors.append("spec/examples/breakglass.receipt.rejected.json repair_outcome.status must be observation-only")
    if rout.get("authoritative_receipt_digests"):
        errors.append("spec/examples/breakglass.receipt.rejected.json must not carry authoritative_receipt_digests for observation-only closeout")

    doc_checks = {
        "adrs/ADR-0295-breakglass-closeout-stays-explicit-repair-outcome-and-receipt-joined.md": [
            "repair_outcome", "authoritative_receipt_digests", "do **not** count as repair proof"
        ],
        "docs/705-breakglass-closeout-stays-explicit-repair-outcome-and-receipt-joined.md": [
            "repair-pending-confirmation", "authoritative_receipt_digests", "proving the repair succeeded"
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "breakglass.receipt.repair_outcome", "repair-pending-confirmation", "repair-confirmed"
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "repair_outcome", "Session end is not repair proof", "exact authoritative receipt digests"
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "typed `repair_outcome` closeout truth"
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0295", "breakglass.receipt.repair_outcome"
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_repair_outcome_boundary.py", "session end or notes masquerade as repair proof"
        ],
        "docs/99-llm-runbook.md": [
            "check_breakglass_repair_outcome_boundary.py", "docs/705-breakglass-closeout-stays-explicit-repair-outcome-and-receipt-joined.md"
        ],
        "docs/00-index.md": [
            "docs/705-breakglass-closeout-stays-explicit-repair-outcome-and-receipt-joined.md", "check_breakglass_repair_outcome_boundary.py"
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
    print("Breakglass repair outcome boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
