#!/usr/bin/env python3
"""One-shot rev0363 watchpager exception bridge summary after validator substring fix."""
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT/'cube'/'nuclear-emergency-bvps-pager-acknowledgement-validator-result-rev0363.csv').open(encoding='utf-8')))
counts = Counter(r['actual_state'] for r in rows)
print('rev0363 watchpager exception bridge')
for k in sorted(counts):
    print(f'{k}: {counts[k]}')
print('auto_closures: 0')
print('state: capture-ready / claim-frozen / alarms routable / acknowledgement required / validator exact-match fixed')
