#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append(json.loads(p.read_text(encoding='utf-8')))
body=[]; missing=[]; unblocked=[]
for d in records:
    classes=set(d.get('record_classes',[]))
    if 'body_disposition_axis' in classes:
        body.append(d['record_id'])
        if not d.get('axes',{}).get('body_disposition'):
            missing.append((d['record_id'],'axes.body_disposition'))
        if not d.get('provenance',{}).get('evidence_class',{}).get('body_disposition_channel'):
            missing.append((d['record_id'],'provenance.evidence_class.body_disposition_channel'))
        if not d.get('safety',{}).get('body_disposition_gate'):
            missing.append((d['record_id'],'safety.body_disposition_gate'))
        if not d.get('review',{}).get('body_disposition_review_state'):
            missing.append((d['record_id'],'review.body_disposition_review_state'))
        if d.get('review',{}).get('publication_review_state')!='blocked':
            unblocked.append(d['record_id'])
report=json.loads((ROOT/'BODY-DISPOSITION-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('body_disposition_axis_records') != len(body):
    raise SystemExit(f'BODY DISPOSITION AUDIT FAIL report count mismatch: report={report.get("scope",{}).get("body_disposition_axis_records")} actual={len(body)}')
if missing:
    raise SystemExit('BODY DISPOSITION AUDIT FAIL missing '+repr(missing[:20]))
if unblocked:
    raise SystemExit('BODY DISPOSITION AUDIT FAIL unblocked '+repr(unblocked[:20]))
print(f'BODY DISPOSITION AUDIT OK: {len(body)} body-disposition-axis records; all publication-blocked')
