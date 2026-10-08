#!/usr/bin/env python3
"""rev0035 strict/front lane rerun helper.

Runs the three existing strict/front maintainer artifacts against an extracted
rev0003 source bundle containing source-trees/github-tag-3.3.10,
source-trees/github-branch-3.3.x, and source-trees/github-branch-master.

The artifacts assert current behavior. Passing means the archived lane still
matches the witness; it does not mean the behavior is fixed.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

LANES = ["github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"]


def run_pytest(test_file: Path, source: Path, timeout: int = 60) -> dict:
    code = (
        "import os, sys, pytest; "
        "code=pytest.main(['-q','-p','no:cacheprovider', sys.argv[1]]); "
        "sys.stdout.flush(); sys.stderr.flush(); os._exit(int(code))"
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(source)
    env["NICOTINE_SOURCE"] = str(source)
    proc = subprocess.run(
        [sys.executable, "-B", "-c", code, str(test_file)],
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout,
        check=False,
    )
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def run_script(test_file: Path, source: Path, timeout: int = 60) -> dict:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(source)
    proc = subprocess.run(
        [sys.executable, "-B", str(test_file)],
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout,
        check=False,
    )
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_bundle_or_source_trees", type=Path)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    src = args.source_bundle_or_source_trees
    if (src / "source-trees").is_dir():
        src = src / "source-trees"

    artifacts = [
        ("U-123", root / "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py", run_script),
        ("PB-01", root / "maintainer_artifacts/pb01/test_peer_connection_primary_election_reproducer.py", run_pytest),
        ("SEARCH-RESP-01", root / "maintainer_artifacts/search-resp-01/test_search_response_scope_and_parse_order_reproducer.py", run_pytest),
    ]
    rows = []
    for lane in LANES:
        lane_src = src / lane
        for packet, test_file, runner in artifacts:
            try:
                result = runner(test_file, lane_src)
                status = "pass" if result["returncode"] == 0 else "fail"
            except subprocess.TimeoutExpired as exc:
                result = {"returncode": "timeout", "stdout": exc.stdout or "", "stderr": exc.stderr or ""}
                status = "timeout"
            row = {"lane": lane, "packet": packet, "status": status, **result}
            rows.append(row)
            print(json.dumps(row, sort_keys=True))
    return 0 if all(row["status"] == "pass" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
