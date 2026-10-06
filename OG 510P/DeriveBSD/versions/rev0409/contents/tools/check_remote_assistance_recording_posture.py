#!/usr/bin/env python3
"""Guardrail for remote-assistance recording/detail/export posture staying profile-shaped."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md": [
        "new product-profile key",
        "output-only TTY recording is the default stronger content-evidence lane",
        "session-metadata-plus-output-only-tty-recording-required-for-brokered-admin-sessions",
        "session-metadata-always-terminal-output-only-when-terminal-assist-is-used-no-ambient-screen-recording",
        "session-metadata-always-output-only-tty-preferred-for-brokered-operator-lanes-richer-capture-explicit",
        "session-metadata-plus-output-only-tty-recording-required-in-approved-maintenance-lanes-only",
    ],
    "adrs/ADR-0206-remote-assistance-recording-detail-and-export-posture-by-profile.md": [
        "support.session",
        "output-only TTY/console recording",
        "TTY input capture is a higher-risk recording scope",
        "new `product.profiles.defaults` key",
    ],
    "docs/461-remote-assistance-posture-by-profile.md": [
        "docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md",
        "recording/detail/export defaults now live in `docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md`",
    ],
    "docs/291-remote-assistance-sessions-as-evidence.md": [
        "recording/detail/export defaults for that lane now live in `docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md`",
        "docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md",
    ],
    "docs/292-terminal-session-recording-as-evidence.md": [
        "The product-shaped defaults for when this stronger lane is routine now live in `docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md`",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0206",
        "remote assistance recording/detail/export posture stays profile-shaped",
    ],
    "docs/98-archive-hygiene.md": [
        "check_remote_assistance_recording_posture.py",
        "keeps A/D on session-metadata + output-only TTY trails",
    ],
    "docs/99-llm-runbook.md": [
        "docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md",
        "check_remote_assistance_recording_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Remote assistance evidence should be profile-shaped, not one-size-fits-all",
        "docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md",
    ],
    "README.md": [
        "docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md",
        "session metadata plus output-only TTY trails",
    ],
    "docs/00-index.md": [
        "docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md",
        "2026-03-21r346",
    ],
    "CHANGELOG.md": [
        "2026-03-21r346",
        "docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md",
        "tools/check_remote_assistance_recording_posture.py",
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
    print("Remote-assistance recording posture check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
