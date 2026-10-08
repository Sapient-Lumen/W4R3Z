#!/usr/bin/env python3
"""Scan media quarantine directories for missing packet folders.
This scan intentionally does not accept evidence; it reports readiness-to-receive only."""
from pathlib import Path
import csv
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'field-kits/bvps-rev0355/media-quarantine'
rows=[]
for i in range(1,61):
    pkt=f'PKT-{i:03d}'
    p=base/pkt
    lanes=['inbound','safe_copy','scan','rejected','candidate','review']
    missing=[x for x in lanes if not (p/x).is_dir()]
    rows.append({'packet_id':pkt,'quarantine_path':str(p.relative_to(ROOT)),'missing_lanes':';'.join(missing),'ready_to_receive':'no' if missing else 'yes_no_evidence','closure_effect':'directory readiness is not evidence'})
out=ROOT/'cube/nuclear-emergency-bvps-media-quarantine-filesystem-scan-rev0355.csv'
with out.open('w', newline='', encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f'wrote {out}')
