#!/usr/bin/env python3
"""Build a manifest-bound, reproducible TimeSync release ZIP."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import stat
import sys
import zipfile

sys.dont_write_bytecode = True

from release_integrity import (  # noqa: E402
    ARCHIVE_RE,
    check_release_integrity,
    is_generated_path,
    load_receipt,
    validate_receipt,
)


def release_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f'symbolic links are forbidden in release source: {rel}')
        if not path.is_file():
            continue
        if rel == Path('MANIFEST.json'):
            continue
        if is_generated_path(rel):
            raise ValueError(f'generated artifact is forbidden in release source: {rel}')
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def write_manifest(root: Path, archive_root: str) -> None:
    receipt = load_receipt(root)
    entries = []
    for path in release_files(root):
        data = path.read_bytes()
        entries.append({
            'path': path.relative_to(root).as_posix(),
            'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
        })
    manifest = {
        'manifest_version': 'timesync-manifest-v2',
        'revision': receipt['revision'],
        'archive_root': archive_root,
        'files': entries,
    }
    (root / 'MANIFEST.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )


def _zip_datetime(issued_at: str) -> tuple[int, int, int, int, int, int]:
    parsed = datetime.fromisoformat(issued_at.replace('Z', '+00:00'))
    second = parsed.second - parsed.second % 2  # ZIP stores seconds at two-second resolution.
    return parsed.year, parsed.month, parsed.day, parsed.hour, parsed.minute, second


def _zip_info(name: str, timestamp: tuple[int, int, int, int, int, int], mode: int, *, directory: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=timestamp)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.flag_bits |= 0x800
    file_type = stat.S_IFDIR if directory else stat.S_IFREG
    info.external_attr = (file_type | mode) << 16
    if directory:
        info.external_attr |= 0x10
    return info


def write_zip(root: Path, output: Path, archive_root: str, issued_at: str) -> None:
    timestamp = _zip_datetime(issued_at)
    all_files = sorted(
        [root / 'MANIFEST.json', *release_files(root)],
        key=lambda path: path.relative_to(root).as_posix(),
    )
    directory_set: set[str] = set()
    for path in all_files:
        current = path.parent.relative_to(root)
        while current != Path('.'):
            directory_set.add(current.as_posix())
            current = current.parent
    directories = sorted(directory_set)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + '.tmp')
    temp.unlink(missing_ok=True)
    with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr(_zip_info(f'{archive_root}/', timestamp, 0o755, directory=True), b'')
        for rel_dir in directories:
            archive.writestr(_zip_info(f'{archive_root}/{rel_dir}/', timestamp, 0o755, directory=True), b'')
        for path in all_files:
            rel = path.relative_to(root).as_posix()
            data = path.read_bytes()
            mode = 0o755 if data.startswith(b'#!') else 0o644
            archive.writestr(_zip_info(f'{archive_root}/{rel}', timestamp, mode), data)
    temp.replace(output)


def build(root: Path, output: Path) -> None:
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError('release output must be outside the source tree')
    receipt = load_receipt(root)
    receipt_errors = validate_receipt(receipt)
    if receipt_errors:
        raise ValueError('; '.join(receipt_errors))
    if ARCHIVE_RE.fullmatch(output.name) is None:
        raise ValueError('output filename does not match required TimeSync release convention')
    if output.name != receipt.get('archive_filename'):
        raise ValueError('output filename must exactly match receipt archive_filename')
    archive_root = output.stem
    write_manifest(root, archive_root)
    integrity_errors = check_release_integrity(root)
    if integrity_errors:
        raise ValueError('; '.join(integrity_errors))
    write_zip(root, output, archive_root, receipt['issued_at'])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        build(args.root.resolve(), args.output.resolve())
    except Exception as exc:  # noqa: BLE001
        print(f'ERROR: {exc}')
        return 1
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f'Built {args.output.name}')
    print(f'sha256 {digest}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
