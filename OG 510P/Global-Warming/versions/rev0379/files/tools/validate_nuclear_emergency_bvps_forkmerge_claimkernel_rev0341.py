#!/usr/bin/env python3
import csv, sys
rows=list(csv.DictReader(open('cube/nuclear-emergency-bvps-forkmerge-validator-result-rev0341.csv', newline='', encoding='utf-8')))
bad=[r for r in rows if r.get('status')!='pass' or r.get('auto_closure_allowed')!='no']
print(('PASS' if not bad else 'FAIL'), len(rows), 'rev0341 forkmerge checks')
sys.exit(1 if bad else 0)
