#!/usr/bin/env python3
import csv, sys
from pathlib import Path
rows=list(csv.DictReader(open(Path(__file__).resolve().parents[1]/'cube/nuclear-emergency-bvps-forensic-dropbox-validator-result-rev0356.csv',newline='',encoding='utf-8')))
counts={}; errors=[]
for r in rows:
 counts[r['observed_classification']]=counts.get(r['observed_classification'],0)+1
 if r['passed']!='yes': errors.append(r['case_id'])
 if r['auto_closure']!='no': errors.append(r['case_id']+' auto')
req={'rejected_closure_attempt':16,'hold_no_upgrade':14,'candidate_for_adjudication_not_closure':10,'accepted_reopen_signal':6,'context_no_upgrade':8}
for k,v in req.items():
 if counts.get(k,0)!=v: errors.append(f'{k}:{counts.get(k,0)}')
if len(rows)!=54: errors.append('rowcount')
print('forensic_dropbox_validator',counts,'errors',errors)
sys.exit(1 if errors else 0)
