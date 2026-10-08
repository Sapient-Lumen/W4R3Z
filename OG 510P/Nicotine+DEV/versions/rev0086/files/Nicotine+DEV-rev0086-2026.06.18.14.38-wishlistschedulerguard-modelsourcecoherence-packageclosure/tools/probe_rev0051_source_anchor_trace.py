#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, os, subprocess, sys, zipfile
from pathlib import Path
LANES={'github-tag-3.3.10','github-branch-3.3.x','github-branch-master'}
PACKETS={'U-123','PB-01','SEARCH-RESP-01A','SEARCH-RESP-01B-BUDDY','SEARCH-RESP-01C-ROOM','SEARCH-RESP-PARSE-BUDGET-A','SEARCH-RESP-PARSE-BUDGET-B'}
BAD={'__pycache__','.pytest_cache','source-trees','git-full','.git'}
def rows(p):
    with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_path(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def source_candidates(arg):
    out=[]
    if arg: out.append(Path(arg))
    env=os.environ.get('NICOTINE_SOURCE_BUNDLE')
    if env: out.append(Path(env))
    out += [Path('/mnt/data/Nicotine-source(1).zip'), Path.cwd().parent/'Nicotine-source(1).zip']
    return [p for p in out if p.exists()]
def build_zip_index(zp):
    idx={}
    z=zipfile.ZipFile(zp)
    for n in z.namelist():
        marker='/source-trees/'
        if marker not in n or '/pynicotine/' not in n: continue
        tail=n.split(marker,1)[1]
        parts=tail.split('/',2)
        if len(parts)==3 and parts[1]=='pynicotine': idx[(parts[0],parts[2])]=n
    return z,idx
def read_source(src, idx, lane, file):
    if src.is_dir():
        p=next(src.rglob(f'source-trees/{lane}/pynicotine/{file}'), None)
        if p: return p.read_bytes()
        p=src/lane/'pynicotine'/file
        if p.exists(): return p.read_bytes()
    else:
        key=(lane,file.replace('pynicotine/',''))
        if key in idx: return idx['_zip'].read(idx[key])
    raise FileNotFoundError(f'{lane} {file}')
def main():
    cube=Path(__file__).resolve().parents[1]; checks=[]; errors=[]
    inherited=cube/'evidence/rev0051-inherited-rev0050-claim-helper-rerun.json'
    try:
        j=json.loads(inherited.read_text(encoding='utf-8'))
    except Exception:
        j={'status':'unparseable'}
    ok=j.get('status')=='pass'
    checks.append({'check':'inherited rev0050 claim helper evidence','status':'pass' if ok else 'fail'})
    errors+=[] if ok else ['inherited rev0050 helper evidence failed']
    cands=source_candidates(sys.argv[1] if len(sys.argv)>1 else None)
    if not cands:
        print(json.dumps({'revision':'rev0051','status':'fail','checks':checks,'errors':errors+['source bundle missing']},indent=2)); return 1
    src=cands[0]; idx={}; z=None
    if src.is_file():
        z,idx0=build_zip_index(src); idx=idx0; idx['_zip']=z
    try:
        anchors=rows(cube/'data/rev0051_source_anchor_trace.csv'); files=rows(cube/'data/rev0051_source_file_manifest.csv')
        ok=len(anchors)==126 and {r['packet'] for r in anchors}==PACKETS and {r['lane'] for r in anchors}==LANES
        checks.append({'check':'anchor ledger shape','status':'pass' if ok else 'fail','rows':len(anchors)}); errors+=[] if ok else ['anchor ledger shape mismatch']
        bad=[]
        for r in anchors:
            b=read_source(src,idx,r['lane'],r['file']); lines=b.decode('utf-8',errors='replace').splitlines(); line=lines[int(r['line'])-1].strip()
            if line!=r['line_text']: bad.append(f"line mismatch {r['anchor_id']} {r['lane']} {r['file']}:{r['line']}")
            if sha_bytes(b)!=r['source_file_sha256']: bad.append(f"hash mismatch {r['lane']} {r['file']}")
        checks.append({'check':'anchor line/hash validation','status':'pass' if not bad else 'fail','bad_count':len(bad),'examples':bad[:5]}); errors+=bad
        badf=[]
        for r in files:
            b=read_source(src,idx,r['lane'],r['file'])
            if sha_bytes(b)!=r['sha256']: badf.append(f"{r['lane']} {r['file']}")
        ok=len(files)==15 and not badf; checks.append({'check':'source file manifest','status':'pass' if ok else 'fail','rows':len(files),'bad':badf[:5]}); errors+=[] if ok else ['source file manifest mismatch']
        merr=[]; man=cube/'handoff/rev0051/MANIFEST.sha256'
        for line in man.read_text(encoding='utf-8').splitlines():
            want,path=line.split('  ',1); p=cube/path
            if not p.exists() or sha_path(p)!=want: merr.append(path)
        checks.append({'check':'rev0051 handoff manifest','status':'pass' if not merr else 'fail','bad':merr[:5]}); errors+=merr
        badpkg=[]
        for p in cube.rglob('*'):
            if any(part in BAD for part in p.relative_to(cube).parts): badpkg.append(str(p.relative_to(cube)))
        checks.append({'check':'package hygiene','status':'pass' if not badpkg else 'fail','bad_count':len(badpkg)}); errors+=badpkg
    finally:
        if z: z.close()
    out={'revision':'rev0051','status':'pass' if not errors else 'fail','source_bundle':str(src),'anchor_rows':len(anchors) if 'anchors' in locals() else 0,'checks':checks,'errors':errors}
    print(json.dumps(out,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
