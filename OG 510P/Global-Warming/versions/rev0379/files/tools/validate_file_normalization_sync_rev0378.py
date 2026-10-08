from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
index=list(csv.DictReader((ROOT/'cube/index.csv').open(newline='',encoding='utf-8')))
files=list(csv.DictReader((ROOT/'cube/file.csv').open(newline='',encoding='utf-8')))
idx_ids={r['id'] for r in index}
file_ids={r['id'] for r in files}
if idx_ids!=file_ids:
    raise SystemExit(f'file.csv id sync mismatch index_only={sorted(idx_ids-file_ids)[-5:]} file_only={sorted(file_ids-idx_ids)[-5:]}')
if '585' not in idx_ids:
    raise SystemExit('file 585 missing from index')
# ensure normalized tables include file 585
for rel, col in [('cube/file-field-value.csv','file_id'),('cube/file-tag-edge-normalized.csv','file_id')]:
    seen=set()
    with (ROOT/rel).open(newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r[col]=='585':
                seen.add(r[col])
                break
    if '585' not in seen:
        raise SystemExit(f'{rel} missing file 585')
print(f'PASS file_normalization_sync_rev0378 ids={len(idx_ids)}')
