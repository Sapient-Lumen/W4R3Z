#!/usr/bin/env python3
"""Guardrail for workstation stale-supersession recovery staying denial-joined and head-pinned."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md": [
        "recovery.mode = from-stale-supersession-denial",
        "stale_denial_receipt_digest",
        "expected_current_receipt_digest",
        "head-pinned",
    ],
    "adrs/ADR-0205-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md": [
        "mode = none | from-stale-supersession-denial",
        "stale_denial_receipt_digest",
        "expected_current_receipt_digest",
        "denial-joined",
    ],
    "docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md": [
        "fresh-explicit-supersession-required",
        "observed_current_receipt_digest",
    ],
    "docs/99-llm-runbook.md": [
        "docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md",
        "check_workstation_candidate_retry_recovery_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_candidate_retry_recovery_boundary.py",
        "stale-supersession recovery denial-joined and head-pinned",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Fresh recovery after stale supersession should stay denial-joined and head-pinned",
        "docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0205",
        "from-stale-supersession-denial",
        "expected_current_receipt_digest",
    ],
    "README.md": [
        "docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md",
        "stale_denial_receipt_digest",
        "expected_current_receipt_digest",
    ],
    "spec/content.reintegrate.plan.schema.json": [
        '"recovery"',
        '"from-stale-supersession-denial"',
        '"stale_denial_receipt_digest"',
        '"expected_current_receipt_digest"',
    ],
    "spec/content.reintegrate.receipt.schema.json": [
        '"recovery"',
        '"from-stale-supersession-denial"',
        '"stale_denial_receipt_digest"',
        '"expected_current_receipt_digest"',
    ],
    "spec/content.reintegrate.plan.stale-target-retry.schema.json": [
        '"from-stale-supersession-denial"',
        '"stale_denial_receipt_digest"',
        '"supersede-prior-candidate"',
    ],
    "spec/content.reintegrate.receipt.stale-target-retry.schema.json": [
        '"from-stale-supersession-denial"',
        '"stale_denial_receipt_digest"',
        '"supersede-prior-candidate"',
    ],
    "spec/examples/content.reintegrate.plan.json": [
        '"recovery": {',
        '"mode": "none"',
    ],
    "spec/examples/content.reintegrate.receipt.json": [
        '"recovery": {',
        '"mode": "none"',
    ],
    "spec/examples/content.reintegrate.receipt.stale-target-denied.json": [
        '"recovery": {',
        '"mode": "none"',
        '"observed_current_receipt_digest"',
    ],
    "spec/examples/content.reintegrate.plan.stale-target-retry.json": [
        '"mode": "from-stale-supersession-denial"',
        '"stale_denial_receipt_digest"',
        '"expected_current_receipt_digest"',
    ],
    "spec/examples/content.reintegrate.receipt.stale-target-retry.json": [
        '"mode": "from-stale-supersession-denial"',
        '"stale_denial_receipt_digest"',
        '"expected_current_receipt_digest"',
    ],
}

def _jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    stale = _load_json("spec/examples/content.reintegrate.receipt.stale-target-denied.json")
    retry_plan = _load_json("spec/examples/content.reintegrate.plan.stale-target-retry.json")
    retry_receipt = _load_json("spec/examples/content.reintegrate.receipt.stale-target-retry.json")

    stale_digest = "sha256:" + hashlib.sha256(_jcs_bytes(stale)).hexdigest()
    stale_result = stale.get("result", {})
    retry_plan_recovery = retry_plan.get("recovery", {})
    retry_receipt_recovery = retry_receipt.get("recovery", {})

    if stale_result.get("reason_code") != "stale-supersession-target":
        errors.append("stale-target denial example must keep result.reason_code = stale-supersession-target")
    if stale_result.get("recovery_posture") != "fresh-explicit-supersession-required":
        errors.append("stale-target denial example must keep result.recovery_posture = fresh-explicit-supersession-required")

    for label, recovery in [("retry plan", retry_plan_recovery), ("retry receipt", retry_receipt_recovery)]:
        if recovery.get("mode") != "from-stale-supersession-denial":
            errors.append(f"{label} recovery.mode must be from-stale-supersession-denial")
        if recovery.get("stale_denial_receipt_digest") != stale_digest:
            errors.append(f"{label} stale_denial_receipt_digest must match computed digest of stale-target denial example")
        for src, dst in [
            ("observed_current_receipt_digest", "expected_current_receipt_digest"),
            ("observed_current_candidate_digest", "expected_current_candidate_digest"),
            ("observed_current_authoritative_origin_digest", "expected_current_authoritative_origin_digest"),
        ]:
            if recovery.get(dst) != stale_result.get(src):
                errors.append(f"{label} {dst} must match stale denial {src}")

    for label, obj in [("retry plan", retry_plan), ("retry receipt", retry_receipt)]:
        supersession = obj.get("supersession", {})
        recovery = obj.get("recovery", {})
        if supersession.get("mode") != "supersede-prior-candidate":
            errors.append(f"{label} supersession.mode must stay supersede-prior-candidate")
        if supersession.get("supersedes_receipt_digest") != recovery.get("expected_current_receipt_digest"):
            errors.append(f"{label} supersedes_receipt_digest must match recovery.expected_current_receipt_digest")
        if supersession.get("superseded_candidate_digest") != recovery.get("expected_current_candidate_digest"):
            errors.append(f"{label} superseded_candidate_digest must match recovery.expected_current_candidate_digest")
        if supersession.get("superseded_authoritative_origin_digest") != recovery.get("expected_current_authoritative_origin_digest"):
            errors.append(f"{label} superseded_authoritative_origin_digest must match recovery.expected_current_authoritative_origin_digest")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Workstation candidate retry-recovery boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
