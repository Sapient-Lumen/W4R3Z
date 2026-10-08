#!/usr/bin/env python3
import csv, os, hashlib, sys
from pathlib import Path
root = Path(sys.argv[1]) if len(sys.argv)>1 else Path('field-kits/bvps-rev0351/offline-packet-forms')
out = Path(sys.argv[2]) if len(sys.argv)>2 else Path('cube/nuclear-emergency-bvps-offline-filesystem-scan-result-rev0351.csv')
rows=[]
for d in sorted(root.glob('PKT-*')):
    files=list(d.glob('*'))
    for f in files:
        if f.is_file():
            h=hashlib.sha256(f.read_bytes()).hexdigest()
            rows.append({'packet_id':d.name,'path':str(f),'size_bytes':f.stat().st_size,'sha256':h,'claim_boundary':'filesystem/form only; not closure'})
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('w', newline='', encoding='utf-8') as fh:
    w=csv.DictWriter(fh, fieldnames=['packet_id','path','size_bytes','sha256','claim_boundary'])
    w.writeheader(); w.writerows(rows)
print(f'wrote {len(rows)} rows to {out}')
