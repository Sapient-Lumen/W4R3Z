#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rerun the rev0036 U-123 production-draft packet against extracted source lanes.

Usage:
  python tools/probe_rev0036_u123_packet.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z

The helper runs:
  1. current-behavior witness, expected OK on current lanes;
  2. fixed-behavior regression, expected non-zero before a fix;
  3. identity-guard simulation, expected OK as a narrow proof-of-target.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")


def run(cmd: list[str], env: dict[str, str], cwd: Path) -> int:
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True)
    print("exit=", proc.returncode)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_bundle", type=Path)
    args = parser.parse_args()

    here = Path(__file__).resolve().parents[1]
    current = here / "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py"
    fixed = here / "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_fixed_regression.py"
    sim = here / "tools/run_u123_identity_guard_sim.py"
    source_trees = args.source_bundle / "source-trees"

    status = 0
    for lane in LANES:
        src = source_trees / lane
        if not src.exists():
            print(f"missing source lane: {src}", file=sys.stderr)
            status = 2
            continue
        env = os.environ.copy()
        env["PYTHONPATH"] = str(src)
        print(f"\n### current-behavior witness: {lane}")
        status |= run([sys.executable, str(current)], env, Path('/tmp'))

        print(f"\n### fixed-behavior regression before fix: {lane}")
        fixed_status = run([sys.executable, str(fixed)], env, Path('/tmp'))
        if fixed_status == 0:
            print("WARNING: fixed regression unexpectedly passed on an unpatched lane")

        env_sim = os.environ.copy()
        env_sim["PYTHONPATH"] = f"{src}{os.pathsep}{here}"
        print(f"\n### identity-guard simulation: {lane}")
        status |= run([sys.executable, str(sim), str(fixed)], env_sim, Path('/tmp'))

    return status


if __name__ == "__main__":
    raise SystemExit(main())
