#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
required={
'RRT-0374-003':'records-requests/bvps-rev0374/rrt-0374-003-pema-rtkl-ans-exercise-afn-capa.md',
'RRT-0374-004':'records-requests/bvps-rev0374/rrt-0374-004-beaver-county-open-records-warning-afn-local-logs.md',
'RRT-0374-005':'records-requests/bvps-rev0374/rrt-0374-005-ohio-ema-columbiana-bvps-exercise-records.md',
}
problems=[]
for rid,rel in required.items():
    p=ROOT/rel
    if not p.exists(): problems.append('missing_'+rid); continue
    t=p.read_text(encoding='utf-8').lower()
    for needle in ['ready_not_sent_from_static_archive','records requested','claim rule','redact']:
        if needle not in t: problems.append(f'{rid}_missing_{needle}')
triage=list(csv.DictReader((ROOT/'cube/bvps-records-dispatch-triage-rev0374.csv').open(newline='', encoding='utf-8')))
tri={r['request_id']:r for r in triage}
for rid,rel in required.items():
    if rid not in tri: problems.append('triage_missing_'+rid)
    elif tri[rid].get('packet_path')!=rel: problems.append('triage_path_mismatch_'+rid)
    elif tri[rid].get('dispatch_posture')!='packet_ready_not_sent_from_static_archive': problems.append('triage_status_'+rid)
manifest=list(csv.DictReader((ROOT/'cube/bvps-local-records-request-packet-manifest-rev0374.csv').open(newline='', encoding='utf-8')))
if {r['request_id'] for r in manifest} != set(required): problems.append('manifest_request_set_mismatch')
if problems:
    print('FAIL local_request_packets_rev0374 '+ '; '.join(problems)); sys.exit(1)
print(f'PASS local_request_packets_rev0374 packets={len(required)} triage_rows={len(triage)}')
