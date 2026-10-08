#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, re

def load(p):
    with open(p,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def defined_tokens(root):
    v=load(root/'STATUS_VOCABULARY.yml'); out=set()
    for cf in v.get('code_families',[]): out.update((cf.get('codes') or {}).keys())
    return out

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    version=(root/'VERSION').read_text(encoding='utf-8').strip()
    mat=load(root/'TRACEABILITY_MATRIX.yml')
    tokens=defined_tokens(root)
    failures=[]; rows=[]
    for r in mat.get('requirements',[]):
        miss=[]
        for key in ['controlling_doc']:
            if r.get(key) and not (root/r[key]).exists(): miss.append(r[key])
        for key in ['primary_artifacts','records','checks']:
            for rel in r.get(key,[]) or []:
                if not (root/rel).exists(): miss.append(rel)
        bad_tokens=[t for t in r.get('status_tokens',[]) if t not in tokens]
        if bad_tokens: failures.append({'requirement_id':r.get('requirement_id'),'bad_status_tokens':bad_tokens})
        if miss: failures.append({'requirement_id':r.get('requirement_id'),'missing_paths':miss})
        if r.get('critical') and (not r.get('primary_artifacts') or not r.get('records') or not r.get('checks') or not r.get('query_names') or not r.get('status_tokens')):
            failures.append({'requirement_id':r.get('requirement_id'),'critical_row_incomplete':True})
        rows.append({'requirement_id':r.get('requirement_id'),'critical':bool(r.get('critical')),'paths_missing':len(miss),'tokens_bad':len(bad_tokens)})
    report={'traceability_report_version':f'{version}-traceability-report-v1','archive_version':version,'status':'TRC3_coverage_checked; TRC4_uncovered_critical_artifact_absent' if not failures else 'TRC6_unsafe_traceability_claim','summary':{'requirements_checked':len(rows),'failures':len(failures)},'rows':rows,'failures':failures}
    print(yaml.safe_dump(report, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__=='__main__': raise SystemExit(main())
