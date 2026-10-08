#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    ledger=load(root/'DEBT_AUDIT_LEDGER.yml')
    rows=load(root/'CUBE/observations/debt_audit.yml').get('debt_audit_observations',[])
    debts=load(root/'CUBE/observations/debts.yml').get('debt_observations',[])
    relations=load(root/'CUBE/observations/debt_relations.yml').get('debt_relation_observations',[])
    summary=ledger.get('summary') or {}
    if summary.get('debt_observation_count') != len(debts): failures.append('debt observation count mismatch')
    if summary.get('debt_relation_count') != len(relations): failures.append('debt relation count mismatch')
    if summary.get('debt_audit_row_count') != len(rows): failures.append('debt audit row count mismatch')
    if summary.get('owner_assignment_claimed') is not False: failures.append('owner assignment must remain unclaimed')
    if summary.get('debt_closure_claimed') is not False: failures.append('debt closure must remain unclaimed')
    if summary.get('external_remediation_review_completed') is not False: failures.append('external remediation review must remain unclaimed')
    for r in rows:
        if not r.get('claim_boundary'): failures.append(f'{r.get("debt_audit_observation_id")} missing claim boundary')
        if r.get('observed_count',0) < r.get('expected_minimum_count',0): failures.append(f'{r.get("audit_subject")}: observed below expected')
        if r.get('audit_issue_count',0) not in (0,None): failures.append(f'{r.get("debt_audit_observation_id")} has blocking issue count')
    if len(rows)<8: failures.append('debt audit rows too few')
    if failures:
        print('DEBT AUDIT CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('DEBT AUDIT CHECK PASSED')
    print(yaml.safe_dump({'debt_audit_rows':len(rows),'debt_observations':len(debts),'debt_relations':len(relations),'debt_closure_claimed':summary.get('debt_closure_claimed'),'status':'local debt audit only'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
