#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Any

from audit_archive_zip_chronology import audit_zip_chronology
from audit_archive_zip_lineage import _default_scan_dir, scan_zip_lineage

ROOT = Path(__file__).resolve().parents[2]


def resolve_authoritative_archive_zip(scan_dir: Path, root_name: str = ROOT.name) -> dict[str, Any]:
    lineage = scan_zip_lineage(scan_dir, root_name=root_name)
    chronology = audit_zip_chronology(scan_dir, root_name=root_name)
    head = lineage['authoritative_external_head']
    timestamp_head = chronology['latest_by_timestamp']
    selected_zip_path = (scan_dir / head['zip_name']).resolve() if head else None
    selected_root_stem = head['root_stem'] if head else None

    selection_trace: list[str] = [
        'scan sibling Golden Rule revision zips in the configured directory',
        'choose the highest revision label as archive head',
        'if a revision label is duplicated, break ties by timestamp inside that revision label only',
    ]
    if chronology['adjacent_revision_timestamp_inversion_count']:
        selection_trace.append(
            'do not let a later timestamp from a lower revision outrank a higher revision label because chronology inversions exist'
        )
    if lineage['duplicate_revision_count']:
        selection_trace.append('do not let duplicated revision labels collapse authority; keep timestamp tie-breaking inside the duplicated label only')

    if head is None:
        recommended = {
            'selected_zip_path': None,
            'selected_zip_name': None,
            'selected_root_stem': None,
            'resume_unzip_command': None,
            'resume_reason': 'no sibling Golden Rule revision zips were found in the scan directory',
        }
    else:
        quoted_zip = shlex.quote(selected_zip_path.as_posix())
        recommended = {
            'selected_zip_path': selected_zip_path.as_posix(),
            'selected_zip_name': head['zip_name'],
            'selected_root_stem': selected_root_stem,
            'resume_unzip_command': f'mkdir -p /path/to/workdir && unzip -q {quoted_zip} -d /path/to/workdir',
            'resume_reason': (
                'selected by highest revision label, with timestamp used only inside a duplicated revision label'
            ),
        }

    return {
        'tool': 'resolve_authoritative_archive_zip',
        'scan_dir': scan_dir.as_posix(),
        'current_archive': lineage['current_archive'],
        'authoritative_external_head': head,
        'latest_by_timestamp': timestamp_head,
        'immediate_predecessor_zip': lineage['immediate_predecessor_zip'],
        'exact_current_zip_present': lineage['exact_current_zip_present'],
        'current_root_vs_authoritative_head_aligned': lineage['current_root_vs_external_head_aligned'],
        'timestamp_head_matches_authoritative_head': bool(
            head and timestamp_head and head['zip_name'] == timestamp_head['zip_name']
        ),
        'duplicate_revision_rows': chronology['duplicate_revision_rows'],
        'duplicate_revision_count': chronology['duplicate_revision_count'],
        'adjacent_revision_timestamp_inversions': chronology['adjacent_revision_timestamp_inversions'],
        'adjacent_revision_timestamp_inversion_count': chronology['adjacent_revision_timestamp_inversion_count'],
        'authority_rule': chronology['authority_rule'],
        'selection_trace': selection_trace,
        'recommended_resume': recommended,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Resolve the authoritative sibling Golden Rule revision zip to reopen when duplicate revisions or timestamp inversions exist.')
    parser.add_argument('--scan-dir', default=_default_scan_dir().as_posix(), help='directory containing sibling Golden Rule revision zip files')
    parser.add_argument(
        '--emit',
        choices=['json', 'zip-path', 'zip-name', 'root-stem', 'unzip-command'],
        default='json',
        help='emit either the full JSON payload or a single selected field',
    )
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir).expanduser().resolve()
    try:
        if not scan_dir.exists():
            raise FileNotFoundError(scan_dir)
        if not scan_dir.is_dir():
            raise NotADirectoryError(scan_dir)
        payload = resolve_authoritative_archive_zip(scan_dir)
    except Exception as exc:  # noqa: BLE001
        print(f'resolve-authoritative-archive-zip: {exc}', file=sys.stderr)
        return 1

    if args.emit == 'json':
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write('\n')
        return 0

    recommended = payload['recommended_resume']
    field_map = {
        'zip-path': recommended['selected_zip_path'],
        'zip-name': recommended['selected_zip_name'],
        'root-stem': recommended['selected_root_stem'],
        'unzip-command': recommended['resume_unzip_command'],
    }
    value = field_map[args.emit]
    if value is None:
        print('resolve-authoritative-archive-zip: no authoritative sibling zip is currently available', file=sys.stderr)
        return 1
    print(value)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
