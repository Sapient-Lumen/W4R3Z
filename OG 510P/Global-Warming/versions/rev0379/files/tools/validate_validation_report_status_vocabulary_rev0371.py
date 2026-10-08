#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'validation-report-rev0371.csv'
ALLOWED={'executed_pass','executed_fail','static_pass','info','pending'}
with REPORT.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
bad=[r for r in rows if r.get('status') not in ALLOWED]
if bad:
    print('FAIL bad_status='+','.join(sorted({r.get('status','') for r in bad}))); sys.exit(1)
if not any(r['status']=='pending' and 'real' in r['check_name'].lower() for r in rows):
    print('FAIL missing_real_packet_pending'); sys.exit(1)
if not any(r['status']=='executed_pass' for r in rows):
    print('FAIL missing_executed_pass'); sys.exit(1)
print(f'PASS validation_report_status_vocabulary_rev0371 rows={len(rows)}')
