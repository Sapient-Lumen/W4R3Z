#!/usr/bin/env python3
"""Guardrail for firmware inventory/mutation evidence posture staying profile-shaped."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md": [
        "fw.inventory.receipt",
        "fw.inventory.diff",
        "fw.update.receipt",
        "uefi.var.set.receipt",
        "new product-profile key",
        "raw vendor updater logs, raw efivar blobs, raw Secure Boot databases, and raw capsule payload bytes are stronger side evidence rather than routine baseline export",
    ],
    "adrs/ADR-0211-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md": [
        "fw.inventory.receipt",
        "fw.inventory.diff",
        "fw.update.receipt",
        "uefi.var.set.receipt",
        "No new `product.profiles.defaults` key is introduced.",
    ],
    "docs/321-firmware-updates-and-uefi-variables-as-evidence.md": [
        "recording/detail/export defaults for inventory and mutation now live in `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`",
        "Official Microsoft guidance now also treats certificate readiness as a fleet-visible operational state",
    ],
    "docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md": [
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/471-firmware-update-posture-by-profile.md": [
        "firmware evidence/detail/export posture: `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`",
    ],
    "docs/229-evidence-spine-overview.md": [
        "Firmware inventory + mutation evidence: `fw.inventory.receipt`, `fw.inventory.diff`, `fw.update.plan`, `fw.update.receipt`, `uefi.var.set.plan`, `uefi.var.set.receipt`",
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0211",
        "Firmware evidence/detail/export posture",
    ],
    "docs/98-archive-hygiene.md": [
        "check_firmware_evidence_posture.py",
        "keep digest-first inventory normal, mutation receipts authoritative, and raw platform material out of routine baseline export",
    ],
    "docs/99-llm-runbook.md": [
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md",
        "check_firmware_evidence_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Firmware mutation evidence should be profile-shaped, not a raw-blob export free-for-all",
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md",
    ],
    "docs/337-secure-boot-certificate-rotation-and-fleet-trust.md": [
        "windows-hardware/design/device-experiences/oem-secure-boot",
        "windows-autopatch/monitor/secure-boot-status-report",
    ],
    "docs/32-curated-references.md": [
        "windows-hardware/design/device-experiences/oem-secure-boot",
        "windows-autopatch/monitor/secure-boot-status-report",
    ],
    "README.md": [
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md",
        "digest-first inventory and diffs normal with mutation receipts authoritative",
    ],
    "docs/00-index.md": [
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md",
        "2026-03-21r351",
    ],
    "CHANGELOG.md": [
        "2026-03-21r351",
        "tools/check_firmware_evidence_posture.py",
        "docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md",
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
    print("Firmware evidence posture check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
