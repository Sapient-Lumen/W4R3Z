#!/usr/bin/env python3
"""Scan rev0346 synthetic payload files. This scanner is intentionally strict:
README placeholders do not count as payloads, and synthetic payloads never count as real evidence."""
from pathlib import Path
import csv, hashlib, json, sys
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'field-kits'/'bvps-rev0343'/'packet-skeletons'
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()
rows=[]
for pkt in sorted(BASE.glob('PKT-*')):
    for folder in ['raw','redacted','custody','qa']:
        d=pkt/folder
        for p in sorted(d.glob('*')):
            if p.name == 'README.md':
                continue
            rows.append({'packet_id':pkt.name,'folder':folder,'artifact_path':str(p.relative_to(ROOT)),'sha256':sha(p),'size_bytes':p.stat().st_size,'counts_as_real_evidence':'no','synthetic_or_real':'synthetic' if ('SYNTHETIC' in p.read_text(errors='ignore')[:4000] or 'synthetic' in p.name.lower()) else 'unknown'})
out=ROOT/'cube'/'nuclear-emergency-bvps-payload-filesystem-scan-result-rev0346.csv'
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['packet_id','folder','artifact_path','sha256','size_bytes','counts_as_real_evidence','synthetic_or_real'])
    w.writeheader(); w.writerows(rows)
print(json.dumps({'payload_file_rows':len(rows),'seeded_packet_count':len(set(r['packet_id'] for r in rows)),'auto_closure_count':0}, indent=2))
