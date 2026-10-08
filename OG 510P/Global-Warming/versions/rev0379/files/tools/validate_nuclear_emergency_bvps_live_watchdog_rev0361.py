#!/usr/bin/env python3
"""Validate rev0361 live watchdog fixture distribution.
Successful validation does not imply readiness; it only proves no auto-closure path exists.
"""
import csv, json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'cube/nuclear-emergency-bvps-watchdog-validator-result-rev0361.csv'
rows=list(csv.DictReader(open(path,newline='',encoding='utf-8')))
counts=Counter(r['classification'] for r in rows)
fail=[]
expected={'rejected_closure_attempt':16,'hold_no_upgrade':14,'candidate_for_adjudication_not_closure':10,'accepted_reopen_signal':6,'context_no_upgrade':8}
for k,v in expected.items():
    if counts.get(k,0)!=v: fail.append(f'{k} expected {v} got {counts.get(k,0)}')
if any(r.get('auto_closure_allowed')!='no' for r in rows): fail.append('auto closure allowed row found')
print(json.dumps({'rows':len(rows),'counts':dict(counts),'failures':fail,'readiness_claim':'none'}, indent=2))
raise SystemExit(1 if fail else 0)
