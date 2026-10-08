#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/'evidence-bags/bvps-response-intake-lockbox-rev0371.zip'
MAN=ROOT/'cube/bvps-response-intake-lockbox-manifest-rev0371.csv'
def read(p):
    with p.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def sha(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def fail(msg): print('FAIL '+msg); sys.exit(1)
if not LOCK.exists(): fail('missing_lockbox')
with zipfile.ZipFile(LOCK) as z:
    bad=z.testzip(); names=z.namelist()
if bad: fail('bad_zip_entry='+bad)
rows=read(MAN)
if len(rows)<7: fail('manifest_too_short')
for r in rows:
    if r['inner_path'] not in names: fail('missing_zip_inner='+r['inner_path'])
    p=ROOT/r['inner_path']
    if not p.exists(): fail('missing_source='+r['inner_path'])
    if sha(p)!=r['sha256']: fail('hash_drift='+r['inner_path'])
required=['response-sidecar-template.csv','response-hash-ledger-template.csv','response-adjudication-ledger-template.csv','nonresponsive-response-ledger-template.csv']
name_text='\n'.join(names)
for req in required:
    if req not in name_text: fail('missing_template='+req)
print(f'PASS response_lockbox_rev0371 files={len(names)} size={LOCK.stat().st_size}')
