#!/usr/bin/env python3
"""Fail if build/runtime cache artifacts are present in the archive.

Rationale:
- We already exclude common cache dirs from MANIFEST.sha256, but shipping them
  bloats the zip and can confuse reviewers.
- This check is a packaging hygiene gate.

Rules:
- Reject any of these directory names anywhere in the tree:
    __pycache__, .pytest_cache, .mypy_cache, .ruff_cache, .venv, node_modules, dist
- Reject any *.pyc / *.pyo and common OS junk files.
- evidence/cache/ MAY exist but MUST be empty.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BAD_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
    "dist",
}

BAD_SUFFIXES = {".pyc", ".pyo"}
BAD_FILENAMES = {".DS_Store"}


def main() -> int:
    bad: list[str] = []

    # Hard fail on known cache dirs.
    for d in ROOT.rglob("*"):
        if d.is_dir() and d.name in BAD_DIRS:
            bad.append(d.relative_to(ROOT).as_posix() + "/")

    # Hard fail on compiled/python cache bytes.
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix in BAD_SUFFIXES or p.name in BAD_FILENAMES:
            bad.append(p.relative_to(ROOT).as_posix())

    # evidence/cache is allowed, but MUST be empty.
    cache_dir = ROOT / "evidence" / "cache"
    if cache_dir.exists():
        cache_files = [x for x in cache_dir.rglob("*") if x.is_file()]
        if cache_files:
            bad.append("evidence/cache/ (must be empty; found files)")

    if bad:
        print("FAIL: cache/build artifacts present")
        # Keep output compact.
        for s in sorted(bad)[:30]:
            print("  ", s)
        if len(bad) > 30:
            print(f"  ... ({len(bad) - 30} more)")
        print("hint: delete these files/dirs before packaging")
        return 2

    print("PASS: no cache/build artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
