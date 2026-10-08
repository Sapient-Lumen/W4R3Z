#!/usr/bin/env python3
"""Validate actual shipped fixture files no longer use risky executable-looking extensions."""
import csv, hashlib, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
risky={'.exe','.vbs','.ps1','.docm','.xlsm','.lnk','.eml','.msg','.7z'}
def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()
actual=[]
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in risky and ('fixtures' in p.parts or 'quarantine' in p.parts):
        actual.append(str(p.relative_to(ROOT)))
rows=list(csv.DictReader(open(ROOT/'cube/nuclear-emergency-bvps-fixture-inert-rename-map-rev0364.csv', newline='', encoding='utf-8')))
errors=[]
if actual:
    errors.append('actual_risky_fixture_paths=' + ','.join(actual[:10]))
if len(rows) < 36:
    errors.append(f'rename_rows<{36}:{len(rows)}')
for r in rows:
    new=ROOT/r['new_path']
    if not new.exists():
        errors.append('missing_new_path:'+r['new_path'])
        continue
    if not r['new_path'].endswith('.fixture.txt'):
        errors.append('not_inert:'+r['new_path'])
    if sha256(new) != r['sha256_preserved']:
        errors.append('hash_mismatch:'+r['new_path'])
    if r['original_extension'] not in risky:
        errors.append('unexpected_original_extension:'+r['original_extension'])
if errors:
    print('FAIL inert_fixture_policy ' + ';'.join(errors[:20]))
    sys.exit(1)
print(f'PASS inert_fixture_policy rename_rows={len(rows)} actual_risky_fixture_paths=0')
