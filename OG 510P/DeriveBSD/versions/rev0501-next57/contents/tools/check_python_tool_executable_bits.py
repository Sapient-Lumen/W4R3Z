#!/usr/bin/env python3
"""Ensure Python tool scripts with shebangs are directly executable.

Why:
  The archive's tools are intentionally self-describing command-line entry
  points: each Python helper begins with ``#!/usr/bin/env python3`` and the
  docs often present them as runnable tool surfaces. If the ZIP loses executable
  mode bits, extracted guardrails remain invokable through ``python3`` but direct
  script execution silently breaks, which is packaging drift rather than a
  design choice.

Rule:
  - Scan top-level ``tools/*.py`` files.
  - Any file whose first bytes are ``#!`` must have at least one executable bit.
  - Any executable Python tool must also carry a shebang.

Usage:
  python3 tools/check_python_tool_executable_bits.py

Exit codes:
  0: ok
  1: one or more tool scripts have inconsistent executable metadata
"""

from __future__ import annotations

import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def _has_shebang(path: Path) -> bool:
    return path.read_bytes().startswith(b"#!")


def _is_executable(path: Path) -> bool:
    mode = path.stat().st_mode
    return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def main() -> int:
    errors: list[str] = []

    for path in sorted(TOOLS.glob("*.py")):
        rel = path.relative_to(ROOT)
        has_shebang = _has_shebang(path)
        is_executable = _is_executable(path)
        if has_shebang and not is_executable:
            errors.append(f"{rel}: has a shebang but no executable bit")
        if is_executable and not has_shebang:
            errors.append(f"{rel}: executable Python tool lacks a shebang")

    if errors:
        print("Python tool executable-bit check FAILED.")
        print("Shebang-bearing tools must stay directly executable after extraction.")
        for error in errors:
            print("-", error)
        return 1

    print("Python tool executable-bit check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
