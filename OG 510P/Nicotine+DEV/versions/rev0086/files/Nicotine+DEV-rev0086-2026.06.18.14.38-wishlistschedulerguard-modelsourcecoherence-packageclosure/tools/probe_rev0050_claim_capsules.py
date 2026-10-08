#!/usr/bin/env python3
from pathlib import Path
import csv,json,subprocess,sys,hashlib
EXP={'U-123','PB-01','SEARCH-RESP-01A','SEARCH-RESP-01B-BUDDY','SEARCH-RESP-01C-ROOM','SEARCH-RESP-PARSE-BUDGET-A','SEARCH-RESP-PARSE-BUDGET-B'}
BAD={'__pycache__','.pytest_cache','source-trees','git-full','.git'}
def rows(p):
    with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def main():
    cube=Path(__file__).resolve().parents[1]; checks=[]; errs=[]
    pr=subprocess.run([sys.executable,str(cube/'tools/probe_rev0049_handoff_gate.py')],cwd=cube,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    try:j=json.loads(pr.stdout)
    except Exception:j={'status':'unparseable'}
    ok=pr.returncode==0 and j.get('status')=='pass'; checks.append({'check':'inherited rev0049 gate','status':'pass' if ok else 'fail'}); errs+=[] if ok else ['rev0049 gate failed']
    ledger=rows(cube/'data/rev0050_claim_ledger.csv'); pk={r['packet'] for r in ledger}; ok=pk==EXP and len(ledger)==7
    checks.append({'check':'claim ledger','status':'pass' if ok else 'fail','count':len(ledger)}); errs+=[] if ok else ['claim ledger mismatch']
    miss=[]
    for r in ledger:
        cap=cube/'handoff/rev0050/capsules'/(r['packet'].lower().replace('/','-')+'.md')
        if not cap.exists(): miss.append(str(cap.relative_to(cube))); continue
        txt=cap.read_text(encoding='utf-8',errors='replace')
        for sec in ['## Minimum claim','## Evidence chain','## Non-claims / filing guardrails','## Public-overlap boundary']:
            if sec not in txt: miss.append(f'{cap.relative_to(cube)} missing {sec}')
    checks.append({'check':'capsule sections','status':'pass' if not miss else 'fail','errors':miss[:10]}); errs+=miss
    non={r['packet'] for r in rows(cube/'data/rev0050_nonclaim_ledger.csv')}; ok=EXP<=non and {'PUBLIC-PATH-JOIN-PR-3781','PUBLIC-PATH-JOIN-PR-3723'}<=non
    checks.append({'check':'nonclaim coverage','status':'pass' if ok else 'fail'}); errs+=[] if ok else ['nonclaim coverage missing']
    merr=[]; man=cube/'handoff/rev0050/MANIFEST.sha256'
    for line in man.read_text(encoding='utf-8').splitlines():
        want,rel=line.split('  ',1); p=cube/rel
        if not p.exists() or sha(p)!=want: merr.append(rel)
    checks.append({'check':'handoff manifest','status':'pass' if not merr else 'fail','errors':merr[:10]}); errs+=merr
    bad=[]
    for p in cube.rglob('*'):
        if any(x in BAD for x in p.relative_to(cube).parts): bad.append(str(p.relative_to(cube)))
    checks.append({'check':'package hygiene','status':'pass' if not bad else 'fail','bad_count':len(bad)}); errs+=bad
    st=(cube/'docs/START-HERE.md').read_text(encoding='utf-8',errors='replace'); rm=(cube/'README.md').read_text(encoding='utf-8',errors='replace')
    ok='rev0050' in st and 'claim capsule' in st and 'rev0050' in rm
    checks.append({'check':'start/readme markers','status':'pass' if ok else 'fail'}); errs+=[] if ok else ['markers missing']
    out={'revision':'rev0050','status':'pass' if not errs else 'fail','claim_capsules':len(ledger),'checks':checks,'errors':errs}
    print(json.dumps(out,indent=2)); return 0 if not errs else 1
if __name__=='__main__':raise SystemExit(main())
