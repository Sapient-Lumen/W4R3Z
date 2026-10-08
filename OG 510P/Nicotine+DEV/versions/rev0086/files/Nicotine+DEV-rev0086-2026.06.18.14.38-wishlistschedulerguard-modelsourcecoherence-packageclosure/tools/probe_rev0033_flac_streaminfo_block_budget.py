#!/usr/bin/env python3
"""Helper for rerunning the rev0033 FLAC-STREAMINFO-BLOCK-BUDGET-01 witness.

Usage:
  python tools/probe_rev0033_flac_streaminfo_block_budget.py /path/to/source-trees

The source-trees directory should contain:
  github-tag-3.3.10/
  github-branch-3.3.x/
  github-branch-master/
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

LANES = ["github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    source_root = Path(sys.argv[1]).resolve()
    test_dir = Path(__file__).resolve().parents[1] / "maintainer_artifacts" / "flac-streaminfo-block-budget-01"
    test_path = test_dir / "test_flac_streaminfo_block_budget_reproducer.py"

    if not test_path.is_file():
        print(f"missing test file: {test_path}", file=sys.stderr)
        return 2

    failed = False
    for lane in LANES:
        lane_root = source_root / lane
        if not lane_root.is_dir():
            print(f"missing lane: {lane_root}", file=sys.stderr)
            failed = True
            continue

        print(f"=== {lane} ===", flush=True)
        env = os.environ.copy()
        env["NICOTINE_SOURCE"] = str(lane_root)
        env["PYTHONPATH"] = str(lane_root)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(test_path)],
            cwd=str(test_dir),
            env=env,
            text=True,
            check=False,
        )
        failed = failed or result.returncode != 0

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
