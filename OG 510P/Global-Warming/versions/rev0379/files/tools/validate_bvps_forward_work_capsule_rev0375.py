#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(rel):
    h=hashlib.sha256()
    with (ROOT/rel).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()
manifest='cube/bvps-forward-work-capsule-manifest-rev0375.csv'
capsule='evidence-bags/bvps-forward-work-capsule-rev0375.zip'
with (ROOT/manifest).open(newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
problems=[]
if len(rows)<35: problems.append('manifest_too_small')
for r in rows:
    rel=r['path']; p=ROOT/rel
    if not p.exists(): problems.append('missing_'+rel); continue
    if str(p.stat().st_size)!=r.get('bytes'): problems.append('size_mismatch_'+rel)
    if sha(rel)!=r.get('sha256'): problems.append('hash_mismatch_'+rel)
if not (ROOT/capsule).exists(): problems.append('missing_capsule')
else:
    with zipfile.ZipFile(ROOT/capsule) as z: names=set(z.namelist())
    if manifest not in names: problems.append('manifest_not_in_capsule')
    for r in rows:
        if r['path'] not in names: problems.append('capsule_missing_'+r['path'])
if problems:
    print('FAIL forward_work_capsule_rev0375 '+ '; '.join(problems[:30])); sys.exit(1)
print(f'PASS forward_work_capsule_rev0375 entries={len(rows)} capsule={capsule}')
