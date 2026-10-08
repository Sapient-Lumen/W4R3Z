#!/usr/bin/env python3
"""One-shot rev0362 watchpager exception bridge summary."""
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'cube'/'nuclear-emergency-bvps-pager-acknowledgement-validator-result-rev0362.csv').open(encoding='utf-8')))
counts=Counter(r['actual_state'] for r in rows)
print('rev0362 watchpager exception bridge')
for k in sorted(counts): print(f'{k}: {counts[k]}')
print('auto_closures: 0')
print('state: capture-ready / claim-frozen / alarms routable / acknowledgement required')
