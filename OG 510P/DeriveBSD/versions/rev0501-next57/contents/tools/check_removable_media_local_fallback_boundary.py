#!/usr/bin/env python3
"""Guardrail for the removable-media local fallback boundary.

Keeps the archive from drifting from a narrow storage-only fallback into a vague
"USB with prompts" story.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    ROOT / 'docs' / '458-removable-media-and-usb-posture-by-profile.md': [
        'storage-only local fallback',
        'session-scoped',
        'no raw HID',
        'no generic USB passthrough',
    ],
    ROOT / 'docs' / '279-usb-quarantine-and-removable-media-workflow.md': [
        'storage-only',
        'session-scoped',
        'read-only-first',
        'no raw HID',
    ],
    ROOT / 'docs' / '723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md': [
        'storage-only',
        'session-scoped',
        'read-only-first',
        'device.attach.grant',
        'devfs.view.plan',
        'content.import.receipt',
    ],
    ROOT / 'docs' / '266-open-questions-and-risk-register.md': [
        'ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md',
    ],
}


def main() -> int:
    failures: list[str] = []
    for path, needles in REQUIRED.items():
        text = path.read_text()
        for needle in needles:
            if needle not in text:
                failures.append(f"{path.relative_to(ROOT)} missing required text: {needle}")
    if failures:
        print('Removable-media local fallback boundary check FAILED')
        for failure in failures:
            print(f'- {failure}')
        return 1
    print('Removable-media local fallback boundary OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
