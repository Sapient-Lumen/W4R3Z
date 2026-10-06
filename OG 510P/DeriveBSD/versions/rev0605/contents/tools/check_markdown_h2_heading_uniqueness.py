#!/usr/bin/env python3
"""Ensure Markdown H2 headings are unique within each document.

Why:
  H2 headings are the main document-local navigation anchors. Reusing the same
  H2 text inside one file creates duplicate generated anchors and makes links,
  skim review, and appendices ambiguous. Lower-level headings may repeat under
  different H2 parents, but top-level sections below the file title must remain
  unique.

Rule:
  - Every tracked Markdown file may use a given visible H2 heading text at most
    once.
  - H2-like text inside fenced code blocks is ignored.

Usage:
  python3 tools/check_markdown_h2_heading_uniqueness.py

Exit codes:
  0: ok
  1: a Markdown file has duplicate H2 heading text
"""

from __future__ import annotations

from collections import defaultdict
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


def _h2_headings(path: Path) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    in_fence = False
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## ") and not line.startswith("### "):
            headings.append((line_no, line[3:].strip()))
    return headings


def main() -> int:
    errors: list[str] = []

    for path in _markdown_files():
        seen: dict[str, list[int]] = defaultdict(list)
        for line_no, heading in _h2_headings(path):
            seen[heading].append(line_no)
        for heading, lines in sorted(seen.items()):
            if len(lines) > 1:
                rel = path.relative_to(ROOT)
                joined = ", ".join(str(line) for line in lines)
                errors.append(f"{rel}: duplicate H2 {heading!r} on lines {joined}")

    if errors:
        print("Markdown H2 heading uniqueness check FAILED.")
        print("Each Markdown file must keep H2 section anchors unique.")
        for error in errors:
            print("-", error)
        return 1

    print(f"Markdown H2 heading uniqueness check OK, {len(_markdown_files())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
