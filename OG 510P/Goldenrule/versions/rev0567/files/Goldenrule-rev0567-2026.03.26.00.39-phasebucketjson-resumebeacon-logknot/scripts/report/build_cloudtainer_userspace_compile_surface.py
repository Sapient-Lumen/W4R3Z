#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RECOVERY_CARD = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_recovery_card.json'
FETCH_SURFACE = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_fetch_surface.json'
WORKSPACE_MANIFEST = ROOT / 'Cargo.toml'
LOCK_FILE = ROOT / 'Cargo.lock'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_compile_surface.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_COMPILE_SURFACE.md'

CODEGEN_SUPPORT_NAMES = {'proc-macro2', 'quote', 'syn'}
NATIVE_BUILD_HELPER_NAMES = {
    'bindgen',
    'cbindgen',
    'cc',
    'cmake',
    'openssl-sys',
    'pkg-config',
    'zstd-sys',
    'libz-sys',
    'libgit2-sys',
    'libsqlite3-sys',
    'ring',
}
DIRECT_ROLE_TAGS = {
    'anyhow': ['error'],
    'clap': ['cli', 'proc-macro-entry'],
    'hex': ['encoding'],
    'pretty_assertions': ['test-output'],
    'proptest': ['property-testing'],
    'rand': ['randomness'],
    'rand_chacha': ['randomness'],
    'serde': ['serialization', 'proc-macro-entry'],
    'serde_json': ['serialization'],
    'sha2': ['hashing'],
    'thiserror': ['error'],
}


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding='utf-8'))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _normalize_dep_spec(name: str, spec: Any, section: str, member: str) -> dict[str, Any]:
    if isinstance(spec, str):
        version = spec
        features: list[str] = []
        default_features = True
        optional = False
    elif isinstance(spec, dict):
        version = str(spec.get('version', 'workspace-or-path'))
        features = [str(v) for v in spec.get('features', [])]
        default_features = bool(spec.get('default-features', True))
        optional = bool(spec.get('optional', False))
    else:
        version = 'workspace-or-path'
        features = []
        default_features = True
        optional = False

    tags = list(DIRECT_ROLE_TAGS.get(name, []))
    if 'derive' in features and 'proc-macro-entry' not in tags:
        tags.append('proc-macro-entry')
    if optional:
        tags.append('optional')
    if not default_features:
        tags.append('default-features-disabled')

    return {
        'workspace_member': member,
        'section': section,
        'name': name,
        'version': version,
        'features': features,
        'default_features': default_features,
        'optional': optional,
        'signal_tags': tags,
    }


def _load_workspace_members() -> list[str]:
    workspace = _load_toml(WORKSPACE_MANIFEST).get('workspace', {})
    return [str(v) for v in workspace.get('members', [])]


def _member_surface(member: str) -> dict[str, Any]:
    manifest_path = ROOT / member / 'Cargo.toml'
    payload = _load_toml(manifest_path)
    bins = payload.get('bin') or []
    direct_rows: list[dict[str, Any]] = []
    for section, key in [
        ('runtime', 'dependencies'),
        ('dev', 'dev-dependencies'),
        ('build', 'build-dependencies'),
    ]:
        deps = payload.get(key) or {}
        for name, spec in sorted(deps.items()):
            direct_rows.append(_normalize_dep_spec(name, spec, section, member))

    build_script_paths = []
    if (manifest_path.parent / 'build.rs').exists():
        build_script_paths.append((manifest_path.parent / 'build.rs').relative_to(ROOT).as_posix())

    return {
        'package_name': str((payload.get('package') or {}).get('name', manifest_path.parent.name)),
        'workspace_member': member,
        'manifest_path': manifest_path.relative_to(ROOT).as_posix(),
        'has_library': 'lib' in payload,
        'bin_count': len(bins),
        'build_script_paths': build_script_paths,
        'direct_dependency_rows': direct_rows,
    }


def _compile_surface_code(*, derive_entry_count: int, build_script_count: int, native_helper_count: int) -> str:
    if build_script_count == 0 and native_helper_count == 0 and derive_entry_count > 0:
        return 'direct_derive_no_native_build'
    if build_script_count == 0 and native_helper_count == 0:
        return 'pure_rust_no_codegen_or_native'
    if native_helper_count == 0:
        return 'build_script_present_no_native_helper_watchlist'
    return 'native_helper_watchlist_present'


