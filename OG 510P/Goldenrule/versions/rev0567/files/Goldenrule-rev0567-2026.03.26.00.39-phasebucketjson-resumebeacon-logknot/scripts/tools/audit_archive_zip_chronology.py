#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from audit_archive_zip_lineage import ZIP_RE, _default_scan_dir, parse_root_identity

ROOT = Path(__file__).resolve().parents[2]


def _scan_rows(scan_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(scan_dir.iterdir(), key=lambda p: p.name):
        if not path.is_file() or path.suffix != '.zip':
            continue
        match = ZIP_RE.match(path.name)
        if not match:
            continue
        revision = int(match.group('revision'))
        rows.append(
            {
                'zip_name': path.name,
                'root_stem': path.name[:-4],
                'revision': revision,
                'revision_label': f'rev{revision:04d}',
                'timestamp': match.group('stamp'),
                'descriptor_slug': match.group('descriptor'),
                'size_bytes': path.stat().st_size,
            }
        )
    return rows


def audit_zip_chronology(scan_dir: Path, root_name: str = ROOT.name) -> dict[str, Any]:
    current = parse_root_identity(root_name)
    rows = _scan_rows(scan_dir)
    by_revision = sorted(rows, key=lambda row: (row['revision'], row['timestamp'], row['zip_name']))
    by_timestamp = sorted(rows, key=lambda row: (row['timestamp'], row['revision'], row['zip_name']))

    revision_groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in by_revision:
        revision_groups[row['revision_label']].append(row)

    duplicate_rows = [
        {
            'revision_label': label,
            'count': len(group),
            'zip_names': [row['zip_name'] for row in group],
            'timestamps': [row['timestamp'] for row in group],
        }
        for label, group in sorted(revision_groups.items())
        if len(group) > 1
    ]

    latest_by_revision = by_revision[-1] if by_revision else None
    latest_by_timestamp = by_timestamp[-1] if by_timestamp else None

    unique_revision_heads = [
        max(group, key=lambda row: (row['timestamp'], row['zip_name']))
        for _, group in sorted(revision_groups.items(), key=lambda item: item[1][0]['revision'])
    ]
    adjacent_inversions: list[dict[str, Any]] = []
    for prev, curr in zip(unique_revision_heads, unique_revision_heads[1:]):
        if curr['timestamp'] < prev['timestamp']:
            adjacent_inversions.append(
                {
                    'previous_revision_label': prev['revision_label'],
                    'previous_timestamp': prev['timestamp'],
                    'previous_zip_name': prev['zip_name'],
                    'current_revision_label': curr['revision_label'],
                    'current_timestamp': curr['timestamp'],
                    'current_zip_name': curr['zip_name'],
                }
            )

    tail_by_revision = [
        {
            'revision_label': row['revision_label'],
            'timestamp': row['timestamp'],
            'zip_name': row['zip_name'],
        }
        for row in unique_revision_heads[-8:]
    ]
    tail_by_timestamp = [
        {
            'revision_label': row['revision_label'],
            'timestamp': row['timestamp'],
            'zip_name': row['zip_name'],
        }
        for row in by_timestamp[-8:]
    ]

    return {
        'tool': 'audit_archive_zip_chronology',
        'scan_dir': scan_dir.as_posix(),
        'current_archive': current,
        'zip_count': len(rows),
        'unique_revision_count': len(unique_revision_heads),
        'duplicate_revision_rows': duplicate_rows,
        'duplicate_revision_count': len(duplicate_rows),
        'latest_by_revision': latest_by_revision,
        'latest_by_timestamp': latest_by_timestamp,
        'revision_and_timestamp_heads_match': bool(
            latest_by_revision and latest_by_timestamp and latest_by_revision['zip_name'] == latest_by_timestamp['zip_name']
        ),
        'adjacent_revision_timestamp_inversions': adjacent_inversions,
        'adjacent_revision_timestamp_inversion_count': len(adjacent_inversions),
        'authority_rule': 'prefer highest revision label for archive head; use timestamp only to order multiple zips that share the same revision label',
        'tail_by_revision': tail_by_revision,
        'tail_by_timestamp': tail_by_timestamp,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit whether sibling Golden Rule revision zips remain chronology-safe across revision labels and timestamps.')
    parser.add_argument('--scan-dir', default=_default_scan_dir().as_posix(), help='directory containing sibling Golden Rule revision zip files')
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir).expanduser().resolve()
    try:
        if not scan_dir.exists():
            raise FileNotFoundError(scan_dir)
        if not scan_dir.is_dir():
            raise NotADirectoryError(scan_dir)
        payload = audit_zip_chronology(scan_dir)
    except Exception as exc:  # noqa: BLE001
        print(f'audit-archive-zip-chronology: {exc}', file=sys.stderr)
        return 1
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
