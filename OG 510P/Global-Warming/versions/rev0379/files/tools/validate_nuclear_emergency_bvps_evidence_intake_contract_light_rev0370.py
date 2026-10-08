#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
contract_path=ROOT/'cube/nuclear-emergency-bvps-evidence-packet-contract-rev0365.csv'
ledger_path=ROOT/'cube/nuclear-emergency-bvps-chain-of-custody-intake-ledger-rev0365.csv'
fixture_ledger_path=ROOT/'cube/nuclear-emergency-bvps-evidence-intake-fixture-ledger-rev0365.csv'
errors=[]
with contract_path.open(newline='',encoding='utf-8') as f: contract=list(csv.DictReader(f))
with ledger_path.open(newline='',encoding='utf-8') as f: ledger=list(csv.DictReader(f))
with fixture_ledger_path.open(newline='',encoding='utf-8') as f: fixture_rows=list(csv.DictReader(f))
required_classes={'preliminary_findings_AAR_IP','alert_notification_system','protective_action_dose_timeline','AFN_transport_access','EOC_EOF_JIC_operations','corrective_action_retest_ARCA'}
classes={r.get('artifact_class') for r in contract}
if len(contract)<12: errors.append('contract_rows<12')
if not required_classes.issubset(classes): errors.append('missing_required_classes='+','.join(sorted(required_classes-classes)))
for r in contract:
    if r.get('claim_effect')!='no_readiness_closure': errors.append('bad_claim_effect:'+r.get('contract_id',''))
    if 'readiness_closure' not in r.get('forbidden_states_or_claims',''): errors.append('no_forbidden_closure:'+r.get('contract_id',''))
    if 'sha256' not in r.get('minimum_required_metadata','') or 'custodian_or_source' not in r.get('minimum_required_metadata',''):
        errors.append('weak_metadata:'+r.get('contract_id',''))
for r in ledger:
    if r.get('packet_state')!='awaiting_real_or_lawfully_anonymized_packet': errors.append('unexpected_real_ledger_state:'+r.get('ledger_row_id',''))
    if r.get('sha256') or r.get('artifact_path'): errors.append('real_ledger_should_be_empty:'+r.get('ledger_row_id',''))
    if 'no_readiness_closure' not in r.get('claim_effect',''): errors.append('bad_ledger_claim_effect:'+r.get('ledger_row_id',''))
for r in fixture_rows:
    if r.get('fixture_only')!='yes': errors.append('fixture_not_marked:'+r.get('intake_row_id',''))
    if len(r.get('sha256',''))!=64: errors.append('bad_fixture_hash:'+r.get('intake_row_id',''))
    if 'no_readiness_closure' not in r.get('claim_effect',''): errors.append('bad_fixture_claim_effect:'+r.get('intake_row_id',''))
    if r.get('packet_state') not in {'candidate_fixture_only','quarantined_needs_review'}: errors.append('bad_fixture_state:'+r.get('intake_row_id',''))
if errors:
    print('FAIL evidence_intake_contract_light_rev0370 '+';'.join(errors[:20])); sys.exit(1)
print(f'PASS evidence_intake_contract_light_rev0370 contract_rows={len(contract)} fixture_rows={len(fixture_rows)} real_ledger_state=awaiting_packet')
