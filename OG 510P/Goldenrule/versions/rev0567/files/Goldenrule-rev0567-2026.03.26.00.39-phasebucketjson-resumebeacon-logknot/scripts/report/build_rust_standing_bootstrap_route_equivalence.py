#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPAIR_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_repair_patch.json'
GUARD_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_guard.json'
INTEGRATION_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_integration_rehearsal.json'
COMEBACK_BUNDLE_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_comeback_bundle.json'
POST_PATCHSET_BUNDLE_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_post_patchset_bundle.json'
REPAIR_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_repair.patch'
GUARD_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_guard.patch'
PATCHSET_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_external_test_patchset.patch'
COMEBACK_BUNDLE_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_comeback_bundle.patch'
POST_PATCHSET_BUNDLE_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_post_patchset_bundle.patch'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_route_equivalence.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_ROUTE_EQUIVALENCE.md'


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_bytes(payload.encode('utf-8'))


def _run_apply(cwd: Path, patch_path: Path, check_only: bool) -> tuple[bool, str]:
    cmd = ['git', 'apply']
    if check_only:
        cmd.append('--check')
    cmd.append(str(patch_path))
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    summary = '\n'.join(part for part in [proc.stdout.strip(), proc.stderr.strip()] if part).strip()
    return proc.returncode == 0, summary


def _copy_if_exists(root: Path, relpath: str) -> None:
    src = ROOT / relpath
    if not src.exists():
        return
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _write_support_file(root: Path, relpath: str, data: bytes) -> Path:
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return dst


