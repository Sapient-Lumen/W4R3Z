#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append(json.loads(p.read_text(encoding='utf-8')))
required=['trajectory','setting','perspective','cultural_tradition_frame','stability','phenomenology','timeline_phase']
missing=[]
for d in records:
    axes=d.get('axes',{})
    for ax in required:
        if not axes.get(ax): missing.append((d['record_id'], ax))
    if 'social_room_axis' in d.get('record_classes',[]) and not axes.get('social_room'):
        missing.append((d['record_id'], 'social_room'))
    if 'pediatric_perinatal_axis' in d.get('record_classes',[]) and not axes.get('pediatric_perinatal'):
        missing.append((d['record_id'], 'pediatric_perinatal'))
    if 'postvention_axis' in d.get('record_classes',[]) and not axes.get('postvention'):
        missing.append((d['record_id'], 'postvention'))
    if 'body_disposition_axis' in d.get('record_classes',[]) and not axes.get('body_disposition'):
        missing.append((d['record_id'], 'body_disposition'))
report=json.loads((ROOT/'AXIS-COVERAGE-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('records_seen') != len(records):
    raise SystemExit('AXIS COVERAGE AUDIT FAIL report count mismatch')
if missing:
    raise SystemExit('AXIS COVERAGE AUDIT FAIL missing axes '+repr(missing[:20]))
print(f'AXIS COVERAGE AUDIT OK: {len(records)} records; pediatric_perinatal_axis={report.get("pediatric_perinatal_integrity",{}).get("pediatric_perinatal_axis_records")}; postvention_axis={report.get("postvention_integrity",{}).get("postvention_axis_records")}; body_disposition_axis={report.get("body_disposition_integrity",{}).get("body_disposition_axis_records")}')
