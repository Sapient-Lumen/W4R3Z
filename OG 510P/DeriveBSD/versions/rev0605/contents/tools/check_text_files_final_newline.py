#!/usr/bin/env python3
"""Ensure tracked text artifacts end with a final newline.

Why:
  Missing final newlines are small but persistent archive-quality drift: shell
  output, concatenated validation excerpts, and generated diffs can visually merge
  the last line of one file with the next prompt or heading. That already obscured
  adjacent release-stamp output while reviewing the package.

Rule:
  - Scan repo text artifacts that are expected to be line-oriented.
  - Empty files are allowed.
  - Non-empty text files must end in exactly at least one ``\n`` byte.

Usage:
  python3 tools/check_text_files_final_newline.py

Exit codes:
  0: ok
  1: one or more text files are missing a final newline
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".json",
    ".log",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_DIRS = {
    ".git",
    "__pycache__",
}


def _is_text_artifact(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.suffix in TEXT_SUFFIXES:
        return True
    # JSON Schema files already have .json suffix, but keep this explicit for readability.
    if path.name.endswith(".schema.json"):
        return True
    return False


def main() -> int:
    errors: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not _is_text_artifact(path):
            continue
        rel = path.relative_to(ROOT)
        data = path.read_bytes()
        if data and not data.endswith(b"\n"):
            errors.append(str(rel))

    if errors:
        print("Text final-newline check FAILED.")
        print("Non-empty line-oriented archive files must end with a final newline:")
        for rel in errors:
            print(f"- {rel}")
        return 1

    print("Text final-newline check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
