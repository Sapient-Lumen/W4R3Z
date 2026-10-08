#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append(json.loads(p.read_text(encoding='utf-8')))
post=[]; missing=[]; unblocked=[]
for d in records:
    classes=set(d.get('record_classes',[]))
    high=set(d.get('safety',{}).get('high_gate_domains',[]))
    is_post='postvention_axis' in classes
    if is_post:
        post.append(d['record_id'])
        if not d.get('axes',{}).get('postvention'): missing.append((d['record_id'],'axes.postvention'))
        if not d.get('axes',{}).get('safe_surface'): missing.append((d['record_id'],'axes.safe_surface'))
        if not d.get('safety',{}).get('safe_surface_gate'): missing.append((d['record_id'],'safety.safe_surface_gate'))
        if not d.get('safety',{}).get('method_silence'): missing.append((d['record_id'],'safety.method_silence'))
        if not d.get('review',{}).get('postvention_review_state'): missing.append((d['record_id'],'review.postvention_review_state'))
        if d.get('review',{}).get('publication_review_state')!='blocked': unblocked.append(d['record_id'])
        if ('suicide_and_self_harm_aftermath' in high or 'suicide_safe' in classes) and not d.get('review',{}).get('suicide_safe_messaging_review_state'):
            missing.append((d['record_id'],'review.suicide_safe_messaging_review_state'))
        if ('overdose_and_substance_related_death_aftermath' in high or 'overdose_stigma_boundary' in classes) and not d.get('review',{}).get('substance_use_stigma_review_state'):
            missing.append((d['record_id'],'review.substance_use_stigma_review_state'))
report=json.loads((ROOT/'POSTVENTION-SAFE-SURFACE-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('postvention_axis_records') != len(post):
    raise SystemExit(f'POSTVENTION SAFE SURFACE AUDIT FAIL report count mismatch: report={report.get("scope",{}).get("postvention_axis_records")} actual={len(post)}')
if missing:
    raise SystemExit('POSTVENTION SAFE SURFACE AUDIT FAIL missing '+repr(missing[:20]))
if unblocked:
    raise SystemExit('POSTVENTION SAFE SURFACE AUDIT FAIL unblocked '+repr(unblocked[:20]))
print(f'POSTVENTION SAFE SURFACE AUDIT OK: {len(post)} postvention-axis records; all publication-blocked')