def _snapshot_hashes(root: Path, relpaths: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in relpaths:
        path = root / rel
        out[rel] = _sha256_bytes(path.read_bytes()) if path.exists() else 'MISSING'
    return out


def _run_route(root: Path, patch_order: list[tuple[str, str]]) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    for step_id, rel_patch in patch_order:
        patch_path = root / rel_patch
        check_ok, check_summary = _run_apply(root, patch_path, True)
        apply_ok = False
        apply_summary = ''
        if check_ok:
            apply_ok, apply_summary = _run_apply(root, patch_path, False)
        steps.append({
            'step_id': step_id,
            'patch_path': rel_patch,
            'check_ok': check_ok,
            'apply_ok': apply_ok,
            'check_summary': check_summary,
            'apply_summary': apply_summary,
        })
        if not (check_ok and apply_ok):
            break
    return {
        'steps': steps,
        'route_apply_ok': len(steps) == len(patch_order) and all(step['check_ok'] and step['apply_ok'] for step in steps),
    }


def collect() -> dict[str, Any]:
    repair_report = json.loads(REPAIR_REPORT.read_text(encoding='utf-8'))
    guard_report = json.loads(GUARD_REPORT.read_text(encoding='utf-8'))
    integration_report = json.loads(INTEGRATION_REPORT.read_text(encoding='utf-8'))
    comeback_bundle_report = json.loads(COMEBACK_BUNDLE_REPORT.read_text(encoding='utf-8'))
    post_patchset_bundle_report = json.loads(POST_PATCHSET_BUNDLE_REPORT.read_text(encoding='utf-8'))

    target_files = sorted({
        str(repair_report['target_file']),
        str(guard_report['target_file']),
        *[str(path) for path in integration_report['target_files']],
    })

    support_files = {
        str(REPAIR_PATCH.relative_to(ROOT)): REPAIR_PATCH.read_bytes(),
        str(GUARD_PATCH.relative_to(ROOT)): GUARD_PATCH.read_bytes(),
        str(PATCHSET_PATCH.relative_to(ROOT)): PATCHSET_PATCH.read_bytes(),
        str(COMEBACK_BUNDLE_PATCH.relative_to(ROOT)): COMEBACK_BUNDLE_PATCH.read_bytes(),
        str(POST_PATCHSET_BUNDLE_PATCH.relative_to(ROOT)): POST_PATCHSET_BUNDLE_PATCH.read_bytes(),
    }

    routes = {
        'layered_clean_head': [
            ('repair', str(REPAIR_PATCH.relative_to(ROOT))),
            ('guard', str(GUARD_PATCH.relative_to(ROOT))),
            ('patchset', str(PATCHSET_PATCH.relative_to(ROOT))),
        ],
        'clean_head_bundle': [
            ('comeback_bundle', str(COMEBACK_BUNDLE_PATCH.relative_to(ROOT))),
        ],
        'patchset_then_post_bundle': [
            ('patchset', str(PATCHSET_PATCH.relative_to(ROOT))),
            ('post_patchset_bundle', str(POST_PATCHSET_BUNDLE_PATCH.relative_to(ROOT))),
        ],
    }

    route_reports: dict[str, Any] = {}
    for route_name, order in routes.items():
        with tempfile.TemporaryDirectory(prefix=f'gr_{route_name}_') as tmp:
            scratch = Path(tmp)
            for rel in target_files:
                _copy_if_exists(scratch, rel)
            for rel, data in support_files.items():
                _write_support_file(scratch, rel, data)
            run_report = _run_route(scratch, order)
            final_hashes = _snapshot_hashes(scratch, target_files)
            route_reports[route_name] = {
                'order': [step_id for step_id, _ in order],
                'route_apply_ok': run_report['route_apply_ok'],
                'steps': run_report['steps'],
                'final_hashes': final_hashes,
                'final_combined_hash': _combined_hash(final_hashes),
            }

    hash_sets = [route_reports[name]['final_hashes'] for name in routes]
    final_state_equivalent = all(h == hash_sets[0] for h in hash_sets[1:])
    differing_files = sorted(
        rel for rel in target_files
        if len({route_reports[name]['final_hashes'][rel] for name in routes}) != 1
    )
    layered_hash = route_reports['layered_clean_head']['final_combined_hash']
    clean_head_bundle_hash = route_reports['clean_head_bundle']['final_combined_hash']
    post_patchset_bundle_hash = route_reports['patchset_then_post_bundle']['final_combined_hash']

    return {
        'tool': 'build_rust_standing_bootstrap_route_equivalence',
        'source_reports': [
            str(REPAIR_REPORT.relative_to(ROOT)),
            str(GUARD_REPORT.relative_to(ROOT)),
            str(INTEGRATION_REPORT.relative_to(ROOT)),
            str(COMEBACK_BUNDLE_REPORT.relative_to(ROOT)),
            str(POST_PATCHSET_BUNDLE_REPORT.relative_to(ROOT)),
        ],
        'source_patches': {
            'repair': str(REPAIR_PATCH.relative_to(ROOT)),
            'guard': str(GUARD_PATCH.relative_to(ROOT)),
            'patchset': str(PATCHSET_PATCH.relative_to(ROOT)),
            'comeback_bundle': str(COMEBACK_BUNDLE_PATCH.relative_to(ROOT)),
            'post_patchset_bundle': str(POST_PATCHSET_BUNDLE_PATCH.relative_to(ROOT)),
        },
        'target_files': target_files,
        'summary': {
            'target_file_count': len(target_files),
            'route_count': len(routes),
            'all_routes_apply_ok': all(route_reports[name]['route_apply_ok'] for name in routes),
            'final_state_equivalent': final_state_equivalent,
            'differing_file_count': len(differing_files),
            'canonical_final_hash': layered_hash,
            'matches_integration_layered_hash': layered_hash == integration_report['sequences']['bootstrap_then_monolithic']['final_combined_hash'],
            'matches_clean_head_bundle_report': clean_head_bundle_hash == comeback_bundle_report['summary']['combined_final_hash'],
            'matches_post_patchset_bundle_report': post_patchset_bundle_hash == post_patchset_bundle_report['summary']['combined_final_hash'],
            'matches_clean_head_bundle_file_hashes': route_reports['clean_head_bundle']['final_hashes'] == comeback_bundle_report['final_hashes'],
            'matches_post_patchset_bundle_file_hashes': route_reports['patchset_then_post_bundle']['final_hashes'] == post_patchset_bundle_report['final_hashes'],
        },
        'routes': route_reports,
        'notes': {
            'meaning': 'The convenience artifacts are trustworthy only if they converge to the same exact 4-file final state as the layered route they compress.',
            'selector_connection': 'The exact-state selector can route to the shortest safe apply path because the routes compared here are byte-equivalent at the target-file surface.',
            'differing_files': differing_files,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Route Equivalence',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_route_equivalence.py`. This fuses the previously separate rehearsals into one exactness proof for the first Rust-capable inheritor: the clean-head layered route, the one-shot clean-head bundle, and the patchset-plus-follow-on bundle route all converge to the same final bytes on the four bootstrap/comeback target files.',
        '',
        '## Snapshot',
        '',
        f"- target_file_count: `{s['target_file_count']}`",
        f"- route_count: `{s['route_count']}`",
        f"- all_routes_apply_ok: `{str(s['all_routes_apply_ok']).lower()}`",
        f"- final_state_equivalent: `{str(s['final_state_equivalent']).lower()}`",
        f"- differing_file_count: `{s['differing_file_count']}`",
        f"- canonical_final_hash: `{s['canonical_final_hash']}`",
        f"- matches_integration_layered_hash: `{str(s['matches_integration_layered_hash']).lower()}`",
        f"- matches_clean_head_bundle_report: `{str(s['matches_clean_head_bundle_report']).lower()}`",
        f"- matches_post_patchset_bundle_report: `{str(s['matches_post_patchset_bundle_report']).lower()}`",
        f"- matches_clean_head_bundle_file_hashes: `{str(s['matches_clean_head_bundle_file_hashes']).lower()}`",
        f"- matches_post_patchset_bundle_file_hashes: `{str(s['matches_post_patchset_bundle_file_hashes']).lower()}`",
        '',
        '## Why this matters',
        '',
        '- The clean-head comeback bundle is not merely convenient; it lands the same target-file bytes as the explicit `repair -> guard -> patchset` route.',
        '- The post-patchset convenience bundle is also exact; applying the monolithic comeback patchset first and then that follow-on bundle lands the same target-file bytes as the clean-head routes.',
        '- This means the exact-state selector is routing among byte-equivalent landings, not between subtly different outcomes.',
        '',
        '## Target files',
        '',
    ]
    for rel in report['target_files']:
        lines.append(f'- `{rel}`')
    lines.extend([
        '',
        '## Route summary',
        '',
        '| route | order | apply_ok | final_combined_hash |',
        '| --- | --- | --- | --- |',
    ])
    for name, entry in report['routes'].items():
        lines.append(
            f"| `{name}` | `{', '.join(entry['order'])}` | {str(entry['route_apply_ok']).lower()} | `{entry['final_combined_hash']}` |"
        )
    lines.extend([
        '',
        '## Safe operational reading',
        '',
        '1. On a clean branch, either apply the explicit layered route or the clean-head comeback bundle; the target-file outcome is the same.',
        '2. If the monolithic comeback patchset is already on branch, the dedicated post-patchset bundle is the shortest route back to that same final target-file state.',
        '3. If the selector reports an unknown/drifted state, stop and inspect the four target files rather than forcing any convenience bundle.',
        '',
    ])
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-route-equivalence: missing outputs; run with --write', file=sys.stderr)
        return 1
    current_report = json.loads(OUT_JSON.read_text(encoding='utf-8'))
    current_markdown = OUT_MD.read_text(encoding='utf-8')
    if current_report != expected_report or current_markdown != expected_markdown:
        print('rust-standing-bootstrap-route-equivalence: drift detected; run with --write', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-route-equivalence: ok')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()

    report = collect()
    markdown = render_markdown(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
        print(f'rust-standing-bootstrap-route-equivalence: wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'rust-standing-bootstrap-route-equivalence: wrote {OUT_MD.relative_to(ROOT)}')
        return 0
    return _check(report, markdown + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
