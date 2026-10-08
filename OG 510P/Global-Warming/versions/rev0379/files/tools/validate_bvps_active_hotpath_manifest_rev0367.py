#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'cube/bvps-active-hotpath-resource-manifest-rev0367.csv'
def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024), b''): h.update(c)
    return h.hexdigest()
errors=[]
with MAN.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)<25: errors.append('too_few_hotpath_rows')
for r in rows:
    p=ROOT/r['path']
    if not p.exists(): errors.append('missing:'+r['path']); continue
    if p.stat().st_size > 5_000_000:
        errors.append('hotpath_file_too_large:'+r['path'])
    if sha(p) != r.get('sha256'):
        errors.append('sha_mismatch:'+r['path'])
    if 'whole_cube_scan' not in r.get('max_session_use',''):
        errors.append('missing_use_limit:'+r['path'])
if not any(r['path'].endswith('datacube-rev0367-hotpath.sqlite') for r in rows):
    errors.append('missing_hotpath_sqlite_pointer')
if errors:
    print('FAIL hotpath_manifest_rev0367 ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS hotpath_manifest_rev0367 rows={len(rows)}')
