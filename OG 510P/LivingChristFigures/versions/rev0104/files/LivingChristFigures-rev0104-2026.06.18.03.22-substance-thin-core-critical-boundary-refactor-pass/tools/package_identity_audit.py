#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

FIELDS=['identity_check_id','check','severity','status','expected_value','observed_value','detail']

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def add(rows, check, sev, ok, expected, observed, detail):
    rows.append({'identity_check_id':f'package_identity_{len(rows)+1:03d}','check':check,'severity':sev if not ok else 'info','status':'pass' if ok else 'fail','expected_value':str(expected),'observed_value':str(observed),'detail':detail})

def run(root: Path):
    rows=[]
    m=read_json(root/'manifest.json')
    pub=read_json(root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json')
    contract=read_json(root/'SCHEMA/Package-Release-Contract-current.json')
    rev=m.get('revision','')
    export=m.get('export_name_without_zip','')
    add(rows,'root_name_matches_manifest_export','high',root.name==export,export,root.name,'package root directory must match manifest export_name_without_zip')
    add(rows,'revision_values_match','high',bool(rev) and pub.get('revision')==rev and pub.get('package_revision')==rev and contract.get('package_revision')==rev,rev,f"public={pub.get('revision')}/{pub.get('package_revision')}; contract={contract.get('package_revision')}",'manifest, public manifest, and package contract must agree on current revision')
    add(rows,'export_name_contains_revision','high',bool(rev) and rev in export,rev,export,'export name should contain current revision')
    add(rows,'export_name_has_no_zip_suffix','medium',not export.endswith('.zip'), 'no .zip suffix', export, 'export_name_without_zip must not include .zip suffix')

    new_refresh=m.get('new_refresh_files') or []
    refresh_rows=read_csv(root/'Refresh-Index-current.csv')
    indexed=[r.get('file_path','') for r in refresh_rows if r.get('revision_added')==rev]
    add(rows,'manifest_new_refresh_file_exists','high',len(new_refresh)==1 and (root/new_refresh[0]).exists(), 'one existing refresh note', '|'.join(new_refresh), 'current manifest should name exactly one existing current revision refresh note')
    add(rows,'refresh_index_current_revision_row_exists','high',len(indexed)>=1 and all((root/p).exists() for p in indexed), 'at least one indexed current refresh note', '|'.join(indexed), 'Refresh-Index must index current revision refresh note(s)')
    add(rows,'manifest_refresh_matches_refresh_index','high',bool(new_refresh) and set(new_refresh).issubset(set(indexed)), '|'.join(new_refresh), '|'.join(indexed), 'manifest current refresh note should be present in Refresh-Index')

    archive_rows=read_csv(root/'META/Archive-Build-Manifest-current.csv')
    archive_root=next((r.get('value','') for r in archive_rows if r.get('check')=='root_directory_matches_export_name'), '')
    add(rows,'archive_build_manifest_root_matches','high',archive_root==export,export,archive_root,'archive-build manifest must carry the same root/export name')
    member_rows=read_csv(root/'META/Archive-Member-Manifest-current.csv')
    member_prefixes={r.get('member_path','').split('/')[0] for r in member_rows if r.get('member_path')}
    add(rows,'archive_member_root_prefix_matches','high',member_rows and member_prefixes=={export},export,'|'.join(sorted(member_prefixes)),'every archive member path should be rooted under manifest export name')
    member_bad=[r.get('package_path','') for r in member_rows if r.get('status')!='pass']
    add(rows,'archive_member_manifest_all_pass','high',not member_bad,'no non-pass member rows','|'.join(member_bad[:12]),'archive member manifest must have no non-pass rows')

    checksum_rows=read_csv(root/'META/Checksum-Scope-Audit-current.csv')
    complete=next((r for r in checksum_rows if r.get('check')=='checksum_scope_complete'), {})
    cardinality=next((r for r in checksum_rows if r.get('check')=='checksum_scope_cardinality'), {})
    add(rows,'checksum_scope_currently_complete','high',complete.get('status')=='pass' and cardinality.get('status')=='pass','checksum scope pass',f"complete={complete.get('status')}; cardinality={cardinality.get('status')}",'checksum-scope audit must prove complete stable-file coverage')

    unicode_rows=read_csv(root/'META/Unicode-Path-Audit-current.csv')
    unicode_bad=[r.get('check','') for r in unicode_rows if r.get('severity')=='high' and r.get('status')!='pass']
    add(rows,'unicode_path_audit_zero_high_fail','high',unicode_rows and not unicode_bad,'zero high/fail Unicode path rows','|'.join(unicode_bad[:12]),'Unicode/path audit must have zero high failures')
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Package-Identity-Audit-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Package-Identity-Audit-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    high=sum(1 for r in rows if r.get('severity')=='high'); fail=sum(1 for r in rows if r.get('status')=='fail')
    lines=['# Package Identity Audit — current','', 'Generated by `tools/package_identity_audit.py`.', '', f'High findings: {high}', f'Failed rows: {fail}', '', 'This audit ties the manifest identity, public manifest, release contract, root folder, refresh index, archive-build manifest, archive-member manifest, checksum scope, and Unicode-path audit into one handoff identity proof.', '', '| check | severity | status | expected | observed |','|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['check']} | {r['severity']} | {r['status']} | `{str(r['expected_value']).replace('|','/')}` | `{str(r['observed_value']).replace('|','/')}` |")
    (out/'Package-Identity-Audit-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} package identity audit rows={len(rows)} high_fail={len(high)}")
    for r in high[:20]: print(f"HIGH {r['check']}: {r['observed_value']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
