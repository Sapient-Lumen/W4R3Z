#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RECOVERY_CARD = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_recovery_card.json'
PLAN_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_rustup_plan.json'
WORKSPACE_MANIFEST = ROOT / 'Cargo.toml'
TOOLCHAIN_FILE = ROOT / 'rust-toolchain.toml'
LOCK_FILE = ROOT / 'Cargo.lock'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_fetch_surface.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_FETCH_SURFACE.md'


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding='utf-8'))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_toolchain(path: Path) -> dict[str, Any]:
    payload = _load_toml(path)
    toolchain = dict(payload.get('toolchain') or {})
    return {
        'channel': str(toolchain.get('channel', 'stable')),
        'profile': str(toolchain.get('profile', 'default')),
        'components': [str(v) for v in toolchain.get('components', [])],
        'targets': [str(v) for v in toolchain.get('targets', [])],
    }


def _direct_dependency_summary(manifest_path: Path) -> dict[str, Any]:
    payload = _load_toml(manifest_path)
    package = dict(payload.get('package') or {})
    bins = payload.get('bin') or []
    return {
        'package_name': str(package.get('name') or manifest_path.parent.name),
        'manifest_path': manifest_path.relative_to(ROOT).as_posix(),
        'runtime_dependency_count': len(payload.get('dependencies') or {}),
        'dev_dependency_count': len(payload.get('dev-dependencies') or {}),
        'build_dependency_count': len(payload.get('build-dependencies') or {}),
        'has_library': 'lib' in payload,
        'bin_count': len(bins),
    }


def _surface_code(*, workspace_member_count: int, git_package_count: int, unique_registry_count: int, target_count: int) -> str:
    if git_package_count == 0 and unique_registry_count == 1 and workspace_member_count == 1 and target_count == 0:
        return 'registry_only_single_workspace'
    if git_package_count == 0 and unique_registry_count == 1:
        return 'registry_only_multi_workspace_or_targets'
    if git_package_count == 0:
        return 'multi_registry_no_git'
    return 'mixed_registry_and_git'


def build_report() -> dict[str, Any]:
    recovery = _load_json(RECOVERY_CARD)
    plan = _load_json(PLAN_REPORT)
    workspace_manifest = _load_toml(WORKSPACE_MANIFEST)
    toolchain = _load_toolchain(TOOLCHAIN_FILE)
    lock = _load_toml(LOCK_FILE)
    packages = list(lock.get('package') or [])

    members = [str(member) for member in (workspace_manifest.get('workspace', {}).get('members') or [])]
    member_summaries = []
    for member in members:
        manifest = ROOT / member / 'Cargo.toml'
        member_summaries.append(_direct_dependency_summary(manifest))

    source_counter = Counter()
    registries: list[str] = []
    git_sources: list[str] = []
    workspace_or_path_count = 0
    for package in packages:
        source = str(package.get('source') or 'path-or-workspace')
        source_counter[source] += 1
        if source.startswith('registry+') and source not in registries:
            registries.append(source)
        elif source.startswith('git+') and source not in git_sources:
            git_sources.append(source)
        elif source == 'path-or-workspace':
            workspace_or_path_count += 1

    registry_package_count = sum(count for source, count in source_counter.items() if source.startswith('registry+'))
    git_package_count = sum(count for source, count in source_counter.items() if source.startswith('git+'))
    external_package_count = registry_package_count + git_package_count
    direct_runtime_count = sum(row['runtime_dependency_count'] for row in member_summaries)
    direct_dev_count = sum(row['dev_dependency_count'] for row in member_summaries)
    direct_build_count = sum(row['build_dependency_count'] for row in member_summaries)
    fetch_surface_code = _surface_code(
        workspace_member_count=len(members),
        git_package_count=git_package_count,
        unique_registry_count=len(registries),
        target_count=len(toolchain['targets']),
    )

    risk_flags: list[str] = []
    if git_package_count:
        risk_flags.append('git_deps_present')
    if len(registries) > 1:
        risk_flags.append('multiple_registries')
    if len(members) > 1:
        risk_flags.append('multi_workspace')
    if toolchain['targets']:
        risk_flags.append('extra_targets_requested')

    implications = [
        'The later-machine dependency warm-cache lane is still compact: the lockfile resolves to registry packages only plus the local workspace package, so the first egress window does not also need ad hoc git dependency debugging.',
        'Only one workspace member currently participates in the Rust surface, which keeps the first successful compile/test foothold focused on gr_engine rather than a multi-crate workspace bring-up.',
        'The checked-in toolchain override still asks for stable plus rustfmt and no extra targets, so the repo-local userspace bootstrap lane remains narrow.',
        'Because Cargo.lock is present and all external packages are registry-backed, the current later-machine strategy should stay cargo fetch --locked first, exact witness second, archive prune last.',
    ]
    tripwires = [
        'If a future Cargo.lock adds any git+ sources, widen the later-machine egress budget and re-audit the comeback lane before assuming the current fetch window is still enough.',
        'If the workspace grows beyond crates/gr_engine, refresh this surface before treating the first compile/test foothold as a single-crate bring-up.',
        'If rust-toolchain.toml starts requesting explicit cross targets, treat the userspace bootstrap as more than a host-only lane and widen the cleanup/accounting discipline accordingly.',
    ]

    return {
        'tool': 'build_cloudtainer_userspace_fetch_surface',
        'summary': {
            'current_state_code': recovery.get('summary', {}).get('current_state_code'),
            'fetch_surface_code': fetch_surface_code,
            'workspace_member_count': len(members),
            'workspace_members': members,
            'lock_package_count': len(packages),
            'external_package_count': external_package_count,
            'registry_package_count': registry_package_count,
            'git_package_count': git_package_count,
            'workspace_or_path_package_count': workspace_or_path_count,
            'unique_registry_count': len(registries),
            'unique_git_source_count': len(git_sources),
            'direct_runtime_dependency_count': direct_runtime_count,
            'direct_dev_dependency_count': direct_dev_count,
            'direct_build_dependency_count': direct_build_count,
            'toolchain_component_count': len(toolchain['components']),
            'toolchain_target_count': len(toolchain['targets']),
            'transient_roots': list(plan.get('summary', {}).get('transient_roots') or []),
            'warm_cache_phase_present': 'warm_cache' in (plan.get('summary', {}).get('phase_ids') or []),
            'risk_flags': risk_flags,
        },
        'workspace_packages': member_summaries,
        'source_breakdown': [
            {'source': source, 'package_count': count}
            for source, count in sorted(source_counter.items())
        ],
        'registries': registries,
        'git_sources': git_sources,
        'toolchain': toolchain,
        'implications': implications,
        'tripwires': tripwires,
    }


