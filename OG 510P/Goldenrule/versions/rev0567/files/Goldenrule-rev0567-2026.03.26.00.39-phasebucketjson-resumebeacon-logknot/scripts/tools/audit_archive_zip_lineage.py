#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCAN_DIR_CANDIDATES = [Path('/mnt/data'), ROOT.parent]
ROOT_RE = re.compile(
    r'^Goldenrule-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<descriptor>.+)$'
)
ZIP_RE = re.compile(
    r'^Goldenrule-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<descriptor>.+)\.zip$'
)


def _default_scan_dir() -> Path:
    for candidate in SCAN_DIR_CANDIDATES:
        if not candidate.exists() or not candidate.is_dir():
            continue
        for path in candidate.iterdir():
            if path.is_file() and ZIP_RE.match(path.name):
                return candidate.resolve()
    for candidate in SCAN_DIR_CANDIDATES:
        if candidate.exists() and candidate.is_dir():
            return candidate.resolve()
    return ROOT.parent.resolve()


def parse_root_identity(root_name: str) -> dict[str, Any]:
    match = ROOT_RE.match(root_name)
    if not match:
        raise ValueError(f'root name does not match archive naming pattern: {root_name}')
    revision = int(match.group('revision'))
    stamp = match.group('stamp')
    return {
        'root_name': root_name,
        'revision': revision,
        'revision_label': f'rev{revision:04d}',
        'timestamp': stamp,
        'descriptor_slug': match.group('descriptor'),
        'expected_zip_name': f'{root_name}.zip',
    }


def scan_zip_lineage(scan_dir: Path, root_name: str = ROOT.name) -> dict[str, Any]:
    identity = parse_root_identity(root_name)
    zips: list[dict[str, Any]] = []
    for path in sorted(scan_dir.iterdir(), key=lambda p: p.name):
        if not path.is_file() or path.suffix != '.zip':
            continue
        match = ZIP_RE.match(path.name)
        if not match:
            continue
        revision = int(match.group('revision'))
        stem = path.name[:-4]
        zips.append(
            {
                'zip_name': path.name,
                'root_stem': stem,
                'revision': revision,
                'revision_label': f'rev{revision:04d}',
                'timestamp': match.group('stamp'),
                'descriptor_slug': match.group('descriptor'),
                'size_bytes': path.stat().st_size,
            }
        )

    zips_sorted = sorted(zips, key=lambda row: (row['revision'], row['timestamp'], row['zip_name']))
    revision_groups: dict[str, list[dict[str, Any]]] = {}
    for row in zips_sorted:
        revision_groups.setdefault(row['revision_label'], []).append(row)

    duplicates = [
        {
            'revision_label': revision_label,
            'count': len(rows),
            'zip_names': [row['zip_name'] for row in rows],
            'timestamps': [row['timestamp'] for row in rows],
        }
        for revision_label, rows in revision_groups.items()
        if len(rows) > 1
    ]
    authoritative_head = zips_sorted[-1] if zips_sorted else None
    exact_current = next((row for row in zips_sorted if row['root_stem'] == identity['root_name']), None)
    predecessor = next((row for row in reversed(zips_sorted) if row['revision'] < identity['revision']), None)
    tail = [
        {
            'revision_label': row['revision_label'],
            'timestamp': row['timestamp'],
            'zip_name': row['zip_name'],
        }
        for row in zips_sorted[-8:]
    ]
    return {
        'tool': 'audit_archive_zip_lineage',
        'scan_dir': scan_dir.as_posix(),
        'current_archive': identity,
        'zip_count': len(zips_sorted),
        'revision_count': len(revision_groups),
        'exact_current_zip_present': exact_current is not None,
        'exact_current_zip_name': exact_current['zip_name'] if exact_current else None,
        'current_root_vs_external_head_aligned': bool(authoritative_head and authoritative_head['root_stem'] == identity['root_name']),
        'authoritative_external_head': authoritative_head,
        'immediate_predecessor_zip': predecessor,
        'duplicate_revision_rows': duplicates,
        'duplicate_revision_count': len(duplicates),
        'tail': tail,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit sibling Golden Rule archive zip lineage in a scan directory.')
    parser.add_argument('--scan-dir', default=_default_scan_dir().as_posix(), help='directory containing sibling Golden Rule revision zip files')
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir).expanduser().resolve()
    try:
        if not scan_dir.exists():
            raise FileNotFoundError(scan_dir)
        if not scan_dir.is_dir():
            raise NotADirectoryError(scan_dir)
        payload = scan_zip_lineage(scan_dir)
    except Exception as exc:  # noqa: BLE001
        print(f'audit-archive-zip-lineage: {exc}', file=sys.stderr)
        return 1
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
