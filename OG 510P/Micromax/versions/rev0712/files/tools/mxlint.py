#!/usr/bin/env python3
"""Tiny, dependency-free repo checks.

This is NOT a full linter. It's a pragmatic set of checks that work offline:
- python syntax compilation for src/ + tests/
- trailing whitespace / tabs
- missing final newline

If `ruff` is available, you probably want to use it instead.
"""

from __future__ import annotations

import compileall
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTS = {".py", ".md", ".toml", ".sh", ".txt", ".mf"}


def check_text_files() -> int:
    bad = 0
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith(".") and p.parent == ROOT:
            continue
        if p.suffix not in TEXT_EXTS and p.name not in {"Makefile", "LICENSE"}:
            continue

        data = p.read_bytes()
        try:
            s = data.decode("utf-8")
        except UnicodeDecodeError:
            continue

        lines = s.splitlines(keepends=True)
        for i, line in enumerate(lines, start=1):
            if p.name != "Makefile" and "\t" in line:
                print(f"TAB: {p}:{i}", file=sys.stderr)
                bad += 1
            if line.rstrip("\n").rstrip("\r").endswith(" "):
                print(f"TRAILING SPACE: {p}:{i}", file=sys.stderr)
                bad += 1

        if data and not data.endswith(b"\n"):
            print(f"NO FINAL NEWLINE: {p}", file=sys.stderr)
            bad += 1
    return bad


def main() -> int:
    # Syntax compile
    ok = compileall.compile_dir(str(ROOT / "src"), quiet=1)
    ok2 = compileall.compile_dir(str(ROOT / "tests"), quiet=1)
    if not (ok and ok2):
        print("Python compile failed", file=sys.stderr)
        return 2

    bad = check_text_files()
    if bad:
        print(f"mxlint: {bad} issue(s)", file=sys.stderr)
        return 1

    print("mxlint: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
