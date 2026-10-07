#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, shutil, sys, tempfile, zipfile
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['check','severity','status','observed_value','detail']

def sha(p: Path) -> str:
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def iter_files(root: Path):
    skip={'SHA256SUMS.txt','SHA256SUMS.txt.sig','QA-REPORT-current.txt'}
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=str(p.relative_to(root))
        if rel in skip or rel.endswith('.zip') or '/__pycache__/' in rel or rel.endswith(('.pyc','.pyo')):
            continue
        yield rel,p

def run(root: Path):
    files=list(iter_files(root))
    rows=[]
    rows.append({'check':'roundtrip_file_set_nonempty','severity':'high','status':'pass' if files else 'fail','observed_value':str(len(files)),'detail':'files eligible for archive roundtrip excluding generated checksum/signature/report surfaces'})
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); z=td/'roundtrip.zip'; out=td/'extract'
        with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
            for rel,p in files:
                zf.write(p, arcname=rel)
        with zipfile.ZipFile(z,'r') as zf:
            infos=[i for i in zf.infolist() if not i.is_dir()]
            zf.extractall(out)
        stored=[i.filename for i in infos if i.compress_type != zipfile.ZIP_DEFLATED]
        total_file=sum(i.file_size for i in infos)
        total_comp=sum(i.compress_size for i in infos)
        ratio=(total_comp/total_file) if total_file else 1.0
        rows.append({'check':'zip_members_all_deflated','severity':'high','status':'pass' if not stored and bool(infos) else 'fail','observed_value':str(len(stored)),'detail':'temporary roundtrip zip must use ZIP_DEFLATED for every file member; stored examples: '+('; '.join(stored[:5]) if stored else 'none')})
        rows.append({'check':'zip_compression_saves_bytes','severity':'high','status':'pass' if total_file>0 and total_comp<total_file else 'fail','observed_value':f'{total_comp}/{total_file} ratio={ratio:.4f}','detail':'temporary roundtrip zip must reduce bytes, catching accidental ZIP_STORED/no-compression package builds'})
        missing=[]; changed=[]
        for rel,p in files:
            q=out/rel
            if not q.exists(): missing.append(rel)
            elif sha(q)!=sha(p): changed.append(rel)
        rows.append({'check':'roundtrip_no_missing_files','severity':'high','status':'pass' if not missing else 'fail','observed_value':str(len(missing)),'detail':'; '.join(missing[:10])})
        rows.append({'check':'roundtrip_no_hash_drift','severity':'high','status':'pass' if not changed else 'fail','observed_value':str(len(changed)),'detail':'; '.join(changed[:10])})
        rows.append({'check':'roundtrip_member_count_matches','severity':'medium','status':'pass' if len(infos)==len(files) else 'fail','observed_value':f'zip={len(infos)} source={len(files)}','detail':'temporary archive file-member count equals eligible source files'})
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root, 'META/Archive-Roundtrip-Audit-current.csv', FIELDS, rows, 'Archive Roundtrip Audit', 'tools/archive_roundtrip_audit.py', columns=['check','severity','status','observed_value','detail'], intro_lines=[f'High failures: {sum(1 for r in rows if r.get("severity")=="high" and r.get("status")!="pass")}', 'Rev0086 adds deflate/compression-savings assertions so a package cannot silently regress to ZIP_STORED/no-compression output.'])
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} archive roundtrip rows={len(rows)} high_fail={len(bad)}")
    if args.fail_on_fail and bad: sys.exit(1)
if __name__=='__main__': main()
