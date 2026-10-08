from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
allowed={'pass','static_pass','pending','info'}
with (ROOT/'validation-report-rev0377.csv').open(newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
bad=[r for r in rows if r.get('status') not in allowed]
if bad: raise SystemExit(f'bad status vocabulary: {bad[:5]}')
print(f'PASS validation report status vocabulary rows={len(rows)}')
