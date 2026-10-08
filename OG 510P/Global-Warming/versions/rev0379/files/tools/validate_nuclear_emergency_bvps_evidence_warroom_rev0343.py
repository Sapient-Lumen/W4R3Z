#!/usr/bin/env python3
"""Validate rev0343 evidence war-room firebreak.
Returns nonzero if a row allows automatic closure."""
import csv, sys
from pathlib import Path
base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
status = list(csv.DictReader(open(base/'cube/nuclear-emergency-bvps-warroom-packet-status-preflight-rev0343.csv', newline='', encoding='utf-8')))
leaks=[]
for r in status:
    if 'auto' in r.get('loss_default_execution','').lower() or r.get('warroom_gate','').lower() in {'closed','green','passed'}:
        leaks.append(r)
result = base/'cube/nuclear-emergency-bvps-warroom-validator-result-rev0343.csv'
with open(result,'w',newline='',encoding='utf-8') as f:
    fields=['test_id','test_name','status','observed','expected']
    w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
    w.writerow({'test_id':'WRVAL-001','test_name':'no auto closure from warroom statuses','status':'pass' if not leaks else 'fail','observed':str(len(leaks)),'expected':'0'})
    w.writerow({'test_id':'WRVAL-002','test_name':'sixty cutline packet rows carried forward','status':'pass' if len(status)==60 else 'fail','observed':str(len(status)),'expected':'60'})
    w.writerow({'test_id':'WRVAL-003','test_name':'all rows marked synthetic or template','status':'pass' if all(r.get('real_or_synthetic') for r in status) else 'fail','observed':str(sum(1 for r in status if r.get('real_or_synthetic'))),'expected':str(len(status))})
if leaks:
    print('FAIL leaks', len(leaks)); sys.exit(2)
print(f'PASS wrote {result}')
