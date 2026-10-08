#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_byte_triage_card.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_BYTE_TRIAGE_CARD.md'


def fail(message: str) -> int:
    print(f'archive-byte-triage-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    for cmd in [
        ['python3', 'scripts/report/build_archive_size_guardrail_card.py'],
        ['python3', 'scripts/report/build_archive_byte_triage_card.py'],
    ]:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if proc.returncode != 0:
            if proc.stdout:
                print(proc.stdout, end='', file=sys.stderr)
            if proc.stderr:
                print(proc.stderr, end='', file=sys.stderr)
            return fail(f'builder drifted or failed: {" ".join(cmd)}')

    if not REPORT_PATH.exists():
        return fail('missing report json')
    if not DOC_PATH.exists():
        return fail('missing rendered doc')

    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    protected = report.get('protected_stack_totals', {})
    cap_pack = report.get('cap_first_markdown_pack_totals', {})
    cap_rows = report.get('cap_first_markdown_pack', [])
    next_rows = report.get('next_review_markdown_tier', [])
    guardrail = report.get('guardrail_reference', {})

    if protected.get('file_count', 0) <= 0:
        return fail('protected_stack_totals.file_count must be positive')
    if protected.get('raw_bytes', 0) <= 0:
        return fail('protected_stack_totals.raw_bytes must be positive')
    if guardrail.get('package_boundary_ready') is not True:
        return fail('guardrail package boundary must stay ready')
    if cap_pack.get('file_count', 0) <= 0:
        return fail('expected at least one cap-first markdown file')
    if cap_pack.get('recoverable_if_capped_at_128k_bytes', 0) <= 0:
        return fail('expected positive recoverable bytes in cap-first markdown pack')
    if len(cap_rows) < 3:
        return fail('expected at least three cap-first markdown rows')
    if any(row.get('raw_bytes', 0) <= 128 * 1024 for row in cap_rows):
        return fail('cap-first markdown pack contains a row at or below the cap')
    if sorted((row.get('raw_bytes', 0) for row in cap_rows), reverse=True) != [row.get('raw_bytes', 0) for row in cap_rows]:
        return fail('cap-first markdown rows are not sorted by descending raw_bytes')
    if any(row.get('path', '').startswith(('docs/RUST_', 'docs/CLOUDTAINER_')) for row in cap_rows):
        return fail('protected blocked-session docs leaked into the cap-first markdown pack')
    if any(row.get('raw_bytes', 0) > 128 * 1024 for row in next_rows):
        return fail('next review markdown tier contains a row above the cap')

    text = DOC_PATH.read_text(encoding='utf-8')
    required_fragments = [
        '# Archive Byte Triage Card',
        'package_boundary_ready: `True`',
        'Protected blocked-session handoff stack',
        'Cap-first markdown pack (>128 KiB)',
        'Next markdown review tier (64 KiB to 128 KiB)',
    ]
    missing = [frag for frag in required_fragments if frag not in text]
    if missing:
        return fail(f'missing required doc fragments: {missing}')

    print(
        'archive-byte-triage-card: ok '
        f"(protected_bytes={protected['raw_bytes']}, recoverable_bytes={cap_pack['recoverable_if_capped_at_128k_bytes']}, cap_files={cap_pack['file_count']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
