#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_size_guardrail_card.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_SIZE_GUARDRAIL_CARD.md'


def fail(message: str) -> int:
    print(f'archive-size-guardrail-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(
        ['python3', 'scripts/report/build_archive_size_guardrail_card.py'],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end='', file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return fail('builder drifted or failed')

    if not REPORT_PATH.exists():
        return fail('missing report json')
    if not DOC_PATH.exists():
        return fail('missing rendered doc')

    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    totals = report.get('archive_totals', {})
    hygiene = report.get('package_hygiene', {})
    growth = report.get('top_level_growth', [])
    families = report.get('largest_report_families', [])

    if totals.get('retained_file_count', 0) <= 0:
        return fail('retained_file_count must be positive')
    if totals.get('raw_bytes', 0) <= 0:
        return fail('raw_bytes must be positive')
    if totals.get('approx_revision_zip_bytes', 0) <= 0:
        return fail('approx_revision_zip_bytes must be positive')
    if hygiene.get('pdf_count') != 0:
        return fail('expected pdf_count to stay zero at the package boundary')
    if hygiene.get('scratch_file_count') != 0:
        return fail('expected scratch_file_count to stay zero at the package boundary')
    if hygiene.get('package_boundary_ready') is not True:
        return fail('package_boundary_ready must be true when pdf/scratch counts are zero')
    if len(growth) < 3:
        return fail('expected at least three growth rows')
    if sorted((row.get('delta_raw_bytes', 0) for row in growth), reverse=True) != [row.get('delta_raw_bytes', 0) for row in growth]:
        return fail('growth rows are not sorted by descending delta_raw_bytes')
    if len(families) < 5:
        return fail('expected at least five report families in the live report surface')

    text = DOC_PATH.read_text(encoding='utf-8')
    required_fragments = [
        '# Archive Size Guardrail Card',
        'package_boundary_ready: `True`',
        'Top-level growth since 2026-03-16',
        'Largest report families',
        'Guardrails',
    ]
    missing = [frag for frag in required_fragments if frag not in text]
    if missing:
        return fail(f'missing required doc fragments: {missing}')

    print(
        'archive-size-guardrail-card: ok '
        f"(files={totals['retained_file_count']}, raw_bytes={totals['raw_bytes']}, zip_bytes={totals['approx_revision_zip_bytes']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
