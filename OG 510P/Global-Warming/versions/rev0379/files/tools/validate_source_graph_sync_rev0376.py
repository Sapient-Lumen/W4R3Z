from __future__ import annotations
import csv, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def rows(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def sids(s): return [x for x in re.split(r'[;|,\s]+', s or '') if re.fullmatch(r'S\d+', x)]
idx=rows('cube/index.csv'); source=rows('cube/source.csv'); ledger=rows('cube/source-use-ledger.csv'); edges=rows('cube/source-edge-table.csv'); fse=rows('cube/file-source-edge.csv')
sids_index=set()
for r in idx: sids_index.update(sids(r.get('source_ids','')))
source_ids={r['source_id'] for r in source}; ledger_ids={r['source_id'] for r in ledger}
missing_source=sids_index-source_ids; missing_ledger=source_ids-ledger_ids
if missing_source or missing_ledger:
    raise SystemExit(f'source graph mismatch missing_source={sorted(missing_source)} missing_ledger={sorted(missing_ledger)[:10]}')
edge_pairs={(r['file_id'],r['source_id']) for r in edges}
fse_pairs={(r['file_id'],r['source_id']) for r in fse}
expected={(r['id'],sid) for r in idx for sid in sids(r.get('source_ids',''))}
if expected-edge_pairs or expected-fse_pairs:
    raise SystemExit('edge tables missing expected pairs')
print(f'PASS source graph synced: sources={len(source_ids)} indexed_sids={len(sids_index)} edges={len(edge_pairs)}')
