#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
region=rows('cube/bvps-fema-region-split-audit-rev0375.csv')
triage=rows('cube/bvps-records-dispatch-triage-rev0375.csv')
problems=[]
text='\n'.join(' '.join(r.values()) for r in region).lower()
for needle in ['region 3','region 5','columbiana','11:00','en58200','no readiness']:
    if needle not in text: problems.append('missing_'+needle.replace(' ','_').replace(':',''))
ids={r['request_id']:r for r in triage}
for rid in ['RRT-0375-006','RRT-0375-007','RRT-0375-008']:
    if rid not in ids: problems.append('missing_triage_'+rid)
    elif 'ready_not_sent' not in ids[rid].get('dispatch_posture',''): problems.append('bad_posture_'+rid)
packet_checks={
    'records-requests/bvps-rev0375/rrt-0375-006-fema-region-v-ohio-columbiana-results-briefing-and-evaluator-materials.md':['fema region v','11:00','evaluator','ready_not_sent_from_static_archive'],
    'records-requests/bvps-rev0375/rrt-0375-007-columbiana-county-ema-11am-results-briefing-evidence-packet.md':['columbiana','11:00','results announcement','ready_not_sent_from_static_archive'],
    'records-requests/bvps-rev0375/rrt-0375-008-ohio-ema-radiological-branch-bvps-exercise-ipaws-afn-capa.md':['ohio ema','ipaws','afn','ready_not_sent_from_static_archive'],
}
for rel,needles in packet_checks.items():
    p=ROOT/rel
    if not p.exists(): problems.append('missing_packet_'+rel); continue
    t=p.read_text(encoding='utf-8').lower()
    for n in needles:
        if n not in t: problems.append('packet_missing_'+rel+':'+n)
    if 'request is a dispatch packet, not evidence' not in t and 'this text is a dispatch packet, not evidence' not in t:
        problems.append('packet_claim_rule_weak_'+rel)
if problems:
    print('FAIL bvps_region_split_rev0375 '+ '; '.join(problems[:40])); sys.exit(1)
print(f'PASS bvps_region_split_rev0375 rows={len(region)} packets=3 triage_rows={len(triage)}')
