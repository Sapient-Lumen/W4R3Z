#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-eof-ler-adams-watch-rev0368.csv'
required=['root cause','10 cfr 50.73','ler','restored','retest','compensatory','extent-of-play','nrc inspection']
errors=[]
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
if len(rows)<8: errors.append('too_few_eof_ler_rows')
text=' '.join(' '.join(r.values()).lower() for r in rows)
for term in required:
    if term not in text: errors.append('missing_term:'+term)
for r in rows:
    wid=r.get('watch_id','?')
    if 'no_readiness_closure' not in r.get('claim_effect','').lower(): errors.append('bad_claim_effect:'+wid)
    if not r.get('current_state','').startswith('open_'): errors.append('not_open:'+wid)
    if not r.get('minimum_artifacts') or not r.get('next_action'): errors.append('missing_artifacts_or_action:'+wid)
if errors:
    print('FAIL eof_ler_watch_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS eof_ler_watch_rev0368 rows={len(rows)}')
