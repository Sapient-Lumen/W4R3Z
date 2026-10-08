#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_zip_chronology_card.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_ZIP_CHRONOLOGY_CARD.md'


def fail(message: str) -> int:
    print(f'archive-zip-chronology-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(['python3', 'scripts/report/build_archive_zip_chronology_card.py', '--write'], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout, end='', file=sys.stderr)
        print(proc.stderr, end='', file=sys.stderr)
        return fail('builder drifted or failed')

    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    if report.get('card') != 'archive_zip_chronology_card':
        return fail('card id mismatch')
    if report['adjacent_revision_timestamp_inversion_count'] != len(report['adjacent_revision_timestamp_inversions']):
        return fail('inversion count mismatch')
    if report['duplicate_revision_count'] != len(report['duplicate_revision_rows']):
        return fail('duplicate revision count mismatch')
    stewardship = report['stewardship']
    if stewardship['audit_command'] != 'python3 scripts/tools/audit_archive_zip_chronology.py':
        return fail('audit command drifted')

    tool_proc = subprocess.run(['python3', 'scripts/tools/audit_archive_zip_chronology.py'], cwd=ROOT, text=True, capture_output=True)
    if tool_proc.returncode != 0:
        print(tool_proc.stdout, end='', file=sys.stderr)
        print(tool_proc.stderr, end='', file=sys.stderr)
        return fail('chronology audit tool failed')
    tool_payload = json.loads(tool_proc.stdout)
    if tool_payload['current_archive']['root_name'] != report['current_archive']['root_name']:
        return fail('tool and card disagree on current root')
    if tool_payload['adjacent_revision_timestamp_inversion_count'] != report['adjacent_revision_timestamp_inversion_count']:
        return fail('tool and card disagree on inversion count')
    if tool_payload['revision_and_timestamp_heads_match'] != report['revision_and_timestamp_heads_match']:
        return fail('tool and card disagree on head match status')
    if report['tail_by_revision'] and len(report['tail_by_revision']) > 8:
        return fail('tail by revision should stay capped at eight rows')
    if report['tail_by_timestamp'] and len(report['tail_by_timestamp']) > 8:
        return fail('tail by timestamp should stay capped at eight rows')

    text = DOC_PATH.read_text(encoding='utf-8')
    for frag in [
        '# Archive Zip Chronology Card',
        '## Head comparison',
        '## Adjacent revision/timestamp inversions',
        '## Tail by timestamp',
        '`python3 scripts/tools/audit_archive_zip_chronology.py`',
    ]:
        if frag not in text:
            return fail(f'missing doc fragment: {frag}')
    print(
        'archive-zip-chronology-card: ok '
        f"(head_match={report['revision_and_timestamp_heads_match']} inversions={report['adjacent_revision_timestamp_inversion_count']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
