from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'cube/bvps-dispatch-deadline-clock-rev0378.csv').open(newline='',encoding='utf-8')))
if len(rows)!=8:
    raise SystemExit(f'expected 8 clock rows, found {len(rows)}')
for r in rows:
    if r['status']!='estimate_until_receipt_is_captured':
        raise SystemExit(f'{r["request_id"]} bad status')
    if not r['clock_source_ids']:
        raise SystemExit(f'{r["request_id"]} missing clock source ids')
    if r['jurisdiction'].startswith('federal') and r['estimated_initial_due_if_received_2026_06_15']!='2026-07-14':
        raise SystemExit(f'{r["request_id"]} wrong federal due date')
    if 'pennsylvania' in r['jurisdiction'] and r['estimated_initial_due_if_received_2026_06_15']!='2026-06-22':
        raise SystemExit(f'{r["request_id"]} wrong PA due date')
    if 'west_virginia' in r['jurisdiction'] and r['estimated_initial_due_if_received_2026_06_15']!='2026-06-22':
        raise SystemExit(f'{r["request_id"]} wrong WV due date')
    if 'ohio' in r['jurisdiction'] and r['estimated_initial_due_if_received_2026_06_15']!='reasonable_period_no_fixed_statutory_due':
        raise SystemExit(f'{r["request_id"]} wrong Ohio due marker')
print('PASS deadline_clock_rev0378')
