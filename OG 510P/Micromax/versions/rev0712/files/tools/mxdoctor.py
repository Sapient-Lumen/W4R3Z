#!/usr/bin/env python3
"""mxdoctor: a single command that checks the repo is runnable.

This is aimed at future LLMs (and humans) picking up the archive.
It only depends on stdlib + pytest (already in the container).
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(ROOT))


def main() -> int:
    print("micromax doctor")
    print("python:", sys.version.replace("\n", " "))
    print("platform:", platform.platform())
    print("cwd:", os.getcwd())
    print()

    rc = 0
    rc |= run([sys.executable, "tools/mxlint.py"])
    rc |= run([sys.executable, "-m", "pytest", "-q"])

    # Archive hygiene checks (best-effort).
    transient = []
    for name in (".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"):
        if any((ROOT / p).exists() for p in (name, "src/" + name)):
            transient.append(name)
    if transient:
        print("warning: transient caches present:", ", ".join(transient))
        print("         run: make pack   (to build a clean zip archive)")

    # Optional tools
    for opt in ("ruff", "mypy"):
        try:
            subprocess.check_output([opt, "--version"], stderr=subprocess.STDOUT)
            print(f"found: {opt}")
        except Exception:
            print(f"missing: {opt} (optional)")

    return int(bool(rc))


if __name__ == "__main__":
    raise SystemExit(main())
