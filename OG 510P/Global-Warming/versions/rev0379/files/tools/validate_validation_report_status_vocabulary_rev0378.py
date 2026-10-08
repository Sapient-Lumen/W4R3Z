from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'validation-report-rev0378.csv'
allowed={'static_pass','executed_pass','pending','info','executed_fail','static_fail'}
rows=list(csv.DictReader(path.open(newline='',encoding='utf-8')))
if not rows:
    raise SystemExit('validation report empty')
for r in rows:
    if r['status'] not in allowed:
        raise SystemExit(f'bad status {r}')
if any(r['status']=='executed_fail' for r in rows):
    raise SystemExit('executed failure present')
print(f'PASS validation_report_status_vocabulary_rev0378 rows={len(rows)}')
