from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'cube/bvps-tristate-custodian-dispatch-board-rev0377.csv').open(newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
req={r['request_id'] for r in rows}
needed={'RRT-0373-001','RRT-0377-011','RRT-0377-012','RRT-0374-003','RRT-0374-004','RRT-0375-006','RRT-0376-009','RRT-0376-010','RRT-0373-002'}
missing=needed-req
if missing: raise SystemExit(f'missing dispatch board requests: {sorted(missing)}')
for r in rows:
    if r['dispatch_status']!='ready_not_sent': raise SystemExit(f"unexpected dispatch status {r['request_id']}={r['dispatch_status']}")
    if not r['proofcuts'] or not r['next_human_action'] or not r['followup_clock']:
        raise SystemExit(f'incomplete dispatch row {r}')
print(f'PASS tri-state dispatch board complete rows={len(rows)}')
