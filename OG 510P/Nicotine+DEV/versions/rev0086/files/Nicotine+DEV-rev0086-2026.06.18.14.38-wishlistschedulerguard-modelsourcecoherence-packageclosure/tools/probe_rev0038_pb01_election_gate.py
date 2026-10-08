#!/usr/bin/env python3
"""Run the rev0038 PB-01 fixed-regression gate against a source bundle.

Usage:
    python tools/probe_rev0038_pb01_election_gate.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z

The helper does not require the compact cube to contain source trees. It
imports each archived lane from the external source bundle, verifies that
the fixed regression fails on current source, applies the selected
primary-guard patch to a temporary copy, and verifies the fixed regression
passes on the patched copy.
"""
from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANES = ["github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"]
ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "maintainer_artifacts" / "pb01" / "test_peer_connection_primary_election_fixed_regression.py"
PATCHER = ROOT / "tools" / "apply_pb01_primary_guard_patch_rev0038.py"

def run_pytest(source: Path) -> dict:
    env = os.environ.copy()
    env["NICOTINE_SOURCE"] = str(source)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short", str(TEST)],
        text=True, capture_output=True, env=env, timeout=90
    )
    output = proc.stdout + proc.stderr
    summary = None
    for line in output.splitlines():
        if re.search(r"\d+ failed, \d+ passed", line) or re.search(r"\d+ passed in", line):
            summary = line.strip()
    return {"returncode": proc.returncode, "summary": summary, "output_tail": output.splitlines()[-20:]}

def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    bundle = Path(sys.argv[1]).resolve()
    source_base = bundle / "source-trees"
    if not source_base.exists():
        source_base = bundle
    results = []
    overall_ok = True
    with tempfile.TemporaryDirectory(prefix="pb01-rev0038-") as tmp:
        tmp = Path(tmp)
        for lane in LANES:
            current = source_base / lane
            if not current.exists():
                results.append({"lane": lane, "error": f"missing lane: {current}"})
                overall_ok = False
                continue
            current_run = run_pytest(current)
            patched = tmp / lane
            shutil.copytree(current, patched)
            subprocess.run([sys.executable, str(PATCHER), str(patched)], check=True, text=True)
            patched_run = run_pytest(patched)
            lane_ok = (current_run["returncode"] != 0 and patched_run["returncode"] == 0)
            overall_ok = overall_ok and lane_ok
            results.append({
                "lane": lane,
                "current_fixed_regression": current_run,
                "patched_fixed_regression": patched_run,
                "gate_ok": lane_ok,
            })
    print(json.dumps({"status": "ok" if overall_ok else "failed", "results": results}, indent=2))
    return 0 if overall_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
