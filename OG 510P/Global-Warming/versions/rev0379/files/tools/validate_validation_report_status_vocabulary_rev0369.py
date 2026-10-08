#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'validation-report-rev0369.csv'
allowed={'executed_pass','executed_fail','static_pass','info','pending'}
if not P.exists(): print('FAIL missing_validation_report_rev0369'); sys.exit(1)
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
errors=[]
for r in rows:
    if r.get('status') not in allowed: errors.append('bad_status:'+r.get('check_name','?')+':'+r.get('status',''))
if not any(r.get('status')=='executed_pass' for r in rows): errors.append('no_executed_pass')
if any(r.get('status')=='executed_fail' for r in rows): errors.append('executed_fail_present')
if errors:
    print('FAIL validation_report_status_vocabulary_rev0369 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS validation_report_status_vocabulary_rev0369 rows={len(rows)}')
