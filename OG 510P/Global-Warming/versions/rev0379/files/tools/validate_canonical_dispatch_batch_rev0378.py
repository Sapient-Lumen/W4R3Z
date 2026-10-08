from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
batch=ROOT/'cube/bvps-canonical-dispatch-batch-rev0378.csv'
sup=ROOT/'cube/records-request-supersession-ledger-rev0378.csv'
rows=list(csv.DictReader(batch.open(newline='',encoding='utf-8')))
if len(rows)!=8:
    raise SystemExit(f'expected 8 active requests, found {len(rows)}')
ids=[r['active_request_id'] for r in rows]
if len(ids)!=len(set(ids)):
    raise SystemExit('duplicate active request ids')
for r in rows:
    if r['status']!='ready_not_sent':
        raise SystemExit(f"{r['active_request_id']} bad status {r['status']}")
    if not (ROOT/r['request_file']).exists():
        raise SystemExit(f"missing request file {r['request_file']}")
    if not (ROOT/r['receipt_sidecar']).exists():
        raise SystemExit(f"missing sidecar {r['receipt_sidecar']}")
ledger={r['request_id']:r for r in csv.DictReader(sup.open(newline='',encoding='utf-8'))}
for rid in ids:
    if rid not in ledger or ledger[rid]['status']!='canonical_active_ready_not_sent':
        raise SystemExit(f'{rid} not marked canonical active in supersession ledger')
for rid in ['RRT-0373-001','RRT-0375-006','RRT-0373-002','RRT-0374-005']:
    if rid in ledger and ledger[rid]['status']!='superseded_do_not_dispatch':
        raise SystemExit(f'{rid} should be superseded_do_not_dispatch')
print(f'PASS canonical_dispatch_batch_rev0378 active_requests={len(rows)}')
