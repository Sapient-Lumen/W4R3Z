#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    ledger=load(root/'CLAIM_AUDIT_LEDGER.yml')
    audit=load(root/'CUBE/observations/claim_audit.yml').get('claim_audit_observations', [])
    claims=load(root/'CUBE/observations/claims.yml').get('claim_observations', [])
    relations=load(root/'CUBE/observations/claim_relations.yml').get('claim_relation_observations', [])
    if ledger.get('claim_audit_row_count') != len(audit): failures.append('claim audit ledger row count mismatch')
    if ledger.get('claim_observation_count') != len(claims): failures.append('claim observation count mismatch')
    if ledger.get('claim_relation_count') != len(relations): failures.append('claim relation count mismatch')
    for r in audit:
        if not r.get('claim_boundary'): failures.append(f"{r.get('claim_audit_observation_id')} missing claim boundary")
        if r.get('audit_issue_count', 0) not in (0, None): failures.append(f"{r.get('claim_audit_observation_id')} has blocking audit issue count {r.get('audit_issue_count')}")
    if len(audit) < 8: failures.append('claim audit rows too few')
    if failures:
        print('CLAIM AUDIT CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('CLAIM AUDIT CHECK PASSED')
    print(yaml.safe_dump({'claim_audit_rows': len(audit), 'claim_observations': len(claims), 'claim_relations': len(relations), 'external_claim_audit_completed': False, 'status': 'local claim audit only'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
