from pathlib import Path
import csv, sys
ROOT=Path(__file__).resolve().parents[1]
board=ROOT/'records-requests/bvps-rev0379/operator-submit-board-rev0379.csv'
work=ROOT/'records-requests/bvps-rev0379/workorders'
side=ROOT/'evidence-intake/bvps-rev0379/receipt-sidecars'
if not board.exists():
    raise SystemExit('missing operator submit board')
rows=list(csv.DictReader(board.open(encoding='utf-8')))
if len(rows)!=8:
    raise SystemExit(f'expected 8 active request rows, found {len(rows)}')
missing=[]
for r in rows:
    rid=r['request_id']
    if r.get('dispatch_status')!='ready_not_sent':
        missing.append(f'{rid}: dispatch_status not ready_not_sent')
    if not r.get('route_url') or not r.get('route_source_ids'):
        missing.append(f'{rid}: missing route url/source ids')
    if not (work/f'workorder-{rid}.md').exists():
        missing.append(f'{rid}: missing workorder')
    if not (side/f'sidecar-{rid}.md').exists():
        missing.append(f'{rid}: missing sidecar')
if missing:
    raise SystemExit('\n'.join(missing))
print(f'PASS route target workorders: {len(rows)} active requests')
