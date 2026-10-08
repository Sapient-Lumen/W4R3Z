#!/usr/bin/env python3
"""Scan rev0350 red-team live-drop drill files and emit SHA-256 hashes."""
from pathlib import Path
import hashlib, csv, sys
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
base = root / 'field-kits' / 'bvps-rev0350' / 'redteam-dropbox-drill' / 'bundles'
out = root / 'cube' / 'nuclear-emergency-bvps-live-drop-redteam-filesystem-hash-index-rev0350.csv'
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()
rows=[]
for p in sorted(base.rglob('*')):
    if p.is_file():
        parts=p.relative_to(base).parts
        case=parts[0].split('-PKT-')[0] if parts else ''
        rows.append({'case_id':case,'relative_path':str(p.relative_to(root)),'size_bytes':p.stat().st_size,'sha256':sha(p),'auto_closure_allowed':'no'})
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['case_id','relative_path','size_bytes','sha256','auto_closure_allowed'])
    w.writeheader(); w.writerows(rows)
print(f'wrote {len(rows)} rows to {out}')
