#!/usr/bin/env python3
"""Validate rev0365 BVPS field kit uses pointers rather than duplicate copies."""
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'field-kits/bvps-rev0365/fieldkit-pointer-manifest-rev0365.csv'
rows=list(csv.DictReader(open(manifest, newline='', encoding='utf-8')))
errors=[]
def sha(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
if len(rows)<4: errors.append('pointer_rows<4')
canonical_hashes=set()
for r in rows:
    target=ROOT/r.get('canonical_path','')
    if not target.exists(): errors.append('missing_target:'+r.get('canonical_path',''))
    if r.get('copy_policy')!='reference_do_not_duplicate': errors.append('bad_copy_policy:'+r.get('fieldkit_item_id',''))
    if target.exists() and target.is_file(): canonical_hashes.add(sha(target))
for p in (ROOT/'field-kits/bvps-rev0365').rglob('*'):
    if p.is_file() and p.name!='fieldkit-pointer-manifest-rev0365.csv':
        if sha(p) in canonical_hashes:
            errors.append('new_fieldkit_duplicate_copy:'+str(p.relative_to(ROOT)))
if errors:
    print('FAIL fieldkit_pointer_manifest ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS fieldkit_pointer_manifest pointer_rows={len(rows)} duplicate_new_copies=0')
