#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

FIELDS=['finding_id','severity','check','file','row','reference','target_path','status','detail']
SKIP_NAMES={'SHA256SUMS.txt'}
SKIP_DIR_PARTS={'__pycache__'}
SCAN_PREFIXES=('PUBLIC/','GOVERNANCE/','META/','SCHEMA/','CANDIDATES/','OFFICE-CARDS/','LONGFORM/','tools/')
ROOT_FILES={'000-START-HERE.txt','CURRENT-SPINE.md','CUBE-MAP.md','CUBE-RULES.txt','LivingChristFigures.txt','manifest.json','DOOR-ETHICS.txt','THRESHOLD-MERCY.txt'}
HISTORICAL_ARCHIVE_RE=re.compile(r'LivingChristFigures-rev\d{4}.*\.zip$')
PATHISH_RE=re.compile(r'(?<!https://)(?<!http://)(?<!mailto:)(?:PUBLIC|GOVERNANCE|META|SCHEMA|CANDIDATES|OFFICE-CARDS|LONGFORM|tools)/[A-Za-z0-9_./()\-]+(?:\*|\.[A-Za-z0-9*]+)?|(?:000-START-HERE\.txt|CURRENT-SPINE\.md|CUBE-MAP\.md|CUBE-RULES\.txt|LivingChristFigures\.txt|manifest\.json)')
BACKTICK_RE=re.compile(r'`([^`]+)`')
JSON_STRING_RE=re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')

def add(rows, sev, check, file, row, ref, target, status, detail):
    rows.append({'finding_id':f'pra_{len(rows)+1:04d}','severity':sev,'check':check,'file':file,'row':str(row),'reference':ref,'target_path':target,'status':status,'detail':detail})

def candidate_files(root: Path):
    """Scan handoff and policy surfaces, not every generated row report.

    Generated audit reports often contain pipe-separated or display-truncated paths
    whose integrity is already checked by mirror/provenance/dependency audits. This
    audit is deliberately scoped to human-facing current handoff surfaces and JSON
    contracts where stale path references are most likely to mislead a reader.
    """
    explicit=set(ROOT_FILES) | {
        'PUBLIC/README-public-edition.md','PUBLIC/Public-Redaction-Policy-current.md','PUBLIC/Public-Safe-Prose-Templates-current.md','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json',
        'GOVERNANCE/README-governance-current.md','GOVERNANCE/Indigenous-Data-Governance-Protocol-current.md','GOVERNANCE/Governance-Decision-and-Review-Protocol-current.md','GOVERNANCE/Public-Export-Eligibility-Protocol-current.md','GOVERNANCE/Public-Release-Lint-and-Sensitive-Surface-Protocol-current.md','GOVERNANCE/Takedown-and-Reclassification-Protocol-current.md',
        'SCHEMA/README-schema-current.md','SCHEMA/Package-Release-Contract-current.json','SCHEMA/Ledger-Contract-current.json','SCHEMA/Frontmatter-Contract-current.json','SCHEMA/Row-Validation-Contract-current.json',
        'META/README-meta-instruments-current.md','META/MetaPass-Roadmap-current.md','META/Public-Export-Checklist-current.md','META/Update-Behavior-Gate-current.md',
        'tools/README.md',
    }
    return sorted([root/rel for rel in explicit if (root/rel).exists()])

def normalize(ref: str) -> str:
    r=ref.strip().strip('.,;:')
    r=r.replace('`','')
    if r.startswith('./'): r=r[2:]
    return r

