#!/usr/bin/env python3
"""Very small formatter (offline-friendly).

If `ruff format` is available, we use it.
Otherwise we do a safe subset:
- strip trailing whitespace
- ensure final newline
- normalize CRLF -> LF (best-effort)

This keeps the repo tidy even without external tooling.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTS = {".py", ".md", ".toml", ".sh", ".txt", ".mf"}


def run_ruff() -> bool:
    if shutil.which("ruff") is None:
        return False
    try:
        subprocess.check_call(["ruff", "format", str(ROOT)])
        return True
    except Exception:
        return False


def whitespace_format() -> int:
    changed = 0
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in TEXT_EXTS and p.name not in {"Makefile", "LICENSE"}:
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        # normalize newlines
        s2 = s.replace("\r\n", "\n")
        # strip trailing whitespace
        s2 = "\n".join([ln.rstrip() for ln in s2.split("\n")])
        if not s2.endswith("\n"):
            s2 += "\n"
        if s2 != s:
            p.write_text(s2, encoding="utf-8")
            changed += 1
    print(f"mxformat: updated {changed} file(s)")
    return 0


def main() -> int:
    if run_ruff():
        print("mxformat: ruff format ok")
        return 0
    return whitespace_format()


if __name__ == "__main__":
    raise SystemExit(main())
