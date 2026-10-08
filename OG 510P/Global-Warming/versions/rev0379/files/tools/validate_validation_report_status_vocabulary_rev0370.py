#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'validation-report-rev0370.csv'
allowed={'executed_pass','executed_fail','static_pass','info','pending'}
with P.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
bad=[r for r in rows if r.get('status') not in allowed]
if bad:
    print('FAIL bad_status='+str(bad[:3])); sys.exit(1)
print(f'PASS validation_report_status_vocabulary_rev0370 rows={len(rows)}')
