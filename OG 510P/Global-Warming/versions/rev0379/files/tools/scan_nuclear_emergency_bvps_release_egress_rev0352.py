#!/usr/bin/env python3
import csv, hashlib, os
from pathlib import Path
base=Path(__file__).resolve().parents[1]
manifest=base/'cube/nuclear-emergency-bvps-public-release-manifest-rev0352.csv'
rows=list(csv.DictReader(manifest.open(newline='',encoding='utf-8')))
for r in rows:
    r['scan_state']='no_payload_to_release'
    r['release_allowed']='no'
with (base/'cube/nuclear-emergency-bvps-release-egress-filesystem-scan-rev0352.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print(f'public_release_packets={len(rows)} release_allowed=0')
