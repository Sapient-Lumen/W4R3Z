#!/usr/bin/env python3
"""Check Markdown inline code spans for line-local backtick balance.

Why:
  Historical release-note and guardrail prose can become hard to read when a
  ``Last updated:`` stamp or short code span loses its closing backtick. The
  ordinary path/link checks still pass, but reviewers see malformed Markdown and
  truncated release guidance.

Rule:
  - Scan repository Markdown files in the root, ``docs/``, ``adrs/``, and
    ``rfcs/``.
  - Ignore fenced code blocks opened with ````` or ``~~~``.
  - Outside fences, require each physical line to contain an even number of
    backtick characters. Keep code spans line-local; do not split inline code
    across lines in prose.
  - Reject unclosed fenced code blocks.

Usage:
  python3 tools/check_markdown_inline_code_balance.py

Exit codes:
  0: ok
  1: unbalanced inline code span or fence
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT, ROOT / "docs", ROOT / "adrs", ROOT / "rfcs"]


def _markdown_paths() -> list[Path]:
    paths: set[Path] = set()
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        if base == ROOT:
            paths.update(p for p in base.glob("*.md") if p.is_file())
        else:
            paths.update(p for p in base.rglob("*.md") if p.is_file())
    return sorted(paths, key=lambda p: str(p.relative_to(ROOT)))


def _check_file(path: Path) -> list[str]:
    errors: list[str] = []
    in_fence = False
    fence_marker = ""

    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue

        if in_fence:
            continue

        if line.count("`") % 2:
            rel = path.relative_to(ROOT)
            errors.append(f"{rel}:{line_no}: unbalanced inline backticks")

    if in_fence:
        rel = path.relative_to(ROOT)
        errors.append(f"{rel}: unclosed fenced code block opened with {fence_marker!r}")

    return errors


def main() -> int:
    errors: list[str] = []
    for path in _markdown_paths():
        errors.extend(_check_file(path))

    if errors:
        print("Markdown inline-code balance check FAILED.")
        print("Keep inline code spans line-local and balanced outside fenced code blocks.")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Markdown inline-code balance check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
