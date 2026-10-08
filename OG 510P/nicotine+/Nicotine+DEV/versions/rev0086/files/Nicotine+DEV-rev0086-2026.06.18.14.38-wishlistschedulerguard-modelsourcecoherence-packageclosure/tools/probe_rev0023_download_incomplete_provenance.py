#!/usr/bin/env python3
"""Convenience runner for the rev0023 download-incomplete provenance witness."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: probe_rev0023_download_incomplete_provenance.py /path/to/nicotine-source [pytest args...]", file=sys.stderr)
        return 2

    source = Path(sys.argv[1]).resolve()
    test_path = Path(__file__).resolve().parents[1] / "maintainer_artifacts" / "download-incomplete-provenance-01" / "test_download_incomplete_provenance_reproducer.py"
    env = os.environ.copy()
    env["NICOTINE_SOURCE"] = str(source)
    return subprocess.call([sys.executable, "-m", "pytest", "-q", str(test_path), *sys.argv[2:]], env=env)


if __name__ == "__main__":
    raise SystemExit(main())
