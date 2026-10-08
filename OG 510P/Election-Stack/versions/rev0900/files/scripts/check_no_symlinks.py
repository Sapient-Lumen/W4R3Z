#!/usr/bin/env python3
"""scripts/check_no_symlinks.py

Fail the release gate if any symlinks exist in the archive.

Rationale:
Evidence packets and supporting artifacts are intended to be self-contained and
portable. Symlinks can:
  - cause accidental non-portability in published bundles, and
  - enable "escape" reads if a verifier follows a link outside the packet root.

This check is deliberately simple and conservative: no symlinks anywhere.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    found: list[str] = []

    for root, dirs, files in os.walk(ROOT, topdown=True, followlinks=False):
        r = Path(root)
        # Check dir entries (without descending into symlink dirs).
        for d in list(dirs):
            p = r / d
            if p.is_symlink():
                found.append(str(p.relative_to(ROOT)))
        for f in files:
            p = r / f
            if p.is_symlink():
                found.append(str(p.relative_to(ROOT)))

    if found:
        print("FAIL: symlinks are not allowed in the archive")
        for s in sorted(found):
            print(" -", s)
        return 2

    print("PASS: no symlinks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
