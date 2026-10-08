#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_review_queue.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_review_queue.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-review-queue: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'review queue builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    if data.get('queue_kind') != 'cooperation_benchmark_card_review_queue':
        return fail('unexpected queue_kind')
    if data.get('inventory_kind') != 'cooperation_benchmark_card_inventory':
        return fail('unexpected inventory_kind')
    if data.get('heads_register_kind') != 'cooperation_benchmark_card_heads_register':
        return fail('unexpected heads_register_kind')
    items = data.get('items', [])
    counts = data.get('counts', {})
    if counts.get('total_items') != len(items):
        return fail('total_items does not match items length')
    for row in items:
        if not row.get('reason_codes'):
            return fail('queue item missing reason_codes')
        if not row.get('review_command'):
            return fail('queue item missing review_command')
    print('cooperation-benchmark-card-review-queue: ok')
    print(f'cooperation-benchmark-card-review-queue: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
