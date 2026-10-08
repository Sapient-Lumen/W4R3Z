from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
allowed={'static_pass','pass','pending','info','skip'}
path=ROOT/'validation-report-rev0376.csv'
if not path.exists():
    print('PENDING validation report not written yet')
    sys.exit(0)
with path.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
bad=[r for r in rows if r.get('status') not in allowed]
if bad:
    raise SystemExit(f'bad statuses: {bad[:5]}')
if not rows:
    raise SystemExit('empty validation report')
print(f'PASS validation report status vocabulary rows={len(rows)}')
