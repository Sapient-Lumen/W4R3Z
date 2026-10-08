#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'field-kits/bvps-rev0367/fieldkit-pointer-manifest-rev0367.csv'
errors=[]
def sha(p: Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024), b''): h.update(c)
    return h.hexdigest()
with P.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)<8: errors.append('too_few_pointers')
for r in rows:
    target=ROOT/r['canonical_path']
    if not target.exists(): errors.append('missing_target:'+r['canonical_path']); continue
    if r.get('copy_policy')!='pointer_only_do_not_duplicate_bytes': errors.append('bad_policy:'+r['pointer_id'])
    if r.get('canonical_sha256') not in ('PENDING', sha(target)):
        errors.append('sha_mismatch:'+r['canonical_path'])
if errors:
    print('FAIL fieldkit_pointer_rev0367 ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS fieldkit_pointer_rev0367 pointers={len(rows)}')
