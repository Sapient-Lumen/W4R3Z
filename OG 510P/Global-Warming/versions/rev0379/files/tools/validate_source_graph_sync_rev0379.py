from pathlib import Path
import csv, re, sys
ROOT=Path(__file__).resolve().parents[1]
def rows(p): return list(csv.DictReader((ROOT/p).open(encoding='utf-8')))
idx=rows('cube/index.csv'); src=rows('cube/source.csv'); ledger=rows('cube/source-use-ledger.csv'); edge=rows('cube/source-edge-table.csv')
source_ids={r['source_id'] for r in src}
ledger_ids={r['source_id'] for r in ledger}
edge_pairs={(r['file_id'],r['source_id']) for r in edge}
missing=[]
for r in idx:
    for sid in [x.strip() for x in re.split(r'[;|]', r.get('source_ids','')) if x.strip()]:
        if sid not in source_ids: missing.append(f'{sid}: missing source.csv')
        if sid not in ledger_ids: missing.append(f'{sid}: missing ledger')
        if (r['id'],sid) not in edge_pairs: missing.append(f'{r["id"]}-{sid}: missing edge')
if missing:
    raise SystemExit('\n'.join(missing[:20]))
print(f'PASS source graph sync: sources={len(source_ids)} index_rows={len(idx)} edges={len(edge_pairs)}')
