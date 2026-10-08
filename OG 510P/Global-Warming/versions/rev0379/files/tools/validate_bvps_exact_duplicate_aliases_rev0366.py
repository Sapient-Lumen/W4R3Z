#!/usr/bin/env python3
"""Validate known exact-duplicate aliases are explicit and not miscounted as independent."""
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/'cube/bvps-exact-duplicate-alias-refactor-rev0366.csv'
def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()
errors=[]
with MAP.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)<2: errors.append('too_few_alias_rows')
for r in rows:
    c=ROOT/r['canonical_path']; a=ROOT/r['alias_path']
    if not c.exists() or not a.exists(): errors.append('missing_pair:'+r.get('alias_id','?')); continue
    cs=sha(c); als=sha(a)
    if cs != r.get('canonical_sha256') or als != r.get('alias_sha256'):
        errors.append('sha_mismatch:'+r.get('alias_id','?'))
    if cs != als or r.get('exact_duplicate')!='true':
        errors.append('not_exact_duplicate:'+r.get('alias_id','?'))
    if 'not_count_alias_as_independent' not in r.get('forward_policy',''):
        errors.append('missing_independence_policy:'+r.get('alias_id','?'))
if errors:
    print('FAIL duplicate_aliases ' + ';'.join(errors)); sys.exit(1)
print(f'PASS duplicate_aliases rows={len(rows)}')
