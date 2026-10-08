#!/usr/bin/env python3
"""Rerun the rev0041 SEARCH-RESP-PARSE-BUDGET-A prefix-cap matrix.

Usage:
    python tools/probe_rev0041_search_resp_prefix_budget_gate.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

LANES = ('github-tag-3.3.10', 'github-branch-3.3.x', 'github-branch-master')


def lane_root(source_root: pathlib.Path, lane: str) -> pathlib.Path:
    for candidate in (source_root / 'source-trees' / lane, source_root / lane):
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f'missing source lane {lane} under {source_root}')


def run_pytest(package_root: pathlib.Path, source_tree: pathlib.Path, test_name: str) -> tuple[int, str]:
    env = os.environ.copy()
    env['PYTHONPATH'] = str(source_tree)
    env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    proc = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', '--tb=short', str(package_root / 'maintainer_artifacts/search-resp-01' / test_name)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        cwd=package_root,
        timeout=45,
    )
    return proc.returncode, proc.stdout


def one_line(output: str) -> str:
    return output.strip().splitlines()[-1] if output.strip() else '<no output>'


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.strip())
        return 2
    package_root = pathlib.Path(__file__).resolve().parents[1]
    source_root = pathlib.Path(argv[0]).resolve()
    patch_script = package_root / 'tools/apply_search_resp_prefix_budget_patch_rev0041.py'
    old_test = 'test_search_response_scope_and_parse_order_reproducer.py'
    fixed_test = 'test_search_response_prefix_budget_fixed_regression.py'
    ok = True

    with tempfile.TemporaryDirectory(prefix='rev0041-prefix-cap-') as tmp:
        tmp_path = pathlib.Path(tmp)
        for lane in LANES:
            original = lane_root(source_root, lane)
            patched = tmp_path / lane
            shutil.copytree(original, patched, ignore=shutil.ignore_patterns('.git', '__pycache__', '.pytest_cache', '*.pyc'))
            subprocess.run([sys.executable, str(patch_script), str(patched)], check=True)

            print(f'===== {lane} =====', flush=True)
            cases = [
                ('current rev0013 witness', original, old_test, True),
                ('current source + prefix fixed regression', original, fixed_test, False),
                ('selected prefix cap + fixed regression', patched, fixed_test, True),
                ('selected prefix cap + old witness', patched, old_test, False),
            ]
            for label, tree, test, should_pass in cases:
                code, out = run_pytest(package_root, tree, test)
                passed = code == 0
                ok = ok and (passed if should_pass else not passed)
                status = 'PASS' if passed else f'rc={code}'
                print(f'{label}: {status} :: {one_line(out)}', flush=True)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
