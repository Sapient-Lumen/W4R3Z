#!/usr/bin/env python3
"""scripts/clean_local_artifacts.py

Remove local cache/build artifacts that should never be committed or packaged.

Why:
- release gate fails closed if cache artifacts are present
- deterministic release zips should not contain local build state

This script is intentionally stdlib-only.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Directory names to remove anywhere in the tree.
TRASH_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
}

# Root-relative directory prefixes that are always non-normative outputs.
TRASH_DIR_PREFIXES = {
    "evidence/cache",
    "dist",
}

TRASH_FILE_SUFFIXES = {
    ".pyc",
}


def _is_under_prefix(rel: str) -> bool:
    rel = rel.strip("/")
    for pref in TRASH_DIR_PREFIXES:
        if rel == pref or rel.startswith(pref + "/"):
            return True
    return False


def clean(dry_run: bool) -> int:
    removed = 0

    # Remove prefix directories first (if present).
    for pref in sorted(TRASH_DIR_PREFIXES):
        p = ROOT / pref
        if p.exists():
            if dry_run:
                print("DRY-RUN rmtree", p)
            else:
                shutil.rmtree(p)
            removed += 1

    # Remove named cache dirs anywhere.
    for p in sorted(ROOT.rglob("*")):
        if not p.exists():
            continue
        try:
            rel = p.relative_to(ROOT).as_posix()
        except Exception:
            continue

        if p.is_dir():
            if _is_under_prefix(rel):
                # already handled above
                continue
            if p.name in TRASH_DIR_NAMES:
                if dry_run:
                    print("DRY-RUN rmtree", p)
                else:
                    shutil.rmtree(p)
                removed += 1

        elif p.is_file():
            for suf in TRASH_FILE_SUFFIXES:
                if p.name.endswith(suf):
                    if dry_run:
                        print("DRY-RUN unlink", p)
                    else:
                        p.unlink(missing_ok=True)
                    removed += 1
                    break

    return removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print what would be removed")
    args = ap.parse_args()

    n = clean(dry_run=args.dry_run)
    print(f"Removed {n} local artifact path(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
