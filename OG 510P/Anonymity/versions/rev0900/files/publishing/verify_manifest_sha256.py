#!/usr/bin/env python3
"""Verify MANIFEST.sha256 against the files it lists."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys


def parse_manifest_sha256(path: pathlib.Path) -> list[tuple[str, str]]:
    entries = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        parts = line.split('  ', 1)
        if len(parts) != 2:
            raise ValueError(f'malformed MANIFEST.sha256 line: {line!r}')
        entries.append((parts[0], parts[1]))
    return entries


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify(root: pathlib.Path) -> dict:
    release = json.loads((root / 'RELEASE_MANIFEST.json').read_text(encoding='utf-8'))
    missing = []
    mismatched = []
    verified = 0
    entries = parse_manifest_sha256(root / 'MANIFEST.sha256')
    for expected, rel in entries:
        path = root / rel
        if not path.exists():
            missing.append(rel)
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatched.append({'path': rel, 'expected': expected, 'actual': actual})
        else:
            verified += 1
    return {
        'status': 'pass' if not missing and not mismatched else 'fail',
        'generated_for_revision': release['revision'],
        'checked_bundle': release['bundle'],
        'publication_authorized': False,
        'checked_root': '.',
        'verified_entry_count': verified,
        'missing_paths': missing,
        'mismatched_paths': mismatched,
        'fail_closed_rule': 'If checksum verification fails, default to no publication and regenerate MANIFEST.sha256 before trusting archive integrity.'
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--write-report', default='')
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = verify(root)
    text = json.dumps(report, indent=2) + '\n'
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