def status_for(root: Path, ref: str):
    r=normalize(ref)
    if not r or r.startswith(('http://','https://','mailto:')): return None
    if HISTORICAL_ARCHIVE_RE.fullmatch(Path(r).name): return None
    if '[' in r or ']' in r: return None
    # shorthand triads like META/Foo-current.csv/json/md
    if r.endswith('.csv/json/md'):
        base=r[:-len('.csv/json/md')]
        needed=[base+'.csv', base+'.json', base+'.md']
        missing=[x for x in needed if not (root/x).exists()]
        return (r, 'pass' if not missing else 'missing_reference', 'triad shorthand expands to existing csv/json/md companions' if not missing else 'triad shorthand missing: '+ '; '.join(missing))
    # wildcard triads like META/Foo-current.* or SCHEMA/*-Fields-current.*
    if '*' in r:
        matches=list(root.glob(r))
        return (r, 'glob_matched' if matches else 'missing_reference', f'{len(matches)} glob matches')
    if r.endswith('/'):
        return (r, 'pass' if (root/r).is_dir() else 'missing_reference', 'directory reference exists' if (root/r).is_dir() else 'directory reference is missing')
    if any(r.startswith(x) for x in SCAN_PREFIXES) or r in ROOT_FILES:
        return (r, 'pass' if (root/r).exists() else 'missing_reference', 'referenced package path exists' if (root/r).exists() else 'referenced package path is missing')
    return None

def add_ref_tokens(refs, text: str):
    raw=normalize(text)
    # Whole-string path only when it is not prose or a pipe-separated list.
    if raw and (' ' not in raw) and ('|' not in raw) and (PATHISH_RE.fullmatch(raw) or raw in ROOT_FILES):
        refs.append(raw)
        return
    # Otherwise pull path-like tokens out of prose/list cells.
    for m in PATHISH_RE.finditer(text):
        refs.append(m.group(0))

def extract_refs_from_line(line: str, is_json: bool):
    refs=[]
    for m in BACKTICK_RE.finditer(line):
        add_ref_tokens(refs, m.group(1))
    if is_json:
        for m in JSON_STRING_RE.finditer(line):
            add_ref_tokens(refs, m.group(1).encode('utf-8').decode('unicode_escape'))
    for m in PATHISH_RE.finditer(line): refs.append(m.group(0))
    # de-duplicate in line preserving order
    out=[]; seen=set()
    for r in refs:
        nr=normalize(r)
        if nr.startswith('tools/') and nr not in {'tools/README.md'} and not (nr.endswith('.py') or nr.endswith('/')):
            continue
        if nr not in seen:
            seen.add(nr); out.append(nr)
    return out

def run(root: Path):
    rows=[]
    for p in candidate_files(root):
        rel=str(p.relative_to(root)); is_json=p.suffix.lower()=='.json'
        try: lines=p.read_text(encoding='utf-8', errors='ignore').splitlines()
        except Exception as e:
            add(rows,'high','read_file',rel,0,'','', 'read_error', str(e)); continue
        for i,line in enumerate(lines, start=1):
            for ref in extract_refs_from_line(line, is_json):
                st=status_for(root, ref)
                if not st: continue
                target,status,detail=st
                sev='high' if status=='missing_reference' else 'info'
                add(rows,sev,'path_reference_resolves' if sev=='info' else 'path_reference_missing',rel,i,ref,target,status,detail)
    if not rows:
        add(rows,'info','path_reference_audit','.',0,'','.', 'pass','No configured path-like references found')
    elif not any(r['severity']=='high' for r in rows):
        add(rows,'info','path_reference_audit','.',0,'','.', 'pass',f'PASS {len(rows)} configured package path references resolved or glob-matched')
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Path-Reference-Audit-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Path-Reference-Audit-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    high=sum(1 for r in rows if r.get('severity')=='high')
    lines=['# Path Reference Audit — current','', 'Generated by `tools/path_reference_audit.py`.', '', f'Rows: {len(rows)}', f'High findings: {high}', '', 'This audit checks package-relative path references in current handoff, governance, public, schema, and meta surfaces. Historical archive ZIP names are treated as provenance metadata rather than required bundled files.', '', '| finding_id | severity | file | row | reference | status | detail |','|---|---|---:|---:|---|---|---|']
    for r in rows[:240]:
        detail=(r.get('detail','') or '').replace('|','/')
        lines.append(f"| {r['finding_id']} | {r['severity']} | `{r['file']}` | {r['row']} | `{r['reference']}` | {r['status']} | {detail} |")
    if len(rows)>240: lines.append(f'\n... {len(rows)-240} additional rows omitted from Markdown view; see CSV/JSON.')
    (out/'Path-Reference-Audit-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high']
    print(f"{'FAIL' if high else 'PASS'} path reference audit rows={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['file']}:{r['row']} {r['reference']} -> {r['target_path']} {r['detail']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
