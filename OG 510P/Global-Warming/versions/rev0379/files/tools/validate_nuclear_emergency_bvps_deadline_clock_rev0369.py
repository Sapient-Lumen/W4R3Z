#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-deadline-clock-rev0369.csv'
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
errors=[]
text=' '.join(' '.join(r.values()).lower() for r in rows)
for term in ['2026-06-12','90 days','120 days','2026-05-13','ans','eof','records request']:
    if term.lower() not in text: errors.append('missing_clock_term:'+term)
if len(rows)<8: errors.append('too_few_deadline_rows')
if sum(1 for r in rows if r.get('priority')=='P0')<7: errors.append('too_few_P0_clocks')
for r in rows:
    if 'readiness_closure' not in r.get('claim_effect','') and r.get('priority')=='P0': errors.append('bad_claim_effect:'+r.get('clock_id','?'))
    if not r.get('required_artifacts_by_date') or not r.get('next_action'): errors.append('missing_artifacts_or_action:'+r.get('clock_id','?'))
if errors:
    print('FAIL deadline_clock_rev0369 ' + ';'.join(errors[:40])); sys.exit(1)
print(f'PASS deadline_clock_rev0369 rows={len(rows)}')
