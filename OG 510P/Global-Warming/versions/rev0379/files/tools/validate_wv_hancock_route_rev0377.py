from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def rows(rel):
    with (ROOT/rel).open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
required_paths=[
 'records-requests/bvps-rev0377/rrt-0377-011-wv-dhs-wvemd-hancock-bvps-exercise-evaluator-materials.md',
 'records-requests/bvps-rev0377/rrt-0377-012-hancock-county-oem-bvps-exercise-alerting-eoc-afn-capa.md',
 'cube/bvps-wv-hancock-route-gap-audit-rev0377.csv'
]
missing=[p for p in required_paths if not (ROOT/p).exists()]
if missing: raise SystemExit('missing WV/Hancock path(s): '+repr(missing))
text='\n'.join((ROOT/p).read_text(encoding='utf-8') for p in required_paths if p.endswith('.md'))
for term in ['West Virginia','Hancock County','five business days','AFN','corrective action','withheld']:
    if term not in text: raise SystemExit(f'missing required WV/Hancock request term: {term}')
source_ids={r['source_id'] for r in rows('cube/source.csv')}
for sid in ['S1388','S1389','S1390','S1391','S1392']:
    if sid not in source_ids: raise SystemExit(f'missing source {sid}')
print('PASS WV/Hancock acquisition lane present and route-source backed')
