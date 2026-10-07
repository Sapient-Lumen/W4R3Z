#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['finding_id','severity','check','file','row','detail','field_schema_status']
REQUIRED_SCHEMA_HEADER=['field','required','allowed_values_or_pattern','meaning']
SEARCH_DIRS=['.','META','GOVERNANCE','SCHEMA','PUBLIC']


def read_csv_rows(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def read_header(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f:
        try: return next(csv.reader(f))
        except StopIteration: return []


def add(rows, sev, check, file, row, detail, status):
    rows.append({'finding_id':f'fsca_{len(rows)+1:04d}','severity':sev,'check':check,'file':file,'row':str(row),'detail':detail,'field_schema_status':status})


def exact_target(root: Path, schema_file: Path):
    base=schema_file.name[:-len('-Fields-current.csv')]
    for d in SEARCH_DIRS:
        p=(root/d/(base+'-current.csv')).resolve() if d!='.' else (root/(base+'-current.csv')).resolve()
        try:
            rel=str(p.relative_to(root))
        except Exception:
            rel=str(p)
        if p.exists(): return p, rel
    return None, ''


def run(root: Path):
    rows=[]
    schemas=sorted((root/'SCHEMA').glob('*-Fields-current.csv'))
    exact_count=0
    schema_only=0
    for sp in schemas:
        rel=str(sp.relative_to(root))
        header=read_header(sp)
        if header != REQUIRED_SCHEMA_HEADER:
            add(rows,'high','field_schema_header',rel,0,f'header {header} != {REQUIRED_SCHEMA_HEADER}','invalid_schema')
            continue
        sr=read_csv_rows(sp)
        fields=[r.get('field','') for r in sr]
        for comp in [sp.with_suffix('.json'), sp.with_suffix('.md')]:
            if not comp.exists():
                add(rows,'high','field_schema_companion',rel,0,f'missing companion {comp.name}','missing_companion')
        seen=set(); dup=[]
        for i,f in enumerate(fields, start=2):
            if not f:
                add(rows,'high','field_schema_field_nonempty',rel,i,'empty field name','invalid_schema')
            if f in seen: dup.append(f)
            seen.add(f)
        if dup:
            add(rows,'high','field_schema_field_unique',rel,0,'duplicate field names: '+ '; '.join(sorted(set(dup))[:8]),'duplicate_field')
        target, target_rel=exact_target(root, sp)
        if not target:
            schema_only += 1
            add(rows,'info','field_schema_no_exact_target',rel,0,'conceptual or crosswalk field schema has no exact same-basename current table','schema_only_no_exact_table')
            continue
        exact_count += 1
        th=read_header(target)
        missing=[h for h in th if h not in fields]
        extra=[f for f in fields if f not in th]
        if missing:
            add(rows,'high','field_schema_missing_target_fields',rel,0,f'{target_rel} fields missing from schema: '+ '; '.join(missing[:12]),'missing_field')
        if extra:
            add(rows,'high','field_schema_extra_fields',rel,0,f'field schema fields absent from {target_rel}: '+ '; '.join(extra[:12]),'extra_field')
        if not missing and not extra:
            add(rows,'info','field_schema_matches_target',rel,0,f'field schema matches {target_rel} header exactly ({len(th)} fields)','pass')
    if not schemas:
        add(rows,'high','field_schema_present','SCHEMA',0,'no *-Fields-current.csv files found','invalid_schema')
    elif not any(r['severity']=='high' for r in rows):
        add(rows,'info','field_schema_consistency','.',0,f'PASS {exact_count} exact field schemas matched targets; {schema_only} conceptual schemas documented without exact same-basename target','pass')
    return rows


def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Field-Schema-Consistency-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Field Schema Consistency Audit',
        generated_by='tools/field_schema_consistency.py',
        columns=['finding_id', 'severity', 'check', 'file', 'field_schema_status', 'detail'],
        intro_lines=[f'High findings: {sum(1 for r in rows if r.get('severity')=='high')}'],
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    for r in rows[:80]: print(f"{r.get('severity','?').upper()} {r.get('check')} {r.get('file')}: {r.get('detail')}")
    if len(rows)>80: print(f'... {len(rows)-80} more rows')
    if args.fail_on_high and any(r.get('severity')=='high' for r in rows): sys.exit(1)
if __name__=='__main__': main()
