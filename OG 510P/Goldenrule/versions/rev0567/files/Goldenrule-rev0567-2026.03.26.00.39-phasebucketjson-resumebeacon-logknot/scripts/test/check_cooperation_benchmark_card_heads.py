#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_heads.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_heads.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_HEADS.md'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-heads: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'heads builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    if data.get('register_kind') != 'cooperation_benchmark_card_heads_register':
        return fail('unexpected register_kind')
    if data.get('inventory_kind') != 'cooperation_benchmark_card_inventory':
        return fail('unexpected inventory_kind')
    lineages = data.get('lineages', [])
    if len(lineages) < 1:
        return fail('expected at least one lineage')
    counts = data.get('counts', {})
    if counts.get('lineage_count') != len(lineages):
        return fail('lineage_count does not match lineages length')
    if counts.get('unique_operational_head_count', 0) < 1:
        return fail('expected at least one unique operational head')
    for row in lineages:
        if not row.get('card_ids'):
            return fail('lineage missing card ids')
        if not row.get('tip_card_ids'):
            return fail('lineage missing tip ids')
        op = row.get('operational_head_card_ids', [])
        cite = row.get('citation_head_card_ids', [])
        if not isinstance(row.get('warning_reason_codes', []), list):
            return fail('warning_reason_codes should be a list')
        if row.get('unique_operational_head_id') and len(op) != 1:
            return fail('unique operational head should imply exactly one operational head card id')
        if row.get('unique_citation_head_id') and len(cite) != 1:
            return fail('unique citation head should imply exactly one citation head card id')
    print('cooperation-benchmark-card-heads: ok')
    print(f'cooperation-benchmark-card-heads: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
