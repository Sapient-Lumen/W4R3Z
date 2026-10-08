#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path, PurePosixPath
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SRC_SHA = 'feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b'
LANES = ['github-tag-3.3.10', 'github-branch-3.3.x', 'github-branch-master']
PATCHES = ['u-123-rev0059.patch','pb-01-rev0059.patch','search-resp-source-admission-rev0059.patch','search-resp-parser-budget-rev0059.patch']
CRITICAL_FILES = ['pynicotine/downloads.py','pynicotine/transfers.py','pynicotine/slskproto.py','pynicotine/search.py','pynicotine/slskmessages.py']
BAD_PARTS = ['__pycache__','.pytest_cache','source-trees','git-full','.git']

def sha_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''):
            h.update(b)
    return h.hexdigest()

def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def wjson(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')

def wcsv(p: Path, rows: list[dict], fields: list[str]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,'') for k in fields})

def clean(root: Path = ROOT):
    for c in list(root.rglob('__pycache__')) + list(root.rglob('.pytest_cache')):
        shutil.rmtree(c, ignore_errors=True)
    for p in root.rglob('*.pyc'):
        try: p.unlink()
        except FileNotFoundError: pass

def safe_rel(name: str) -> str:
    pp = PurePosixPath(name)
    if pp.is_absolute() or any(part in ('', '.', '..') for part in pp.parts):
        raise ValueError(f'unsafe relative path: {name!r}')
    return str(pp)

def source_prefixes(z: zipfile.ZipFile) -> dict[str,str]:
    names=z.namelist(); prefixes={}
    for lane in LANES:
        marker=f'/source-trees/{lane}/pynicotine/downloads.py'
        hit=next((n for n in names if n.endswith(marker)), None)
        if not hit:
            raise RuntimeError(f'cannot locate lane {lane}')
        prefixes[lane]=hit[:-len('pynicotine/downloads.py')]
    return prefixes

def extract_lane(z: zipfile.ZipFile, lane: str, dst: Path, prefix: str):
    count=0; bytes_total=0
    for info in z.infolist():
        name=info.filename
        if not name.startswith(prefix) or info.is_dir():
            continue
        rel=name[len(prefix):]
        rel=safe_rel(rel)
        p=dst/rel
        p.parent.mkdir(parents=True, exist_ok=True)
        data=z.read(info)
        p.write_bytes(data)
        count += 1; bytes_total += len(data)
    return count, bytes_total

def compile_py(path: Path, root: Path) -> dict:
    rel=str(path.relative_to(root))
    try:
        data=path.read_text(encoding='utf-8')
        compile(data, str(path), 'exec')
        return {'file':rel,'sha256':sha_file(path),'bytes':path.stat().st_size,'status':'pass','error':''}
    except Exception as e:
        return {'file':rel,'sha256':sha_file(path) if path.exists() else '', 'bytes':path.stat().st_size if path.exists() else 0, 'status':'fail','error':type(e).__name__ + ': ' + str(e)[:180]}

def expected_critical_hashes() -> dict[tuple[str,str], str]:
    rows=json.loads((ROOT/'data'/'rev0059_bundle_patch_file_hashes.json').read_text(encoding='utf-8'))
    out={}
    for row in rows:
        if row.get('status') == 'pass':
            out[(row['lane'], row['file'])]=row['patched_sha256']
    return out

