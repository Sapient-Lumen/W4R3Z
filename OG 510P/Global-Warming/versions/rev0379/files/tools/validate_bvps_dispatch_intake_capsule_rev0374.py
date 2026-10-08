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
manifest='cube/bvps-dispatch-intake-capsule-manifest-rev0374.csv'
capsule='evidence-bags/bvps-dispatch-intake-capsule-rev0374.zip'
with (ROOT/manifest).open(newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
problems=[]
if len(rows)<30: problems.append('manifest_too_small')
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
    print('FAIL dispatch_intake_capsule_rev0374 '+ '; '.join(problems[:30])); sys.exit(1)
print(f'PASS dispatch_intake_capsule_rev0374 entries={len(rows)} capsule={capsule}')
