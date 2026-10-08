
#!/usr/bin/env python3
"""Recompute a lightweight preflight snapshot seal for rev0349 control files."""
from pathlib import Path
import csv, hashlib
ROOT=Path(__file__).resolve().parents[1]
CUBE=ROOT/'cube'
FILES=[
 'cube/nuclear-emergency-bvps-live-intake-console-rev0348.csv',
 'cube/nuclear-emergency-bvps-intake-receipt-ledger-rev0349.csv',
 'cube/nuclear-emergency-bvps-claim-embargo-lint-result-rev0349.csv',
 'cube/nuclear-emergency-bvps-replay-canary-negative-control-rev0349.csv'
]
def h(path):
    hh=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            hh.update(chunk)
    return hh.hexdigest()
rows=[]
for rel in FILES:
    p=ROOT/rel
    rows.append({'path':rel,'sha256':h(p),'size_bytes':p.stat().st_size})
merkle=hashlib.sha256(''.join(r['sha256'] for r in rows).encode()).hexdigest()
print(merkle)
