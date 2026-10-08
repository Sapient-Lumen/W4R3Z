#!/usr/bin/env python3
"""Operate rev0343 BVPS evidence war-room preflight tables.

This is a package-local utility. It summarizes packet status and emits claim caps.
It does not import real evidence and it never auto-closes readiness.
"""
import csv, sys
from collections import Counter
from pathlib import Path
base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
status_path = base/'cube/nuclear-emergency-bvps-warroom-packet-status-preflight-rev0343.csv'
out_path = base/'cube/nuclear-emergency-bvps-warroom-operator-run-output-rev0343.csv'
rows = list(csv.DictReader(open(status_path, newline='', encoding='utf-8')))
counts = Counter(r['preflight_state'] for r in rows)
out=[]
for state,count in sorted(counts.items()):
    out.append({'metric':state,'count':count,'claim_rule':'no automatic closure'})
out.append({'metric':'total_packets','count':len(rows),'claim_rule':'all are synthetic preflight rows, not real evidence'})
with open(out_path,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['metric','count','claim_rule'])
    w.writeheader(); w.writerows(out)
print(f'wrote {out_path} with {len(out)} rows')
