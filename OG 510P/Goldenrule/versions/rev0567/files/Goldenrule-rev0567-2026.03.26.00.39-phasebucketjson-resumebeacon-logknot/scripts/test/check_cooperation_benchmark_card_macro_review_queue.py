#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_macro_review_queue.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_macro_review_queue.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_MACRO_REVIEW_QUEUE.md'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-macro-review-queue: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'macro review queue builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    if data.get('queue_kind') != 'cooperation_benchmark_card_macro_review_queue':
        return fail('unexpected queue_kind')
    if data.get('review_queue_kind') != 'cooperation_benchmark_card_review_queue':
        return fail('unexpected review_queue_kind')
    if data.get('citation_surface_kind') != 'cooperation_benchmark_card_citation_surface':
        return fail('unexpected citation_surface_kind')
    counts = data.get('counts', {})
    groups = data.get('groups', [])
    if counts.get('queued_lineage_count') != len(groups):
        return fail('queued_lineage_count does not match groups length')
    if counts.get('total_item_count') != sum(int(row.get('item_count', 0)) for row in groups):
        return fail('total_item_count does not match grouped item_count total')
    if counts.get('total_apply_command_count') != sum(len(row.get('apply_commands', [])) for row in groups):
        return fail('total_apply_command_count does not match groups')
    lineage_ids = [row.get('lineage_id') for row in groups]
    if len(lineage_ids) != len(set(lineage_ids)):
        return fail('groups should not repeat lineage_id')
    for row in groups:
        if row['item_count'] != len(row['item_ids']):
            return fail('item_count does not match item_ids length')
        if row['primary_review_command'] not in row['review_commands']:
            return fail('primary_review_command must appear in review_commands')
        if len(row['item_ids']) != len(set(row['item_ids'])):
            return fail('item_ids should be unique')
        if len(row['item_kinds']) != len(set(row['item_kinds'])):
            return fail('item_kinds should be unique')
        if len(row['review_commands']) != len(set(row['review_commands'])):
            return fail('review_commands should be unique')
        if len(row['apply_commands']) != len(set(row['apply_commands'])):
            return fail('apply_commands should be unique')
    print('cooperation-benchmark-card-macro-review-queue: ok')
    print(f'cooperation-benchmark-card-macro-review-queue: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
