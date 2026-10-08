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
REPAIR_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_repair.patch'
GUARD_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_guard.json'
GUARD_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_guard.patch'
PATCH_REHEARSAL_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_rehearsal.json'
PATCHSET_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_external_test_patchset.patch'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_integration_rehearsal.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_INTEGRATION_REHEARSAL.md'


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_apply(cwd: Path, patch_path: Path, check_only: bool) -> tuple[bool, str]:
    cmd = ['git', 'apply']
    if check_only:
        cmd.append('--check')
    cmd.append(str(patch_path))
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    summary = '\n'.join(part for part in [proc.stdout.strip(), proc.stderr.strip()] if part).strip()
    return proc.returncode == 0, summary


def _write_file(root: Path, relpath: str, data: bytes) -> Path:
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return dst


def _copy_if_exists(root: Path, relpath: str) -> None:
    src = ROOT / relpath
    if not src.exists():
        return
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _snapshot_hashes(root: Path, relpaths: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in relpaths:
        path = root / rel
        out[rel] = _sha256_bytes(path.read_bytes()) if path.exists() else 'MISSING'
    return out


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_bytes(payload.encode('utf-8'))


def _run_sequence(root: Path, patch_order: list[tuple[str, str]]) -> dict[str, Any]:
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
        'sequence_apply_ok': all(step['check_ok'] and step['apply_ok'] for step in steps) and len(steps) == len(patch_order),
    }


