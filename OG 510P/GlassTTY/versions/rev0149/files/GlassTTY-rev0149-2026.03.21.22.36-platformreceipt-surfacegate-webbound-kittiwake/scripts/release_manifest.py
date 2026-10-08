#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_RE = re.compile(r'^GlassTTY-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<slug>.+)$')
MANIFEST_NAME = 'RELEASE-MANIFEST.json'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def parse_archive_name(value: str) -> dict[str, Any]:
    match = ARCHIVE_RE.match(value)
    if not match:
        return {'archive_name': value, 'matches_pattern': False}
    return {
        'archive_name': value,
        'matches_pattern': True,
        'revision': int(match.group('revision')),
        'packaging_timestamp': match.group('stamp'),
        'slug': match.group('slug'),
    }


def _files_for_manifest(package_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(package_root.rglob('*')):
        if not path.is_file():
            continue
        if path.name == MANIFEST_NAME:
            continue
        rel = str(path.relative_to(package_root))
        rows.append({
            'path': rel,
            'size': path.stat().st_size,
            'sha256': sha256_file(path),
        })
    return rows


def build_release_manifest(*, package_root: Path, archive_name: str) -> dict[str, Any]:
    parsed = parse_archive_name(archive_name)
    archive_manifest = _read_json(package_root / 'ARCHIVE_MANIFEST.json') or {}
    revision = parsed.get('revision', archive_manifest.get('archive_revision'))
    packaging_timestamp = parsed.get('packaging_timestamp', archive_manifest.get('archive_created_at_from_name'))
    files = _files_for_manifest(package_root)
    return {
        'manifest_version': 1,
        'archive_name': archive_name,
        'archive_root': package_root.name,
        'revision': revision,
        'packaging_timestamp': packaging_timestamp,
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'file_count': len(files),
        'files': files,
    }


def write_release_manifest(*, package_root: Path, archive_name: str) -> dict[str, Any]:
    payload = build_release_manifest(package_root=package_root, archive_name=archive_name)
    target = package_root / MANIFEST_NAME
    target.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Write a self-describing release manifest for a packaged GlassTTY tree.')
    parser.add_argument('--package-root', required=True)
    parser.add_argument('--archive-name', required=True)
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    payload = write_release_manifest(package_root=Path(args.package_root), archive_name=args.archive_name)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
