#!/usr/bin/env python3
"""Validate rev0365 BVPS evidence packet contract and intake fixture."""
import csv, hashlib, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
contract_path=ROOT/'cube/nuclear-emergency-bvps-evidence-packet-contract-rev0365.csv'
ledger_path=ROOT/'cube/nuclear-emergency-bvps-chain-of-custody-intake-ledger-rev0365.csv'
fixture_ledger_path=ROOT/'cube/nuclear-emergency-bvps-evidence-intake-fixture-ledger-rev0365.csv'
fixture_dir=ROOT/'fixtures/bvps-evidence-intake-rev0365/mock-drop'
sidecar=fixture_dir/'metadata.csv'
errors=[]
contract=list(csv.DictReader(open(contract_path, newline='', encoding='utf-8')))
ledger=list(csv.DictReader(open(ledger_path, newline='', encoding='utf-8')))
fixture_rows=list(csv.DictReader(open(fixture_ledger_path, newline='', encoding='utf-8')))
required_classes={'preliminary_findings_AAR_IP','alert_notification_system','protective_action_dose_timeline','AFN_transport_access','EOC_EOF_JIC_operations','corrective_action_retest_ARCA'}
classes={r.get('artifact_class') for r in contract}
if len(contract)<12: errors.append('contract_rows<12')
if not required_classes.issubset(classes): errors.append('missing_required_classes=' + ','.join(sorted(required_classes-classes)))
for r in contract:
    if r.get('claim_effect')!='no_readiness_closure': errors.append('bad_claim_effect:'+r.get('contract_id',''))
    if 'readiness_closure' not in r.get('forbidden_states_or_claims',''): errors.append('no_forbidden_closure:'+r.get('contract_id',''))
    if 'sha256' not in r.get('minimum_required_metadata','') or 'custodian_or_source' not in r.get('minimum_required_metadata',''):
        errors.append('weak_metadata:'+r.get('contract_id',''))
for r in ledger:
    if r.get('packet_state') != 'awaiting_real_or_lawfully_anonymized_packet': errors.append('unexpected_real_ledger_state:'+r.get('ledger_row_id',''))
    if r.get('sha256') or r.get('artifact_path'): errors.append('real_ledger_should_be_empty:'+r.get('ledger_row_id',''))
    if 'no_readiness_closure' not in r.get('claim_effect',''): errors.append('bad_ledger_claim_effect:'+r.get('ledger_row_id',''))
for r in fixture_rows:
    if r.get('fixture_only')!='yes': errors.append('fixture_not_marked:'+r.get('intake_row_id',''))
    if len(r.get('sha256',''))!=64: errors.append('bad_fixture_hash:'+r.get('intake_row_id',''))
    if 'no_readiness_closure' not in r.get('claim_effect',''): errors.append('bad_fixture_claim_effect:'+r.get('intake_row_id',''))
    if r.get('packet_state') not in {'candidate_fixture_only','quarantined_needs_review'}: errors.append('bad_fixture_state:'+r.get('intake_row_id',''))
# Re-run intake tool into a temp file so the validator proves the code path, not just saved output.
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'ledger.csv'
    proc=subprocess.run([sys.executable, str(ROOT/'tools/intake_nuclear_emergency_bvps_evidence_packet_rev0365.py'), '--drop-dir', str(fixture_dir), '--sidecar', str(sidecar), '--out', str(out), '--fixture-mode', '--strict'], cwd=ROOT, text=True, capture_output=True, timeout=20)
    if proc.returncode!=0:
        errors.append('intake_cli_failed=' + (proc.stdout+proc.stderr).replace('\n',' ')[:300])
    else:
        rerun=list(csv.DictReader(open(out, newline='', encoding='utf-8')))
        if len(rerun)!=len(fixture_rows): errors.append('rerun_rowcount_mismatch')
        if [r.get('sha256') for r in rerun] != [r.get('sha256') for r in fixture_rows]: errors.append('rerun_hash_mismatch')
if errors:
    print('FAIL evidence_intake_contract ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS evidence_intake_contract contract_rows={len(contract)} fixture_rows={len(fixture_rows)} real_ledger_state=awaiting_packet')
