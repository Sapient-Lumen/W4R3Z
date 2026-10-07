#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['scope_check_id','check','severity','status','expected_count','observed_count','detail']
SAFE_REL_RE=re.compile(r'^[^/\\][^\\]*$')

def package_files(root: Path) -> list[str]:
    out=[]
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        rel=str(p.relative_to(root)).replace('\\','/')
        parts=rel.split('/')
        if rel in {'SHA256SUMS.txt','SHA256SUMS.txt.sig','QA-REPORT-current.txt'}:
            continue
        if p.suffix.lower()=='.zip':
            continue
        if '__pycache__' in parts or p.suffix.lower() in {'.pyc','.pyo'}:
            continue
        out.append(rel)
    return sorted(out)

def read_sha_lines(root: Path):
    p=root/'SHA256SUMS.txt'
    if not p.exists():
        return [], ['missing SHA256SUMS.txt']
    entries=[]; malformed=[]
    for n,line in enumerate(p.read_text(encoding='utf-8', errors='ignore').splitlines(), start=1):
        if not line.strip():
            continue
        parts=line.split(None,1)
        if len(parts)!=2 or not re.fullmatch(r'[0-9a-f]{64}', parts[0]):
            malformed.append(f'line {n}')
            continue
        rel=parts[1].strip()
        if rel.startswith('./'): rel=rel[2:]
        entries.append((parts[0], rel, n))
    return entries, malformed

def add(rows, check, sev, status, exp, obs, detail):
    rows.append({'scope_check_id':f'checksum_scope_{len(rows)+1:03d}','check':check,'severity':sev,'status':status,'expected_count':str(exp),'observed_count':str(obs),'detail':detail})

def run(root: Path):
    rows=[]
    expected=package_files(root)
    entries, malformed=read_sha_lines(root)
    observed=[rel for _digest,rel,_line in entries]
    observed_sorted=sorted(observed)
    if malformed:
        add(rows,'checksum_lines_parse','high','fail',0,len(malformed),'Malformed checksum lines: '+ '; '.join(malformed[:12]))
    else:
        add(rows,'checksum_lines_parse','info','pass',len(observed),len(observed),'All checksum lines parse as sha256 + package-relative path')
    unsafe=[]
    for _digest,rel,line in entries:
        if rel.startswith('/') or '..' in Path(rel).parts or '\\' in rel:
            unsafe.append(f'line {line}: {rel}')
    add(rows,'checksum_paths_package_relative','high' if unsafe else 'info','fail' if unsafe else 'pass',0,len(unsafe),'Unsafe checksum paths: '+ '; '.join(unsafe[:12]) if unsafe else 'All checksum paths are package-relative and contain no traversal/backslash')
    dup=sorted({rel for rel in observed if observed.count(rel)>1})
    add(rows,'checksum_paths_unique','high' if dup else 'info','fail' if dup else 'pass',len(set(observed)),len(observed),'Duplicate checksum paths: '+ '; '.join(dup[:12]) if dup else 'Checksum paths are unique')
    missing_on_disk=sorted(rel for rel in observed if not (root/rel).exists())
    add(rows,'checksum_entries_resolve','high' if missing_on_disk else 'info','fail' if missing_on_disk else 'pass',len(observed),len(observed)-len(missing_on_disk),'Listed checksum paths missing on disk: '+ '; '.join(missing_on_disk[:12]) if missing_on_disk else 'Every checksum entry resolves to a package file')
    expected_set=set(expected); observed_set=set(observed)
    missing_from_sha=sorted(expected_set-observed_set)
    extra_in_sha=sorted(observed_set-expected_set)
    add(rows,'checksum_scope_complete','high' if missing_from_sha else 'info','fail' if missing_from_sha else 'pass',len(expected),len(observed_set & expected_set),'Stable files missing from SHA256SUMS: '+ '; '.join(missing_from_sha[:20]) if missing_from_sha else 'Every stable package file except SHA256SUMS.txt, SHA256SUMS.txt.sig, and QA-REPORT-current.txt is listed')
    add(rows,'checksum_scope_no_extras','high' if extra_in_sha else 'info','fail' if extra_in_sha else 'pass',len(expected),len(observed_set),'Extra checksum entries outside stable scope: '+ '; '.join(extra_in_sha[:20]) if extra_in_sha else 'SHA256SUMS contains no entries outside the stable package scope')
    add(rows,'checksum_entries_sorted','medium' if observed!=observed_sorted else 'info','review' if observed!=observed_sorted else 'pass',len(observed_sorted),len(observed),'Checksum entries are not sorted lexicographically' if observed!=observed_sorted else 'Checksum entries are sorted lexicographically')
    add(rows,'checksum_scope_cardinality','high' if len(expected)!=len(observed_set) else 'info','fail' if len(expected)!=len(observed_set) else 'pass',len(expected),len(observed_set),f'Expected {len(expected)} stable files listed; observed {len(observed_set)} unique checksum entries')
    add(rows,'checksum_hash_values_externalized','info','pass',len(expected),len(observed),'Hash-value correctness is verified by tools/qa_cube.py SHA256SUMS verification after this report is written, avoiding a self-referential checksum loop')
    return rows

def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Checksum-Scope-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Checksum Scope Audit',
        generated_by='tools/checksum_scope_audit.py',
        columns=['check','severity','status','expected_count','observed_count','detail'],
        intro_lines=[
            f"High findings: {sum(1 for r in rows if r.get('severity')=='high')}",
            f"Non-pass rows: {sum(1 for r in rows if r.get('status') not in {'pass'})}",
            'This report audits the scope of SHA256SUMS.txt; actual digest verification remains in tools/qa_cube.py to avoid a self-referential report-hash loop.',
        ],
    )

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high']
    print(f"{'FAIL' if high else 'PASS'} checksum scope rows={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['check']}: {r['detail']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
