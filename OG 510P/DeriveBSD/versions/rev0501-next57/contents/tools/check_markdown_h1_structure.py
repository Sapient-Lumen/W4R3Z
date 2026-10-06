#!/usr/bin/env python3
"""Ensure Markdown documents have one top-level title at the top.

Why:
  Markdown discovery surfaces are used as stable review maps. A missing top H1
  makes the first release body look like the document title, while buried H1s
  split a single document into multiple apparent roots. Both patterns make
  anchors, skim review, and generated context surfaces ambiguous.

Rule:
  - Every tracked Markdown file in the archive must have exactly one H1 line.
  - That H1 must be the first line of the file.
  - H1-like text inside fenced code blocks is ignored.

Usage:
  python3 tools/check_markdown_h1_structure.py

Exit codes:
  0: ok
  1: a Markdown file has no H1, multiple H1s, or a non-terminal-root H1
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_ROOTS = [ROOT, ROOT / "docs", ROOT / "adrs", ROOT / "rfcs"]
EXCLUDED_PARTS = {".git", "__pycache__"}


def _markdown_files() -> list[Path]:
    files: set[Path] = set()
    for root in MARKDOWN_ROOTS:
        if root == ROOT:
            files.update(root.glob("*.md"))
        elif root.exists():
            files.update(root.rglob("*.md"))
    return sorted(
        p for p in files
        if not any(part in EXCLUDED_PARTS for part in p.relative_to(ROOT).parts)
    )


def _visible_lines(path: Path) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    in_fence = False
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append((line_no, line))
    return lines


def _h1_lines(visible_lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    return [(line_no, line.strip()) for line_no, line in visible_lines if line.startswith("# ")]


def main() -> int:
    errors: list[str] = []

    for path in _markdown_files():
        rel = path.relative_to(ROOT)
        raw_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        visible_lines = _visible_lines(path)
        h1s = _h1_lines(visible_lines)
        if len(h1s) != 1:
            where = ", ".join(f"line {line_no}: {text}" for line_no, text in h1s) or "none"
            errors.append(f"{rel}: expected exactly one H1; found {len(h1s)} ({where})")
            continue
        line_no, text = h1s[0]
        first_line = raw_lines[0] if raw_lines else ""
        if line_no != 1 or not first_line.startswith("# "):
            errors.append(f"{rel}: H1 must be first line; found {text!r} on line {line_no}")

    if errors:
        print("Markdown H1 structure check FAILED.")
        for error in errors:
            print("-", error)
        return 1

    print(f"Markdown H1 structure check OK, {len(_markdown_files())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
