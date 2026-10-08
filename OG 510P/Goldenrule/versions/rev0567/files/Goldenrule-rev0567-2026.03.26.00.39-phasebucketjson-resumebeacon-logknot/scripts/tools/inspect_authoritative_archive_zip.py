#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from audit_archive_zip_lineage import _default_scan_dir
from resolve_authoritative_archive_zip import resolve_authoritative_archive_zip


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def inspect_authoritative_archive_zip(scan_dir: Path) -> dict[str, Any]:
    resolved = resolve_authoritative_archive_zip(scan_dir)
    recommended = resolved['recommended_resume']
    selected_path_str = recommended['selected_zip_path']
    if selected_path_str is None:
        return {
            'tool': 'inspect_authoritative_archive_zip',
            'scan_dir': scan_dir.as_posix(),
            'resolved': resolved,
            'selected_zip': None,
        }
    selected_path = Path(selected_path_str)
    if not selected_path.exists():
        raise FileNotFoundError(selected_path)
    stat = selected_path.stat()
    selected = {
        'zip_name': selected_path.name,
        'zip_path': selected_path.as_posix(),
        'sha256': _sha256(selected_path),
        'size_bytes': stat.st_size,
        'mtime_epoch_seconds': stat.st_mtime,
    }
    return {
        'tool': 'inspect_authoritative_archive_zip',
        'scan_dir': scan_dir.as_posix(),
        'resolved': resolved,
        'selected_zip': selected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Inspect the authoritative sibling Golden Rule revision zip and emit its digest and size.')
    parser.add_argument('--scan-dir', default=_default_scan_dir().as_posix(), help='directory containing sibling Golden Rule revision zip files')
    parser.add_argument('--emit', choices=['json', 'zip-path', 'zip-name', 'sha256', 'size-bytes'], default='json')
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir).expanduser().resolve()
    try:
        if not scan_dir.exists():
            raise FileNotFoundError(scan_dir)
        if not scan_dir.is_dir():
            raise NotADirectoryError(scan_dir)
        payload = inspect_authoritative_archive_zip(scan_dir)
    except Exception as exc:  # noqa: BLE001
        print(f'inspect-authoritative-archive-zip: {exc}', file=sys.stderr)
        return 1

    if args.emit == 'json':
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write('\n')
        return 0

    selected = payload['selected_zip']
    if selected is None:
        print('inspect-authoritative-archive-zip: no authoritative sibling zip is currently available', file=sys.stderr)
        return 1
    field = {
        'zip-path': selected['zip_path'],
        'zip-name': selected['zip_name'],
        'sha256': selected['sha256'],
        'size-bytes': str(selected['size_bytes']),
    }[args.emit]
    print(field)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
