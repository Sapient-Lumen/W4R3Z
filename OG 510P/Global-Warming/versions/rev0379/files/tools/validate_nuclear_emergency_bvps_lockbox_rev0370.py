#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ZIP=ROOT/'evidence-bags/bvps-public-meeting-lockbox-rev0370.zip'
MAN=ROOT/'cube/bvps-public-meeting-lockbox-manifest-rev0370.csv'

def read(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

def sha_bytes(data):
    h=hashlib.sha256(); h.update(data); return h.hexdigest()

def fail(msg): print('FAIL '+msg); sys.exit(1)
if not ZIP.exists(): fail('missing_lockbox_zip')
rows=read(MAN)
if len(rows)<5: fail('too_few_lockbox_rows')
with zipfile.ZipFile(ZIP) as z:
    if z.testzip(): fail('bad_zip_member')
    names=z.namelist()
    if any(n.endswith('/') for n in names): fail('directory_entry_in_lockbox')
    for r in rows:
        if r['inner_path'] not in names: fail('manifest_missing_inner='+r['inner_path'])
        if sha_bytes(z.read(r['inner_path']))!=r['sha256']: fail('hash_mismatch='+r['inner_path'])
        if 'template_only' not in r['claim_effect']: fail('non_template_claim_effect='+r['inner_path'])
    combined='\n'.join(z.read(n).decode('utf-8','replace').lower() for n in names)
    if 'no readiness closure' not in combined and 'no_readiness_closure' not in combined: fail('missing_lockbox_nonclosure_text')
    if 'real evidence imported' in combined: fail('false_real_evidence_text')
print(f'PASS lockbox_rev0370 files={len(rows)}')
