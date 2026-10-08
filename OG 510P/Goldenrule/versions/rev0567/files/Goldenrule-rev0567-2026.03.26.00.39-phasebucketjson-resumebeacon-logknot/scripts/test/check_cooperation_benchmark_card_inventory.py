#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_inventory.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_inventory.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_INVENTORY.md'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-inventory: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'inventory builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    if data.get('card_inventory_kind') != 'cooperation_benchmark_card_inventory':
        return fail('unexpected card_inventory_kind')
    cards = data.get('cards', [])
    if len(cards) < 2:
        return fail('expected at least two cooperation benchmark cards in inventory')
    ids = [card['id'] for card in cards]
    if len(ids) != len(set(ids)):
        return fail('card ids should be unique in inventory')
    latest = data.get('latest_claim_ready_card_ids', [])
    if not latest:
        return fail('expected at least one latest claim-ready card id')
    counts = data.get('counts', {})
    if counts.get('freeze_receipt_count', 0) < 1:
        return fail('expected at least one freeze receipt in inventory')
    if counts.get('verified_freeze_receipt_count', 0) + counts.get('drifted_freeze_receipt_count', 0) != counts.get('freeze_receipt_count', -1):
        return fail('verified + drifted freeze receipt counts should add up to total freeze receipts')
    if counts.get('delta_receipt_count', 0) < 1:
        return fail('expected at least one delta receipt in inventory')
    if counts.get('verified_delta_receipt_count', 0) + counts.get('drifted_delta_receipt_count', 0) != counts.get('delta_receipt_count', -1):
        return fail('verified + drifted delta receipt counts should add up to total delta receipts')
    if counts.get('orphan_freeze_receipt_count', 1) != 0:
        return fail('expected zero orphan freeze receipts')
    if counts.get('orphan_delta_receipt_count', 1) != 0:
        return fail('expected zero orphan delta receipts')
    print('cooperation-benchmark-card-inventory: ok')
    print(f'cooperation-benchmark-card-inventory: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
