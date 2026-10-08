#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, hashlib, importlib.util

def load(p):
    with open(p,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def load_query_module(root):
    spec=importlib.util.spec_from_file_location('query_cube_module', root/'tools/query_cube.py')
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    suite=load(root/'QUERY_REGRESSION_SUITE.yml'); mod=load_query_module(root)
    failures=[]; results=[]
    for q in suite.get('queries',[]):
        name=q['name']
        try:
            out=mod.render_query(root, name)
            rc=0; err=''
        except Exception as e:
            out=''; rc=1; err=repr(e)
        lines=[l for l in out.splitlines() if l.strip()]
        missing=[s for s in q.get('required_substrings',[]) if s not in out]
        if rc or len(lines)<q.get('min_lines',0) or missing:
            failures.append({'query':name,'returncode':rc,'line_count':len(lines),'missing_substrings':missing,'stderr':err})
        results.append({'query':name,'line_count':len(lines),'sha256':hashlib.sha256(out.encode()).hexdigest()[:16]})
    if failures:
        print('QUERY REGRESSION FAILED')
        print(yaml.safe_dump({'failures': failures}, sort_keys=False)); return 1
    print('QUERY REGRESSION PASSED')
    print(yaml.safe_dump({'results': results}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
