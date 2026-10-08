#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REDUNDANT_PATTERNS = (
    'validation/*.zip',
    'validation/*/*.zip',
    'validation/*.patch',
    'validation/*/*.patch',
)
ARCHIVE_NAME_RE = re.compile(r'^GlassTTY-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<slug>.+)$')


def display_path(path: Path, *, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def file_size(path: Path) -> int:
    return path.stat().st_size if path.exists() else 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def collect_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob('*') if path.is_file())


def parse_archive_name(value: str) -> dict[str, Any]:
    match = ARCHIVE_NAME_RE.match(value)
    info: dict[str, Any] = {'archive_name': value, 'matches_pattern': bool(match)}
    if not match:
        return info
    info['archive_revision'] = int(match.group('revision'))
    info['archive_created_at_from_name'] = match.group('stamp')
    info['archive_slug'] = match.group('slug')
    return info


def audit_identity(root: Path) -> dict[str, Any]:
    worktree = parse_archive_name(root.name)
    manifest_path = root / 'ARCHIVE_MANIFEST.json'
    manifest: dict[str, Any] | None = None
    issues: list[str] = []
    if manifest_path.exists():
        try:
            loaded = json.loads(manifest_path.read_text(encoding='utf-8'))
        except Exception as exc:
            issues.append(f'failed to parse ARCHIVE_MANIFEST.json: {exc}')
        else:
            if isinstance(loaded, dict):
                manifest = loaded
            else:
                issues.append('ARCHIVE_MANIFEST.json is not a JSON object')
    else:
        issues.append('ARCHIVE_MANIFEST.json is missing')

    manifest_info: dict[str, Any] = {}
    if manifest is not None:
        for key in ('archive_name', 'archive_revision', 'archive_created_at_from_name', 'archive_slug', 'worktree_name'):
            if key in manifest:
                manifest_info[key] = manifest[key]
        archive_name = manifest.get('archive_name')
        if isinstance(archive_name, str):
            parsed_manifest = parse_archive_name(archive_name)
            manifest_info['parsed_archive_name'] = parsed_manifest
            if archive_name != root.name:
                issues.append(f'manifest archive_name {archive_name!r} does not match worktree {root.name!r}')
            for key in ('archive_revision', 'archive_created_at_from_name', 'archive_slug'):
                expected = parsed_manifest.get(key)
                actual = manifest.get(key)
                if expected is not None and actual != expected:
                    issues.append(f'manifest {key} {actual!r} does not match archive_name-derived {expected!r}')
        elif worktree.get('matches_pattern'):
            issues.append('manifest archive_name missing or not a string for archive-shaped worktree')

    if worktree.get('matches_pattern'):
        for key in ('archive_revision', 'archive_created_at_from_name', 'archive_slug'):
            actual = manifest_info.get(key)
            expected = worktree.get(key)
            if actual is not None and expected is not None and actual != expected:
                issues.append(f'manifest {key} {actual!r} does not match worktree-derived {expected!r}')

    return {
        'worktree': worktree,
        'manifest': manifest_info,
        'issues': issues,
        'ok': not issues,
    }


def top_level_sizes(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if child.is_dir():
            size = sum(file_size(path) for path in child.rglob('*') if path.is_file())
            count = sum(1 for path in child.rglob('*') if path.is_file())
        elif child.is_file():
            size = file_size(child)
            count = 1
        else:
            continue
        rows.append({'path': display_path(child, root=root), 'size_bytes': size, 'file_count': count})
    return sorted(rows, key=lambda row: row['size_bytes'], reverse=True)


def largest_files(root: Path, *, limit: int) -> list[dict[str, Any]]:
    rows = [
        {'path': display_path(path, root=root), 'size_bytes': file_size(path)}
        for path in collect_files(root)
    ]
    return sorted(rows, key=lambda row: row['size_bytes'], reverse=True)[:limit]


def duplicate_groups(root: Path, *, limit: int) -> list[dict[str, Any]]:
    by_size: dict[int, list[Path]] = defaultdict(list)
    for path in collect_files(root):
        by_size[file_size(path)].append(path)
    groups: list[dict[str, Any]] = []
    for size, paths in by_size.items():
        if size == 0 or len(paths) < 2:
            continue
        by_hash: dict[str, list[Path]] = defaultdict(list)
        for path in paths:
            by_hash[sha256_file(path)].append(path)
        for digest, dupes in by_hash.items():
            if len(dupes) < 2:
                continue
            groups.append(
                {
                    'sha256': digest,
                    'size_bytes_each': size,
                    'duplicate_count': len(dupes),
                    'wasted_bytes': size * (len(dupes) - 1),
                    'paths': [display_path(path, root=root) for path in sorted(dupes)],
                }
            )
    return sorted(groups, key=lambda row: (row['wasted_bytes'], row['size_bytes_each']), reverse=True)[:limit]


def redundant_candidates(root: Path) -> list[dict[str, Any]]:
    matched: dict[str, Path] = {}
    for pattern in REDUNDANT_PATTERNS:
        for path in root.glob(pattern):
            if path.is_file():
                matched[str(path)] = path
    rows = [
        {'path': display_path(path, root=root), 'size_bytes': file_size(path)}
        for path in matched.values()
    ]
    return sorted(rows, key=lambda row: row['size_bytes'], reverse=True)


def build_report(root: Path, *, top_files_limit: int = 20, duplicate_limit: int = 10) -> dict[str, Any]:
    files = collect_files(root)
    return {
        'root': str(root),
        'identity': audit_identity(root),
        'total_file_count': len(files),
        'total_bytes': sum(file_size(path) for path in files),
        'top_level_sizes': top_level_sizes(root)[:12],
        'largest_files': largest_files(root, limit=top_files_limit),
        'duplicate_groups': duplicate_groups(root, limit=duplicate_limit),
        'redundant_validation_candidates': redundant_candidates(root),
        'suggested_package_excludes': list(REDUNDANT_PATTERNS),
        'generated_by': 'scripts/archive-audit.py',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Audit GlassTTY archive size hotspots and likely redundant artifacts')
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_report(root)
    print(json.dumps(report, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
