#!/usr/bin/env python3
from __future__ import annotations
import csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
allowed={'executed_pass','executed_fail','static_pass','info','pending'}
errors=[]
for rel in ['validation-report-rev0368.csv','cube/validation-report-rev0368.csv']:
    p=ROOT/rel
    if not p.exists(): errors.append('missing:'+rel); continue
    rows=list(csv.DictReader(p.open(newline='', encoding='utf-8')))
    if not rows: errors.append('empty:'+rel)
    for r in rows:
        if r.get('status') not in allowed: errors.append('bad_status:'+rel+':'+r.get('check_name','?')+':'+str(r.get('status')))
    if not any(r.get('status')=='executed_pass' for r in rows): errors.append('no_executed_pass:'+rel)
    if not any(r.get('status')=='pending' for r in rows): errors.append('no_pending:'+rel)
for rel in ['validation-rules.json','cube/validation-rules.json']:
    p=ROOT/rel
    if not p.exists(): errors.append('missing:'+rel); continue
    obj=json.loads(p.read_text())
    if obj.get('revision')!='rev0368': errors.append('bad_revision:'+rel)
    if set(obj.get('status_vocabulary',[]))!=allowed: errors.append('bad_vocab:'+rel)
if errors:
    print('FAIL status_vocabulary_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print('PASS status_vocabulary_rev0368')
