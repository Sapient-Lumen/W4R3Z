#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append(json.loads(p.read_text(encoding='utf-8')))
missing=[]
count=0
for d in records:
    classes=set(d.get('record_classes',[]))
    if 'official_trace_axis' in classes:
        count += 1
        axes=d.get('axes',{})
        if not axes.get('official_trace'):
            missing.append((d['record_id'],'axes.official_trace'))
        if not axes.get('absence_axis'):
            missing.append((d['record_id'],'axes.absence_axis'))
        ev=d.get('provenance',{}).get('evidence_class',{})
        if not ev.get('official_trace_channel'):
            missing.append((d['record_id'],'provenance.evidence_class.official_trace_channel'))
        if not ev.get('absence_channel'):
            missing.append((d['record_id'],'provenance.evidence_class.absence_channel'))
        review=d.get('review',{})
        if not review.get('official_trace_review_state'):
            missing.append((d['record_id'],'review.official_trace_review_state'))
        if review.get('publication_review_state') != 'blocked':
            missing.append((d['record_id'],'publication_review_state_blocked'))
report=json.loads((ROOT/'OFFICIAL-TRACE-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('official_trace_axis_records') != count:
    raise SystemExit('OFFICIAL TRACE AUDIT FAIL report count mismatch')
if missing:
    raise SystemExit('OFFICIAL TRACE AUDIT FAIL '+repr(missing[:20]))
print(f'OFFICIAL TRACE AUDIT OK: {count} official-trace records; publication blocked')
