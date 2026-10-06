#!/usr/bin/env python3
"""Guardrail for restore staying official, quarantine-first, and promotion-shaped."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md": [
        "restore.plan",
        "restore.receipt",
        "quarantine-first",
        "replacement-target",
        "new product-profile key",
        "prior_restore_receipt_digest",
        "authority_receipt_digest",
    ],
    "adrs/ADR-0210-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md": [
        "restore.plan",
        "restore.receipt",
        "replacement_precondition",
        "No new `product.profiles.defaults` key is introduced.",
    ],
    "docs/316-backups-and-restores-as-derived-operations.md": [
        "This archive now standardizes `restore.plan`/`restore.receipt`",
        "replacement_precondition",
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
    ],
    "docs/317-restore-drills-and-continuous-recovery-testing.md": [
        "supplement, rather than replace, the official restore apply lane",
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
    ],
    "docs/464-backup-and-restore-posture-by-profile.md": [
        "ordinary restore should stay quarantine-first through `restore.plan` → `restore.receipt`",
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
    ],
    "docs/309-installation-and-recovery-as-derived-operations.md": [
        "restore.plan` → `restore.receipt`",
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
    ],
    "docs/229-evidence-spine-overview.md": [
        "Restore apply evidence: `restore.plan`, `restore.receipt`",
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0210",
        "quarantine-first",
    ],
    "docs/98-archive-hygiene.md": [
        "check_restore_boundary.py",
        "keep restore official and quarantine-first",
    ],
    "docs/99-llm-runbook.md": [
        "restore official and quarantine-first",
        "check_restore_boundary.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Restore is only trustworthy when rehearsal and live replacement are different typed steps",
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
    ],
    "README.md": [
        "restore plans + receipts (quarantine-first recovery lane)",
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
    ],
    "docs/00-index.md": [
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
        "2026-03-21r350",
    ],
    "CHANGELOG.md": [
        "2026-03-21r350",
        "tools/check_restore_boundary.py",
        "docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md",
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Restore boundary check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
