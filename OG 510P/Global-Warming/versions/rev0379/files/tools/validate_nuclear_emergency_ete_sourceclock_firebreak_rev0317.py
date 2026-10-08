#!/usr/bin/env python3
import csv, sys
from pathlib import Path
base = Path(__file__).resolve().parents[1]
res = []
def read(name):
    with open(base/'cube'/name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))
clock = read('nuclear-emergency-bvps-kld-ete-source-clock-reconciliation-rev0317.csv')
fire = read('nuclear-emergency-bvps-ete-clock-firebreak-test-result-rev0317.csv')
han = read('nuclear-emergency-bvps-hancock-wv-offsite-packet-gap-rev0317.csv')
par = read('nuclear-emergency-bvps-tristate-evidence-parity-rev0317.csv')
checks = [
    ('kld_conflict_present', any(r['status']=='conflict_open' for r in clock)),
    ('ohio_kld_reference_found_not_closed', any(r['source_id']=='S1040' and r['status']=='artifact_reference_found_not_closed' for r in clock)),
    ('no_firebreak_closure_leaks', all(r['closure_leak']=='no' and r['status']=='pass' for r in fire)),
    ('hancock_wv_has_p0_packet_gaps', sum(1 for r in han if r['priority']=='P0' and r['status']=='open') >= 10),
    ('wv_parity_hard_block_present', any(r['jurisdiction'].startswith('West Virginia') and 'hard_block' in r['status'] for r in par)),
]
for name, ok in checks:
    res.append({'check_id':name,'status':'pass' if ok else 'fail'})
out = base/'cube'/'nuclear-emergency-bvps-ete-clock-firebreak-validator-run-rev0317.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['check_id','status'])
    w.writeheader(); w.writerows(res)
if not all(r['status']=='pass' for r in res):
    sys.exit(1)
