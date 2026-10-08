#!/usr/bin/env python3
"""Rerun the rev0042 SEARCH-RESP-PARSE-BUDGET-B gate against an external source bundle."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")


def run(pyroot: Path, test: Path) -> tuple[int, str]:
    env = os.environ.copy()
    env.update({"PYTHONPATH": str(pyroot), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short", str(test)], env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    return proc.returncode, (lines[-1] if lines else "<no output>")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: probe_rev0042_search_resp_result_budget_gate.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z")
        return 2
    package_root = Path(__file__).resolve().parents[1]
    source_root = Path(argv[1]) / "source-trees"
    patcher = package_root / "tools/apply_search_resp_result_budget_patch_rev0042.py"
    fixed = package_root / "maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py"
    prefix = package_root / "maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py"
    ok = True
    with tempfile.TemporaryDirectory(prefix="rev0042-result-budget-") as tmp:
        tmp = Path(tmp)
        for lane in LANES:
            orig = source_root / lane
            patched = tmp / lane
            patched.mkdir()
            shutil.copytree(orig / "pynicotine", patched / "pynicotine", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            subprocess.check_call([sys.executable, str(patcher), str(patched)])
            rc, tail = run(patched, fixed)
            print(f"{lane}: selected patch + rev0042 fixed regression: rc={rc} :: {tail}")
            ok &= (rc == 0)
            rc, tail = run(patched, prefix)
            print(f"{lane}: selected patch + rev0041 prefix regression: rc={rc} :: {tail}")
            ok &= (rc == 0)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
