#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

FIELDS=['lineage_check_id','check','severity','status','expected','observed','detail']

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def add(rows, check, sev, ok, expected, observed, detail):
    rows.append({'lineage_check_id':f'lineage_{len(rows)+1:03d}','check':check,'severity':sev if not ok else 'info','status':'pass' if ok else 'fail','expected':str(expected),'observed':str(observed),'detail':detail})

def rev_num(rev: str) -> int:
    m=re.fullmatch(r'rev(\d{4})', rev or '')
    return int(m.group(1)) if m else -1

def run(root: Path):
    rows=[]
    m=read_json(root/'manifest.json')
    pub=read_json(root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json')
    contract=read_json(root/'SCHEMA/Package-Release-Contract-current.json')
    prev=read_json(root/'META/Previous-Release-Fingerprint-current.json')
    build=read_json(root/'BUILD-PROVENANCE-current.json')
    rev=m.get('revision','')
    prev_rev=prev.get('baseline_revision','')
    export=m.get('export_name_without_zip','')
    add(rows,'manifest_revision_shape','high',rev_num(rev)>=0,'revNNNN',rev,'manifest revision must be a normalized four-digit revision id')
    add(rows,'previous_release_fingerprint_present','high',bool(prev.get('stable_files')) and rev_num(prev_rev)>=0,'previous release fingerprint with stable_files',f"{prev_rev} files={prev.get('stable_file_count')}",'previous-release fingerprint is required for delta accountability')
    overlay_rev=prev.get('intervening_overlay_revision','')
    one_step=rev_num(rev)==rev_num(prev_rev)+1
    overlay_bridge=(rev_num(overlay_rev)==rev_num(prev_rev)+1 and rev_num(rev)==rev_num(overlay_rev)+1)
    expected_step=f'{prev_rev}+1' if not overlay_rev else f'{prev_rev}+1 or documented overlay bridge via {overlay_rev}'
    add(rows,'revision_advances_one_step_or_documented_overlay_bridge','high',one_step or overlay_bridge, expected_step, rev, 'current revision should advance from the previous full-cube fingerprint, or explicitly document a one-step diagnostic overlay bridge')
    add(rows,'root_name_matches_export','high',root.name==export, export, root.name, 'extracted package root must match manifest export_name_without_zip')
    add(rows,'export_contains_revision','high',rev in export, rev, export, 'export name must include current revision')
    add(rows,'public_manifest_revision_sync','high',pub.get('revision')==rev and pub.get('package_revision')==rev, rev, f"{pub.get('revision')}/{pub.get('package_revision')}", 'public export manifest revision fields must match manifest')
    add(rows,'release_contract_revision_sync','high',contract.get('package_revision')==rev and contract.get('revision_updated')==rev, rev, f"{contract.get('package_revision')}/{contract.get('revision_updated')}", 'release contract current revision fields must match manifest')
    refresh_paths=m.get('new_refresh_files') or []
    indexed=[r.get('file_path','') for r in read_csv(root/'Refresh-Index-current.csv') if r.get('revision_added')==rev or r.get('indexed_at_revision')==rev]
    add(rows,'current_refresh_note_declared','high',len(refresh_paths)==1 and (root/refresh_paths[0]).exists(),'one manifest current refresh note','|'.join(refresh_paths),'manifest should declare exactly one current refresh note')
    add(rows,'current_refresh_note_indexed','high',bool(refresh_paths) and refresh_paths[0] in indexed, refresh_paths[0] if refresh_paths else '', '|'.join(indexed), 'Refresh-Index must index manifest current refresh note')
    prev_export=str(prev.get('baseline_export_name_without_zip',''))
    add(rows,'previous_export_name_recorded','medium',bool(prev_export), 'baseline export name present', prev_export, 'delta baseline should record previous export identity')
    add(rows,'build_provenance_revision_sync','high',build.get('revision')==rev and build.get('package_revision')==rev, rev, f"{build.get('revision','')}/{build.get('package_revision','')}", 'BUILD-PROVENANCE must carry current package revision')
    add(rows,'build_provenance_export_sync','high',build.get('export_name_without_zip')==export and build.get('package_export_name_without_zip')==export, export, f"{build.get('export_name_without_zip','')} / {build.get('package_export_name_without_zip','')}", 'BUILD-PROVENANCE export names must match manifest/root export')
    add(rows,'build_provenance_previous_revision_sync','high',not prev_rev or build.get('previous_revision')==prev_rev, prev_rev, build.get('previous_revision',''), 'BUILD-PROVENANCE previous revision must match the previous-release fingerprint baseline')
    add(rows,'build_provenance_previous_export_sync','high',not prev_export or build.get('previous_export_name_without_zip')==prev_export, prev_export, build.get('previous_export_name_without_zip',''), 'BUILD-PROVENANCE previous export must match the previous-release fingerprint baseline')
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Version-Lineage-Audit-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Version-Lineage-Audit-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    lines=['# Version Lineage Audit — current','', 'Generated by `tools/version_lineage_audit.py`.', '', f'Checks: {len(rows)}', f'High failures: {len(high)}', '', 'This audit ties the current manifest identity to the previous-release fingerprint, public manifest, release contract, root folder, and current refresh note.', '', '| check | severity | status | observed | detail |','|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['check']} | {r['severity']} | {r['status']} | {str(r['observed']).replace('|','/')} | {r['detail'].replace('|','/')} |")
    (out/'Version-Lineage-Audit-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} version lineage rows={len(rows)} high_fail={len(high)}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