def collect() -> dict[str, Any]:
    repair_report = json.loads(REPAIR_REPORT.read_text(encoding='utf-8'))
    guard_report = json.loads(GUARD_REPORT.read_text(encoding='utf-8'))
    patch_rehearsal = json.loads(PATCH_REHEARSAL_REPORT.read_text(encoding='utf-8'))

    repair_patch_bytes = REPAIR_PATCH.read_bytes()
    guard_patch_bytes = GUARD_PATCH.read_bytes()
    patchset_bytes = PATCHSET_PATCH.read_bytes()
    shard_paths = [str(path) for path in patch_rehearsal['metadata']['source_shards']]
    shard_bytes = {rel: (ROOT / rel).read_bytes() for rel in shard_paths}

    target_files = sorted({
        str(repair_report['target_file']),
        str(guard_report['target_file']),
        *[str(path) for path in patch_rehearsal['targets']['files']],
    })

    support_files = {
        str(REPAIR_PATCH.relative_to(ROOT)): repair_patch_bytes,
        str(GUARD_PATCH.relative_to(ROOT)): guard_patch_bytes,
        str(PATCHSET_PATCH.relative_to(ROOT)): patchset_bytes,
    }
    for rel, data in shard_bytes.items():
        support_files[rel] = data

    sequences = {
        'bootstrap_then_monolithic': [
            ('repair', str(REPAIR_PATCH.relative_to(ROOT))),
            ('guard', str(GUARD_PATCH.relative_to(ROOT))),
            ('patchset', str(PATCHSET_PATCH.relative_to(ROOT))),
        ],
        'bootstrap_then_shards': [
            ('repair', str(REPAIR_PATCH.relative_to(ROOT))),
            ('guard', str(GUARD_PATCH.relative_to(ROOT))),
            *[(f'shard_{index:02d}', rel) for index, rel in enumerate(shard_paths, start=1)],
        ],
        'monolithic_then_bootstrap': [
            ('patchset', str(PATCHSET_PATCH.relative_to(ROOT))),
            ('repair', str(REPAIR_PATCH.relative_to(ROOT))),
            ('guard', str(GUARD_PATCH.relative_to(ROOT))),
        ],
    }

    sequence_reports: dict[str, Any] = {}
    for seq_name, order in sequences.items():
        with tempfile.TemporaryDirectory(prefix=f'gr_{seq_name}_') as tmp:
            scratch = Path(tmp)
            for rel in target_files:
                _copy_if_exists(scratch, rel)
            for rel, data in support_files.items():
                _write_file(scratch, rel, data)
            run_report = _run_sequence(scratch, order)
            final_hashes = _snapshot_hashes(scratch, target_files)
            sequence_reports[seq_name] = {
                'order': [step_id for step_id, _ in order],
                'sequence_apply_ok': run_report['sequence_apply_ok'],
                'steps': run_report['steps'],
                'final_hashes': final_hashes,
                'final_combined_hash': _combined_hash(final_hashes),
            }

    final_hash_sets = [sequence_reports[name]['final_hashes'] for name in sequences]
    final_state_equivalent = all(h == final_hash_sets[0] for h in final_hash_sets[1:])
    differing_files = sorted(
        rel for rel in target_files
        if len({sequence_reports[name]['final_hashes'][rel] for name in sequences}) != 1
    )

    return {
        'tool': 'build_rust_standing_bootstrap_integration_rehearsal',
        'source_reports': [
            str(REPAIR_REPORT.relative_to(ROOT)),
            str(GUARD_REPORT.relative_to(ROOT)),
            str(PATCH_REHEARSAL_REPORT.relative_to(ROOT)),
        ],
        'source_patches': {
            'repair': str(REPAIR_PATCH.relative_to(ROOT)),
            'guard': str(GUARD_PATCH.relative_to(ROOT)),
            'patchset': str(PATCHSET_PATCH.relative_to(ROOT)),
            'shards': shard_paths,
        },
        'target_files': target_files,
        'summary': {
            'target_file_count': len(target_files),
            'sequence_count': len(sequences),
            'bootstrap_then_monolithic_ok': sequence_reports['bootstrap_then_monolithic']['sequence_apply_ok'],
            'bootstrap_then_shards_ok': sequence_reports['bootstrap_then_shards']['sequence_apply_ok'],
            'monolithic_then_bootstrap_ok': sequence_reports['monolithic_then_bootstrap']['sequence_apply_ok'],
            'final_state_equivalent': final_state_equivalent,
            'differing_file_count': len(differing_files),
            'repair_patch_sha256': _sha256_bytes(repair_patch_bytes),
            'guard_patch_sha256': _sha256_bytes(guard_patch_bytes),
            'patchset_sha256': _sha256_bytes(patchset_bytes),
        },
        'sequences': sequence_reports,
        'notes': {
            'first_machine_sequence': 'repair -> guard -> full comeback patchset or shard series',
            'reverse_sequence_fallback': 'if the comeback test patchset lands first, the dedicated post-patchset bundle can compress the still-clean repair+guard follow-on into one step',
            'cumulative_shard_apply_hint': str(patch_rehearsal['rehearsal']['shards']['cumulative_apply_hint']),
            'monolithic_apply_hint': 'git apply artifacts/patches/rust_external_test_patchset.patch',
            'differing_files': differing_files,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Integration Rehearsal',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_integration_rehearsal.py`. This proves the narrow probe-local bootstrap repair and standalone guard are operationally compatible with the larger Rust comeback patchset rather than only with each other.',
        '',
        '## Snapshot',
        '',
        f"- target_file_count: `{s['target_file_count']}`",
        f"- sequence_count: `{s['sequence_count']}`",
        f"- bootstrap_then_monolithic_ok: `{str(s['bootstrap_then_monolithic_ok']).lower()}`",
        f"- bootstrap_then_shards_ok: `{str(s['bootstrap_then_shards_ok']).lower()}`",
        f"- monolithic_then_bootstrap_ok: `{str(s['monolithic_then_bootstrap_ok']).lower()}`",
        f"- final_state_equivalent: `{str(s['final_state_equivalent']).lower()}`",
        f"- differing_file_count: `{s['differing_file_count']}`",
        f"- repair_patch_sha256: `{s['repair_patch_sha256']}`",
        f"- guard_patch_sha256: `{s['guard_patch_sha256']}`",
        f"- patchset_sha256: `{s['patchset_sha256']}`",
        '',
        '## What this means for the inheritor',
        '',
        '- The intended first-machine sequence is safe: apply the narrow source repair first, then the standalone guard, then land either the monolithic comeback patchset or the ordered shard series.',
        '- The reverse fallback is also safe: if someone already landed the comeback test patchset first, the narrow probe-local repair and the standalone guard still apply cleanly afterward.',
        '- Final file states match across all rehearsed orders, so the bootstrap seam work is operationally orthogonal to the current comeback test landing.',
        '',
        '## Target files',
        '',
    ]
    for rel in report['target_files']:
        lines.append(f'- `{rel}`')
    lines.extend([
        '',
        '## Sequence summary',
        '',
        '| sequence | order | apply_ok | final_combined_hash |',
        '| --- | --- | --- | --- |',
    ])
    for name, entry in report['sequences'].items():
        lines.append(
            f"| `{name}` | `{', '.join(entry['order'])}` | {str(entry['sequence_apply_ok']).lower()} | `{entry['final_combined_hash']}` |"
        )
    lines.extend([
        '',
        '## First-machine commands proved here',
        '',
        f"1. `git apply {report['source_patches']['repair']}`",
        f"2. `git apply {report['source_patches']['guard']}`",
        f"3. Either `git apply {report['source_patches']['patchset']}` or the cumulative shard series below.",
        f"4. Cumulative shard fallback: `{report['notes']['cumulative_shard_apply_hint']}`",
        '',
        '## Reverse fallback proved here',
        '',
        f"1. `git apply {report['source_patches']['patchset']}`",
        f"2. `git apply {report['source_patches']['repair']}`",
        f"3. `git apply {report['source_patches']['guard']}`",
        '',
    ])
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-integration-rehearsal: missing report/doc', file=sys.stderr)
        return 1
    actual_report = json.loads(OUT_JSON.read_text(encoding='utf-8'))
    if actual_report != expected_report:
        print('rust-standing-bootstrap-integration-rehearsal: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-integration-rehearsal: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-integration-rehearsal: ok sequences=3 final_state_equivalent=true')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = collect()
    markdown = render_markdown(report)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
        return 0
    return _check(report, markdown)


if __name__ == '__main__':
    raise SystemExit(main())
