#!/usr/bin/env python3
"""Ensure packaged root validation logs do not carry stale failure output.

Why:
  A repaired archive should not ship top-level validation logs that still say an
  older guardrail failed. Those stale logs are high-entropy evidence: they make a
  green source tree look red and waste reviewer time.

Rule:
  - Scan root-level ``*.log`` files only.
  - Reject explicit validation-failure markers: ``ERROR:``, ``FAIL``, ``FAILED``,
    and Python tracebacks.

Usage:
  python3 tools/check_validation_logs_clean.py

Exit codes:
  0: ok
  1: stale/failing validation output found
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BAD_PATTERNS = [
    re.compile(r"^ERROR:", re.MULTILINE),
    re.compile(r"^FAIL\b", re.MULTILINE),
    re.compile(r"\bFAILED\b"),
    re.compile(r"Traceback \(most recent call last\):"),
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    errors: list[str] = []

    for path in sorted(ROOT.glob("*.log")):
        text = _read(path)
        for pattern in BAD_PATTERNS:
            match = pattern.search(text)
            if match:
                line_no = text.count("\n", 0, match.start()) + 1
                rel = path.relative_to(ROOT)
                errors.append(f"{rel}: line {line_no}: stale validation marker {match.group(0)!r}")
                break

    if errors:
        print("Validation log cleanliness check FAILED.")
        print("Root validation logs must not ship stale failure markers after repairs.")
        for error in errors:
            print("-", error)
        return 1

    print("Validation log cleanliness check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
