#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, collections

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def row_key(data):
    for k,v in data.items():
        if isinstance(v, list): return k
    return None

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    datasets=load(root/'CUBE/datasets.yml').get('datasets', [])
    audit=load(root/'CUBE/observations/cube_audit.yml').get('cube_audit_observations', [])
    by={r.get('dataset_id'):r for r in audit}
    for d in datasets:
        ds=d.get('dataset_id'); art=d.get('artifact')
        if ds not in by: failures.append(f'missing audit row for dataset {ds}')
        if art and not (root/art).exists(): failures.append(f'dataset artifact missing: {art}')
        if ds in by and art and (root/art).exists():
            data=load(root/art); key=row_key(data); actual=len(data.get(key, [])) if key else 0
            if by[ds].get('dataset_row_count') != actual: failures.append(f'{ds}: audit row_count {by[ds].get("dataset_row_count")} != actual {actual}')
    if not audit: failures.append('cube audit observations absent')
    for r in audit:
        if r.get('duplicate_id_count', 0) != 0: failures.append(f'{r.get("dataset_id")}: duplicate IDs detected')
        if not r.get('audit_boundary'): failures.append(f'{r.get("dataset_id")}: missing audit boundary')
    if failures:
        print('CUBE AUDIT CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('CUBE AUDIT CHECK PASSED')
    print(yaml.safe_dump({'datasets_audited': len(audit), 'status': 'local structural audit only'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
