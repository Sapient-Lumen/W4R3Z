#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    ledger=load(root/'SOURCE_AUDIT_LEDGER.yml')
    rows=load(root/'CUBE/observations/source_audit.yml').get('source_audit_observations', [])
    summary=ledger.get('summary') or {}
    source_rows=load(root/'CUBE/observations/sources.yml').get('source_observations', [])
    relation_rows=load(root/'CUBE/observations/source_relations.yml').get('source_relation_observations', [])
    if summary.get('source_observation_count') != len(source_rows): failures.append('summary source_observation_count mismatch')
    if summary.get('source_relation_count') != len(relation_rows): failures.append('summary source_relation_count mismatch')
    if summary.get('source_observation_count', 0) < 400: failures.append('source observation count below expected floor')
    if summary.get('source_citation_row_count', 0) < 300: failures.append('source citation row count below expected floor')
    if summary.get('normalized_crosswalk_count', 0) < 100: failures.append('normalized crosswalk count below expected floor')
    if not rows: failures.append('source audit observations absent')
    for r in rows:
        if not r.get('source_audit_observation_id') or not r.get('audit_subject') or not r.get('claim_boundary'):
            failures.append('source audit row missing ID/subject/boundary')
        if r.get('observed_count', 0) < r.get('expected_minimum_count', 0):
            failures.append(f'{r.get("audit_subject")}: observed count below expected minimum')
    if summary.get('live_url_check_completed') is not False: failures.append('ledger should not claim live URL check completed')
    if summary.get('external_source_review_completed') is not False: failures.append('ledger should not claim external source review completed')
    if failures:
        print('SOURCE AUDIT CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('SOURCE AUDIT CHECK PASSED')
    print(yaml.safe_dump({'source_audit_rows': len(rows), 'source_observations': len(source_rows), 'source_relations': len(relation_rows), 'live_url_check_completed': summary.get('live_url_check_completed'), 'status': 'local source audit only'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
