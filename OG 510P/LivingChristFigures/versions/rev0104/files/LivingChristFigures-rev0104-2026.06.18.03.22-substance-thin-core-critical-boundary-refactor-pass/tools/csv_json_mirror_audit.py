#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['finding_id','severity','check','file','row','detail']


def read_csv(path: Path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f)), (csv.DictReader(path.open(encoding='utf-8', newline='')).fieldnames or [])


def csv_rows_and_header(path: Path):
    with path.open(encoding='utf-8', newline='') as f:
        reader=csv.DictReader(f)
        rows=list(reader)
        return rows, (reader.fieldnames or [])


def norm(value) -> str:
    if value is None: return ''
    if isinstance(value, bool): return 'true' if value else 'false'
    return str(value)


def add(rows, sev, check, file, row, detail):
    rows.append({'finding_id':f'cjma_{len(rows)+1:04d}','severity':sev,'check':check,'file':file,'row':str(row),'detail':detail})


def candidate_pairs(root: Path):
    for csv_path in sorted(root.rglob('*.csv')):
        rel=str(csv_path.relative_to(root))
        if rel == 'SHA256SUMS.txt':
            continue
        json_path=csv_path.with_suffix('.json')
        if json_path.exists():
            yield csv_path, json_path


def run(root: Path):
    findings=[]
    pair_count=0
    for csv_path, json_path in candidate_pairs(root):
        pair_count += 1
        csv_rel=str(csv_path.relative_to(root)); json_rel=str(json_path.relative_to(root))
        try:
            csv_rows, header = csv_rows_and_header(csv_path)
        except Exception as e:
            add(findings,'high','csv_parse',csv_rel,0,f'CSV parse failed: {e}')
            continue
        try:
            data=json.loads(json_path.read_text(encoding='utf-8'))
        except Exception as e:
            add(findings,'high','json_parse',json_rel,0,f'JSON parse failed: {e}')
            continue
        if not isinstance(data, list):
            add(findings,'high','json_list_shape',json_rel,0,'JSON mirror is not a list of row objects')
            continue
        if len(data) != len(csv_rows):
            add(findings,'high','row_count_mismatch',f'{csv_rel}|{json_rel}',0,f'CSV has {len(csv_rows)} rows; JSON has {len(data)} rows')
        for i, row in enumerate(data, start=2):
            if not isinstance(row, dict):
                add(findings,'high','json_row_object',json_rel,i,'JSON row is not an object')
                continue
            keys=list(row.keys())
            if keys != header:
                add(findings,'high','key_order_or_header_mismatch',json_rel,i,f'JSON keys {keys} do not exactly match CSV header {header}')
                # Keep checking overlapping fields when possible.
            if i-2 < len(csv_rows):
                c=csv_rows[i-2]
                for field in header:
                    if field in row and norm(row.get(field)) != norm(c.get(field,'')):
                        add(findings,'high','cell_value_mismatch',f'{csv_rel}|{json_rel}',i,f'{field}: CSV={norm(c.get(field,""))!r}; JSON={norm(row.get(field))!r}')
                        if sum(1 for r in findings if r['check']=='cell_value_mismatch') > 100:
                            add(findings,'high','cell_value_mismatch_truncated',f'{csv_rel}|{json_rel}',i,'More than 100 mirror cell mismatches; remaining cells skipped')
                            break
    if not findings:
        add(findings,'info','csv_json_mirror_audit','.',0,f'PASS exact CSV/JSON mirror audit across {pair_count} sibling pairs')
    return findings


def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/CSV-JSON-Mirror-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='CSV/JSON Mirror Audit',
        generated_by='tools/csv_json_mirror_audit.py',
        columns=['finding_id', 'severity', 'check', 'file', 'row', 'detail'],
        intro_lines=[f'High findings: {sum(1 for r in rows if r.get('severity')=='high')}', f'Medium findings: {sum(1 for r in rows if r.get('severity')=='medium')}'],
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    for r in rows[:80]: print(f"{r.get('severity','?').upper()} {r.get('check')} {r.get('file')} row {r.get('row')}: {r.get('detail')}")
    if len(rows)>80: print(f'... {len(rows)-80} more rows')
    if args.fail_on_high and any(r.get('severity')=='high' for r in rows): sys.exit(1)
if __name__=='__main__': main()
