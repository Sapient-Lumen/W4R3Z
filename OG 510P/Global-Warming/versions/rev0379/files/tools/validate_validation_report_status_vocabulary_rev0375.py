#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
allowed={'executed_pass','executed_fail','static_pass','info','pending'}
path=ROOT/'validation-report-rev0375.csv'
with path.open(newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
bad=[(i+2,r.get('status','')) for i,r in enumerate(rows) if r.get('status') not in allowed]
if bad:
    print('FAIL validation_report_status_vocabulary_rev0375 '+str(bad[:20])); sys.exit(1)
print(f'PASS validation_report_status_vocabulary_rev0375 rows={len(rows)}')
