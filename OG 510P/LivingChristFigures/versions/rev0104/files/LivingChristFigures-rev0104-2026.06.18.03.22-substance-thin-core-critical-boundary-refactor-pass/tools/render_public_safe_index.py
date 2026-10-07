#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, subprocess, sys
from pathlib import Path

sys.dont_write_bytecode = True
from public_template_policy import public_boundary_overrides

PUBLIC_FIELDS=[
    'candidate_id','name','location','office','status_current','capacity_state',
    'live_referral_safe','sensitivity','public_export_tier','public_shape_template','public_use_note'
]

CONTACT_DIGIT_CONTEXT = __import__('re').compile(r'(?i)\b(hotline|helpline|lifeline|phone|call|text|sms|whatsapp|toll[- ]?free|emergency|crisis line|contact number|intake number)\b')
CONTACT_DIGITS = __import__('re').compile(r'\b\d[\d\s().-]{2,}\d\b')

def redact_public_contact_digits(value: str) -> str:
    if not value:
        return value
    if CONTACT_DIGIT_CONTEXT.search(value):
        return CONTACT_DIGITS.sub('[public contact digits redacted]', value)
    return value

def read_csv(path: Path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

def load_eligibility(root: Path) -> dict[str, dict]:
    p=root/'META/Public-Export-Eligibility-current.csv'
    if not p.exists():
        tool=root/'tools/public_export_eligibility.py'
        if tool.exists():
            subprocess.run([sys.executable, str(tool), str(root), '--write-report'], check=True)
    if not p.exists():
        return {}
    return {r.get('candidate_id',''): r for r in read_csv(p)}

def safe_row(r: dict, eligibility: dict[str, dict]) -> dict:
    cid=r.get('candidate_id','')
    elig=eligibility.get(cid, {})
    tier=elig.get('public_export_tier','public_index_shape_only')
    template=elig.get('public_shape_template','boundary_only_generic')
    overrides=public_boundary_overrides(template)
    out={
        'candidate_id':cid,
        'name':r.get('name',''),
        'location':overrides.get('location', r.get('location','')),
        'office':overrides.get('office', r.get('office','')),
        'status_current':'public_safe_boundary_index_row_not_release_approval',
        'capacity_state':'not_a_public_capacity_claim',
        'live_referral_safe':'false',
        'sensitivity':r.get('sensitivity',''),
        'public_export_tier':tier,
        'public_shape_template':template,
        'public_use_note':overrides.get('public_use_note','High-level research index only; not a referral or operational guide.'),
    }
    for _k in ['name','location','office','status_current','capacity_state','sensitivity','public_use_note']:
        out[_k] = redact_public_contact_digits(out.get(_k, ''))
    return out

def write_outputs(root: Path, rows: list[dict]):
    pub=root/'PUBLIC'; pub.mkdir(exist_ok=True)
    csvp=pub/'Candidate-Index-public.csv'
    with csvp.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=PUBLIC_FIELDS); w.writeheader(); w.writerows(rows)
    (pub/'Candidate-Index-public.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines=['# Candidate Index — public-safe current','',
           'This Markdown index is generated from `tools/render_public_safe_index.py`. It is a scrubbed, non-referral index and not a public reading edition. It depends on `META/Public-Export-Eligibility-current.*`; eligibility does not equal release approval.',
           '',f'Rows: {len(rows)}','']
    lines.append('| candidate_id | name | location | office | public_export_tier | public_shape_template | public_use_note |')
    lines.append('|---|---|---|---|---|---|---|')
    for r in rows:
        vals=[r['candidate_id'], r['name'], r['location'], r['office'], r['public_export_tier'], r['public_shape_template'], r['public_use_note']]
        lines.append('| ' + ' | '.join(str(v).replace('|','/').replace('\n',' ') for v in vals) + ' |')
    (pub/'Candidate-Index-public.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--write', action='store_true')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    eligibility=load_eligibility(root)
    rows=[safe_row(r, eligibility) for r in read_csv(root/'Candidate-Ledger-current.csv')]
    if args.write:
        write_outputs(root, rows)
    print(f'public_safe_index_rows={len(rows)} eligibility_rows={len(eligibility)}')

if __name__=='__main__':
    main()
