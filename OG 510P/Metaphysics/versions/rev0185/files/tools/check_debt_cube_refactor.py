#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, collections

def load(p):
    with open(p,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    debts=load(root/'CUBE/observations/debts.yml').get('debt_observations',[])
    index=load(root/'DEBT_OBSERVATION_INDEX.yml').get('debt_observation_index',[])
    relations=load(root/'CUBE/observations/debt_relations.yml').get('debt_relation_observations',[])
    audits=load(root/'CUBE/observations/debt_audit.yml').get('debt_audit_observations',[])
    datasets=[d.get('dataset_id') for d in load(root/'CUBE/datasets.yml').get('datasets',[])]
    for ds in ['DebtCube','DebtRelationCube','DebtAuditCube']:
        if ds not in datasets: failures.append(f'missing dataset: {ds}')
    if len(debts) < 800: failures.append(f'debt observations too few for debt refactor: {len(debts)}')
    if len(index) != len(debts): failures.append(f'debt index mismatch: {len(index)} vs {len(debts)}')
    if len(relations) < len(debts)*5: failures.append('debt relation observations fewer than five per debt')
    if len(audits) < 8: failures.append('debt audit rows too few')
    ids=[r.get('debt_observation_id') for r in debts]
    if len(ids)!=len(set(ids)): failures.append('duplicate debt observation IDs')
    rids=[r.get('debt_relation_observation_id') for r in relations]
    if len(rids)!=len(set(rids)): failures.append('duplicate debt relation IDs')
    required=['debt_family','severity','priority_class','blocked_claim_class','owner_status','lifecycle_status','closure_evidence_required','recurrence_count','claim_boundary']
    for r in debts[:]:
        for f in required:
            if f not in r or r.get(f) in (None,''):
                failures.append(f'{r.get("debt_observation_id")}: missing {f}')
    rel_by_debt=collections.defaultdict(set)
    for r in relations: rel_by_debt[r.get('debt_observation_id')].add(r.get('relation_type'))
    needed={'originates_in_artifact','member_of_debt_family','blocks_claim_class','has_priority_class','has_lifecycle_status'}
    for did in ids:
        if not needed.issubset(rel_by_debt.get(did,set())):
            failures.append(f'{did}: missing relation types')
    if any(r.get('closure_status')=='closed' for r in debts): failures.append('generated debt rows should not claim closed status')
    if failures:
        print('DEBT CUBE REFACTOR CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('DEBT CUBE REFACTOR CHECK PASSED')
    print(yaml.safe_dump({'debt_observations':len(debts),'debt_relation_observations':len(relations),'debt_audit_observations':len(audits),'status':'local debt-cube structural/refactor check only'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
