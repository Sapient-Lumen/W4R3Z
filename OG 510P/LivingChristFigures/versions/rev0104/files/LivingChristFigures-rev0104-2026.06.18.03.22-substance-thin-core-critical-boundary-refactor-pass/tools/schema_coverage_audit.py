#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['finding_id','severity','check','file','row','detail','coverage_status']


def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None


def read_csv_header(path: Path):
    try:
        with path.open(encoding='utf-8', newline='') as f:
            return next(csv.reader(f), [])
    except Exception:
        return []


def add(rows, sev, check, file, row, detail, status):
    rows.append({'finding_id':f'sca_{len(rows)+1:04d}','severity':sev,'check':check,'file':file,'row':str(row),'detail':detail,'coverage_status':status})


def expected_field_schema(rel: str) -> str:
    name=Path(rel).name
    if name.endswith('-current.csv'):
        return 'SCHEMA/'+name[:-len('-current.csv')]+'-Fields-current.csv'
    return ''


def run(root: Path):
    rows=[]
    ledger_contract=read_json(root/'SCHEMA/Ledger-Contract-current.json') or {}
    ledger_paths=set((ledger_contract.get('ledgers') or {}).keys())
    current_csv=[p for p in sorted(root.rglob('*-current.csv')) if 'archive' not in p.parts]
    # Mirror coverage is a hard handoff issue.
    for p in current_csv:
        rel=str(p.relative_to(root))
        jp=p.with_suffix('.json')
        if not jp.exists():
            add(rows,'high','current_csv_json_mirror_missing',rel,0,'current CSV lacks sibling JSON mirror','missing_json_mirror')
        md=p.with_suffix('.md')
        if p.parent.name in {'META','SCHEMA','GOVERNANCE'} and not md.exists():
            add(rows,'medium','current_csv_markdown_companion_missing',rel,0,'current audit/schema/governance CSV lacks sibling Markdown companion','missing_markdown_companion')
    # Field-schema triad coverage.
    field_schema_paths=[p for p in sorted((root/'SCHEMA').glob('*-Fields-current.csv'))]
    for p in field_schema_paths:
        rel=str(p.relative_to(root))
        for suffix in ['.json','.md']:
            companion=p.with_suffix(suffix)
            if not companion.exists():
                add(rows,'high','field_schema_companion_missing',rel,0,f'field schema lacks {suffix} companion','missing_field_schema_companion')
    # Documentation coverage for current tables. Legacy/current tables may be governed by Ledger-Contract or a field schema.
    covered=0; backlog=0
    for p in current_csv:
        rel=str(p.relative_to(root))
        if rel.startswith('SCHEMA/') and rel.endswith('-Fields-current.csv'):
            covered += 1
            continue
        fs=expected_field_schema(rel)
        if rel in ledger_paths:
            covered += 1
            continue
        if fs and (root/fs).exists():
            covered += 1
            continue
        # Controlled vocabularies in SCHEMA are allowed to be self-norming if explicitly mirrored and described in README.
        if rel.startswith('SCHEMA/') and 'Controlled-Vocabulary' in rel:
            add(rows,'medium','controlled_vocab_field_schema_backlog',rel,0,'controlled vocabulary is mirrored but lacks a separate field-schema triad','schema_backlog')
            backlog += 1
        else:
            add(rows,'medium','current_table_field_contract_backlog',rel,0,'current CSV is mirrored but not yet covered by Ledger-Contract or a dedicated *-Fields schema','schema_backlog')
            backlog += 1
    if not rows:
        add(rows,'info','schema_coverage_audit','.',0,f'PASS schema coverage across {len(current_csv)} current CSV tables and {len(field_schema_paths)} field-schema tables','pass')
    elif not any(r['severity']=='high' for r in rows):
        add(rows,'info','schema_coverage_audit','.',0,f'PASS no blocking schema-coverage failures; {covered} current tables covered and {backlog} non-blocking schema-backlog rows recorded','pass_with_backlog')
    return rows


def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Schema-Coverage-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Schema Coverage Audit',
        generated_by='tools/schema_coverage_audit.py',
        columns=['finding_id', 'severity', 'check', 'file', 'coverage_status', 'detail'],
        intro_lines=[f'High findings: {sum(1 for r in rows if r.get('severity')=='high')}', f'Medium findings: {sum(1 for r in rows if r.get('severity')=='medium')}', 'This audit distinguishes blocking release failures from non-blocking schema-backlog rows.'],
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    for r in rows[:80]: print(f"{r.get('severity','?').upper()} {r.get('check')} {r.get('file')} {r.get('coverage_status')}: {r.get('detail')}")
    if len(rows)>80: print(f'... {len(rows)-80} more rows')
    if args.fail_on_high and any(r.get('severity')=='high' for r in rows): sys.exit(1)
if __name__=='__main__': main()
