#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_zip_authority_card.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_ZIP_AUTHORITY_CARD.md'


def fail(message: str) -> int:
    print(f'archive-zip-authority-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(['python3', 'scripts/report/build_archive_zip_authority_card.py', '--write'], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout, end='', file=sys.stderr)
        print(proc.stderr, end='', file=sys.stderr)
        return fail('builder drifted or failed')

    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    if report.get('card') != 'archive_zip_authority_card':
        return fail('card id mismatch')
    if report['duplicate_revision_count'] != len(report['duplicate_revision_rows']):
        return fail('duplicate revision count mismatch')
    if report['adjacent_revision_timestamp_inversion_count'] != len(report['adjacent_revision_timestamp_inversions']):
        return fail('inversion count mismatch')
    stewardship = report['stewardship']
    if stewardship['resolve_command'] != 'python3 scripts/tools/resolve_authoritative_archive_zip.py':
        return fail('resolve command drifted')

    tool_proc = subprocess.run(['python3', 'scripts/tools/resolve_authoritative_archive_zip.py'], cwd=ROOT, text=True, capture_output=True)
    if tool_proc.returncode != 0:
        print(tool_proc.stdout, end='', file=sys.stderr)
        print(tool_proc.stderr, end='', file=sys.stderr)
        return fail('resolver tool failed')
    tool_payload = json.loads(tool_proc.stdout)
    if tool_payload['current_archive']['root_name'] != report['current_archive']['root_name']:
        return fail('tool and card disagree on current root')
    if tool_payload['recommended_resume']['selected_zip_name'] != stewardship['selected_zip_name']:
        return fail('tool and card disagree on selected zip')
    if tool_payload['adjacent_revision_timestamp_inversion_count'] != report['adjacent_revision_timestamp_inversion_count']:
        return fail('tool and card disagree on inversion count')

    if report['authoritative_external_head']:
        zip_path_proc = subprocess.run(
            ['python3', 'scripts/tools/resolve_authoritative_archive_zip.py', '--emit', 'zip-path'],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if zip_path_proc.returncode != 0:
            print(zip_path_proc.stdout, end='', file=sys.stderr)
            print(zip_path_proc.stderr, end='', file=sys.stderr)
            return fail('zip-path emit failed')
        if zip_path_proc.stdout.strip() != stewardship['selected_zip_path']:
            return fail('zip-path emit drifted')
        unzip_proc = subprocess.run(
            ['python3', 'scripts/tools/resolve_authoritative_archive_zip.py', '--emit', 'unzip-command'],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if unzip_proc.returncode != 0:
            print(unzip_proc.stdout, end='', file=sys.stderr)
            print(unzip_proc.stderr, end='', file=sys.stderr)
            return fail('unzip-command emit failed')
        if unzip_proc.stdout.strip() != stewardship['resume_unzip_command']:
            return fail('unzip-command emit drifted')
    text = DOC_PATH.read_text(encoding='utf-8')
    for frag in [
        '# Archive Zip Authority Card',
        '## Selected authoritative zip',
        '## Resolution rule',
        '## Recommended reopen commands',
        '`python3 scripts/tools/resolve_authoritative_archive_zip.py`',
        '`python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path`',
    ]:
        if frag not in text:
            return fail(f'missing doc fragment: {frag}')
    print(
        'archive-zip-authority-card: ok '
        f"(selected={stewardship['selected_zip_name'] or 'none'} inversions={report['adjacent_revision_timestamp_inversion_count']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
