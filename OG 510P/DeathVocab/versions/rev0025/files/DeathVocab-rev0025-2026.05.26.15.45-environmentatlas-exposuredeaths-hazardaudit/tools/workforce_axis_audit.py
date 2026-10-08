#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append(json.loads(p.read_text(encoding='utf-8')))
worker=[]; missing=[]; unblocked=[]
for d in records:
    classes=set(d.get('record_classes',[]))
    if 'worker_distress_axis' in classes:
        worker.append(d['record_id'])
        axes=d.get('axes',{})
        safety=d.get('safety',{})
        review=d.get('review',{})
        ev=d.get('provenance',{}).get('evidence_class',{})
        if not axes.get('worker_distress'): missing.append((d['record_id'],'axes.worker_distress'))
        if not safety.get('worker_surface_gate'): missing.append((d['record_id'],'safety.worker_surface_gate'))
        if not review.get('worker_support_review_state'): missing.append((d['record_id'],'review.worker_support_review_state'))
        if not review.get('workforce_privacy_review_state'): missing.append((d['record_id'],'review.workforce_privacy_review_state'))
        if not ev.get('worker_distress_channel'): missing.append((d['record_id'],'provenance.evidence_class.worker_distress_channel'))
        if review.get('publication_review_state')!='blocked': unblocked.append(d['record_id'])
report=json.loads((ROOT/'WORKFORCE-AXIS-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('worker_distress_axis_records') != len(worker):
    raise SystemExit(f'WORKFORCE AXIS AUDIT FAIL report count mismatch: report={report.get("scope",{}).get("worker_distress_axis_records")} actual={len(worker)}')
if missing:
    raise SystemExit('WORKFORCE AXIS AUDIT FAIL missing '+repr(missing[:20]))
if unblocked:
    raise SystemExit('WORKFORCE AXIS AUDIT FAIL unblocked '+repr(unblocked[:20]))
print(f'WORKFORCE AXIS AUDIT OK: {len(worker)} worker-distress-axis records; all publication-blocked')