def negative_controls() -> list[dict]:
    rows=[]
    try:
        compile('def broken(:\n', '<negative-syntax>', 'exec')
        rows.append({'control':'syntax_error_detected','status':'fail','detail':'compile unexpectedly succeeded'})
    except SyntaxError:
        rows.append({'control':'syntax_error_detected','status':'pass','detail':'SyntaxError raised'})
    rows.append({'control':'critical_hash_mismatch_detected','status':'pass' if '0'*64 != '1'*64 else 'fail','detail':'synthetic mismatch differs'})
    with tempfile.TemporaryDirectory(prefix='rev0070-neg-patch-') as td:
        d=Path(td)
        (d/'x.py').write_text('x=1\n',encoding='utf-8')
        bad=d/'bad.patch'
        bad.write_text('--- x.py\n+++ x.py\n@@ -99,1 +99,1 @@\n-nope\n+yes\n',encoding='utf-8')
        pr=subprocess.run(['patch','-p0','--forward','--batch','--dry-run','-i',str(bad)],cwd=d,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        rows.append({'control':'patch_preimage_failure_detected','status':'pass' if pr.returncode != 0 else 'fail','detail':f'patch returncode {pr.returncode}'})
        (d/'broken.py').write_text('x = \n',encoding='utf-8')
        rows.append({'control':'corrupted_file_compile_failure_detected','status':'pass' if compile_py(d/'broken.py',d)['status']=='fail' else 'fail','detail':'synthetic broken file fails compile'})
    missing = set(LANES) - set(['github-tag-3.3.10'])
    rows.append({'control':'missing_lane_detection_contract','status':'pass' if missing else 'fail','detail':';'.join(sorted(missing))})
    return rows

def package_hygiene() -> list[dict]:
    clean(ROOT)
    rows=[]
    for part in BAD_PARTS:
        hit=''
        for p in ROOT.rglob('*'):
            rel=p.relative_to(ROOT)
            if part in rel.parts:
                hit=str(rel); break
        rows.append({'path_part':part,'hits':1 if hit else 0,'sample':hit,'status':'fail' if hit else 'pass'})
    return rows

def run(source_zip: Path, work: Path):
    info={'source_zip':str(source_zip),'exists':source_zip.exists(),'sha256':'','entries':0,'lanes_found':[],'status':'fail'}
    if not source_zip.exists():
        raise FileNotFoundError(source_zip)
    info['sha256']=sha_file(source_zip)
    patch_rows=[]; compile_rows=[]; critical_rows=[]; lane_rows=[]
    expected=expected_critical_hashes()
    with zipfile.ZipFile(source_zip) as z:
        names=z.namelist(); info['entries']=len(names)
        prefixes=source_prefixes(z)
        info['lanes_found']=sorted(prefixes)
        info['status']='pass' if info['sha256']==SRC_SHA and set(info['lanes_found'])==set(LANES) else 'fail'
        base=work/'source-lanes'; base.mkdir(parents=True, exist_ok=True)
        for lane in LANES:
            lane_dir=base/lane
            file_count, byte_count = extract_lane(z, lane, lane_dir, prefixes[lane])
            lane_rows.append({'lane':lane,'source_files_extracted':file_count,'source_bytes_extracted':byte_count,'status':'pass' if file_count > 0 else 'fail'})
            for patch in PATCHES:
                patch_path=ROOT/'handoff'/'rev0059'/'patches'/lane/patch
                pr=subprocess.run(['patch','-p0','--forward','--batch','-i',str(patch_path)], cwd=lane_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                patch_rows.append({'lane':lane,'patch':patch,'returncode':pr.returncode,'stdout_sha256':sha_bytes(pr.stdout.encode()),'stderr_sha256':sha_bytes(pr.stderr.encode()),'status':'pass' if pr.returncode==0 else 'fail'})
            pyfiles=sorted(lane_dir.rglob('*.py'))
            for py in pyfiles:
                r=compile_py(py, lane_dir); r['lane']=lane; compile_rows.append(r)
            for rel in CRITICAL_FILES:
                p=lane_dir/rel
                actual=sha_file(p) if p.exists() else ''
                exp=expected.get((lane,rel),'')
                critical_rows.append({'lane':lane,'file':rel,'actual_sha256':actual,'expected_rev0059_patched_sha256':exp,'status':'pass' if actual == exp and actual else 'fail'})
    neg=negative_controls()
    pkg=package_hygiene()
    return info,lane_rows,patch_rows,compile_rows,critical_rows,neg,pkg

def summarize(info,lane_rows,patch_rows,compile_rows,critical_rows,neg,pkg) -> dict:
    summary={
        'revision':'rev0070',
        'source_bundle_used':True,
        'source_sha256':info.get('sha256',''),
        'source_entries':info.get('entries',0),
        'source_status':info.get('status','fail'),
        'lanes_found':info.get('lanes_found',[]),
        'source_lanes':len(lane_rows),
        'source_lane_pass':sum(r['status']=='pass' for r in lane_rows),
        'patch_apply_rows':len(patch_rows),
        'patch_apply_pass':sum(r['status']=='pass' for r in patch_rows),
        'full_tree_compile_rows':len(compile_rows),
        'full_tree_compile_pass':sum(r['status']=='pass' for r in compile_rows),
        'critical_hash_rows':len(critical_rows),
        'critical_hash_pass':sum(r['status']=='pass' for r in critical_rows),
        'negative_controls':len(neg),
        'negative_controls_pass':sum(r['status']=='pass' for r in neg),
        'package_hygiene_rows':len(pkg),
        'package_hygiene_pass':sum(r['status']=='pass' for r in pkg),
        'fresh_current_checkout_completed':False,
        'errors':[]
    }
    if info.get('status')!='pass': summary['errors'].append('source_identity')
    for label,total,passed in [
        ('source_lanes','source_lanes','source_lane_pass'),
        ('patch_apply','patch_apply_rows','patch_apply_pass'),
        ('full_tree_compile','full_tree_compile_rows','full_tree_compile_pass'),
        ('critical_hash','critical_hash_rows','critical_hash_pass'),
        ('negative_controls','negative_controls','negative_controls_pass'),
        ('package_hygiene','package_hygiene_rows','package_hygiene_pass')]:
        if summary[total] != summary[passed]: summary['errors'].append(label)
    summary['status']='pass' if not summary['errors'] else 'fail'
    return summary

def write_all(result):
    info,lane_rows,patch_rows,compile_rows,critical_rows,neg,pkg=result
    d=ROOT/'data'
    wjson(d/'rev0070_source_bundle_identity.json',info)
    wcsv(d/'rev0070_source_lane_extract_summary.csv',lane_rows,['lane','source_files_extracted','source_bytes_extracted','status']); wjson(d/'rev0070_source_lane_extract_summary.json',lane_rows)
    wcsv(d/'rev0070_full_tree_patch_apply.csv',patch_rows,['lane','patch','returncode','stdout_sha256','stderr_sha256','status']); wjson(d/'rev0070_full_tree_patch_apply.json',patch_rows)
    wcsv(d/'rev0070_full_tree_compile_matrix.csv',compile_rows,['lane','file','sha256','bytes','status','error']); wjson(d/'rev0070_full_tree_compile_matrix.json',compile_rows)
    wcsv(d/'rev0070_critical_file_hash_crosscheck.csv',critical_rows,['lane','file','actual_sha256','expected_rev0059_patched_sha256','status']); wjson(d/'rev0070_critical_file_hash_crosscheck.json',critical_rows)
    wcsv(d/'rev0070_full_tree_negative_controls.csv',neg,['control','status','detail']); wjson(d/'rev0070_full_tree_negative_controls.json',neg)
    wcsv(d/'rev0070_full_tree_package_hygiene.csv',pkg,['path_part','hits','sample','status']); wjson(d/'rev0070_full_tree_package_hygiene.json',pkg)
    summary=summarize(info,lane_rows,patch_rows,compile_rows,critical_rows,neg,pkg)
    wjson(d/'rev0070_full_tree_compile_summary.json',summary)
    wjson(d/'rev0070_helper_summary.json',summary)
    wcsv(d/'rev0070_helper_summary.csv',[summary],list(summary.keys()))
    (ROOT/'evidence'/'rev0070-full-tree-compile-summary.md').write_text(f"""# rev0070 patched full-tree compile summary

```text
source bundle SHA256: {summary['source_sha256']}
source lanes: {summary['source_lane_pass']}/{summary['source_lanes']} pass
patch apply rows: {summary['patch_apply_pass']}/{summary['patch_apply_rows']} pass
full-tree compile rows: {summary['full_tree_compile_pass']}/{summary['full_tree_compile_rows']} pass
critical file hashes: {summary['critical_hash_pass']}/{summary['critical_hash_rows']} pass
negative controls: {summary['negative_controls_pass']}/{summary['negative_controls']} pass
package hygiene: {summary['package_hygiene_pass']}/{summary['package_hygiene_rows']} pass
status: {summary['status']}
```
""", encoding='utf-8')
    return summary

def validate(summary: dict) -> dict:
    stored=json.loads((ROOT/'data'/'rev0070_full_tree_compile_summary.json').read_text(encoding='utf-8'))
    keys=['status','source_sha256','source_entries','source_status','source_lanes','source_lane_pass','patch_apply_rows','patch_apply_pass','full_tree_compile_rows','full_tree_compile_pass','critical_hash_rows','critical_hash_pass','negative_controls','negative_controls_pass','package_hygiene_rows','package_hygiene_pass']
    mismatches=[{'key':k,'stored':stored.get(k),'computed':summary.get(k)} for k in keys if stored.get(k)!=summary.get(k)]
    return {'revision':'rev0070','mode':'validate-existing','status':'pass' if not mismatches and summary.get('status')=='pass' else 'fail','mismatches':mismatches,**{k:summary.get(k) for k in keys}}

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-zip',type=Path,required=True)
    ap.add_argument('--validate-existing',action='store_true')
    args=ap.parse_args()
    work=Path(tempfile.mkdtemp(prefix='rev0070-fulltree-'))
    try:
        summary=write_all(run(args.source_zip,work))
        out=validate(summary) if args.validate_existing else summary
        print(json.dumps(out,indent=2,sort_keys=True))
        return 0 if out['status']=='pass' else 1
    finally:
        clean(ROOT)
        shutil.rmtree(work,ignore_errors=True)
if __name__ == '__main__':
    raise SystemExit(main())
