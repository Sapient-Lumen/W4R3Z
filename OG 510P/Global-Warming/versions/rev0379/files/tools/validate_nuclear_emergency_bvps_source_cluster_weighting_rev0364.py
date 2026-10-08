#!/usr/bin/env python3
"""Validate source aliases are not counted as independent corroboration."""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
rows=list(csv.DictReader(open(ROOT/'cube/nuclear-emergency-bvps-source-cluster-weighted-proof-register-rev0364.csv', newline='', encoding='utf-8')))
errors=[]
if len(rows) < 5:
    errors.append('rowcount')
for r in rows:
    raw=int(r.get('raw_source_count') or 0)
    clu=int(r.get('canonical_cluster_count') or 0)
    if clu > raw:
        errors.append('cluster_gt_raw:'+r.get('proof_surface_id',''))
    if r.get('claim_effect') != 'no_readiness_closure':
        errors.append('claim_effect:'+r.get('proof_surface_id',''))
clock=[r for r in rows if 'clock_BVPS' in r.get('claim_surface','')]
if not clock or clock[0].get('duplicate_alias_present')!='yes' or int(clock[0].get('canonical_cluster_count') or 0) != 1:
    errors.append('BVPS_clock_alias_gate_missing')
if errors:
    print('FAIL source_cluster_weighting ' + ';'.join(errors))
    sys.exit(1)
print(f'PASS source_cluster_weighting rows={len(rows)} aliases_do_not_upgrade_independence')
