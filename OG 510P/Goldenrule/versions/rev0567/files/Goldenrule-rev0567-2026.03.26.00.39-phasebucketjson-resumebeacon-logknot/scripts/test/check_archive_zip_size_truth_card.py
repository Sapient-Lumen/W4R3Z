#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / 'artifacts' / 'reports' / 'archive_zip_size_truth_card.json'
MD_PATH = ROOT / 'docs' / 'ARCHIVE_ZIP_SIZE_TRUTH_CARD.md'
SIZE_JSON = ROOT / 'artifacts' / 'reports' / 'archive_size_guardrail_card.json'


def fail(message: str) -> int:
    print(f'archive-zip-size-truth-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    if not JSON_PATH.exists():
        return fail('missing report json')
    if not MD_PATH.exists():
        return fail('missing markdown doc')
    report = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    if report.get('card') != 'archive_zip_size_truth_card':
        return fail('card id mismatch')
    current = report.get('current_internal_proxy')
    if not isinstance(current, dict):
        return fail('current_internal_proxy missing')
    size = json.loads(SIZE_JSON.read_text(encoding='utf-8'))
    if current.get('approx_revision_zip_bytes') != size['archive_totals']['approx_revision_zip_bytes']:
        return fail('current proxy drifted from size guardrail')
    proc = subprocess.run(
        ['python3', 'scripts/tools/inspect_authoritative_archive_zip.py', '--emit', 'size-bytes'],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end='', file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return fail('live size emit command failed')
    try:
        live_size = int(proc.stdout.strip())
    except ValueError:
        return fail('live size emit output malformed')
    if live_size <= 0:
        return fail('live size must be positive')
    if report.get('selected_matches_current_root_zip') and live_size <= current['approx_revision_zip_bytes']:
        return fail('current live zip size should exceed the internal proxy for the self-referential head case')
    predecessor = report.get('predecessor_empirical_calibration')
    if predecessor is not None:
        zip_path = Path(predecessor['zip_path'])
        if not zip_path.exists():
            return fail('predecessor zip path missing')
        if zip_path.stat().st_size != predecessor['actual_external_zip_bytes']:
            return fail('predecessor actual zip size mismatch')
        with zipfile.ZipFile(zip_path) as zf:
            matches = [name for name in zf.namelist() if name.endswith('artifacts/reports/archive_size_guardrail_card.json')]
            if len(matches) != 1:
                return fail('predecessor embedded size guardrail missing or ambiguous')
            embedded = json.loads(zf.read(matches[0]).decode('utf-8'))
        embedded_proxy = embedded['archive_totals']['approx_revision_zip_bytes']
        if embedded_proxy != predecessor['embedded_proxy_bytes']:
            return fail('predecessor embedded proxy mismatch')
        if predecessor['actual_minus_proxy_bytes'] != predecessor['actual_external_zip_bytes'] - predecessor['embedded_proxy_bytes']:
            return fail('predecessor delta mismatch')
        if predecessor['actual_minus_proxy_bytes'] <= 0:
            return fail('predecessor delta should be positive')
    print('archive-zip-size-truth-card: ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
