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

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_rehearsal.json'
OUT_MD = ROOT / 'docs' / 'RUST_EXTERNAL_TEST_PATCH_REHEARSAL.md'
PATCHSET_JSON = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patchset.json'
PATCHSET_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_external_test_patchset.patch'
SHARDS_JSON = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_shards.json'


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode('utf-8'))


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _run_apply(cwd: Path, patch_path: Path, check_only: bool) -> tuple[bool, str]:
    cmd = ['git', 'apply']
    if check_only:
        cmd.append('--check')
    cmd.append(str(patch_path))
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    summary = '\n'.join(part for part in [proc.stdout.strip(), proc.stderr.strip()] if part).strip()
    return proc.returncode == 0, summary


def _copy_targets(scratch_root: Path, target_files: list[str]) -> None:
    for rel in target_files:
        src = ROOT / rel
        dst = scratch_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _materialize_patch_assets(scratch_root: Path, patchset_text: str, shard_texts: dict[str, str]) -> tuple[Path, dict[str, Path]]:
    patchset_path = scratch_root / 'artifacts' / 'patches' / 'rust_external_test_patchset.patch'
    patchset_path.parent.mkdir(parents=True, exist_ok=True)
    patchset_path.write_text(patchset_text, encoding='utf-8')

    shard_paths: dict[str, Path] = {}
    for rel, text in shard_texts.items():
        dst = scratch_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding='utf-8')
        shard_paths[rel] = dst
    return patchset_path, shard_paths


def _snapshot_hashes(root: Path, target_files: list[str]) -> dict[str, str]:
    return {rel: _sha256_bytes((root / rel).read_bytes()) for rel in target_files}


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_text(payload)