def emit_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    toolchain = report['toolchain']
    rows = report['workspace_packages']
    lines = [
        '# Cloudtainer userspace fetch surface',
        '',
        'Generated by `scripts/report/build_cloudtainer_userspace_fetch_surface.py`.',
        '',
        'This card is the static companion to `docs/CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md`: it does **not** emit the command sequence, it records how complicated the later-machine dependency/bootstrap surface actually is right now.',
        '',
        '## Summary',
        '',
        f"- current recovery state: `{summary['current_state_code']}`",
        f"- fetch surface code: `{summary['fetch_surface_code']}`",
        f"- workspace members: `{summary['workspace_member_count']}` ({', '.join(summary['workspace_members'])})",
        f"- lock packages: `{summary['lock_package_count']}` total / `{summary['registry_package_count']}` registry / `{summary['git_package_count']}` git / `{summary['workspace_or_path_package_count']}` workspace-path",
        f"- unique registries: `{summary['unique_registry_count']}`",
        f"- direct dependencies (`gr_engine` workspace total): runtime `{summary['direct_runtime_dependency_count']}`, dev `{summary['direct_dev_dependency_count']}`, build `{summary['direct_build_dependency_count']}`",
        f"- toolchain additives: components `{', '.join(toolchain['components']) if toolchain['components'] else 'none'}` / targets `{', '.join(toolchain['targets']) if toolchain['targets'] else 'none'}`",
        f"- transient prune roots: `{', '.join(summary['transient_roots'])}`",
        '',
        '## Why the current later-machine lane is still compact',
        '',
    ]
    for item in report['implications']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Workspace package surface',
        '',
        '| package | manifest | lib? | bins | runtime deps | dev deps | build deps |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: |',
    ])
    for row in rows:
        lines.append(
            f"| `{row['package_name']}` | `{row['manifest_path']}` | `{'yes' if row['has_library'] else 'no'}` | {row['bin_count']} | {row['runtime_dependency_count']} | {row['dev_dependency_count']} | {row['build_dependency_count']} |"
        )
    lines.extend([
        '',
        '## Lockfile source breakdown',
        '',
        '| source | packages |',
        '| --- | ---: |',
    ])
    for row in report['source_breakdown']:
        lines.append(f"| `{row['source']}` | {row['package_count']} |")
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
        '- Open this card when you want to know whether the existing userspace-rustup comeback lane is still a small registry-only fetch story or has widened into a multi-source bring-up problem.',
        '- Open `docs/CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md` when you are ready to execute the actual later-machine bootstrap/fetch/probe/prune sequence.',
        '- If this card drifts to any non-`registry_only_single_workspace` surface code, refresh the comeback plan and widen the handoff note before assuming the old egress budget still fits.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a static dependency-surface card for the later-machine userspace Rust comeback lane.')
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
