#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_zip_lineage_card.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_ZIP_LINEAGE_CARD.md'


def fail(message: str) -> int:
    print(f'archive-zip-lineage-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(['python3', 'scripts/report/build_archive_zip_lineage_card.py', '--write'], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout, end='', file=sys.stderr)
        print(proc.stderr, end='', file=sys.stderr)
        return fail('builder drifted or failed')

    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    if report.get('card') != 'archive_zip_lineage_card':
        return fail('card id mismatch')
    current = report['current_archive']
    head = report['authoritative_external_head']
    duplicates = report['duplicate_revision_rows']
    stewardship = report['stewardship']
    if stewardship['audit_command'] != 'python3 scripts/tools/audit_archive_zip_lineage.py':
        return fail('audit command drifted')
    if report['duplicate_revision_count'] != len(duplicates):
        return fail('duplicate revision count mismatch')
    tool_proc = subprocess.run(['python3', 'scripts/tools/audit_archive_zip_lineage.py'], cwd=ROOT, text=True, capture_output=True)
    if tool_proc.returncode != 0:
        print(tool_proc.stdout, end='', file=sys.stderr)
        print(tool_proc.stderr, end='', file=sys.stderr)
        return fail('lineage audit tool failed')
    tool_payload = json.loads(tool_proc.stdout)
    if tool_payload['current_archive']['root_name'] != current['root_name']:
        return fail('tool and card disagree on current root')
    if tool_payload['duplicate_revision_count'] != report['duplicate_revision_count']:
        return fail('tool and card disagree on duplicate revision count')
    if report['tail'] and len(report['tail']) > 8:
        return fail('tail should stay capped at eight rows')
    if head:
        if not stewardship['exact_current_zip_present']:
            return fail('expected exact current zip to exist in sibling lineage')
        if head['revision'] < current['revision']:
            return fail('authoritative external head cannot trail current revision')
    text = DOC_PATH.read_text(encoding='utf-8')
    for frag in ['# Archive Zip Lineage Card', '## External zip authority', '## Duplicate revision labels among sibling zips', '`python3 scripts/tools/audit_archive_zip_lineage.py`', '`python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`']:
        if frag not in text:
            return fail(f'missing doc fragment: {frag}')
    print(
        'archive-zip-lineage-card: ok '
        f"(head={head['revision_label'] if head else 'none'} duplicates={report['duplicate_revision_count']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
