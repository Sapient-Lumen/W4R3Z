#!/usr/bin/env python3
"""Audit the exact ZIP intended for delivery, not a synthetic temporary archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('artifact', type=Path)
    ap.add_argument('--expected-root', required=True)
    ap.add_argument('--source-root', type=Path)
    ap.add_argument('--json-out', type=Path)
    ap.add_argument('--text-out', type=Path)
    args = ap.parse_args()

    checks = []
    def add(name: str, passed: bool, observed: object, detail: str) -> None:
        checks.append({'check': name, 'status': 'pass' if passed else 'fail', 'observed': observed, 'detail': detail})

    artifact = args.artifact.resolve()
    if not artifact.is_file():
        print(f'FAIL missing artifact: {artifact}', file=sys.stderr)
        return 2

    with zipfile.ZipFile(artifact, 'r') as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        names = [i.filename for i in infos]
        stored = [i.filename for i in infos if i.compress_type != zipfile.ZIP_DEFLATED]
        total_raw = sum(i.file_size for i in infos)
        total_comp = sum(i.compress_size for i in infos)
        roots = sorted({n.split('/', 1)[0] for n in names if '/' in n})
        nested_zips = [n for n in names if n.lower().endswith('.zip')]
        duplicate_names = sorted({n for n in names if names.count(n) > 1})

        add('artifact_has_members', bool(infos), len(infos), 'delivered ZIP must contain file members')
        add('all_file_members_deflated', not stored and bool(infos), len(stored), 'every file member must use ZIP_DEFLATED')
        add('compression_saves_bytes', total_raw > 0 and total_comp < total_raw, f'{total_comp}/{total_raw}', 'aggregate compressed bytes must be lower than uncompressed bytes')
        add('single_expected_root', roots == [args.expected_root], roots, 'all files must be rooted under the declared package directory')
        add('no_nested_zip_payload', not nested_zips, nested_zips[:10], 'release ZIP must not contain another ZIP')
        add('no_duplicate_member_names', not duplicate_names, duplicate_names[:10], 'ZIP member names must be unique')
        add('checksum_manifest_present', f'{args.expected_root}/SHA256SUMS.txt' in names, f'{args.expected_root}/SHA256SUMS.txt' in names, 'package must contain extracted-file checksum manifest')

        if args.source_root:
            source_root = args.source_root.resolve()
            source_files = sorted(p for p in source_root.rglob('*') if p.is_file())
            expected_names = [f'{args.expected_root}/{p.relative_to(source_root).as_posix()}' for p in source_files]
            add('member_set_matches_source_tree', names == expected_names, f'zip={len(names)} source={len(expected_names)}', 'sorted delivered members must exactly match the source tree')
            drift = []
            for p, name in zip(source_files, expected_names):
                if name not in names:
                    continue
                with zf.open(name, 'r') as f:
                    zh = hashlib.sha256()
                    for chunk in iter(lambda: f.read(1024 * 1024), b''):
                        zh.update(chunk)
                if zh.hexdigest() != sha256_file(p):
                    drift.append(name)
            add('member_hashes_match_source_tree', not drift, drift[:10], 'each ZIP member must match the built source tree byte-for-byte')

    result = {
        'artifact': str(artifact),
        'artifact_sha256': sha256_file(artifact),
        'artifact_size_bytes': artifact.stat().st_size,
        'expected_root': args.expected_root,
        'member_count': len(infos),
        'uncompressed_member_bytes': total_raw,
        'compressed_member_bytes': total_comp,
        'compression_ratio': (total_comp / total_raw) if total_raw else None,
        'all_pass': all(c['status'] == 'pass' for c in checks),
        'checks': checks,
    }
    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    text = [
        ('PASS' if result['all_pass'] else 'FAIL') + ' exact delivered ZIP audit',
        f"artifact={artifact}",
        f"sha256={result['artifact_sha256']}",
        f"size_bytes={result['artifact_size_bytes']}",
        f"members={result['member_count']}",
        f"compressed_member_bytes={total_comp}",
        f"uncompressed_member_bytes={total_raw}",
        f"compression_ratio={result['compression_ratio']:.6f}" if result['compression_ratio'] is not None else 'compression_ratio=n/a',
    ]
    text.extend(f"{c['status'].upper()} {c['check']} observed={c['observed']} — {c['detail']}" for c in checks)
    text_out = '\n'.join(text) + '\n'
    if args.text_out:
        args.text_out.write_text(text_out, encoding='utf-8')
    print(text_out, end='')
    return 0 if result['all_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
