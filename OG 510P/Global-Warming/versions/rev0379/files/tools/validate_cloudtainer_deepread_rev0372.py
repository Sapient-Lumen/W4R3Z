#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import csv, json, sys
ROOT = Path(__file__).resolve().parents[1]
errors=[]
required=[
    '579-nuclear-emergency-preparedness-deepread-compilefix-wasteburn-sourceledger-refactor-compact-canon.md',
    'structural-audit-rev0372.md',
    'CHANGELOG-rev0372.md',
    'cube/cloudtainer-deepread-audit-rev0372.csv',
    'cube/cube-waste-audit-rev0372.csv',
    'cube/source-use-ledger-sync-audit-rev0372.csv',
]
for name in required:
    p=ROOT/name
    if not p.exists() or p.stat().st_size == 0:
        errors.append(f'missing_or_empty {name}')
with (ROOT/'cube/cloudtainer-deepread-audit-rev0372.csv').open(newline='', encoding='utf-8') as f:
    rows={r['metric']:r for r in csv.DictReader(f)}
if rows.get('real_bvps_evidence_packet_rows',{}).get('value') != '0':
    errors.append('real_evidence_packet_rows_not_zero')
claim=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8')).get('claim_state','')
if 'no local readiness conclusion' not in claim or 'claim-frozen' not in claim:
    errors.append('claim_freeze_missing_from_manifest')
with (ROOT/'cube/source-use-ledger-sync-audit-rev0372.csv').open(newline='', encoding='utf-8') as f:
    source_rows=list(csv.DictReader(f))
for sid in ['S1356','S1357','S1358']:
    row=next((r for r in source_rows if r.get('source_id')==sid), None)
    if not row:
        errors.append(f'missing_source_sync_row {sid}')
    elif row.get('in_source_use_ledger_csv') != 'false':
        errors.append(f'expected_ledger_gap_flag_for {sid}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('PASS cloudtainer_deepread_rev0372 audits=3 claim_freeze=ok')
