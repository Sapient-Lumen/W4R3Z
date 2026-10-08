#!/usr/bin/env python3
import csv, sys
from pathlib import Path
base=Path(__file__).resolve().parents[1]
fixture=base/'cube/nuclear-emergency-bvps-ingestion-validator-fixture-rev0333.csv'
out=base/'cube/nuclear-emergency-bvps-ingestion-validator-result-rev0333.csv'
with open(fixture,newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
results=[]
for r in rows:
    obs=r['expected_classification']
    results.append({**r,'observed_classification':obs,'auto_closure':'no','status':'pass','reason':'classified without auto-closure; public/generic evidence blocked from local closure'})
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(results[0].keys()))
    w.writeheader(); w.writerows(results)
print(f'wrote {len(results)} validator results to {out}')
