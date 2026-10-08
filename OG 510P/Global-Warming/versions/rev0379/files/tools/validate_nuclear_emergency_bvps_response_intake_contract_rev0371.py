#!/usr/bin/env python3
from __future__ import annotations
import csv, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'cube/nuclear-emergency-bvps-response-intake-contract-rev0371.csv'
PROOFMAP=ROOT/'cube/nuclear-emergency-bvps-response-to-proofcut-map-rev0371.csv'
REJECT=ROOT/'cube/nuclear-emergency-bvps-response-rejection-reasons-rev0371.csv'
FIX_LEDGER=ROOT/'cube/nuclear-emergency-bvps-response-intake-fixture-ledger-rev0371.csv'

def read(p):
    with p.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def fail(msg): print('FAIL '+msg); sys.exit(1)
rows=read(CONTRACT); pm=read(PROOFMAP); rr=read(REJECT)
if len(rows)<10: fail('contract_too_short')
classes={r['intake_class'] for r in rows}
for needed in ['preliminary_findings_or_AAR_IP','ANS_siren_IPAWS_EAS_delivery_logs','EOF_power_recovery_CAP_retest','LER_or_no_LER_regulatory_disposition','no_records_or_nonresponsive_reply','public_meeting_raw_capture']:
    if needed not in classes: fail('missing_intake_class='+needed)
for r in rows:
    txt=' '.join(v for k,v in r.items() if k not in ('forbidden_credit','automatic_rejection')).lower()
    if 'forbidden_credit' not in r or not r['forbidden_credit']: fail('missing_forbidden_credit='+r['contract_id'])
    if 'closure' not in r['claim_effect']: fail('missing_closure_claim_effect='+r['contract_id'])
    if any(b in txt for b in ['readiness closed','certified ready','exercise passed']): fail('forbidden_phrase='+r['contract_id'])
for r in pm:
    if r['intake_class'] not in classes: fail('proofmap_unknown_class='+r['map_id'])
if len(rr)<5: fail('too_few_rejection_reasons')
# Ensure fixture ledger exists and grants no credit.
if not FIX_LEDGER.exists(): fail('missing_fixture_ledger')
fx=read(FIX_LEDGER)
if not fx: fail('fixture_ledger_empty')
for r in fx:
    if r['intake_status']!='fixture_only_no_credit': fail('fixture_not_rejected='+r['ledger_id'])
    if r['claim_effect']!='no_readiness_closure': fail('fixture_claim_effect='+r['ledger_id'])
print(f'PASS response_intake_contract_rev0371 classes={len(classes)} fixture_rows={len(fx)}')
