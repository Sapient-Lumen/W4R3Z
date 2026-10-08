#!/usr/bin/env python3
"""Rerun the rev0043 SEARCH-RESP-01C room source-set gate matrix.

Usage:
    python tools/probe_rev0043_search_resp_room_scope_gate.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z

The helper copies only each lane's pynicotine package into a temporary patched
checkout, applies the selected stacked source-set patch, and runs the current
witness plus the rev0043 room fixed regression.
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
        timeout=20,
    )
    return proc.returncode, proc.stdout


def last_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def copy_minimal_checkout(archived: pathlib.Path, patched: pathlib.Path) -> None:
    patched.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        archived / "pynicotine",
        patched / "pynicotine",
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"),
    )


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2

    package_root = pathlib.Path(__file__).resolve().parents[1]
    source_bundle = pathlib.Path(sys.argv[1]).resolve()
    source_root = source_bundle / "source-trees"
    fixed_room_test = package_root / "maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py"
    old_test = package_root / "maintainer_artifacts/search-resp-01/test_search_response_scope_and_parse_order_reproducer.py"
    patch_script = package_root / "tools/apply_search_resp_room_scope_patch_rev0043.py"

    all_ok = True

    for lane in LANES:
        archived = source_root / lane
        if not (archived / "pynicotine" / "search.py").exists():
            print(f"missing lane: {archived}")
            return 2

        with tempfile.TemporaryDirectory(prefix=f"rev0043-search-resp-room-{lane}-") as tmp_name:
            patched = pathlib.Path(tmp_name) / "patched"
            copy_minimal_checkout(archived, patched)
            subprocess.run([sys.executable, str(patch_script), str(patched)], check=True, stdout=subprocess.DEVNULL)

            rc_old, out_old = run_pytest(archived, old_test)
            rc_fixed_current, out_fixed_current = run_pytest(archived, fixed_room_test)
            rc_fixed_patch, out_fixed_patch = run_pytest(patched, fixed_room_test)
            rc_old_patch, out_old_patch = run_pytest(patched, old_test)

        print(f"===== {lane} =====")
        print("current witness on archived source:", "PASS" if rc_old == 0 else f"rc={rc_old}")
        print(last_line(out_old))
        print("rev0043 room fixed regression on archived source:", "expected pre-fix failure" if rc_fixed_current != 0 else "UNEXPECTED PASS")
        print(last_line(out_fixed_current))
        print("selected source-set patch + rev0043 room fixed regression:", "PASS" if rc_fixed_patch == 0 else f"rc={rc_fixed_patch}")
        print(last_line(out_fixed_patch))
        print("selected source-set patch + old current witness:", "expected inversion" if rc_old_patch != 0 else "UNEXPECTED PASS")
        print(last_line(out_old_patch))

        all_ok = all_ok and rc_old == 0 and rc_fixed_current != 0 and rc_fixed_patch == 0 and rc_old_patch != 0

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
