#!/usr/bin/env python3
import csv, sys
from pathlib import Path
base = Path(__file__).resolve().parents[1]
result = base/'cube/nuclear-emergency-bvps-conflict-repair-validator-result-rev0353.csv'
rows = list(csv.DictReader(open(result, newline='', encoding='utf-8')))
allowed = {'rejected_closure_attempt','hold_no_upgrade','candidate_for_adjudication_not_closure','accepted_reopen_signal','context_no_upgrade'}
errors=[]
if len(rows) != 54:
    errors.append(f'expected 54 validator rows, found {len(rows)}')
for r in rows:
    if r['observed_classification'] not in allowed:
        errors.append(f"bad class {r['case_id']} {r['observed_classification']}")
    if r.get('auto_closure') != 'no':
        errors.append(f"auto closure leak {r['case_id']}")
counts={k:sum(1 for r in rows if r['observed_classification']==k) for k in allowed}
expected={'rejected_closure_attempt':16,'hold_no_upgrade':14,'candidate_for_adjudication_not_closure':10,'accepted_reopen_signal':6,'context_no_upgrade':8}
for k,v in expected.items():
    if counts.get(k,0)!=v:
        errors.append(f'expected {v} {k}, found {counts.get(k,0)}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('rev0353 rehydration conflict repair validator passed')