def build_report() -> dict[str, object]:
    required = [PATCHSET_JSON, PATCHSET_PATCH, SHARDS_JSON]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError('missing required source artifact(s): ' + ', '.join(missing))

    patchset_report = _read_json(PATCHSET_JSON)
    shards_report = _read_json(SHARDS_JSON)
    patchset_text = PATCHSET_PATCH.read_text(encoding='utf-8')
    shard_series = [str(path) for path in shards_report['series']['patch_paths']]
    shard_texts = {
        rel: (ROOT / rel).read_text(encoding='utf-8')
        for rel in shard_series
    }
    target_files = sorted({str(path) for entry in shards_report['entries'] for path in entry['target_files']})

    baseline_hashes = _snapshot_hashes(ROOT, target_files)
    baseline_combined = _combined_hash(baseline_hashes)

    with tempfile.TemporaryDirectory(prefix='gr_patch_rehearsal_') as monolithic_tmp, tempfile.TemporaryDirectory(prefix='gr_patch_rehearsal_') as shard_tmp:
        monolithic_root = Path(monolithic_tmp)
        shard_root = Path(shard_tmp)
        _copy_targets(monolithic_root, target_files)
        _copy_targets(shard_root, target_files)
        monolithic_patch_path, shard_paths = _materialize_patch_assets(monolithic_root, patchset_text, shard_texts)
        _materialize_patch_assets(shard_root, patchset_text, shard_texts)

        mono_check_ok, mono_check_summary = _run_apply(monolithic_root, monolithic_patch_path, check_only=True)
        mono_apply_ok = False
        mono_apply_summary = ''
        monolithic_hashes: dict[str, str] = {}
        monolithic_combined = ''
        if mono_check_ok:
            mono_apply_ok, mono_apply_summary = _run_apply(monolithic_root, monolithic_patch_path, check_only=False)
            if mono_apply_ok:
                monolithic_hashes = _snapshot_hashes(monolithic_root, target_files)
                monolithic_combined = _combined_hash(monolithic_hashes)

        shard_steps: list[dict[str, object]] = []
        shard_apply_ok = True
        for index, rel in enumerate(shard_series, start=1):
            patch_path = shard_root / rel
            check_ok, check_summary = _run_apply(shard_root, patch_path, check_only=True)
            apply_ok = False
            apply_summary = ''
            after_hashes: dict[str, str] = _snapshot_hashes(shard_root, target_files)
            after_combined = _combined_hash(after_hashes)
            if check_ok:
                apply_ok, apply_summary = _run_apply(shard_root, patch_path, check_only=False)
                after_hashes = _snapshot_hashes(shard_root, target_files)
                after_combined = _combined_hash(after_hashes)
            else:
                shard_apply_ok = False
            if not apply_ok:
                shard_apply_ok = False
            entry = shards_report['entries'][index - 1]
            shard_steps.append({
                'series_index': index,
                'patch_path': rel,
                'seed_path': str(entry['seed_path']),
                'lane_mix': str(entry['lane_mix']),
                'lift_bands': list(entry['lift_bands']),
                'target_files': list(entry['target_files']),
                'check_ok': check_ok,
                'apply_ok': apply_ok,
                'check_summary': check_summary,
                'apply_summary': apply_summary,
                'after_hashes': after_hashes,
                'after_combined_hash': after_combined,
            })

        shard_hashes = _snapshot_hashes(shard_root, target_files)
        shard_combined = _combined_hash(shard_hashes)

    final_state_equivalent = bool(monolithic_hashes) and monolithic_hashes == shard_hashes
    differing_files = sorted(rel for rel in target_files if monolithic_hashes.get(rel) != shard_hashes.get(rel))

    return {
        'metadata': {
            'inventory_version': '2026-03-23.rust_external_test_patch_rehearsal.v1',
            'crate': 'gr_engine',
            'source_reports': [
                PATCHSET_JSON.relative_to(ROOT).as_posix(),
                SHARDS_JSON.relative_to(ROOT).as_posix(),
            ],
            'source_patchset': PATCHSET_PATCH.relative_to(ROOT).as_posix(),
            'source_shards': shard_series,
        },
        'summary': {
            'target_file_count': len(target_files),
            'shard_count': len(shard_steps),
            'monolithic_check_ok': mono_check_ok,
            'monolithic_apply_ok': mono_apply_ok,
            'shard_series_apply_ok': shard_apply_ok,
            'final_state_equivalent': final_state_equivalent,
            'equivalent_file_count': sum(1 for rel in target_files if monolithic_hashes.get(rel) == shard_hashes.get(rel)),
            'differing_file_count': len(differing_files),
            'baseline_combined_hash': baseline_combined,
            'monolithic_combined_hash': monolithic_combined,
            'shard_combined_hash': shard_combined,
        },
        'targets': {
            'files': target_files,
            'baseline_hashes': baseline_hashes,
            'monolithic_final_hashes': monolithic_hashes,
            'shard_final_hashes': shard_hashes,
            'differing_files': differing_files,
        },
        'rehearsal': {
            'monolithic': {
                'check_ok': mono_check_ok,
                'apply_ok': mono_apply_ok,
                'check_summary': mono_check_summary,
                'apply_summary': mono_apply_summary,
                'patch_bytes': len(patchset_text.encode('utf-8')),
                'patch_sha256': _sha256_text(patchset_text),
                'apply_hint': str(patchset_report['summary']['patch_hunks']) + ' hunks via git apply artifacts/patches/rust_external_test_patchset.patch',
            },
            'shards': {
                'apply_ok': shard_apply_ok,
                'steps': shard_steps,
                'cumulative_apply_hint': str(shards_report['summary']['cumulative_apply_hint']),
            },
        },
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report['summary']
    targets = report['targets']
    monolithic = report['rehearsal']['monolithic']
    shards = report['rehearsal']['shards']
    lines = [
        '# Rust External Test Patch Rehearsal',
        '',
        'Generated by `scripts/report/build_rust_external_test_patch_rehearsal.py`. This rehearses the blocked-Rust comeback patchset on scratch copies of the target files, then replays the cumulative shard series and compares the final file states.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- target_file_count: {summary['target_file_count']}",
        f"- shard_count: {summary['shard_count']}",
        f"- monolithic_check_ok: {str(summary['monolithic_check_ok']).lower()}",
        f"- monolithic_apply_ok: {str(summary['monolithic_apply_ok']).lower()}",
        f"- shard_series_apply_ok: {str(summary['shard_series_apply_ok']).lower()}",
        f"- final_state_equivalent: {str(summary['final_state_equivalent']).lower()}",
        f"- differing_file_count: {summary['differing_file_count']}",
        '',
        '## Combined hashes',
        '',
        f"- baseline_combined_hash: `{summary['baseline_combined_hash']}`",
        f"- monolithic_combined_hash: `{summary['monolithic_combined_hash']}`",
        f"- shard_combined_hash: `{summary['shard_combined_hash']}`",
        '',
        '## Target files',
        '',
    ]
    for rel in targets['files']:
        lines.append(f"- `{rel}`")
    lines.extend([
        '',
        '## Monolithic patchset rehearsal',
        '',
        f"- check_ok: {str(monolithic['check_ok']).lower()}",
        f"- apply_ok: {str(monolithic['apply_ok']).lower()}",
        f"- patch_sha256: `{monolithic['patch_sha256']}`",
        f"- apply_hint: `{monolithic['apply_hint']}`",
        '',
        '## Shard series rehearsal',
        '',
        f"- apply_ok: {str(shards['apply_ok']).lower()}",
        f"- cumulative_apply_hint: `{shards['cumulative_apply_hint']}`",
        '',
        '| shard | seed | lane_mix | check_ok | apply_ok | combined_hash |',
        '| --- | --- | --- | --- | --- | --- |',
    ])
    for step in shards['steps']:
        lines.append(
            f"| {step['series_index']} | `{step['seed_path']}` | `{step['lane_mix']}` | {str(step['check_ok']).lower()} | {str(step['apply_ok']).lower()} | `{step['after_combined_hash']}` |"
        )
    lines.extend(['', '## Final-state comparison', ''])
    if targets['differing_files']:
        lines.append('The monolithic patchset and cumulative shard series do **not** land on identical final target files:')
        lines.append('')
        for rel in targets['differing_files']:
            lines.append(f'- `{rel}`')
    else:
        lines.append('The monolithic patchset and cumulative shard series land on identical final target files for every rehearsed target.')
    lines.append('')
    return '\n'.join(lines)


def write_outputs(report: dict[str, object]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_markdown(report), encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the generated rehearsal outputs')
    args = parser.parse_args(argv)

    try:
        report = build_report()
    except FileNotFoundError as exc:
        print(f'rust-external-test-patch-rehearsal: {exc}', file=sys.stderr)
        return 1
    rendered = render_markdown(report)
    payload = json.dumps(report, indent=2, sort_keys=True) + '\n'

    if args.write:
        write_outputs(report)
        print(f'rust-external-test-patch-rehearsal: wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'rust-external-test-patch-rehearsal: wrote {OUT_MD.relative_to(ROOT)}')
        return 0

    missing = [path.relative_to(ROOT).as_posix() for path in [OUT_JSON, OUT_MD] if not path.exists()]
    if missing:
        for rel in missing:
            print(f'rust-external-test-patch-rehearsal: missing {rel}', file=sys.stderr)
        return 1

    stale = False
    if OUT_JSON.read_text(encoding='utf-8') != payload:
        print('rust-external-test-patch-rehearsal: JSON output is stale; run with --write', file=sys.stderr)
        stale = True
    if OUT_MD.read_text(encoding='utf-8') != rendered:
        print('rust-external-test-patch-rehearsal: Markdown output is stale; run with --write', file=sys.stderr)
        stale = True
    if stale:
        return 1

    print(
        'rust-external-test-patch-rehearsal: ok '
        f"(equivalent={str(report['summary']['final_state_equivalent']).lower()} shards={report['summary']['shard_count']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
