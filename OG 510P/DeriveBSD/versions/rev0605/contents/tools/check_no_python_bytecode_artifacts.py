#!/usr/bin/env python3
"""Reject transient Python bytecode/cache artifacts in linked revision zips.

The cube executes many local Python guardrails while preparing a cut.  CPython's
__pycache__ directories are useful transiently but should never become part of a
linked revision: they are host/interpreter-specific, stale quickly, and obscure
whether the source tree itself is the durable artifact.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DIR_NAMES = {"__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
HYGIENE = ROOT / "tools" / "hygiene.py"


def is_ignored(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    # Keep this guard focused on checked-in cube content.  Hidden VCS metadata is
    # not part of linked revision zips here, and skipping it avoids noisy local
    # developer environments if the cube is later unpacked into a repository.
    return rel.startswith(".git/") or rel == ".git"


def main() -> int:
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if is_ignored(path):
            continue
        if path.is_dir() and path.name in FORBIDDEN_DIR_NAMES:
            offenders.append(path.relative_to(ROOT).as_posix() + "/")
            # Also list bytecode children only if the cache directory itself is
            # somehow missed by a future edit; avoid duplicating a long cache tree.
            continue
        if path.is_file() and path.suffix in FORBIDDEN_SUFFIXES:
            offenders.append(path.relative_to(ROOT).as_posix())
    hygiene = HYGIENE.read_text(encoding="utf-8", errors="replace") if HYGIENE.exists() else ""
    for token in ["PYTHONDONTWRITEBYTECODE", "child_env()", "child_cmd", "-B"]:
        if token not in hygiene:
            offenders.append(f"tools/hygiene.py missing {token}")

    if offenders:
        print("Python bytecode artifact check FAILED.")
        print("Remove transient __pycache__ directories and .pyc/.pyo files before packaging.")
        for offender in sorted(offenders)[:100]:
            print(f"- {offender}")
        if len(offenders) > 100:
            print(f"... {len(offenders) - 100} more")
        return 1
    print("Python bytecode artifact check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
