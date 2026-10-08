#!/usr/bin/env python3
"""Validate the rev0366 BVPS field kit remains pointer-only."""
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'field-kits/bvps-rev0366/fieldkit-pointer-manifest-rev0366.csv'
def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()
errors=[]
with MAN.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)<10: errors.append('too_few_pointers')
for r in rows:
    p=ROOT/r['canonical_path']
    if not p.exists(): errors.append('missing_target:'+r['canonical_path']); continue
    if sha(p)!=r.get('canonical_sha256'): errors.append('hash_mismatch:'+r['canonical_path'])
    if r.get('copy_policy')!='pointer_only_do_not_duplicate_bytes': errors.append('bad_copy_policy:'+r.get('pointer_id','?'))
for p in (ROOT/'field-kits/bvps-rev0366').glob('*'):
    if p.name != 'fieldkit-pointer-manifest-rev0366.csv': errors.append('unexpected_fieldkit_copy:'+p.name)
if errors:
    print('FAIL fieldkit_rev0366 ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS fieldkit_rev0366 pointers={len(rows)}')
