#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))
route=rows('cube/bvps-records-route-reverification-rev0373.csv')
triage=rows('cube/bvps-records-dispatch-triage-rev0373.csv')
templates=rows('cube/nuclear-emergency-bvps-records-request-templates-rev0373.csv')
problems=[]
if len(route)<7: problems.append('route_rows_lt_7')
if len(triage)<5: problems.append('triage_rows_lt_5')
for r in route:
    if not r.get('current_route_url'): problems.append('route_missing_url_'+r.get('route_id',''))
    if 'not evidence' not in (r.get('do_not_infer','').lower()) and 'not proof' not in (r.get('do_not_infer','').lower()): problems.append('weak_do_not_infer_'+r.get('route_id',''))
for r in triage:
    if 'sent' in r.get('dispatch_posture','').lower() and 'not_sent' not in r.get('dispatch_posture','').lower():
        problems.append('forbidden_sent_posture_'+r.get('request_id',''))
required_templates={'records-requests/bvps-rev0373/rrt-0373-001-fema-region-3-online-foia-public-meeting-followup.md','records-requests/bvps-rev0373/rrt-0373-002-nrc-adams-foia-eof-ler-fema-transmittal-followup.md','records-requests/bvps-rev0373/immediate-dispatch-order-rev0373.md'}
for rel in required_templates:
    if not (ROOT/rel).exists(): problems.append('missing_template_'+rel)
source_ids=';'.join(r.get('source_ids','') for r in route+triage) + ';' + ';'.join(r.get('route_source_ids','') for r in templates)
for sid in [f'S{i}' for i in range(1365,1372)]:
    if sid not in source_ids: problems.append('missing_route_source_'+sid)
if problems:
    print('FAIL route_reverification_rev0373 '+ '; '.join(problems)); sys.exit(1)
print(f'PASS route_reverification_rev0373 routes={len(route)} triage={len(triage)} templates={len(templates)}')
