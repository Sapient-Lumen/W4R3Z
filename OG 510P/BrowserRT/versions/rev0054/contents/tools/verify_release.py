#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

NAME_RE = re.compile(r'^BrowserRT-(rev\d{4})-(\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.zip$')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(msg: str) -> None:
    print(f'[verify_release] FAIL: {msg}')
    raise SystemExit(1)


def verify(path: Path) -> None:
    m = NAME_RE.match(path.name)
    if not m:
        fail(f'bad BrowserRT release filename: {path.name}')
    with ZipFile(path) as zf:
        names = zf.namelist()
        if 'RELEASE-MANIFEST.json' not in names:
            fail('missing RELEASE-MANIFEST.json')
        manifest = json.loads(zf.read('RELEASE-MANIFEST.json').decode('utf-8'))
        if manifest.get('archive_name') != path.name:
            fail('manifest archive_name does not match filename')
        if manifest.get('revision') != m.group(1):
            fail('manifest revision does not match filename')
        if manifest.get('packaging_timestamp') != m.group(2):
            fail('manifest timestamp does not match filename')
        if manifest.get('slug') != m.group(3):
            fail('manifest slug does not match filename')
        file_rows = manifest.get('files')
        if not isinstance(file_rows, list) or not file_rows:
            fail('manifest files list missing')
        manifest_paths = {row['path'] for row in file_rows}
        zip_paths = set(names) - {'RELEASE-MANIFEST.json'}
        if manifest_paths != zip_paths:
            missing = sorted(zip_paths - manifest_paths)[:5]
            extra = sorted(manifest_paths - zip_paths)[:5]
            fail(f'manifest path mismatch missing={missing} extra={extra}')
        for row in file_rows:
            data = zf.read(row['path'])
            if len(data) != row['size']:
                fail(f'size mismatch for {row["path"]}')
            if sha256(data) != row['sha256']:
                fail(f'sha256 mismatch for {row["path"]}')
        for info in zf.infolist():
            if info.date_time[5] != 0:
                fail(f'non-normalized seconds for {info.filename}')
    print(f'[verify_release] OK: {path}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: verify_release.py /path/to/BrowserRT-rev####-YYYY.MM.DD.HH.MM-slug.zip')
    verify(Path(sys.argv[1]))
