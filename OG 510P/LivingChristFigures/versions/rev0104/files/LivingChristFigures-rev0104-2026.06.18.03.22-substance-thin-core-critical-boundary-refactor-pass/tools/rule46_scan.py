#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

TEXT_EXTS={'.txt','.md','.csv','.json'}
SCAN_PREFIXES=('PUBLIC/Candidate-Index-public', 'CANDIDATES/Bridget-Tolley-FSIS-MMIWG-Canada.txt', 'LONGFORM/Boundary-004-Family-Led-Search-Is-Not-A-Case-List.txt')
POLICY_ALLOW_FILES={
    'PUBLIC/Public-Redaction-Policy-current.md',
    'PUBLIC/Public-Safe-Prose-Templates-current.md',
    'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json',
    'PUBLIC/README-public-edition.md',
    'CURRENT-SPINE.md',
    'CUBE-RULES.txt',
}
HIGH_PATTERNS=[
    ('submit_or_report_path', re.compile(r'(?i)\b(submit a name|report a case|submit[- ]a[- ]name|report[- ]a[- ]case)\b')),
    ('family_contact_path', re.compile(r'(?i)\b(family contact|contact the family|support/contact|support path|social-media route|facebook group|private message)\b')),
    ('case_list_export', re.compile(r'(?i)\b(case list|victim/survivor/family name roll|name roll|case rows?|person-by-person)\b')),
    ('vigil_event_map', re.compile(r'(?i)\b(vigil/event map|event logistics|march planning|event map|vigil map|installation map)\b')),
    ('police_or_testimony_detail', re.compile(r'(?i)\b(police-file detail|testimony fragment|testimony excerpts?|death or disappearance circumstances)\b')),
    ('image_reuse', re.compile(r'(?i)\b(red-dress image|red dress image|photographs?|image reuse|family tributes?)\b')),
]
MEDIUM_PATTERNS=[
    ('mmiwg_boundary_term', re.compile(r'(?i)\b(MMIWG2S\+|Families of Sisters in Spirit|Sisters in Spirit|Red Dress Day|family-led search|annual vigil)\b')),
]
NEGATION_RE=re.compile(r'(?i)\b(no|not|do not|does not|blocked|without|must not|is not|not a|not treated|permission to extract|does not release|do not release)\b')
MMIWG_CONTEXT_RE=re.compile(r'(?i)\b(MMIWG2S\+|MMIWG|Families of Sisters in Spirit|FSIS|Sisters in Spirit|Red Dress|Bridget Tolley|Gladys Tolley|Indigenous-led search)\b')


def context(txt,start,end,n=100):
    return txt[max(0,start-n):min(len(txt),end+n)].replace('\n',' ')


def is_negated_boundary(ctx: str) -> bool:
    return bool(NEGATION_RE.search(ctx))


def iter_targets(root: Path):
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
            continue
        rel=str(p.relative_to(root))
        if rel in POLICY_ALLOW_FILES:
            continue
        if rel.startswith('SCHEMA/') or rel.startswith('META/') or rel.startswith('tools/') or rel.startswith('GOVERNANCE/'):
            continue
        if any(rel.startswith(prefix) for prefix in SCAN_PREFIXES):
            yield p


def scan(root: Path):
    findings=[]
    for p in iter_targets(root):
        rel=str(p.relative_to(root))
        txt=p.read_text(encoding='utf-8', errors='ignore')
        for risk_type, rx in HIGH_PATTERNS:
            for m in rx.finditer(txt):
                ctx=context(txt,m.start(),m.end(),180)
                # Rule 46 is MMIWG2S+-specific; ignore generic family/contact words in unrelated public-index rows.
                if rel.startswith('PUBLIC/Candidate-Index-public') and not MMIWG_CONTEXT_RE.search(ctx):
                    continue
                # Boundary-language mentions are acceptable when the nearby context clearly blocks the pattern.
                if is_negated_boundary(ctx):
                    continue
                line=txt[:m.start()].count('\n')+1
                findings.append({'severity':'high','risk_type':risk_type,'file_path':rel,'line':line,'match':m.group(0),'context':ctx,'note':'Rule 46 high-risk extraction phrase appears without nearby blocking language'})
        for risk_type, rx in MEDIUM_PATTERNS:
            for m in rx.finditer(txt):
                ctx=context(txt,m.start(),m.end())
                line=txt[:m.start()].count('\n')+1
                # Medium rows are review reminders only; policy/negated boundary language is not high risk.
                findings.append({'severity':'medium','risk_type':risk_type,'file_path':rel,'line':line,'match':m.group(0),'context':ctx,'note':'MMIWG2S+ boundary term appears; confirm no case-list/no-vigil-map/no-contact extraction'})
    return findings


def write_report(root: Path, findings):
    out=root/'META'; out.mkdir(exist_ok=True)
    fields=['severity','risk_type','file_path','line','match','context','note']
    with (out/'Rule46-Scan-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(findings)
    (out/'Rule46-Scan-current.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    high=[r for r in findings if r['severity']=='high']
    med=[r for r in findings if r['severity']=='medium']
    lines=['# Rule 46 Scan — current','',f'High findings: {len(high)}',f'Medium review reminders: {len(med)}','']
    if findings:
        lines.append('| severity | risk_type | file | line | match | note |')
        lines.append('|---|---|---:|---:|---|---|')
        for r in findings[:200]:
            lines.append(f"| {r['severity']} | {r['risk_type']} | `{r['file_path']}` | {r['line']} | `{str(r['match']).replace('|','/')}` | {r['note'].replace('|','/')} |")
    else:
        lines.append('No configured rule-46 findings.')
    (out/'Rule46-Scan-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    findings=scan(root)
    if args.write_report:
        write_report(root, findings)
    if args.json:
        print(json.dumps(findings,ensure_ascii=False,indent=2))
    else:
        high=sum(1 for r in findings if r['severity']=='high')
        med=sum(1 for r in findings if r['severity']=='medium')
        if high==0:
            print(f'PASS rule46 scan — high findings=0; medium review reminders={med}')
        else:
            for r in findings:
                print(f"{r['severity'].upper()} {r['risk_type']} {r['file_path']}:{r['line']} {r['match']!r}")
    if args.fail_on_high and any(r['severity']=='high' for r in findings):
        raise SystemExit(1)

if __name__=='__main__': main()
