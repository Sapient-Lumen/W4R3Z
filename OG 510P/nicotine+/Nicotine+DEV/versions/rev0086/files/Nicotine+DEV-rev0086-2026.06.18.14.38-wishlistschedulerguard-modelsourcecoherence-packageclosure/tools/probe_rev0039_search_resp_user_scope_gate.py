#!/usr/bin/env python3
"""Rerun the rev0039 SEARCH-RESP-01A user-scope gate matrix.

Usage:
    python tools/probe_rev0039_search_resp_user_scope_gate.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z

The helper expects the supplied source bundle to contain source-trees/github-tag-3.3.10,
source-trees/github-branch-3.3.x, and source-trees/github-branch-master.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")


def run_pytest(source_tree: pathlib.Path, test_file: pathlib.Path) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(source_tree)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short", str(test_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        timeout=45,
    )
    return proc.returncode, proc.stdout


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2

    package_root = pathlib.Path(__file__).resolve().parents[1]
    source_bundle = pathlib.Path(sys.argv[1]).resolve()
    source_root = source_bundle / "source-trees"
    fixed_test = package_root / "maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py"
    old_test = package_root / "maintainer_artifacts/search-resp-01/test_search_response_scope_and_parse_order_reproducer.py"
    patch_script = package_root / "tools/apply_search_resp_user_scope_patch_rev0039.py"

    with tempfile.TemporaryDirectory(prefix="rev0039-search-resp-") as tmp_name:
        tmp_root = pathlib.Path(tmp_name)
        patched_root = tmp_root / "patched"
        patched_root.mkdir()

        all_ok = True
        for lane in LANES:
            archived = source_root / lane
            patched = patched_root / lane
            if not archived.exists():
                print(f"missing lane: {archived}")
                return 2
            shutil.copytree(archived, patched, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc"))
            subprocess.run([sys.executable, str(patch_script), str(patched)], check=True)

            rc_old, out_old = run_pytest(archived, old_test)
            rc_fixed_current, out_fixed_current = run_pytest(archived, fixed_test)
            rc_fixed_patch, out_fixed_patch = run_pytest(patched, fixed_test)
            rc_old_patch, out_old_patch = run_pytest(patched, old_test)

            print(f"===== {lane} =====")
            print("current witness on archived source:", "PASS" if rc_old == 0 else f"rc={rc_old}")
            print(out_old.strip().splitlines()[-1] if out_old.strip() else "")
            print("fixed regression on archived source:", "expected pre-fix failure" if rc_fixed_current != 0 else "UNEXPECTED PASS")
            print(out_fixed_current.strip().splitlines()[-1] if out_fixed_current.strip() else "")
            print("selected patch + fixed regression:", "PASS" if rc_fixed_patch == 0 else f"rc={rc_fixed_patch}")
            print(out_fixed_patch.strip().splitlines()[-1] if out_fixed_patch.strip() else "")
            print("selected patch + old witness:", "expected inversion" if rc_old_patch != 0 else "UNEXPECTED PASS")
            print(out_old_patch.strip().splitlines()[-1] if out_old_patch.strip() else "")

            all_ok = all_ok and rc_old == 0 and rc_fixed_current != 0 and rc_fixed_patch == 0 and rc_old_patch != 0

        return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
