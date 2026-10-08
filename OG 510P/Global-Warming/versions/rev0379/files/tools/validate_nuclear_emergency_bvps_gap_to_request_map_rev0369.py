#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
blockers=list(csv.DictReader((ROOT/'cube/nuclear-emergency-bvps-closure-blocker-board-rev0368.csv').open(newline='', encoding='utf-8')))
rows=list(csv.DictReader((ROOT/'cube/nuclear-emergency-bvps-gap-to-request-map-rev0369.csv').open(newline='', encoding='utf-8')))
templates={r['template_id'] for r in csv.DictReader((ROOT/'cube/nuclear-emergency-bvps-records-request-templates-rev0369.csv').open(newline='', encoding='utf-8'))}
errors=[]
by_blocker={r.get('blocker_id'):r for r in rows}
for b in blockers:
    bid=b['blocker_id']
    if bid not in by_blocker: errors.append('missing_blocker_map:'+bid); continue
    r=by_blocker[bid]
    tids=[t for t in r.get('linked_template_ids','').split(';') if t and not t.startswith('not_a')]
    if b.get('priority')=='P0' and not tids and 'hotpath' not in r.get('linked_proofcut_class',''): errors.append('P0_without_template:'+bid)
    for t in tids:
        if t not in templates: errors.append('unknown_template:'+bid+':'+t)
    if r.get('claim_effect')!='no_readiness_closure': errors.append('bad_claim_effect:'+bid)
if len(rows)!=len(blockers): errors.append(f'row_count_mismatch maps={len(rows)} blockers={len(blockers)}')
if errors:
    print('FAIL gap_to_request_map_rev0369 ' + ';'.join(errors[:50])); sys.exit(1)
print(f'PASS gap_to_request_map_rev0369 mapped_blockers={len(rows)} templates={len(templates)}')
