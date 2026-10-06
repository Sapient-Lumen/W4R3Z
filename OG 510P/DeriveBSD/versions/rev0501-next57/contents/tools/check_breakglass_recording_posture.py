#!/usr/bin/env python3
"""Guardrail for breakglass recording/detail/export posture staying profile-shaped."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
        "new product-profile key",
        "output-only TTY/console recording is the default stronger emergency-session evidence lane",
        "session-metadata-plus-output-only-tty-recording-required-for-breakglass-shell-or-console-sessions",
        "session-metadata-always-output-only-terminal-recording-required-for-breakglass-shell-or-recovery-console-no-ambient-screen-recording",
        "session-metadata-always-output-only-tty-preferred-for-derive-managed-breakglass-explicit-local-recovery-adapter",
        "session-metadata-plus-output-only-tty-recording-required-in-approved-offline-breakglass-maintenance-lanes-only",
    ],
    "adrs/ADR-0208-breakglass-recording-detail-and-export-posture-by-profile.md": [
        "breakglass.receipt",
        "output-only TTY/console recording",
        "TTY input capture is a higher-risk recording scope",
        "new `product.profiles.defaults` key",
    ],
    "docs/236-breakglass-and-recovery-mode.md": [
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
        "The product-shaped recording/detail/export defaults for emergency sessions now live in `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`",
    ],
    "docs/250-breakglass-and-recovery-workflows.md": [
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
        "The product-shaped recording/detail/export defaults for those emergency sessions now live in `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`",
    ],
    "docs/473-installation-and-recovery-posture-by-profile.md": [
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
    ],
    "docs/292-terminal-session-recording-as-evidence.md": [
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0208",
        "product-shaped recording/detail/export default is now fixed",
    ],
    "docs/98-archive-hygiene.md": [
        "check_breakglass_recording_posture.py",
        "keeps A/D on session-metadata + output-only TTY trails for breakglass shell/console sessions",
    ],
    "docs/99-llm-runbook.md": [
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
        "check_breakglass_recording_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "breakglass recording/detail/export posture profile-shaped",
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
    ],
    "README.md": [
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
        "breakglass stronger than ordinary local admin",
    ],
    "docs/00-index.md": [
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
        "2026-03-21r348",
    ],
    "CHANGELOG.md": [
        "2026-03-21r348",
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md",
        "tools/check_breakglass_recording_posture.py",
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
    print("Breakglass recording posture check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
