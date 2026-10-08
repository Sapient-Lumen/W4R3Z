#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'cube/bvps-dlp-redaction-intake-gate-rev0374.csv').open(newline='', encoding='utf-8')))
problems=[]
if len(rows)<6: problems.append('too_few_dlp_rows')
text='\n'.join(str(r).lower() for r in rows)
for needle in ['special assistance','security-sensitive','dispatch receipts','hash','redact','public release']:
    if needle not in text: problems.append('missing_'+needle.replace(' ','_'))
for r in rows:
    if 'public' not in r.get('public_release_rule','').lower(): problems.append('missing_public_rule_'+r.get('gate_id',''))
    if not r.get('required_handling'): problems.append('missing_required_handling_'+r.get('gate_id',''))
sidecar=ROOT/'evidence-intake/bvps-response-sidecar-template-rev0374.csv'
if not sidecar.exists(): problems.append('missing_sidecar_template')
else:
    header=sidecar.read_text(encoding='utf-8').splitlines()[0]
    for col in ['file_name','request_id','redaction_state','dlp_status','proofcut_ids','fixture_only']:
        if col not in header: problems.append('sidecar_missing_'+col)
if problems:
    print('FAIL dlp_redaction_gate_rev0374 '+ '; '.join(problems)); sys.exit(1)
print(f'PASS dlp_redaction_gate_rev0374 rows={len(rows)}')