def build_report() -> dict[str, Any]:
    recovery = _load_json(RECOVERY_CARD)
    fetch_surface = _load_json(FETCH_SURFACE)
    lock = _load_toml(LOCK_FILE)
    packages = list(lock.get('package') or [])
    package_names = sorted({str(pkg.get('name')) for pkg in packages})

    members = _load_workspace_members()
    member_surfaces = [_member_surface(member) for member in members]
    direct_rows = [row for member in member_surfaces for row in member['direct_dependency_rows']]
    derive_rows = [row for row in direct_rows if 'derive' in row['features']]
    build_script_paths = [p for member in member_surfaces for p in member['build_script_paths']]
    codegen_support_names = sorted(
        name for name in package_names if name in CODEGEN_SUPPORT_NAMES or 'derive' in name
    )
    native_helper_names = sorted(name for name in package_names if name in NATIVE_BUILD_HELPER_NAMES)

    implication_rows = [
        'The first later-machine compile lane still includes proc-macro/codegen entry points because the checked-in manifest requests the `derive` feature on both `clap` and `serde`.',
        'No workspace member currently ships a `build.rs`, and no member declares build-dependencies, so the local crate surface itself is not yet asking Cargo to compile and execute a custom build script before `gr_engine` builds.',
        'The current lockfile does not hit the explicit native-helper watchlist (`cc`, `cmake`, `pkg-config`, `bindgen`, common `*-sys` helpers), so the first compile/test witness still looks more like a pure-Rust plus proc-macro lane than a host-C-toolchain rescue lane.',
    ]
    tripwires = [
        'If a future workspace member adds `build.rs`, refresh this card before assuming the first compile/test lane is still a straightforward host-only compile.',
        'If any member starts using build-dependencies, widen the first-machine bring-up notes because Cargo may need an extra pre-build tool stage even if the fetch lane stays registry-only.',
        'If the native-helper watchlist starts matching lockfile packages such as `cc`, `cmake`, `pkg-config`, `bindgen`, or `*-sys`, treat the first compile/test witness as potentially requiring host packages outside the current compact comeback lane.',
    ]

    summary = {
        'current_state_code': recovery.get('summary', {}).get('current_state_code'),
        'fetch_surface_code': fetch_surface.get('summary', {}).get('fetch_surface_code'),
        'compile_surface_code': _compile_surface_code(
            derive_entry_count=len(derive_rows),
            build_script_count=len(build_script_paths),
            native_helper_count=len(native_helper_names),
        ),
        'workspace_member_count': len(members),
        'direct_dependency_count': len(direct_rows),
        'direct_runtime_dependency_count': sum(1 for row in direct_rows if row['section'] == 'runtime'),
        'direct_dev_dependency_count': sum(1 for row in direct_rows if row['section'] == 'dev'),
        'direct_build_dependency_count': sum(1 for row in direct_rows if row['section'] == 'build'),
        'direct_derive_feature_dependency_count': len(derive_rows),
        'workspace_build_script_count': len(build_script_paths),
        'lockfile_codegen_support_package_count': len(codegen_support_names),
        'lockfile_native_helper_watchlist_count': len(native_helper_names),
        'has_library': any(member['has_library'] for member in member_surfaces),
        'total_bin_count': sum(int(member['bin_count']) for member in member_surfaces),
        'risk_flags': [],
    }
    if build_script_paths:
        summary['risk_flags'].append('workspace_build_scripts_present')
    if summary['direct_build_dependency_count']:
        summary['risk_flags'].append('build_dependencies_present')
    if native_helper_names:
        summary['risk_flags'].append('native_helper_watchlist_present')

    return {
        'tool': 'build_cloudtainer_userspace_compile_surface',
        'summary': summary,
        'workspace_members': member_surfaces,
        'direct_dependency_rows': direct_rows,
        'derive_feature_rows': [
            {
                'workspace_member': row['workspace_member'],
                'section': row['section'],
                'name': row['name'],
                'features': row['features'],
            }
            for row in derive_rows
        ],
        'workspace_build_script_paths': build_script_paths,
        'lockfile_codegen_support_names': codegen_support_names,
        'lockfile_native_helper_watchlist_names': native_helper_names,
        'implications': implication_rows,
        'tripwires': tripwires,
    }


