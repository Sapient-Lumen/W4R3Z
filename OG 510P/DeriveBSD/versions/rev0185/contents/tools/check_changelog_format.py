#!/usr/bin/env python3
"""Check CHANGELOG formatting stays compact and diff-friendly.

Rationale:
  The changelog is a primary discovery surface and a stable review artifact.
  Excess blank space creates noisy diffs and erodes the archive's 'amnesia resistor'
  quality.

Rules (conservative):
  - First non-empty line must be '# Changelog'.
  - After that heading, allow at most 2 consecutive blank lines before the first
    '## <version>' entry.
  - No trailing whitespace on any line.

Usage:
  python3 tools/check_changelog_format.py

Exit codes:
  0: ok
  1: violations
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"


def main() -> int:
    if not CHANGELOG.exists():
        print("Missing CHANGELOG.md")
        return 1

    txt = CHANGELOG.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()

    # Trailing whitespace is churn.
    bad_ws = [i + 1 for i, ln in enumerate(lines) if ln != ln.rstrip(" \t")]
    if bad_ws:
        print("CHANGELOG.md has trailing whitespace on lines:")
        for n in bad_ws[:50]:
            print(f"- {n}")
        if len(bad_ws) > 50:
            print(f"(and {len(bad_ws) - 50} more)")
        return 1

    # Find first non-empty line.
    first_nonempty = None
    for i, ln in enumerate(lines):
        if ln.strip():
            first_nonempty = i
            break

    if first_nonempty is None:
        print("CHANGELOG.md is empty")
        return 1

    if lines[first_nonempty].strip() != "# Changelog":
        print("CHANGELOG.md must start with '# Changelog'")
        return 1

    # Count blank lines after heading until first version header.
    j = first_nonempty + 1
    blanks = 0
    while j < len(lines) and not lines[j].strip():
        blanks += 1
        j += 1

    if blanks > 2:
        print(
            "CHANGELOG.md has too many blank lines after '# Changelog' "
            f"({blanks}; max 2)."
        )
        return 1

    if j >= len(lines) or not lines[j].startswith("## "):
        print("CHANGELOG.md must have a '## <version>' entry immediately after the heading")
        return 1

    print("Changelog format: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
