#!/usr/bin/env python3
import csv, sys
from pathlib import Path
base=Path(__file__).resolve().parents[1]
result=base/'cube/nuclear-emergency-bvps-release-egress-validator-result-rev0352.csv'
rows=list(csv.DictReader(result.open(newline='',encoding='utf-8')))
bad=[r for r in rows if r.get('auto_closure')!='no' or r.get('pass_fail')!='pass']
leaks=[r for r in rows if 'closure' in r.get('public_release_effect','').lower() and r.get('validator_decision')!='candidate_for_adjudication_not_closure']
print(f'rows={len(rows)} bad={len(bad)} leaks={len(leaks)}')
if len(rows)!=54 or bad or leaks:
    sys.exit(1)
