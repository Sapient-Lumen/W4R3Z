#!/usr/bin/env python3
from __future__ import annotations

import runpy
import sys
from pathlib import Path

from build_steps import BUILD_STEPS

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def main() -> None:
    for script in BUILD_STEPS:
        print(f"== {script}")
        runpy.run_path(str(TOOLS / script), run_name="__main__")


if __name__ == "__main__":
    main()
