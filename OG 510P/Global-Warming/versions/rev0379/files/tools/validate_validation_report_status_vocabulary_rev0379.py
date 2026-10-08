from pathlib import Path
import csv, sys
ROOT=Path(__file__).resolve().parents[1]
report=ROOT/'validation-report-rev0379.csv'
allowed={'pass','pending','info','fail'}
rows=list(csv.DictReader(report.open(encoding='utf-8')))
bad=[r for r in rows if r.get('status') not in allowed]
if bad:
    raise SystemExit('bad statuses: '+str(bad[:5]))
if any(r['status']=='fail' for r in rows):
    raise SystemExit('validation report contains fail')
print(f'PASS validation report status vocabulary: {len(rows)} rows')
