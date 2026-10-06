#!/usr/bin/env python3
"""Guardrail for keeping richer breakglass adapter/runtime detail off the first-class bundle contract."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    schema = load_json("spec/incident.bundle.schema.json")
    includes = ((schema.get("properties") or {}).get("includes") or {}).get("properties") or {}

    extra_desc = (includes.get("extra") or {}).get("description") or ""
    for needle in [
        "Supplementary evidence only.",
        "not a substitute for typed contract fields such as `breakglass_receipt_digests`",
        "external case attachments",
    ]:
        if needle not in extra_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.extra description missing required token: {needle}")

    breakglass_desc = (includes.get("breakglass_receipt_digests") or {}).get("description") or ""
    for needle in [
        "first-class official handoff proof",
        "adapter/runtime detail stays supplementary side evidence",
        "dedicated typed family exists",
    ]:
        if needle not in breakglass_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.breakglass_receipt_digests description missing required token: {needle}")

    forbidden_bundle_fields = {
        "breakglass_adapter_detail_digests",
        "breakglass_adapter_runtime_digests",
        "breakglass_console_runtime_digests",
        "breakglass_virtual_media_digests",
        "breakglass_side_evidence_digests",
    }
    overlap = forbidden_bundle_fields & set(includes)
    if overlap:
        errors.append(f"spec/incident.bundle.schema.json must not mint first-class breakglass adapter bundle fields yet: {sorted(overlap)}")

    doc_checks = {
        "adrs/ADR-0301-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md": [
            "authority-first",
            "supplementary side evidence",
            "includes.extra[]",
            "dedicated typed family",
        ],
        "docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md": [
            "authority-first",
            "supplementary side evidence",
            "includes.extra[]",
            "tools/check_breakglass_adapter_bundle_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "breakglass authority proof stays authority-first on `includes.breakglass_receipt_digests`",
            "supplementary `includes.extra[]` evidence digests",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "official support handoff stays authority-first",
            "supplementary `incident.bundle.includes.extra[]` evidence",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "authority-first on `breakglass_receipt_digests`",
            "supplementary `includes.extra[]` evidence or external case attachments",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "first-class proof stays `breakglass_receipt_digests`",
            "`extra[]` is supplementary rather than a replacement",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "authority-first",
            "not a promise that richer breakglass adapter/runtime material already has first-class bundle fields",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "official support handoff stays authority-first on `breakglass_receipt_digests`",
            "supplementary side evidence or external case attachments",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0301",
            "authority-first on `breakglass_receipt_digests`",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_bundle_boundary.py",
            "first-class bundle contract",
        ],
        "docs/99-llm-runbook.md": [
            "docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md",
            "tools/check_breakglass_adapter_bundle_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md",
            "tools/check_breakglass_adapter_bundle_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "authority-first",
            "docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md",
        ],
        "docs/32-curated-references.md": [
            "OpenBMC virtual-media design",
            "Dell iDRAC virtual media (with or without virtual console)",
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
    print("Breakglass adapter bundle boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
