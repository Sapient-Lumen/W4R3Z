#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_fetch_surface.json'
MD_PATH = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_FETCH_SURFACE.md'


def main() -> int:
    if not JSON_PATH.exists():
        print('cloudtainer-userspace-fetch-surface: missing json report', file=sys.stderr)
        return 1
    if not MD_PATH.exists():
        print('cloudtainer-userspace-fetch-surface: missing markdown report', file=sys.stderr)
        return 1

    payload = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    summary = payload.get('summary') or {}
    if summary.get('current_state_code') != 'junest_binary_missing':
        print('cloudtainer-userspace-fetch-surface: expected junest_binary_missing state', file=sys.stderr)
        return 1
    expected_counts = {
        'workspace_member_count': 1,
        'lock_package_count': 80,
        'registry_package_count': 79,
        'git_package_count': 0,
        'workspace_or_path_package_count': 1,
        'unique_registry_count': 1,
        'direct_runtime_dependency_count': 9,
        'direct_dev_dependency_count': 2,
        'direct_build_dependency_count': 0,
        'toolchain_component_count': 1,
        'toolchain_target_count': 0,
    }
    for key, expected in expected_counts.items():
        if int(summary.get(key, -1)) != expected:
            print(f'cloudtainer-userspace-fetch-surface: unexpected {key}={summary.get(key)!r}', file=sys.stderr)
            return 1
    if summary.get('fetch_surface_code') != 'registry_only_single_workspace':
        print(f"cloudtainer-userspace-fetch-surface: unexpected fetch_surface_code={summary.get('fetch_surface_code')!r}", file=sys.stderr)
        return 1
    if summary.get('risk_flags') != []:
        print(f"cloudtainer-userspace-fetch-surface: expected no risk flags, got {summary.get('risk_flags')!r}", file=sys.stderr)
        return 1
    if summary.get('transient_roots') != ['.local/cargo', '.local/rustup', '.local/target']:
        print('cloudtainer-userspace-fetch-surface: transient roots drifted', file=sys.stderr)
        return 1
    if not summary.get('warm_cache_phase_present', False):
        print('cloudtainer-userspace-fetch-surface: warm_cache phase missing', file=sys.stderr)
        return 1
    if payload.get('git_sources') != []:
        print('cloudtainer-userspace-fetch-surface: expected no git sources', file=sys.stderr)
        return 1
    md = MD_PATH.read_text(encoding='utf-8')
    for needle in [
        'registry_only_single_workspace',
        '79` registry / `0` git / `1` workspace-path',
        'CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md',
        'Tripwires',
    ]:
        if needle not in md:
            print(f'cloudtainer-userspace-fetch-surface: markdown missing {needle!r}', file=sys.stderr)
            return 1
    print('cloudtainer-userspace-fetch-surface: ok (packages=80 registry_only_single_workspace)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
