from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def rows(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))
idx=rows('cube/index.csv')
idx_ids={r['id'] for r in idx}
file_rows=rows('cube/file.csv')
file_ids={r['id'] for r in file_rows}
if idx_ids != file_ids:
    raise SystemExit(f'file.csv mismatch: missing={sorted(idx_ids-file_ids)} extra={sorted(file_ids-idx_ids)}')
ffv=rows('cube/file-field-value.csv')
ffv_ids={r['file_id'] for r in ffv}
missing_ffv=[r['id'] for r in idx if r['id'] not in ffv_ids]
if missing_ffv:
    raise SystemExit(f'file-field-value missing ids: {missing_ffv[:20]}')
tag_edges=rows('cube/file-tag-edge-normalized.csv')
tag_ids={r['file_id'] for r in tag_edges}
tag_fields=['domain_tags','service_floor','hazard_tags','clock_tags','actor_tags','instrument_tags','equity_lenses','degraded_modes','bottlenecks','failure_modes','proof_ledgers','restoration_conflicts','assurance_tests']
missing_tags=[r['id'] for r in idx if any((r.get(f,'') or '').strip() for f in tag_fields) and r['id'] not in tag_ids]
if missing_tags:
    raise SystemExit(f'tag normalized missing ids: {missing_tags[:20]}')
for required in ['580','581','582','583']:
    if required not in file_ids or required not in ffv_ids:
        raise SystemExit(f'tail id {required} not fully normalized')
print(f'PASS file normalization synced: index={len(idx_ids)} file_rows={len(file_rows)} field_rows={len(ffv)} tag_edges={len(tag_edges)}')
