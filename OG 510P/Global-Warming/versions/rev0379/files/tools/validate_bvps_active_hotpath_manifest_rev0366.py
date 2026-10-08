#!/usr/bin/env python3
"""Validate the BVPS active hotpath manifest points to real, small operational files."""
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'cube/bvps-active-hotpath-resource-manifest-rev0366.csv'
def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()
errors=[]
with MAN.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)<15: errors.append('too_few_hotpath_rows')
for r in rows:
    p=ROOT/r['path']
    if not p.exists(): errors.append('missing:'+r['path']); continue
    if p.stat().st_size > 250000:
        errors.append('hotpath_file_too_large:'+r['path'])
    if sha(p) != r.get('sha256'):
        errors.append('sha_mismatch:'+r['path'])
    if 'whole_cube_scan' not in r.get('max_session_use',''):
        errors.append('missing_use_limit:'+r['path'])
if errors:
    print('FAIL hotpath_manifest ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS hotpath_manifest rows={len(rows)}')
