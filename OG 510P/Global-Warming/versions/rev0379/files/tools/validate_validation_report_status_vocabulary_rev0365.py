#!/usr/bin/env python3
"""Validate current rev0365 validation report uses explicit status vocabulary."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
allowed={'executed_pass','executed_fail','static_pass','info','pending'}
for rel in ['validation-report-rev0365.json','cube/validation-report-rev0365.json']:
    p=ROOT/rel
    if not p.exists(): print('FAIL missing '+rel); sys.exit(1)
    data=json.load(open(p, encoding='utf-8'))
    statuses=[c.get('status') for c in data.get('checks',[])]
    bad=[s for s in statuses if s not in allowed]
    if bad: print('FAIL bad_statuses '+rel+' '+','.join(sorted(set(map(str,bad))))); sys.exit(1)
    summary=data.get('summary',{})
    if 'pass' in summary or 'fail' in summary: print('FAIL legacy_summary_keys '+rel); sys.exit(1)
    if summary.get('executed_fail',0)!=0: print('FAIL executed_fail_nonzero '+rel); sys.exit(1)
    if not any(s=='pending' for s in statuses): print('FAIL expected_pending_row_missing '+rel); sys.exit(1)
print('PASS validation_report_status_vocabulary_rev0365 allowed=' + ','.join(sorted(allowed)))
