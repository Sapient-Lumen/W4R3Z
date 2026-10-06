#!/usr/bin/env python3
"""Guardrail for operator-access recording/detail/export posture staying profile-shaped."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md": [
        "new product-profile key",
        "output-only TTY recording is the default stronger content-evidence lane",
        "session-metadata-plus-output-only-tty-recording-required-for-brokered-remote-operator-sessions",
        "session-metadata-always-output-only-tty-only-for-remote-or-breakglass-operator-sessions-no-ambient-local-admin-recording",
        "session-metadata-always-output-only-tty-preferred-for-brokered-remote-admin-lanes-local-admin-recording-explicit",
        "session-metadata-plus-output-only-tty-recording-required-in-approved-maintenance-operator-lanes-only",
    ],
    "adrs/ADR-0207-operator-access-recording-detail-and-export-posture-by-profile.md": [
        "operator.session",
        "output-only TTY recording",
        "TTY input capture is a higher-risk recording scope",
        "new `product.profiles.defaults` key",
    ],
    "docs/467-operator-access-posture-by-profile.md": [
        "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md",
        "recording/detail/export defaults now live in `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md`",
    ],
    "docs/311-operator-access-leases-and-ssh-certs.md": [
        "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md",
        "The product-shaped recording/detail/export defaults for that lane now live in `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md`",
    ],
    "docs/292-terminal-session-recording-as-evidence.md": [
        "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0207",
        "product-shaped recording/detail/export default is now fixed",
    ],
    "docs/98-archive-hygiene.md": [
        "check_operator_access_recording_posture.py",
        "keeps A/D on session-metadata + output-only TTY trails for brokered remote or approved maintenance operator lanes",
    ],
    "docs/99-llm-runbook.md": [
        "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md",
        "check_operator_access_recording_posture.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "operator-access recording/detail/export posture profile-shaped",
        "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md",
    ],
    "README.md": [
        "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md",
        "ordinary local admin metadata-first",
    ],
    "docs/00-index.md": [
        "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md",
        "2026-03-21r347",
    ],
    "CHANGELOG.md": [
        "2026-03-21r347",
        "docs/617-operator-access-recording-detail-and-export-posture-by-profile.md",
        "tools/check_operator_access_recording_posture.py",
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
    print("Operator-access recording posture check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
