#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_compile_surface.json'
MD_PATH = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_COMPILE_SURFACE.md'


def main() -> int:
    if not JSON_PATH.exists():
        print('cloudtainer-userspace-compile-surface: missing json report', file=sys.stderr)
        return 1
    if not MD_PATH.exists():
        print('cloudtainer-userspace-compile-surface: missing markdown report', file=sys.stderr)
        return 1

    payload = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    summary = payload.get('summary') or {}
    expected = {
        'current_state_code': 'junest_binary_missing',
        'fetch_surface_code': 'registry_only_single_workspace',
        'compile_surface_code': 'direct_derive_no_native_build',
        'workspace_member_count': 1,
        'direct_dependency_count': 11,
        'direct_runtime_dependency_count': 9,
        'direct_dev_dependency_count': 2,
        'direct_build_dependency_count': 0,
        'direct_derive_feature_dependency_count': 2,
        'workspace_build_script_count': 0,
        'lockfile_codegen_support_package_count': 6,
        'lockfile_native_helper_watchlist_count': 0,
        'total_bin_count': 1,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            print(f'cloudtainer-userspace-compile-surface: unexpected {key}={summary.get(key)!r}', file=sys.stderr)
            return 1
    if summary.get('has_library') is not True:
        print('cloudtainer-userspace-compile-surface: expected library target', file=sys.stderr)
        return 1
    if summary.get('risk_flags') != []:
        print(f"cloudtainer-userspace-compile-surface: expected no risk flags, got {summary.get('risk_flags')!r}", file=sys.stderr)
        return 1

    derive_rows = payload.get('derive_feature_rows') or []
    derive_names = sorted(row.get('name') for row in derive_rows)
    if derive_names != ['clap', 'serde']:
        print(f'cloudtainer-userspace-compile-surface: unexpected derive rows {derive_names!r}', file=sys.stderr)
        return 1
    if payload.get('workspace_build_script_paths') != []:
        print('cloudtainer-userspace-compile-surface: expected no build.rs paths', file=sys.stderr)
        return 1
    codegen_names = payload.get('lockfile_codegen_support_names') or []
    if codegen_names != ['clap_derive', 'proc-macro2', 'quote', 'serde_derive', 'syn', 'zerocopy-derive']:
        print(f'cloudtainer-userspace-compile-surface: unexpected codegen support names {codegen_names!r}', file=sys.stderr)
        return 1
    if payload.get('lockfile_native_helper_watchlist_names') != []:
        print('cloudtainer-userspace-compile-surface: expected no native helper hits', file=sys.stderr)
        return 1

    md = MD_PATH.read_text(encoding='utf-8')
    for needle in [
        'direct_derive_no_native_build',
        'lockfile native-helper watchlist hits (heuristic): `0`',
        'CLOUDTAINER_USERSPACE_FETCH_SURFACE.md',
        'Treat the lockfile codegen/native rows as a heuristic support surface',
    ]:
        if needle not in md:
            print(f'cloudtainer-userspace-compile-surface: markdown missing {needle!r}', file=sys.stderr)
            return 1

    print('cloudtainer-userspace-compile-surface: ok (direct_derive_no_native_build)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
