#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path
sys.dont_write_bytecode=True
from lib_cube import write_csv_json_md_report
FIELDS=['check_id','check','surface','expected_value','observed_value','severity','status','note']

def rjson(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return {}
def rcsv(p):
    if not p.exists(): return []
    with p.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
def add(rows, check, surface, exp, obs, ok, note, sev='high'):
    rows.append({'check_id':f'pointer_{len(rows)+1:03d}','check':check,'surface':surface,'expected_value':str(exp),'observed_value':str(obs),'severity':'info' if ok else sev,'status':'pass' if ok else 'fail','note':note})

def run(root: Path):
    rows=[]; m=rjson(root/'manifest.json'); p=rjson(root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json'); c=rjson(root/'SCHEMA/Package-Release-Contract-current.json')
    rev=m.get('revision',''); export=m.get('export_name_without_zip','')
    add(rows,'root_name_matches_manifest_export','package root',export,root.name,root.name==export,'Root directory and manifest export name must match.')
    for surface,obj,fields in [('manifest',m,['revision','package_revision']),('public_manifest',p,['revision','package_revision']),('package_contract',c,['package_revision','revision_updated'])]:
        for f in fields: add(rows,f'{surface}_{f}_current',surface,rev,obj.get(f,''),obj.get(f,'')==rev,f'{f} must carry current revision.')
    for f in ['export_name_without_zip','package_export_name_without_zip','generated_from_package']:
        add(rows,f'manifest_{f}_root','manifest',root.name,m.get(f,''),m.get(f,'')==root.name,f'{f} must equal root/export name.')
        if f in p: add(rows,f'public_manifest_{f}_root','public_manifest',root.name,p.get(f,''),p.get(f,'')==root.name,f'{f} must equal root/export name.')
    refresh=(m.get('new_refresh_files') or [''])[0] if len(m.get('new_refresh_files') or [])==1 else ''
    add(rows,'current_refresh_file_exists','manifest.new_refresh_files','one existing refresh note',refresh,bool(refresh and (root/refresh).exists()),'Manifest should declare one present current refresh note.')
    idx={r.get('file_path','') for r in rcsv(root/'Refresh-Index-current.csv') if r.get('revision_added')==rev or r.get('indexed_at_revision')==rev}
    add(rows,'current_refresh_file_indexed','Refresh-Index-current.csv',refresh,'|'.join(sorted(idx)),bool(refresh and refresh in idx),'Refresh-Index must index current refresh note.')
    qa=m.get('qa_report','')
    add(rows,'qa_report_pointer_exists','manifest.qa_report','existing current QA/gate surface',qa,bool(qa and (root/qa).exists()),'qa_report pointer must resolve to a current evidence surface and not stale numbered QA.')
    note=str(m.get(f'{rev}_note','') or p.get(f'{rev}_note','') or m.get('release_note','') or p.get('release_note',''))
    add(rows,'current_release_note_mentions_closed_public_layer','manifest/public release note',rev+' + public layer remains closed',note,bool(rev in note and 'public layer remains closed' in note.lower()),'Current release note must state revision and public closure.')
    stale=[]
    pats=[re.compile(r'CURRENT REVISION:\s*rev0064',re.I), re.compile(r'current\s+rev0064',re.I), re.compile(r'"package_revision"\s*:\s*"rev0064"'), re.compile(r'"revision_updated"\s*:\s*"rev0064"')]
    for rel in ['000-START-HERE.txt','CURRENT-SPINE.md','CUBE-MAP.md','PUBLIC/README-public-edition.md','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json','manifest.json']:
        txt=(root/rel).read_text(encoding='utf-8', errors='ignore') if (root/rel).exists() else ''
        if any(pat.search(txt) for pat in pats): stale.append(rel)
    add(rows,'front_door_surfaces_no_stale_previous_revision_rev0064','front-door current surfaces','no stale previous-revision pointers','|'.join(stale),not stale,'Front-door surfaces must not identify the previous revision as the current package.')
    return rows

def write_reports(root, rows):
    write_csv_json_md_report(root, 'META/Current-Pointer-Coherence-Audit-current.csv', FIELDS, rows, 'Current Pointer Coherence Audit', 'tools/current_pointer_coherence_audit.py', columns=['check','surface','expected_value','observed_value','status','note'], intro_lines=[f'High failures: {sum(1 for r in rows if r.get("severity")=="high" and r.get("status")!="pass")}'])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} current pointer coherence rows={len(rows)} high_fail={len(bad)}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
