#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/bvps-active-hotpath-resource-manifest-rev0368.csv'
errors=[]
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
if len(rows)<25: errors.append('too_few_hotpath_rows')
required=['cube/nuclear-emergency-bvps-ans-transition-admissibility-matrix-rev0368.csv','cube/nuclear-emergency-bvps-eof-ler-adams-watch-rev0368.csv','cube/nuclear-emergency-bvps-public-records-request-queue-rev0368.csv','cube/datacube-rev0368-hotpath.sqlite']
paths={r.get('path') for r in rows}
for req in required:
    if req not in paths: errors.append('missing_required:'+req)
for r in rows:
    p=ROOT/r.get('path','')
    if not p.exists(): errors.append('missing_file:'+r.get('path','?')); continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h != r.get('sha256'): errors.append('hash_mismatch:'+r.get('path','?'))
    if r.get('max_session_use')!='prefer_this_over_whole_cube_scan': errors.append('bad_use:'+r.get('path','?'))
if errors:
    print('FAIL active_hotpath_manifest_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS active_hotpath_manifest_rev0368 rows={len(rows)}')
