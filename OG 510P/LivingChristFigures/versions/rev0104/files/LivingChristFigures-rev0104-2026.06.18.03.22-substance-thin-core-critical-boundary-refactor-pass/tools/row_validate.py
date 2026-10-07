#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path
from collections import Counter, defaultdict

REPORT_FIELDS = ['severity','check','file','row','field','value','detail']
DATE_RE = re.compile(r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}$')
REV_RE = re.compile(r'^(rev[0-9]{4}|unknown_prior_revision)$')


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def csv_header(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        return next(reader, [])


def split_pipe(value: str) -> list[str]:
    return [x for x in (value or '').split('|') if x]


def finding(sev, check, file, row, field, value, detail):
    return {'severity':sev,'check':check,'file':file,'row':str(row),'field':field,'value':str(value)[:220],'detail':detail}


def target_values(root: Path, spec: dict) -> set[str]:
    p = root / spec.get('target_file','')
    field = spec.get('target_field','')
    return {r.get(field,'') for r in read_csv(p) if r.get(field,'')}


def validate_table(root: Path, rel: str, spec: dict, contract: dict) -> list[dict]:
    out=[]
    path=root/rel
    if not path.exists():
        return [finding('high','row_table_exists',rel,0,'','', 'CSV table missing')]
    rows=read_csv(path)
    header=csv_header(path)
    required_columns=spec.get('required_columns', [])
    for col in required_columns:
        if col not in header:
            out.append(finding('high','row_required_column',rel,0,col,'','required column missing'))
    if out:
        return out
    if spec.get('min_rows', 0) and len(rows) < int(spec['min_rows']):
        out.append(finding('high','row_min_rows',rel,0,'',len(rows),f"expected at least {spec['min_rows']} rows"))
    for field in spec.get('unique_fields', []):
        vals=[r.get(field,'') for r in rows if r.get(field,'')]
        for val, count in Counter(vals).items():
            if count > 1:
                out.append(finding('high','row_unique_field',rel,0,field,val,f'duplicate appears {count} times'))
    path_fields=set(spec.get('path_exists_fields', []))
    path_pipe_fields=set(spec.get('path_exists_pipe_fields', []))
    pattern_fields={k: re.compile(v) for k,v in spec.get('pattern_fields', {}).items()}
    allowed_values=spec.get('allowed_values', {})
    allowed_pipe_values=spec.get('allowed_pipe_values', {})
    refs=spec.get('references', {})
    ref_targets={field: target_values(root, rspec) for field, rspec in refs.items()}
    for idx, row in enumerate(rows, start=2):
        for field in spec.get('required_nonempty', []):
            if not (row.get(field,'') or '').strip():
                out.append(finding('high','row_required_nonempty',rel,idx,field,'','required value is empty'))
        for field in spec.get('boolean_fields', []):
            val=(row.get(field,'') or '').strip().lower()
            if val not in {'true','false'}:
                out.append(finding('high','row_boolean_field',rel,idx,field,row.get(field,''),'expected true or false'))
        for field in spec.get('date_fields', []):
            val=(row.get(field,'') or '').strip()
            if val and not DATE_RE.fullmatch(val):
                out.append(finding('high','row_date_field',rel,idx,field,val,'expected YYYY-MM-DD'))
        for field in spec.get('revision_fields', []):
            val=(row.get(field,'') or '').strip()
            if val and not REV_RE.fullmatch(val):
                out.append(finding('high','row_revision_field',rel,idx,field,val,'expected revNNNN or unknown_prior_revision'))
        for field, rx in pattern_fields.items():
            val=(row.get(field,'') or '').strip()
            if val and not rx.fullmatch(val):
                out.append(finding('high','row_pattern_field',rel,idx,field,val,f'fails pattern {rx.pattern}'))
        for field, allowed in allowed_values.items():
            val=(row.get(field,'') or '').strip()
            if val and val not in set(allowed):
                out.append(finding('high','row_allowed_value',rel,idx,field,val,'not in controlled set'))
        for field, allowed in allowed_pipe_values.items():
            allowed_set=set(allowed)
            for val in split_pipe(row.get(field,'')):
                if val not in allowed_set:
                    out.append(finding('high','row_allowed_pipe_value',rel,idx,field,val,'pipe value not in controlled set'))
        for field in path_fields:
            val=(row.get(field,'') or '').strip()
            if val and not (root/val).exists():
                out.append(finding('high','row_path_exists',rel,idx,field,val,'path does not exist'))
        for field in path_pipe_fields:
            for val in split_pipe(row.get(field,'')):
                if not (root/val).exists():
                    out.append(finding('high','row_pipe_path_exists',rel,idx,field,val,'pipe path does not exist'))
        for field, rspec in refs.items():
            vals=split_pipe(row.get(field,'')) if rspec.get('pipe', False) else [(row.get(field,'') or '').strip()]
            if not vals and not rspec.get('allow_empty', False):
                out.append(finding('high','row_reference_present',rel,idx,field,'','reference value empty'))
            target=ref_targets.get(field,set())
            for val in vals:
                if val and val not in target:
                    out.append(finding('high','row_reference_exists',rel,idx,field,val,f"not present in {rspec.get('target_file')}:{rspec.get('target_field')}"))
    return out


def run(root: Path) -> list[dict]:
    contract_path=root/'SCHEMA/Row-Validation-Contract-current.json'
    if not contract_path.exists():
        return [finding('high','row_validation_contract_exists','SCHEMA/Row-Validation-Contract-current.json',0,'','','missing')]
    contract=json.loads(contract_path.read_text(encoding='utf-8'))
    findings=[]
    for rel, spec in contract.get('tables', {}).items():
        findings.extend(validate_table(root, rel, spec, contract))
    if not findings:
        return [finding('info','row_validation','.',0,'','', 'PASS row-level schema/value/reference validation')]
    return findings


def write_reports(root: Path, rows: list[dict]) -> None:
    out=root/'SCHEMA'; out.mkdir(exist_ok=True)
    csv_path=out/'Row-Validation-Report-current.csv'
    with csv_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=REPORT_FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in REPORT_FIELDS} for r in rows])
    (out/'Row-Validation-Report-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    high=sum(1 for r in rows if r.get('severity')=='high')
    med=sum(1 for r in rows if r.get('severity')=='medium')
    info=sum(1 for r in rows if r.get('severity')=='info')
    lines=['# Row Validation Report — current','', 'Generated by `tools/row_validate.py` from `SCHEMA/Row-Validation-Contract-current.json`.', '', f'High findings: {high}', f'Medium findings: {med}', f'Info rows: {info}', '']
    if high or med:
        lines += ['## Findings','']
        for r in rows[:200]:
            if r.get('severity')!='info':
                lines.append(f"- **{r.get('severity')}** `{r.get('check')}` `{r.get('file')}` row {r.get('row')} field `{r.get('field')}` — {r.get('detail')} ({r.get('value')})")
    else:
        lines.append('PASS: all configured row-level checks passed.')
    (out/'Row-Validation-Report-current.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    rows=run(root)
    if args.write_report:
        write_reports(root, rows)
    for r in rows[:80]:
        print(f"{r.get('severity','?').upper()} {r.get('check')} {r.get('file')} row {r.get('row')} {r.get('field')}: {r.get('detail')}")
    if len(rows)>80:
        print(f"... {len(rows)-80} more rows")
    if args.fail_on_high and any(r.get('severity')=='high' for r in rows):
        sys.exit(1)

if __name__=='__main__':
    main()
