#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'cube/nuclear-emergency-bvps-submission-packet-manifest-rev0370.csv'
LEDGER=ROOT/'cube/nuclear-emergency-bvps-request-dispatch-ledger-rev0370.csv'
TEMPLATES=ROOT/'cube/nuclear-emergency-bvps-records-request-templates-rev0369.csv'

def read(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def fail(msg): print('FAIL '+msg); sys.exit(1)
rows=read(MAN); ledger=read(LEDGER); templates=read(TEMPLATES)
if len(ledger)!=len(templates): fail(f'ledger_template_mismatch ledger={len(ledger)} templates={len(templates)}')
if len(rows)<len(templates): fail('manifest_too_short')
for r in rows:
    p=ROOT/r['path']
    if not p.exists(): fail('missing_packet='+r['path'])
    if sha(p)!=r['sha256']: fail('hash_mismatch='+r['path'])
    txt=p.read_text(encoding='utf-8', errors='replace').lower()
    if 'no readiness closure' not in txt and 'no_readiness_closure' not in txt: fail('missing_nonclosure_text='+r['path'])
    bad=['certified ready','readiness closed','exercise passed']
    if any(b in txt for b in bad): fail('forbidden_overclaim_text='+r['path'])
for r in ledger:
    if r['dispatch_status']!='staged_not_sent': fail('unexpected_dispatch_status='+r['dispatch_status'])
    if r['route_verification_required']!='yes': fail('route_verification_not_required='+r['dispatch_id'])
    if 'no_readiness_closure' not in r['claim_effect']: fail('bad_claim_effect='+r['dispatch_id'])
print(f'PASS submission_packet_rev0370 packets={len(rows)} ledger_rows={len(ledger)}')
