#!/usr/bin/env python3
"""Ensure the human archive index keeps orientation before release history.

Why:
  ``docs/00-index.md`` is the front door for human and LLM review. Release
  sections need to be sorted newest-first, but that ordering must not bury the
  document's orientation prose and reading paths below the release ledger. An
  index that starts directly with release notes is technically complete but hard
  to use as a navigation map.

Rule:
  - ``docs/00-index.md`` must start with the expected H1.
  - The core orientation sentence and ``## Reading paths`` section must appear
    before the first ``## New in ...`` release heading.
  - The orientation sentence should appear exactly once.

Usage:
  python3 tools/check_index_front_matter_order.py

Exit codes:
  0: ok
  1: the index front matter is missing, duplicated, or buried under releases
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "00-index.md"
TITLE = "# DeriveBSD archive index"
INTRO = "This is a living design archive for **DeriveBSD**"
READING_PATHS = "## Reading paths"
RELEASE_RE = re.compile(r"^##\s+New in\s+\S+", re.MULTILINE)


def _line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def main() -> int:
    errors: list[str] = []

    if not INDEX.exists():
        print("Index front-matter order check FAILED.")
        print("- missing docs/00-index.md")
        return 1

    text = INDEX.read_text(encoding="utf-8", errors="replace")
    if not text.startswith(TITLE + "\n"):
        first = text.splitlines()[0] if text.splitlines() else ""
        errors.append(f"docs/00-index.md must start with {TITLE!r}; found {first!r}")

    release_match = RELEASE_RE.search(text)
    if not release_match:
        errors.append("docs/00-index.md has no '## New in ...' release heading")
        first_release = len(text)
    else:
        first_release = release_match.start()

    intro_positions = [m.start() for m in re.finditer(re.escape(INTRO), text)]
    if len(intro_positions) != 1:
        where = ", ".join(str(_line_no(text, p)) for p in intro_positions) or "none"
        errors.append(f"expected exactly one archive orientation sentence; found {len(intro_positions)} ({where})")
    elif intro_positions[0] > first_release:
        errors.append(
            "archive orientation sentence is buried after the first release heading "
            f"(line {_line_no(text, intro_positions[0])} after line {_line_no(text, first_release)})"
        )

    reading_pos = text.find(READING_PATHS)
    if reading_pos == -1:
        errors.append("missing '## Reading paths' section")
    elif reading_pos > first_release:
        errors.append(
            "'## Reading paths' is buried after the first release heading "
            f"(line {_line_no(text, reading_pos)} after line {_line_no(text, first_release)})"
        )

    if errors:
        print("Index front-matter order check FAILED.")
        print("Keep docs/00-index.md as a front-door map: title, orientation, reading paths, then release history.")
        for error in errors:
            print("-", error)
        return 1

    print("Index front-matter order check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
