#!/usr/bin/env python3
"""Rerun the rev0044 U-138 ID3v2 boundary witness.

Usage:
    python tools/probe_rev0044_u138_id3v2_boundary.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z

The helper accepts either the rev0003 source-bundle root or its source-trees/
subdirectory. It runs the current-behavior boundary witness on each archived
lane and expects all tests to pass.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")


def source_root_from_arg(path: pathlib.Path) -> pathlib.Path:
    if (path / "source-trees").is_dir():
        return path / "source-trees"
    return path


def last_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def run_pytest(lane_root: pathlib.Path, test_file: pathlib.Path) -> tuple[int, str]:
    env = os.environ.copy()
    env["NICOTINE_SOURCE"] = str(lane_root)
    env["PYTHONPATH"] = str(lane_root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(test_file), "--tb=short"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        timeout=30,
    )
    return proc.returncode, proc.stdout


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    package_root = pathlib.Path(__file__).resolve().parents[1]
    source_root = source_root_from_arg(pathlib.Path(sys.argv[1]).resolve())
    test_file = package_root / "maintainer_artifacts" / "u138-id3v2-frame-materialization-01" / "test_id3v2_frame_materialization_boundary_reproducer.py"

    if not test_file.is_file():
        print(f"missing test file: {test_file}", file=sys.stderr)
        return 2

    ok = True
    for lane in LANES:
        lane_root = source_root / lane
        if not (lane_root / "pynicotine" / "external" / "tinytag.py").is_file():
            print(f"missing lane: {lane_root}", file=sys.stderr)
            ok = False
            continue

        rc, out = run_pytest(lane_root, test_file)
        print(f"===== {lane} =====")
        print("U-138 ID3v2 boundary witness:", "PASS" if rc == 0 else f"rc={rc}")
        print(last_line(out))
        if rc != 0:
            print(out)
        ok = ok and rc == 0

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
