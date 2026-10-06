#!/usr/bin/env python3
"""Guardrail for destructive-reprovision evidence/detail/export posture staying profile-shaped."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md": [
        "new product-profile key",
        "trusted-UI or attended/presence evidence recorded through `reset.receipt.observed_evidence[]` is the normal stronger human-intent proof",
        "output-only TTY/console recording is the default stronger execution-evidence lane only when reset actually uses a brokered terminal, maintenance console, or recovery shell lane",
        "reset-receipt-plus-disk-layout-receipt-always-output-only-tty-for-remote-maintenance-reset",
        "reset-receipt-plus-observed-trusted-ui-evidence-always-output-only-terminal-only-if-recovery-shell-is-used-no-ambient-screen-recording",
        "reset-receipt-always-trusted-ui-or-admin-evidence-normal-output-only-tty-preferred-for-derive-managed-remote-reset",
        "reset-receipt-plus-disk-layout-receipt-plus-physical-or-station-evidence-always-output-only-tty-for-approved-maintenance-reset",
    ],
    "adrs/ADR-0209-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md": [
        "reset.receipt",
        "disk.layout.receipt",
        "trusted-UI/presence evidence recorded in `reset.receipt.observed_evidence[]` is the normal stronger human-intent proof",
        "Ambient screen/video capture is never the routine baseline",
        "new `product.profiles.defaults` key",
    ],
    "docs/483-destructive-reprovisioning-and-reset-authority.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
        "The product-shaped evidence/detail/export defaults for that destructive lane now live in `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md`",
    ],
    "docs/310-disk-layout-plans-and-receipts.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/473-installation-and-recovery-posture-by-profile.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/478-evidence-collection-posture-by-profile.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/474-high-risk-approval-posture-by-profile.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/250-breakglass-and-recovery-workflows.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/229-evidence-spine-overview.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0209",
        "product-shaped evidence/detail/export default is now fixed",
    ],
    "docs/98-archive-hygiene.md": [
        "check_destructive_reprovision_evidence_posture.py",
        "keeps reset proof profile-shaped so A/D retain typed reset/storage truth plus output-only console trails in maintenance lanes while B stays trusted-UI-first and no profile inherits ambient panic recording",
    ],
    "docs/99-llm-runbook.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
        "check_destructive_reprovision_evidence_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "destructive reprovision evidence/detail/export posture profile-shaped",
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
    ],
    "README.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
        "trusted-UI-first reset proof",
    ],
    "docs/00-index.md": [
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
        "2026-03-21r349",
    ],
    "CHANGELOG.md": [
        "2026-03-21r349",
        "docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md",
        "tools/check_destructive_reprovision_evidence_posture.py",
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
    print("Destructive-reprovision evidence posture check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
