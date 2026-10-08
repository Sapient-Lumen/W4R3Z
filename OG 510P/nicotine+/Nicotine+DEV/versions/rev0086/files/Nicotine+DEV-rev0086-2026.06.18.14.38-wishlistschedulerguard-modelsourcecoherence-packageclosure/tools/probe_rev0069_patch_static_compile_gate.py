#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, csv, hashlib, json, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
SRC_SHA='feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b'
LANES=['github-tag-3.3.10','github-branch-3.3.x','github-branch-master']
PATCHES=['u-123-rev0059.patch','pb-01-rev0059.patch','search-resp-source-admission-rev0059.patch','search-resp-parser-budget-rev0059.patch']
FILES=['pynicotine/downloads.py','pynicotine/transfers.py','pynicotine/slskproto.py','pynicotine/search.py','pynicotine/slskmessages.py']
CONSTS={'MAX_SEARCH_RESPONSE_USERNAME_LENGTH':255,'MAX_SEARCH_RESPONSE_RESULT_COUNT':10000}
BAD=['__pycache__','.pytest_cache','source-trees','git-full','.git']
DANGER_NAMES={'eval','exec','__import__'}; DANGER_ATTRS={'system','popen','spawn','Popen'}

def sha(p:Path):
    h=hashlib.sha256();
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def shab(b:bytes): return hashlib.sha256(b).hexdigest()
def wjson(p,o): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def wcsv(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows([{k:r.get(k,'') for k in fields} for r in rows])
def clean():
    for c in list(ROOT.rglob('__pycache__'))+list(ROOT.rglob('.pytest_cache')): shutil.rmtree(c,ignore_errors=True)

def read_source_zip(zp:Path):
    info={'source_zip':str(zp),'exists':zp.exists(),'sha256':'','entries':0,'lanes_found':[],'status':'fail'}; blobs={}
    if not zp.exists(): return info,blobs
    info['sha256']=sha(zp)
    with zipfile.ZipFile(zp) as z:
        names=z.namelist(); info['entries']=len(names)
        for lane in LANES:
            if any(f'/source-trees/{lane}/' in n for n in names): info['lanes_found'].append(lane)
            for rel in FILES:
                m=next((n for n in names if n.endswith(f'/source-trees/{lane}/{rel}')),None)
                if m: blobs[(lane,rel)]=z.read(m)
    info['status']='pass' if info['sha256']==SRC_SHA and set(info['lanes_found'])==set(LANES) and len(blobs)==len(LANES)*len(FILES) else 'fail'
    return info,blobs

def scan(text,filename):
    compile(text,filename,'exec'); tree=ast.parse(text,filename=filename)
    imps=set(); syms=set(); const={}; danger=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):
            for a in n.names: imps.add('import '+a.name)
        elif isinstance(n,ast.ImportFrom): imps.add('from '+('.'*n.level+(n.module or ''))+' import '+','.join(a.name for a in n.names))
        elif isinstance(n,ast.Call):
            if isinstance(n.func,ast.Name) and n.func.id in DANGER_NAMES: danger.append(f'{n.func.id}:{getattr(n,"lineno",0)}')
            if isinstance(n.func,ast.Attribute) and n.func.attr in DANGER_ATTRS: danger.append(f'{n.func.attr}:{getattr(n,"lineno",0)}')
        elif isinstance(n,(ast.Global,ast.Nonlocal)): danger.append(f'{type(n).__name__}:{getattr(n,"lineno",0)}')
    for n in getattr(tree,'body',[]):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): syms.add(type(n).__name__+':'+n.name)
        if isinstance(n,ast.Assign):
            for t in n.targets:
                if isinstance(t,ast.Name):
                    try: const[t.id]=ast.literal_eval(n.value)
                    except Exception: pass
    return imps,syms,const,danger

def negs():
    def syntax():
        try: ast.parse('def broken(:\n'); return False
        except SyntaxError: return True
    return [
      {'control':'syntax_error_detected','status':'pass' if syntax() else 'fail'},
      {'control':'new_import_detected','status':'pass' if scan('import os\n','x')[0]-scan('x=1\n','x')[0] else 'fail'},
      {'control':'removed_symbol_detected','status':'pass' if scan('def f():\n pass\n','x')[1]-scan('x=1\n','x')[1] else 'fail'},
      {'control':'dangerous_eval_detected','status':'pass' if scan("eval('1')\n",'x')[3] else 'fail'},
      {'control':'missing_constant_detected','status':'pass' if 'MAX_SEARCH_RESPONSE_RESULT_COUNT' not in scan('MAX_SEARCH_RESPONSE_USERNAME_LENGTH=255\n','x')[2] else 'fail'}]

