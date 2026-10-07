#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

TEXT_EXTS={'.txt','.md','.csv','.json','.py'}
EXCLUDE_FILES={'SHA256SUMS.txt'}
CONTACT_KEYWORDS=('helpline','hotline','toll-free','toll free','call centre','call center','phone','number','contact','intake','referral','consultation')
# Long numbers with separators.  Short public emergency-style numbers are caught only when nearby text says toll-free/helpline/hotline.
LONG_PHONE_RE=re.compile(r'(?<![\w/])(?:\+?\d{1,3}[\s.\-()]*)?(?:\(?\d{2,4}\)?[\s.\-]*){2,4}\d{2,4}(?![\w])')
SHORT_CONTACT_RE=re.compile(r'(?i)\b(?:toll[- ]free|helpline|hotline|call(?: |-)?centre|call(?: |-)?center)\s+(?:number\s+)?\d{3,6}\b')
COORD_RE=re.compile(r'(?<!\d)[+-]?\d{1,3}\.\d{4,}\s*,\s*[+-]?\d{1,3}\.\d{4,}(?!\d)')
EMAIL_RE=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
ADDRESS_RE=re.compile(r'\b\d{1,6}\s+[A-Z][A-Za-z0-9\'’.-]+(?:\s+[A-Z][A-Za-z0-9\'’.-]+){0,5}\s+(?:Street|St\.?|Road|Rd\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|Highway|Hwy\.?|Way|Place|Pl\.?|Court|Ct\.?|Terrace|Square)\b')
GRAVE_RE=re.compile(r'(?i)\b(?:plot|grave|medical examiner|ME number|ME#|morgue case|case number)\s*[:#]?\s*(?=[A-Z0-9\-/.]*\d)[A-Z0-9][A-Z0-9\-/.]{3,}\b')
DATE_LIKE_RE=re.compile(r'^(?:19|20)\d{2}[./-]\d{1,2}(?:[./-]\d{1,2})?(?:[./-]\d{1,2})?$')
DOI_LIKE_RE=re.compile(r'10\.\d{4,9}/|doi|PIIS\d|s\d{5}')
REDACTION_PLACEHOLDERS=('redacted — non-referral cube','[redacted','number redacted')

def iter_text_files(root: Path):
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in TEXT_EXTS and p.name not in EXCLUDE_FILES:
            yield p

def line_col(txt: str, pos: int):
    before=txt[:pos]
    line=before.count('\n')+1
    last=before.rfind('\n')
    col=pos+1 if last<0 else pos-last
    return line,col

def context(txt: str, start: int, end: int, n: int=90):
    return txt[max(0,start-n):min(len(txt),end+n)].replace('\n',' ')

def is_false_phone(s: str, ctx: str):
    stripped=s.strip(' ()')
    digits=re.sub(r'\D','',s)
    if len(digits)<3 or len(digits)>15:
        return True
    if DATE_LIKE_RE.match(stripped):
        return True
    if DOI_LIKE_RE.search(ctx):
        return True
    if 'rev00' in ctx or 'LivingChristFigures-rev' in ctx or 'timestamped export' in ctx.lower():
        return True
    # Counts, years, and DOI tails are not public-contact data unless contact keywords are present.
    if not any(k in ctx.lower() for k in CONTACT_KEYWORDS):
        return True
    if any(ph in ctx.lower() for ph in REDACTION_PLACEHOLDERS):
        return True
    return False

def scan(root: Path):
    findings=[]
    for p in iter_text_files(root):
        rel=str(p.relative_to(root))
        txt=p.read_text(encoding='utf-8', errors='ignore')
        for rx, typ, sev, note in [
            (EMAIL_RE,'email_address','high','email-like string appears in working cube'),
            (COORD_RE,'coordinate_pair','high','exact coordinate pair appears in working cube'),
            (ADDRESS_RE,'street_address_like','medium','street-address-like string appears; review if shelter, camp, cemetery, refuge, or patient context'),
            (GRAVE_RE,'grave_or_case_identifier_like','high','grave/case/ME-number-like identifier appears'),
        ]:
            for m in rx.finditer(txt):
                ctx=context(txt,m.start(),m.end())
                if any(ph in ctx.lower() for ph in REDACTION_PLACEHOLDERS):
                    continue
                line,col=line_col(txt,m.start())
                findings.append({'severity':sev,'risk_type':typ,'file_path':rel,'line':line,'column':col,'match':m.group(0),'context':ctx,'note':note})
        for m in LONG_PHONE_RE.finditer(txt):
            ctx=context(txt,m.start(),m.end())
            if is_false_phone(m.group(0), ctx):
                continue
            line,col=line_col(txt,m.start())
            findings.append({'severity':'high','risk_type':'public_contact_number','file_path':rel,'line':line,'column':col,'match':m.group(0),'context':ctx,'note':'phone-like contact digits near hotline/helpline/contact language'})
        for m in SHORT_CONTACT_RE.finditer(txt):
            ctx=context(txt,m.start(),m.end())
            if any(ph in ctx.lower() for ph in REDACTION_PLACEHOLDERS):
                continue
            line,col=line_col(txt,m.start())
            findings.append({'severity':'high','risk_type':'short_public_contact_number','file_path':rel,'line':line,'column':col,'match':m.group(0),'context':ctx,'note':'short public-contact number near hotline/helpline/toll-free language'})
    return findings

def write_report(root: Path, findings):
    outdir=root/'META'; outdir.mkdir(exist_ok=True)
    fields=['severity','risk_type','file_path','line','column','match','context','note']
    csvp=outdir/'Redaction-Risk-Open-Findings-current.csv'
    with csvp.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(findings)
    (outdir/'Redaction-Risk-Open-Findings-current.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Redaction Risk Open Findings — current','',f'Open findings: {len(findings)}','']
    if findings:
        lines.append('| severity | risk_type | file | line | match | note |')
        lines.append('|---|---|---:|---:|---|---|')
        for r in findings[:200]:
            match=str(r['match']).replace('|','/').replace('\n',' ')
            note=str(r['note']).replace('|','/')
            lines.append(f"| {r['severity']} | {r['risk_type']} | `{r['file_path']}` | {r['line']} | `{match}` | {note} |")
    else:
        lines.append('No open automated findings under the rev0030 scanner. This is not a guarantee of public-export safety; it only means the configured high-risk patterns did not fire.')
    (outdir/'Redaction-Risk-Open-Findings-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

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
        if not findings:
            print('PASS redaction scan — no configured open findings')
        else:
            for r in findings:
                print(f"{r['severity'].upper()} {r['risk_type']} {r['file_path']}:{r['line']} {r['match']!r}")
    if args.fail_on_high and any(r['severity']=='high' for r in findings):
        raise SystemExit(1)

if __name__=='__main__':
    main()
