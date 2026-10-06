#!/usr/bin/env python3
"""Guardrail for keeping breakglass accepted case-object visible protection posture exact to the same object revision."""
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

    required = [
        "same accepted object revision/version",
        "ambient case/container/bucket policy",
        "context only",
    ]
    for field in ["extra", "breakglass_receipt_digests"]:
        desc = (includes.get(field) or {}).get("description") or ""
        for needle in required:
            if needle not in desc:
                errors.append(f"spec/incident.bundle.schema.json includes.{field} description missing required token: {needle}")

    ex = load_json("spec/examples/incident.bundle.json")
    extra = ((ex.get("includes") or {}).get("extra") or [])
    if not any("remoteprotectionexactrevision" in item for item in extra):
        errors.append("spec/examples/incident.bundle.json includes.extra missing remote-protection exact-revision accepted case-object proof example")

    doc_checks = {
        "adrs/ADR-0309-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md": [
            "same accepted object revision/version",
            "ambient case/container/bucket policy",
            "remote-locator continuity",
        ],
        "docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md": [
            "same accepted object revision/version",
            "ambient case/container/bucket policy",
            "tools/check_breakglass_adapter_case_object_remote_protection_exactness_boundary.py",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "same accepted object revision/version",
            "ambient case/container/bucket policy",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "same accepted object revision/version",
            "ambient case/container/bucket policy",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "same accepted object revision/version",
            "ambient case/container/bucket policy",
        ],
        "docs/253-bundle-plans-and-deterministic-exports.md": [
            "same accepted object revision/version",
            "ambient case/container/bucket policy",
        ],
        "docs/481-support-bundle-contract-and-timeline-first-handoff.md": [
            "same accepted object revision/version",
            "ambient case/container/bucket policy",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "same accepted object revision/version",
            "ambient case/container/bucket policy",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0309",
            "remote-locator continuity",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_case_object_remote_protection_exactness_boundary.py",
            "same accepted object revision/version",
        ],
        "docs/99-llm-runbook.md": [
            "docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md",
            "tools/check_breakglass_adapter_case_object_remote_protection_exactness_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md",
            "tools/check_breakglass_adapter_case_object_remote_protection_exactness_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "accepted case-object anchors should keep visible remote protection posture exact to the same object revision",
            "docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md",
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
    print("Breakglass accepted case-object visible protection exactness boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
