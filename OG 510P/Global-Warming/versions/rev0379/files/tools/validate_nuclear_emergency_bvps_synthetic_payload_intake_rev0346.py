#!/usr/bin/env python3
"""Validate rev0346 synthetic payload intake firebreak."""
from pathlib import Path
import csv, json, sys
ROOT=Path(__file__).resolve().parents[1]
res=ROOT/'cube'/'nuclear-emergency-bvps-synthetic-intake-validator-result-rev0346.csv'
rows=list(csv.DictReader(open(res, encoding='utf-8')))
fail=[r for r in rows if r.get('status')!='pass']
auto=[r for r in rows if r.get('actual_auto_closure') not in ('no','false','False','0')]
classes={}
for r in rows: classes[r['actual_classification']]=classes.get(r['actual_classification'],0)+1
payload=list(csv.DictReader(open(ROOT/'cube'/'nuclear-emergency-bvps-packet-intake-classification-rev0346.csv', encoding='utf-8')))
ready=[r for r in payload if r.get('claim_state')!='not_ready_to_claim']
summary={'validator_rows':len(rows),'failures':len(fail),'auto_closures':len(auto),'class_counts':classes,'claim_ready_rows':len(ready)}
print(json.dumps(summary, indent=2))
if fail or auto or ready:
    sys.exit(1)
