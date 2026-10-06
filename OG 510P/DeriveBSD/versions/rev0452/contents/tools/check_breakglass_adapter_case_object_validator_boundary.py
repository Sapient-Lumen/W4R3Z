#!/usr/bin/env python3
"""Guardrail for keeping breakglass accepted case-object proof validator-pinned when visible."""
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
        "revision/version/generation/ETag-like validator",
        "validator-pinned",
        "same accepted remote object",
    ]:
        if needle not in extra_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.extra description missing required token: {needle}")

    breakglass_desc = (includes.get("breakglass_receipt_digests") or {}).get("description") or ""
    for needle in [
        "revision/version/generation/ETag-like validator",
        "validator-pinned",
        "object-latest semantics",
    ]:
        if needle not in breakglass_desc:
            errors.append(f"spec/incident.bundle.schema.json includes.breakglass_receipt_digests description missing required token: {needle}")

    ex = load_json("spec/examples/incident.bundle.json")
    extra = ((ex.get("includes") or {}).get("extra") or [])
    if not any("acceptedcaseobjectproofexactobjectvalidatorpinned" in item for item in extra):
        errors.append("spec/examples/incident.bundle.json includes.extra missing validator-pinned accepted case-object proof example")

    doc_checks = {
        "adrs/ADR-0307-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md": [
            "validator-pinned",
            "revision / version / generation / ETag-like validator",
            "exact object plus the visible validator",
        ],
        "docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md": [
            "validator-pinned when visible",
            "latest object wins",
            "tools/check_breakglass_adapter_case_object_validator_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "keep it validator-pinned too when the adapter can see a revision/version/generation/ETag-like validator",
            "docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "validator-pinned too when visible",
            "object-latest portal semantics",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "accepted-case-object lane, keep it validator-pinned too when the adapter can see one",
            "revision/version/generation/ETag-like validator",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "accepted-case-object lane, keep it validator-pinned when visible too",
            "same accepted object revision/version token",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "validator-pinned when visible",
            "same accepted remote object revision/version token",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "validator-pinned too when visible",
            "object-latest portal semantics",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0307",
            "remote-protection / remote-locator continuity",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_case_object_validator_boundary.py",
            "validator-pinned when visible",
        ],
        "docs/99-llm-runbook.md": [
            "docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md",
            "tools/check_breakglass_adapter_case_object_validator_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md",
            "tools/check_breakglass_adapter_case_object_validator_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "accepted case-object anchors should pin visible remote validators",
            "docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md",
        ],
        "docs/32-curated-references.md": [
            "RFC 7232",
            "strong validators change whenever the representation data changes",
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
    print("Breakglass accepted case-object validator continuity boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