def run(zp:Path,work:Path):
    info,blobs=read_source_zip(zp); base=work/'src'; base.mkdir(parents=True,exist_ok=True)
    patch_rows=[]; comp=[]; imp_rows=[]; sym_rows=[]; const_rows=[]; pre={}; post={}
    for lane in LANES:
        lr=base/lane
        for rel in FILES:
            p=lr/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(blobs[(lane,rel)])
            try: im,sy,co,dg=scan(p.read_text(encoding='utf-8'),str(p)); status='pass' if not dg else 'fail'; err=''
            except Exception as e: im=set(); sy=set(); co={}; dg=[]; status='fail'; err=repr(e)
            pre[(lane,rel)]={'i':im,'s':sy,'c':co}; comp.append({'stage':'pre','lane':lane,'file':rel,'sha256':sha(p),'syntax_status':'pass' if not err else 'fail','import_count':len(im),'symbol_count':len(sy),'dangerous_ast_findings':len(dg),'dangerous_ast_sample':';'.join(dg[:3]) or err,'status':status})
        for pa in PATCHES:
            pr=subprocess.run(['patch','-p0','--forward','--batch','-i',str(ROOT/'handoff'/'rev0059'/'patches'/lane/pa)],cwd=lr,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            patch_rows.append({'lane':lane,'patch':pa,'returncode':pr.returncode,'stdout_sha256':shab(pr.stdout.encode()),'stderr_sha256':shab(pr.stderr.encode()),'status':'pass' if pr.returncode==0 else 'fail'})
        for rel in FILES:
            p=lr/rel
            try: im,sy,co,dg=scan(p.read_text(encoding='utf-8'),str(p)); status='pass' if not dg else 'fail'; err=''
            except Exception as e: im=set(); sy=set(); co={}; dg=[]; status='fail'; err=repr(e)
            post[(lane,rel)]={'i':im,'s':sy,'c':co}; comp.append({'stage':'post','lane':lane,'file':rel,'sha256':sha(p),'syntax_status':'pass' if not err else 'fail','import_count':len(im),'symbol_count':len(sy),'dangerous_ast_findings':len(dg),'dangerous_ast_sample':';'.join(dg[:3]) or err,'status':status})
            ai=sorted(im-pre[(lane,rel)]['i']); ri=sorted(pre[(lane,rel)]['i']-im); asy=sorted(sy-pre[(lane,rel)]['s']); rsy=sorted(pre[(lane,rel)]['s']-sy)
            imp_rows.append({'lane':lane,'file':rel,'pre_import_count':len(pre[(lane,rel)]['i']),'post_import_count':len(im),'added_imports':';'.join(ai),'removed_imports':';'.join(ri),'status':'pass' if not ai and not ri and status=='pass' else 'fail'})
            sym_rows.append({'lane':lane,'file':rel,'pre_symbol_count':len(pre[(lane,rel)]['s']),'post_symbol_count':len(sy),'added_symbols':';'.join(asy),'removed_symbols':';'.join(rsy),'status':'pass' if not asy and not rsy and status=='pass' else 'fail'})
        co=post[(lane,'pynicotine/slskmessages.py')]['c']
        for name,exp in CONSTS.items(): const_rows.append({'lane':lane,'constant':name,'value':co.get(name,''),'expected':exp,'status':'pass' if co.get(name)==exp else 'fail'})
    package=[]; clean()
    for part in BAD:
        hit=next((str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if part in p.relative_to(ROOT).parts),'')
        package.append({'path_part':part,'hits':1 if hit else 0,'sample':hit,'status':'fail' if hit else 'pass'})
    return info,patch_rows,comp,imp_rows,sym_rows,const_rows,negs(),package

def write_all(o):
    info,patch_rows,comp,imp_rows,sym_rows,const_rows,neg,package=o; d=ROOT/'data'
    files=[('rev0069_patch_apply_smoke',patch_rows,['lane','patch','returncode','stdout_sha256','stderr_sha256','status']),('rev0069_static_compile_matrix',comp,['stage','lane','file','sha256','syntax_status','import_count','symbol_count','dangerous_ast_findings','dangerous_ast_sample','status']),('rev0069_import_delta',imp_rows,['lane','file','pre_import_count','post_import_count','added_imports','removed_imports','status']),('rev0069_symbol_continuity',sym_rows,['lane','file','pre_symbol_count','post_symbol_count','added_symbols','removed_symbols','status']),('rev0069_constant_contract',const_rows,['lane','constant','value','expected','status']),('rev0069_static_gate_negative_controls',neg,['control','status']),('rev0069_static_gate_package_hygiene',package,['path_part','hits','sample','status'])]
    for stem,rows,fields in files: wcsv(d/f'{stem}.csv',rows,fields); wjson(d/f'{stem}.json',rows)
    wjson(d/'rev0069_source_bundle_identity.json',info)
    summary={'revision':'rev0069','source_bundle_used':True,'source_sha256':info['sha256'],'source_entries':info['entries'],'lanes_found':info['lanes_found'],'source_status':info['status'],'patch_apply_rows':len(patch_rows),'patch_apply_pass':sum(r['status']=='pass' for r in patch_rows),'static_compile_rows':len(comp),'static_compile_pass':sum(r['status']=='pass' and r['syntax_status']=='pass' for r in comp),'import_delta_rows':len(imp_rows),'import_delta_pass':sum(r['status']=='pass' for r in imp_rows),'symbol_continuity_rows':len(sym_rows),'symbol_continuity_pass':sum(r['status']=='pass' for r in sym_rows),'constant_contract_rows':len(const_rows),'constant_contract_pass':sum(r['status']=='pass' for r in const_rows),'negative_controls':len(neg),'negative_controls_pass':sum(r['status']=='pass' for r in neg),'package_hygiene_rows':len(package),'package_hygiene_pass':sum(r['status']=='pass' for r in package),'errors':[]}
    for label,total,passed in [('patch_apply','patch_apply_rows','patch_apply_pass'),('static_compile','static_compile_rows','static_compile_pass'),('import_delta','import_delta_rows','import_delta_pass'),('symbol_continuity','symbol_continuity_rows','symbol_continuity_pass'),('constant_contract','constant_contract_rows','constant_contract_pass'),('negative_controls','negative_controls','negative_controls_pass'),('package_hygiene','package_hygiene_rows','package_hygiene_pass')]:
        if summary[total]!=summary[passed]: summary['errors'].append(label)
    if info['status']!='pass': summary['errors'].append('source_identity')
    summary['status']='pass' if not summary['errors'] else 'fail'; wjson(d/'rev0069_static_compile_summary.json',summary); wjson(d/'rev0069_helper_summary.json',summary); wcsv(d/'rev0069_helper_summary.csv',[summary],list(summary.keys()))
    (ROOT/'evidence'/'rev0069-static-compile-summary.md').write_text(f"# rev0069 static compile / AST contract summary\n\n```text\npatch apply rows: {summary['patch_apply_pass']}/{summary['patch_apply_rows']} pass\nstatic compile rows: {summary['static_compile_pass']}/{summary['static_compile_rows']} pass\nimport delta rows: {summary['import_delta_pass']}/{summary['import_delta_rows']} pass\nsymbol continuity rows: {summary['symbol_continuity_pass']}/{summary['symbol_continuity_rows']} pass\nconstant contract rows: {summary['constant_contract_pass']}/{summary['constant_contract_rows']} pass\nnegative controls: {summary['negative_controls_pass']}/{summary['negative_controls']} pass\nstatus: {summary['status']}\n```\n")
    return summary

def validate(summary):
    stored=json.loads((ROOT/'data'/'rev0069_static_compile_summary.json').read_text()); keys=['status','source_sha256','patch_apply_rows','patch_apply_pass','static_compile_rows','static_compile_pass','import_delta_rows','import_delta_pass','symbol_continuity_rows','symbol_continuity_pass','constant_contract_rows','constant_contract_pass','negative_controls','negative_controls_pass']
    mm=[{'key':k,'stored':stored.get(k),'computed':summary.get(k)} for k in keys if stored.get(k)!=summary.get(k)]
    return {'revision':'rev0069','mode':'validate-existing','status':'pass' if not mm and summary.get('status')=='pass' else 'fail','mismatches':mm,**{k:summary.get(k) for k in keys}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source-zip',type=Path,required=True); ap.add_argument('--validate-existing',action='store_true'); args=ap.parse_args(); work=Path(tempfile.mkdtemp(prefix='rev0069-static-'))
    try:
        summary=write_all(run(args.source_zip,work)); out=validate(summary) if args.validate_existing else summary; print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out['status']=='pass' else 1
    finally:
        clean(); shutil.rmtree(work,ignore_errors=True)
if __name__=='__main__': raise SystemExit(main())
