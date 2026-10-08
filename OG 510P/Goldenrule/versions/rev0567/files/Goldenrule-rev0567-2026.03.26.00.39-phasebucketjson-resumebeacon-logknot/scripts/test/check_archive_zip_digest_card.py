#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / 'artifacts' / 'reports' / 'archive_zip_digest_card.json'
MD_PATH = ROOT / 'docs' / 'ARCHIVE_ZIP_DIGEST_CARD.md'


def fail(message: str) -> int:
    print(f'archive-zip-digest-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    if not JSON_PATH.exists():
        return fail('missing report json')
    if not MD_PATH.exists():
        return fail('missing markdown doc')
    report = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    if report.get('card') != 'archive_zip_digest_card':
        return fail('card id mismatch')
    selected = report.get('selected_zip')
    if not isinstance(selected, dict):
        return fail('selected_zip missing')
    for key in ['zip_name', 'zip_path', 'matches_current_root_zip', 'embedded_digest_stable']:
        if key not in selected:
            return fail(f'missing selected_zip field: {key}')
    path = Path(selected['zip_path'])
    if not path.exists():
        return fail('selected zip path does not exist')
    if path.name != selected['zip_name']:
        return fail('zip name/path mismatch')

    sha_proc = subprocess.run(
        ['python3', 'scripts/tools/inspect_authoritative_archive_zip.py', '--emit', 'sha256'],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if sha_proc.returncode != 0:
        if sha_proc.stdout:
            print(sha_proc.stdout, end='', file=sys.stderr)
        if sha_proc.stderr:
            print(sha_proc.stderr, end='', file=sys.stderr)
        return fail('emit sha256 command failed')

    if report.get('stewardship', {}).get('verify_zip_command') != 'python3 scripts/tools/verify_authoritative_archive_zip.py':
        return fail('verify zip command drifted')

    if selected['matches_current_root_zip']:
        if selected.get('embedded_digest_stable') is not False:
            return fail('current-root zip must not claim embedded stable digest')
        if selected.get('embedded_sha256') is not None or selected.get('embedded_size_bytes') is not None:
            return fail('current-root zip must not embed self-referential digest or size')
        if selected.get('live_emit_sha256_command') != 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256':
            return fail('live emit sha256 command drifted')
        if len(sha_proc.stdout.strip()) != 64:
            return fail('live sha256 output malformed')
    else:
        if selected.get('embedded_digest_stable') is not True:
            return fail('non-current authoritative zip should embed stable digest')
        if len(str(selected.get('embedded_sha256', ''))) != 64:
            return fail('embedded sha256 must be 64 hex chars')
        if path.stat().st_size != selected['embedded_size_bytes']:
            return fail('embedded size bytes mismatch')
        if sha_proc.stdout.strip() != selected['embedded_sha256']:
            return fail('embedded sha256 drifted')

    verify_proc = subprocess.run(
        ['python3', 'scripts/tools/verify_authoritative_archive_zip.py', '--emit', 'status'],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if verify_proc.returncode != 0 or verify_proc.stdout.strip() != 'ok':
        return fail('authoritative zip verifier drifted')

    print(f"archive-zip-digest-card: ok ({selected['zip_name']} stable={selected['embedded_digest_stable']})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
