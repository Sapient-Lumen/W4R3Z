#!/usr/bin/env python3
"""Run the rev0020 UPLOAD-QUEUE-POLICY-01 current-behavior witness against source lanes."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "maintainer_artifacts" / "upload-queue-policy-01" / "test_upload_queue_megabyte_limit_reproducer.py"
DEFAULT_SOURCE_ROOT = ROOT.parent / "sources" / "upstream-current-and-future" / "source-trees"
LANES = ["github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"]


def run_lane(lane: str, source_root: Path) -> int:
    source = source_root / lane
    env = dict(os.environ)
    env["NICOTINE_SOURCE"] = str(source)
    print(f"=== {lane} ===", flush=True)
    return subprocess.call([sys.executable, "-m", "pytest", "-q", str(TEST)], env=env)


def main() -> int:
    source_root = Path(os.environ.get("NICOTINE_SOURCE_ROOT", DEFAULT_SOURCE_ROOT))
    status = 0
    for lane in LANES:
        status |= run_lane(lane, source_root)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
