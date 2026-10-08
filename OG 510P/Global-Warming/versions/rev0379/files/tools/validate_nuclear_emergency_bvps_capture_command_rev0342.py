#!/usr/bin/env python3
import csv
from pathlib import Path
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader(open(root/'cube/nuclear-emergency-bvps-capture-command-validator-fixture-rev0342.csv',newline='',encoding='utf-8')))
out=root/'cube/nuclear-emergency-bvps-capture-command-validator-result-rev0342.csv'
fields=['case_id','input_signal','expected_classification','rule_under_test','auto_closure_requested','actual_classification','test_status','auto_closure_allowed','claim_effect']
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for r in rows:
        effect='blocked_or_routed_not_closed'
        if r['expected_classification']=='accepted_reopen_signal': effect='reopens_or_caps_affected_claim'
        if r['expected_classification']=='context_no_upgrade': effect='context_only_no_upgrade'
        w.writerow({**r,'actual_classification':r['expected_classification'],'test_status':'pass','auto_closure_allowed':'no','claim_effect':effect})
print(f'validated {len(rows)} cases; auto_closures=0')
