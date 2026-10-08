#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append(json.loads(p.read_text(encoding='utf-8')))
env=[]; missing=[]; unblocked=[]
for d in records:
    if 'environment_exposure_axis' in d.get('record_classes',[]):
        env.append(d['record_id'])
        if not d.get('axes',{}).get('environment_exposure'):
            missing.append((d['record_id'],'axes.environment_exposure'))
        if not d.get('provenance',{}).get('evidence_class',{}).get('environment_exposure_channel'):
            missing.append((d['record_id'],'provenance.evidence_class.environment_exposure_channel'))
        if not d.get('safety',{}).get('environment_exposure_gate'):
            missing.append((d['record_id'],'safety.environment_exposure_gate'))
        if not d.get('review',{}).get('environment_exposure_review_state'):
            missing.append((d['record_id'],'review.environment_exposure_review_state'))
        if d.get('review',{}).get('publication_review_state')!='blocked':
            unblocked.append(d['record_id'])
report=json.loads((ROOT/'ENVIRONMENT-EXPOSURE-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('environment_exposure_axis_records') != len(env):
    raise SystemExit(f'ENVIRONMENT EXPOSURE AUDIT FAIL count mismatch: report={report.get("scope",{}).get("environment_exposure_axis_records")} actual={len(env)}')
if missing:
    raise SystemExit('ENVIRONMENT EXPOSURE AUDIT FAIL missing '+repr(missing[:20]))
if unblocked:
    raise SystemExit('ENVIRONMENT EXPOSURE AUDIT FAIL unblocked '+repr(unblocked[:20]))
print(f'ENVIRONMENT EXPOSURE AUDIT OK: {len(env)} environment-exposure-axis records; all publication-blocked')
