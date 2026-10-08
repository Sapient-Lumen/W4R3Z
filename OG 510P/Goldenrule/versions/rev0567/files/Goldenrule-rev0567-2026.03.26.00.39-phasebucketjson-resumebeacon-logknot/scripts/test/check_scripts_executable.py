#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    targets = []
    targets.extend(sorted((root / "scripts").rglob("*.sh")))
    targets.extend(sorted((root / "scripts").rglob("*.py")))
    targets.extend(sorted((root / ".githooks").glob("*")))

    bad: list[str] = []
    for p in targets:
        if not p.is_file():
            continue
        mode = p.stat().st_mode
        if not (mode & stat.S_IXUSR):
            bad.append(p.relative_to(root).as_posix())

    if bad:
        for b in bad:
            print(f"scripts-exec: missing +x {b}", file=sys.stderr)
        return 1

    print(f"scripts-exec: ok ({len(targets)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
