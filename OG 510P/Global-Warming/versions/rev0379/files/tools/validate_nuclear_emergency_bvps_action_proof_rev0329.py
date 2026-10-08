#!/usr/bin/env python3
import csv, sys
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
fixture = BASE/'cube/nuclear-emergency-bvps-action-proof-validator-fixture-rev0329.csv'
out = BASE/'cube/nuclear-emergency-bvps-action-proof-validator-result-rev0329.csv'
rows=[]
with fixture.open(newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        ok = (r.get('expected_classification') == r.get('observed_classification') and r.get('public_closure_leak') == 'false')
        r['status'] = 'pass' if ok else 'fail'
        r['auto_closure_allowed'] = 'false'
        rows.append(r)
with out.open('w', newline='', encoding='utf-8') as f:
    fieldnames = list(rows[0].keys())
    w=csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader(); w.writerows(rows)
if any(r['status']!='pass' for r in rows):
    sys.exit(1)