def emit_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    members = report['workspace_members']
    rows = report['direct_dependency_rows']
    build_scripts = report['workspace_build_script_paths']
    lines = [
        '# Cloudtainer userspace compile surface',
        '',
        'Generated by `scripts/report/build_cloudtainer_userspace_compile_surface.py`.',
        '',
        'This card is the static companion to `docs/CLOUDTAINER_USERSPACE_FETCH_SURFACE.md`: it keeps one compact answer to a different later-machine question — once the registry-only fetch succeeds, is the first compile/test foothold still mainly a proc-macro/Pure-Rust bring-up, or has the workspace started asking for extra native/build-script repair work?',
        '',
        '## Summary',
        '',
        f"- current recovery state: `{summary['current_state_code']}`",
        f"- upstream fetch surface: `{summary['fetch_surface_code']}`",
        f"- compile surface code: `{summary['compile_surface_code']}`",
        f"- direct dependencies: `{summary['direct_dependency_count']}` total / runtime `{summary['direct_runtime_dependency_count']}` / dev `{summary['direct_dev_dependency_count']}` / build `{summary['direct_build_dependency_count']}`",
        f"- direct derive-feature entry points: `{summary['direct_derive_feature_dependency_count']}`",
        f"- workspace build scripts: `{summary['workspace_build_script_count']}`",
        f"- lockfile codegen-support packages (heuristic): `{summary['lockfile_codegen_support_package_count']}` ({', '.join(report['lockfile_codegen_support_names']) if report['lockfile_codegen_support_names'] else 'none'})",
        f"- lockfile native-helper watchlist hits (heuristic): `{summary['lockfile_native_helper_watchlist_count']}` ({', '.join(report['lockfile_native_helper_watchlist_names']) if report['lockfile_native_helper_watchlist_names'] else 'none'})",
        f"- workspace targets: library `{'yes' if summary['has_library'] else 'no'}` / bins `{summary['total_bin_count']}`",
        '',
        '## Why the first compile lane still looks narrow',
        '',
    ]
    for item in report['implications']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Workspace members',
        '',
        '| package | manifest | lib? | bins | build.rs paths |',
        '| --- | --- | --- | ---: | --- |',
    ])
    for member in members:
        build_rs = ', '.join(member['build_script_paths']) if member['build_script_paths'] else 'none'
        lines.append(
            f"| `{member['package_name']}` | `{member['manifest_path']}` | `{'yes' if member['has_library'] else 'no'}` | {member['bin_count']} | `{build_rs}` |"
        )
    lines.extend([
        '',
        '## Direct dependency rows',
        '',
        '| section | name | version | features | signal tags |',
        '| --- | --- | --- | --- | --- |',
    ])
    for row in rows:
        features = ', '.join(row['features']) if row['features'] else '—'
        tags = ', '.join(row['signal_tags']) if row['signal_tags'] else '—'
        lines.append(
            f"| `{row['section']}` | `{row['name']}` | `{row['version']}` | `{features}` | `{tags}` |"
        )
    lines.extend([
        '',
        '## Tripwires',
        '',
    ])
    for item in report['tripwires']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Reentry use',
        '',
        '- Open this card after `docs/CLOUDTAINER_USERSPACE_FETCH_SURFACE.md` when you want to know whether the next later-machine step is still just “compile the fetched graph and check the first witness,” or whether the workspace has drifted into build-script/native-helper repair.',
        '- Open `docs/CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md` when you are ready to execute the actual bootstrap/fetch/probe/prune commands.',
        '- Treat the lockfile codegen/native rows as a heuristic support surface, not as a substitute for the exact manifest/build-script facts above.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a static compile-friction card for the later-machine userspace Rust comeback lane.')
    parser.add_argument('--write', action='store_true', help='write the JSON and markdown outputs instead of printing JSON only')
    args = parser.parse_args()

    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(emit_markdown(report), encoding='utf-8')
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
