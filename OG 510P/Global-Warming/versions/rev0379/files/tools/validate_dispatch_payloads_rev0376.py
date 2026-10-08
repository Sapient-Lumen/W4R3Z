from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'records-requests/bvps-rev0376/online-form-payloads-rev0376.csv').open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows) < 2:
    raise SystemExit('expected at least two payloads')
for r in rows:
    if r.get('dispatch_status') != 'ready_not_sent_from_static_archive':
        raise SystemExit(f'bad dispatch status {r}')
    body=(r.get('copy_paste_body') or '').lower()
    for term in ['records requested','ens','ipaws','proofcuts targeted','not evidence']:
        if term not in body:
            raise SystemExit(f'payload {r.get("payload_id")} missing {term}')
    if len(body) < 1000:
        raise SystemExit(f'payload {r.get("payload_id")} too short')
print(f'PASS dispatch payloads ready-not-sent count={len(rows)}')
