#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append(json.loads(p.read_text(encoding='utf-8')))
inst=[]; missing=[]; unblocked=[]
for d in records:
    classes=set(d.get('record_classes',[]))
    if 'institutional_opacity_axis' in classes:
        inst.append(d['record_id'])
        if not d.get('axes',{}).get('institutional_opacity'):
            missing.append((d['record_id'],'axes.institutional_opacity'))
        if not d.get('provenance',{}).get('evidence_class',{}).get('institutional_opacity_channel'):
            missing.append((d['record_id'],'provenance.evidence_class.institutional_opacity_channel'))
        if not d.get('safety',{}).get('institutional_opacity_gate'):
            missing.append((d['record_id'],'safety.institutional_opacity_gate'))
        if not d.get('review',{}).get('institutional_opacity_review_state'):
            missing.append((d['record_id'],'review.institutional_opacity_review_state'))
        if d.get('review',{}).get('publication_review_state')!='blocked':
            unblocked.append(d['record_id'])
report=json.loads((ROOT/'INSTITUTIONAL-OPACITY-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('institutional_opacity_axis_records') != len(inst):
    raise SystemExit(f'INSTITUTIONAL OPACITY AUDIT FAIL report count mismatch: report={report.get("scope",{}).get("institutional_opacity_axis_records")} actual={len(inst)}')
if missing:
    raise SystemExit('INSTITUTIONAL OPACITY AUDIT FAIL missing '+repr(missing[:20]))
if unblocked:
    raise SystemExit('INSTITUTIONAL OPACITY AUDIT FAIL unblocked '+repr(unblocked[:20]))
print(f'INSTITUTIONAL OPACITY AUDIT OK: {len(inst)} institutional-opacity-axis records; all publication-blocked')
