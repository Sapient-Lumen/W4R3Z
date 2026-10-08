#!/usr/bin/env python3
"""Run the ROOM-SERVER-STATE-01 current-behavior pytest witness.

Usage:
    NICOTINE_SOURCE=/path/to/nicotine-plus python tools/probe_rev0026_room_server_state.py

This wrapper intentionally delegates to pytest so the maintainer artifact remains
single-source. It is included for cube continuity with prior probe revisions.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    cube_root = Path(__file__).resolve().parents[1]
    test_file = cube_root / "maintainer_artifacts" / "room-server-state-01" / "test_room_server_state_reproducer.py"
    env = os.environ.copy()
    if "NICOTINE_SOURCE" not in env:
        print("NICOTINE_SOURCE is not set; pass a Nicotine+ source tree path.", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, "-m", "pytest", "-q", str(test_file)], env=env)


if __name__ == "__main__":
    raise SystemExit(main())
