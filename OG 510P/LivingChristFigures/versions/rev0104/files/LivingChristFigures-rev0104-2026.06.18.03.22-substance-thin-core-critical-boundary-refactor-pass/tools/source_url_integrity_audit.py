#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path
from urllib.parse import urlparse
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['finding_id','source_id','domain','url','check_name','severity','status','recommended_action','note']
TRUNCATED_PATTERNS=(re.compile(r'\(\d{2}$'), re.compile(r'%28\d{2}$', re.I), re.compile(r'\.\.\.$'))

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def balanced_parentheses(url: str) -> bool:
    return url.count('(')==url.count(')')

def audit_url(url: str) -> tuple[str,str,str]:
    problems=[]
    if not url.strip():
        problems.append('empty_url')
    else:
        p=urlparse(url)
        if p.scheme not in {'http','https'}: problems.append('bad_scheme')
        if not p.netloc: problems.append('missing_netloc')
        if any(ch.isspace() for ch in url): problems.append('contains_whitespace')
        if not balanced_parentheses(url): problems.append('unbalanced_parentheses')
        if any(rx.search(url) for rx in TRUNCATED_PATTERNS): problems.append('truncated_suffix_pattern')
        if url.endswith(('http://','https://')): problems.append('scheme_only')
    if problems:
        return 'url_structural_integrity','high','fail: '+'|'.join(problems)
    return 'url_structural_integrity','info','pass'

def run(root: Path):
    rows=[]
    for idx,src in enumerate(read_csv(root/'Source-Registry-current.csv'),1):
        check,sev,status=audit_url(src.get('url',''))
        if status=='pass':
            action='no action; URL is structurally parseable'
            note='scheme/netloc/whitespace/parenthesis/truncation checks passed'
        else:
            action='repair URL from authoritative/indexed source or quarantine source row before release'
            note='structural URL defect can cause silent source-health false positives or broken handoff links'
        rows.append({'finding_id':f'suia_{idx:04d}','source_id':src.get('source_id',''),'domain':src.get('domain',''),'url':src.get('url',''),'check_name':check,'severity':sev,'status':status,'recommended_action':action,'note':note})
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Source-URL-Integrity-Audit-current.csv',FIELDS,rows,'Source URL Integrity Audit','tools/source_url_integrity_audit.py',columns=['finding_id','source_id','domain','check_name','severity','status','recommended_action'],intro_lines=['Structural URL audit for every Source Registry row. It catches parse failures, truncated DOI/article strings, whitespace, scheme-only values, and unbalanced parentheses before source-health gates can pass falsely.'],max_md_rows=160)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} source URL integrity rows={len(rows)} high={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['source_id']}: {r['status']} {r['url']}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
