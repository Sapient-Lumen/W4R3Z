#!/usr/bin/env python3
"""Guardrail for workstation stale supersession denials carrying current-head evidence and recovery target."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md": ["stale_target_evidence = observed-current-head-required", "stale_target_recovery = fresh-explicit-supersession-required", "observed_current_receipt_digest", "fresh-explicit-supersession-required"],
    "adrs/ADR-0204-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md": ["stale_target_evidence = observed-current-head-required", "stale_target_recovery = fresh-explicit-supersession-required", "observed_current_receipt_digest", "current-head evidence"],
    "docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md": ["docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md", "observed current head"],
    "docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md": ["docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md", "observed_current_receipt_digest"],
    "docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md": ["docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md", "fresh-explicit-supersession-required"],
    "docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md": ["docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md", "observed current-head denial evidence"],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": ["docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md", "observed current head"],
    "docs/266-open-questions-and-risk-register.md": ["ADR-0204", "stale_target_evidence = observed-current-head-required", "stale_target_recovery = fresh-explicit-supersession-required"],
    "docs/99-llm-runbook.md": ["docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md", "check_workstation_candidate_stale_denial_boundary.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_candidate_stale_denial_boundary.py", "stale supersession denials carry observed current-head evidence"],
    "docs/110-juicy-os-lessons.md": ["Stale candidate-supersession denials should carry observed current-head evidence", "docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md"],
    "README.md": ["docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md", "stale_target_evidence", "observed_current_receipt_digest"],
    "spec/content.reintegrate.plan.schema.json": ['"stale_target_evidence"', '"observed-current-head-required"', '"stale_target_recovery"', '"fresh-explicit-supersession-required"'],
    "spec/content.reintegrate.receipt.schema.json": ['"stale_target_evidence"', '"observed-current-head-required"', '"reason_code"', '"stale-supersession-target"', '"observed_current_receipt_digest"'],
    "spec/content.reintegrate.receipt.stale-target-denied.schema.json": ['"reason_code"', '"stale-supersession-target"', '"observed_current_receipt_digest"'],
    "spec/examples/content.reintegrate.plan.json": ['"stale_target_evidence": "observed-current-head-required"', '"stale_target_recovery": "fresh-explicit-supersession-required"'],
    "spec/examples/content.reintegrate.receipt.json": ['"stale_target_evidence": "observed-current-head-required"', '"stale_target_recovery": "fresh-explicit-supersession-required"'],
    "spec/examples/content.reintegrate.receipt.stale-target-denied.json": ['"reason_code": "stale-supersession-target"', '"observed_current_receipt_digest"', '"recovery_posture": "fresh-explicit-supersession-required"'],
}

def main() -> int:
    errors = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Workstation candidate stale-denial boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
