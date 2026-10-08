#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_citation_surface.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_citation_surface.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-citation-surface: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'citation surface builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    if data.get('surface_kind') != 'cooperation_benchmark_card_citation_surface':
        return fail('unexpected surface_kind')
    if data.get('inventory_kind') != 'cooperation_benchmark_card_inventory':
        return fail('unexpected inventory_kind')
    if data.get('heads_register_kind') != 'cooperation_benchmark_card_heads_register':
        return fail('unexpected heads_register_kind')
    counts = data.get('counts', {})
    entries = data.get('entries', [])
    unresolved = data.get('unresolved_lineages', [])
    if counts.get('citation_entry_count') != len(entries):
        return fail('citation_entry_count does not match entries length')
    if counts.get('unresolved_lineage_count') != len(unresolved):
        return fail('unresolved_lineage_count does not match unresolved_lineages length')
    if counts.get('lineage_count', 0) != counts.get('citation_lineage_count', 0) + counts.get('unresolved_lineage_count', 0):
        return fail('lineage_count should equal resolved plus unresolved counts')
    for row in entries:
        for field in ['lineage_id', 'card_id', 'freeze_receipt_path', 'rendered_markdown_path']:
            if not row.get(field):
                return fail(f'citation entry missing {field}')
    for row in unresolved:
        if not row.get('reason_codes'):
            return fail('unresolved lineage missing reason_codes')
    print('cooperation-benchmark-card-citation-surface: ok')
    print(f'cooperation-benchmark-card-citation-surface: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
