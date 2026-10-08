#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    records.append(d)
missing=[d['record_id'] for d in records if not d.get('provenance',{}).get('evidence_class')]
if missing:
    raise SystemExit('EVIDENCE CLASS AUDIT FAIL missing evidence_class '+repr(missing[:20]))
if any(d.get('publication_state')!='quarantined_public_source_pilot' for d in records):
    raise SystemExit('EVIDENCE CLASS AUDIT FAIL non-quarantined record present')
basis=Counter(d['provenance']['evidence_class'].get('basis','unknown') for d in records)
inside=Counter(d['provenance']['evidence_class'].get('inside_view_channel','not_declared') for d in records)
report=json.loads((ROOT/'EVIDENCE-CLASS-AUDIT.json').read_text(encoding='utf-8'))
if report.get('scope',{}).get('records_seen') != len(records):
    raise SystemExit('EVIDENCE CLASS AUDIT FAIL report count mismatch')
print('EVIDENCE CLASS AUDIT OK: %d records labeled; basis=%s; inside_channels=%d' % (len(records), dict(basis), len(inside)))
