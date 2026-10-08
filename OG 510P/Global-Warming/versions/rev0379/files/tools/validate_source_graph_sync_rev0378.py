from __future__ import annotations
import csv, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sources={r['source_id'] for r in csv.DictReader((ROOT/'cube/source.csv').open(newline='',encoding='utf-8'))}
reg=(ROOT/'sources/register.md').read_text(encoding='utf-8')
index=list(csv.DictReader((ROOT/'cube/index.csv').open(newline='',encoding='utf-8')))
used=set()
for row in index:
    for sid in [x.strip() for x in row.get('source_ids','').split(';') if x.strip()]:
        used.add(sid)
missing=used-sources
if missing:
    raise SystemExit(f'source ids missing from source.csv: {sorted(missing)[:10]}')
missing_reg=[sid for sid in used if sid.startswith('S') and f'**{sid}**' not in reg]
if missing_reg:
    raise SystemExit(f'source ids missing from register: {missing_reg[:10]}')
ledger={r['source_id']:r for r in csv.DictReader((ROOT/'cube/source-use-ledger.csv').open(newline='',encoding='utf-8'))}
for sid in used:
    if sid not in ledger:
        raise SystemExit(f'{sid} missing from source-use-ledger')
edges={(r['file_id'],r['source_id']) for r in csv.DictReader((ROOT/'cube/source-edge-table.csv').open(newline='',encoding='utf-8'))}
for row in index:
    for sid in [x.strip() for x in row.get('source_ids','').split(';') if x.strip()]:
        if (row['id'],sid) not in edges:
            raise SystemExit(f'missing source edge {(row["id"],sid)}')
print(f'PASS source_graph_sync_rev0378 sources={len(sources)} used={len(used)} edges={len(edges)}')
