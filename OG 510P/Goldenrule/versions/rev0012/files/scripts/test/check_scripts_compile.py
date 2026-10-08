#!/usr/bin/env python3
from __future__ import annotations

import compileall
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    ok_scripts = compileall.compile_dir(str(root / "scripts"), quiet=1, force=False)
    ok_grlab = compileall.compile_dir(str(root / "grlab"), quiet=1, force=False)

    if not ok_scripts or not ok_grlab:
        print("scripts-compile: compileall failure", file=sys.stderr)
        return 1

    print("scripts-compile: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
