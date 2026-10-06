#!/usr/bin/env python3
"""Guardrail for hardware support qualification target-scope boundary."""
from __future__ import annotations

import json
from pathlib import Path
from cube_digest_lib import canonical_digest

ROOT = Path(__file__).resolve().parents[1]
TARGET_BINDINGS = [
    "exact-artifact-digest",
    "same-release-train",
    "same-release-train-and-boot-manifest",
]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))




def main() -> int:
    errors: list[str] = []

    matrix_schema = load_json("spec/hw.support.matrix.schema.json")
    profile_schema = load_json("spec/hw.support.qualification.profile.schema.json")
    receipt_schema = load_json("spec/hw.support.qualification.receipt.schema.json")
    report_schema = load_json("spec/hw.compat.report.schema.json")
    matrix_ex = load_json("spec/examples/hw.support.matrix.json")
    profile_ex = load_json("spec/examples/hw.support.qualification.profile.json")
    receipt_ex = load_json("spec/examples/hw.support.qualification.receipt.json")
    report_ex = load_json("spec/examples/hw.compat.report.json")

    for rel, schema in [("spec/hw.support.matrix.schema.json", matrix_schema), ("spec/hw.support.qualification.profile.schema.json", profile_schema), ("spec/hw.support.qualification.receipt.schema.json", receipt_schema)]:
        target = ((schema.get("properties") or {}).get("target") or {})
        if "release_train" not in (target.get("required") or []):
            errors.append(f"{rel} target must require release_train")

    receipt_qual = ((receipt_schema.get("properties") or {}).get("qualification") or {})
    if "target_binding" not in (receipt_qual.get("required") or []):
        errors.append("spec/hw.support.qualification.receipt.schema.json qualification must require target_binding")
    if (((receipt_qual.get("properties") or {}).get("target_binding") or {}).get("enum") or []) != TARGET_BINDINGS:
        errors.append("spec/hw.support.qualification.receipt.schema.json qualification.target_binding enum must use the canonical target-binding list")

    matrix_qual = ((((matrix_schema.get("properties") or {}).get("entries") or {}).get("items") or {}).get("properties") or {}).get("qualification") or {}
    if "target_binding" not in (matrix_qual.get("required") or []):
        errors.append("spec/hw.support.matrix.schema.json entries[].qualification must require target_binding")
    if (((matrix_qual.get("properties") or {}).get("target_binding") or {}).get("enum") or []) != TARGET_BINDINGS:
        errors.append("spec/hw.support.matrix.schema.json entries[].qualification.target_binding enum must use the canonical target-binding list")

    report_target = ((report_schema.get("properties") or {}).get("target") or {})
    if "release_train" not in (report_target.get("required") or []):
        errors.append("spec/hw.compat.report.schema.json target must require release_train")
    if "release_capsule_digest" not in (report_target.get("properties") or {}):
        errors.append("spec/hw.compat.report.schema.json target must define release_capsule_digest")

    finding_codes = (((((report_schema.get("properties") or {}).get("findings") or {}).get("items") or {}).get("properties") or {}).get("code") or {}).get("enum") or []
    if "qualification-target-mismatch" not in finding_codes:
        errors.append("spec/hw.compat.report.schema.json findings.code must include qualification-target-mismatch")
    sm_props = ((report_schema.get("properties") or {}).get("support_matrix") or {}).get("properties") or {}
    for field in ("matched_target_binding", "target_scope_state"):
        if field not in sm_props:
            errors.append(f"spec/hw.compat.report.schema.json support_matrix must define {field}")

    if profile_ex.get("target", {}).get("release_train") != "r261":
        errors.append("spec/examples/hw.support.qualification.profile.json target.release_train must stay on canonical r261 scope")
    if receipt_ex.get("target", {}).get("release_train") != profile_ex.get("target", {}).get("release_train"):
        errors.append("spec/examples/hw.support.qualification.receipt.json target.release_train must match profile target.release_train")
    if matrix_ex.get("target", {}).get("release_train") != profile_ex.get("target", {}).get("release_train"):
        errors.append("spec/examples/hw.support.matrix.json target.release_train must match profile target.release_train")

    workstation_entry = None
    for entry in matrix_ex.get("entries", []):
        if entry.get("entry_id") == "b-laptop-intel-trusted-ui-floor-v1":
            workstation_entry = entry
            break
    if not workstation_entry:
        errors.append("spec/examples/hw.support.matrix.json missing canonical workstation trusted-UI entry")
    else:
        wb = (workstation_entry.get("qualification") or {}).get("target_binding")
        if wb != "same-release-train-and-boot-manifest":
            errors.append("spec/examples/hw.support.matrix.json canonical workstation entry qualification.target_binding must be same-release-train-and-boot-manifest")
        if wb != (receipt_ex.get("qualification") or {}).get("target_binding"):
            errors.append("spec/examples/hw.support.matrix.json canonical workstation entry qualification.target_binding must match receipt qualification.target_binding")

    receipt_digest = canonical_digest(receipt_ex)
    if report_ex.get("target", {}).get("release_train") == receipt_ex.get("target", {}).get("release_train"):
        errors.append("spec/examples/hw.compat.report.json target.release_train should intentionally differ from the receipt example to demonstrate target-scope mismatch")
    if (report_ex.get("support_matrix") or {}).get("matched_target_binding") != (receipt_ex.get("qualification") or {}).get("target_binding"):
        errors.append("spec/examples/hw.compat.report.json support_matrix.matched_target_binding must match receipt qualification.target_binding")
    if (report_ex.get("support_matrix") or {}).get("target_scope_state") != "mismatch":
        errors.append("spec/examples/hw.compat.report.json support_matrix.target_scope_state must be mismatch in the canonical example")

    finding = None
    for item in report_ex.get("findings", []):
        if item.get("code") == "qualification-target-mismatch":
            finding = item
            break
    if not finding:
        errors.append("spec/examples/hw.compat.report.json findings must include qualification-target-mismatch")
    elif receipt_digest not in (finding.get("refs") or []):
        errors.append("spec/examples/hw.compat.report.json qualification-target-mismatch finding must reference computed receipt digest")
    if (report_ex.get("recommendation") or {}).get("action") != "deny":
        errors.append("spec/examples/hw.compat.report.json recommendation.action must be deny in the canonical target-mismatch example")

    doc_checks = {
        "docs/320-hardware-compatibility-gates-and-safe-upgrades.md": ["`qualification-target-mismatch`", "`matched_target_binding`", "`target_scope_state`"],
        "docs/410-desktop-viability-checklist.md": ["`qualification-target-mismatch`", "`same-release-train-and-boot-manifest`", "`trusted-ui-consent`"],
        "docs/479-hardware-compatibility-posture-by-profile.md": ["`qualification-target-mismatch`", "`target_binding`", "`target_scope_state`"],
        "docs/528-hardware-support-matrix-and-bundled-admission-boundary.md": ["`release_train`", "`target_binding`", "`qualification-target-mismatch`"],
        "docs/529-hardware-support-promotion-and-qualification-boundary.md": ["`target_binding`", "`same-release-train-and-boot-manifest`", "`release-train`"],
        "docs/530-hardware-support-qualification-receipt-boundary.md": ["`target_binding`", "`matched_target_binding`", "`qualification-target-mismatch`"],
        "docs/531-hardware-support-qualification-profile-boundary.md": ["`release_train`", "`qualification.profile_digest`", "`target_binding`"],
        "docs/535-hardware-support-qualification-target-scope-boundary.md": ["`qualification-target-mismatch`", "`target_binding`", "`target_scope_state`"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0125", "`qualification-target-mismatch`"],
        "docs/99-llm-runbook.md": ["check_hw_support_qualification_target_scope_contract.py", "`qualification-target-mismatch`"],
        "docs/98-archive-hygiene.md": ["check_hw_support_qualification_target_scope_contract.py", "`target_binding`"],
        "docs/110-juicy-os-lessons.md": ["ADR-0125", "`target_binding`", "`qualification-target-mismatch`"],
        "adrs/ADR-0125-hardware-support-qualification-target-scope-boundary.md": ["`target_binding`", "`qualification-target-mismatch`", "`release_train`"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Hardware support qualification target-scope contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
