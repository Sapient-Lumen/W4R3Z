#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path
from collections import defaultdict

FIELDS = ['surface_id','file','file_scope','risk_type','severity','occurrence_count','first_line','sample','public_release_effect','review_note']
SKIP_DIRS = {'.git','__pycache__'}
SCAN_EXTS = {'.txt','.md','.csv','.json','.py'}
PATTERNS = [
    ('raw_url', re.compile(r'https?://\S+|\bwww\.[^\s)]+', re.I), 'medium', 'URLs are evidence internally but not automatically public link permission.'),
    ('markdown_or_html_image', re.compile(r'!\[[^\]]*\]\([^)]+\)|<img\b', re.I), 'high', 'Images are blocked by default unless separate consent/governance approval exists.'),
    ('email_like', re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I), 'high', 'Email/contact surfaces are internal-only unless an explicit live-referral exception exists.'),
    ('phone_or_contact_digits', re.compile(r'(?i)\b(?:hotline|helpline|lifeline|phone|call|text|sms|whatsapp|toll[- ]?free|emergency|contact number|intake number)\b[^\n]{0,80}?\b\d[\d\s().-]{2,}\d\b'), 'high', 'Contact digits and shortcodes must not leak to public surfaces.'),
    ('coordinate_pair', re.compile(r'(?<!\d)([-+]?\d{1,2}\.\d{3,})\s*,\s*([-+]?\d{1,3}\.\d{3,})(?!\d)'), 'high', 'Coordinates can become route/map/extraction surfaces.'),
    ('contact_or_intake_language', re.compile(r'(?i)\b(contact|call|text|email|phone|hotline|helpline|whatsapp|intake|referral|support path|shelter|safe house|safe-house|refuge)\b'), 'medium', 'Contact/referral language is allowed internally but must be rendered as non-referral boundary shape publicly.'),
    ('route_or_map_language', re.compile(r'(?i)\b(route|map|coordinates|highway|border crossing|camp|encampment|distress call|rescue|last seen|missing since|search area|tip line|field site|living-site)\b'), 'medium', 'Route/map language requires no-route/no-field-map review.'),
    ('case_or_record_language', re.compile(r'(?i)\b(case number|police file|incident number|ME number|medical examiner|grave number|plot number|registry id|individual record|case list|unidentified remains)\b'), 'medium', 'Case/record language must not become public extraction.'),
    ('image_event_memorial_language', re.compile(r'(?i)\b(vigil|red dress|tribute wall|memorial page|exhibit|photo|photograph|image|poster|event map|name reading)\b'), 'medium', 'Image/event/memorial language requires no-image/no-event-map review.'),
    ('current_capacity_language', re.compile(r'(?i)\b(current capacity|available now|accepting new|open now|service capacity|live referral|waiting time|operational)\b'), 'medium', 'Current-capacity language is blocked from public claim unless refreshed and released.'),
    ('implementation_scorecard_language', re.compile(r'(?i)\b(scorecard|dashboard|completed implementation|implementation success|progress reporting|calls for justice)\b'), 'medium', 'Implementation tracking is not safety/completion proof.'),
]


def scope_for(rel: str) -> str:
    if rel.startswith('PUBLIC/'): return 'public'
    if rel.startswith('CANDIDATES/_REFRESH'): return 'refresh_note'
    if rel.startswith('CANDIDATES/'): return 'candidate'
    if rel.startswith('OFFICE-CARDS/'): return 'office_card'
    if rel.startswith('GOVERNANCE/'): return 'governance'
    if rel.startswith('META/'): return 'meta'
    if rel.startswith('SCHEMA/'): return 'schema'
    if rel.startswith('LONGFORM/'): return 'longform'
    if rel.startswith('tools/'): return 'tool'
    return 'root_or_ledger'


def iter_files(root: Path):
    for p in sorted(root.rglob('*')):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix.lower() not in SCAN_EXTS:
            continue
        if p.name == 'SHA256SUMS.txt':
            continue
        yield p


def run(root: Path) -> list[dict]:
    rows=[]
    for path in iter_files(root):
        rel=str(path.relative_to(root))
        txt=path.read_text(encoding='utf-8', errors='ignore')
        lines=txt.splitlines()
        for risk_type, regex, severity, note in PATTERNS:
            count=0; first_line=''; sample=''
            for i,line in enumerate(lines,1):
                matches=list(regex.finditer(line))
                if not matches: continue
                count += len(matches)
                if not first_line:
                    first_line=str(i)
                    sample=matches[0].group(0)[:180]
            if count:
                release_effect = 'public_handoff_blocker_if_in_public' if severity == 'high' else 'review_before_public_expansion'
                if rel.startswith('PUBLIC/') and severity == 'high':
                    release_effect = 'blocks_public_handoff'
                rows.append({
                    'surface_id': f'ssi_{len(rows)+1:05d}',
                    'file': rel,
                    'file_scope': scope_for(rel),
                    'risk_type': risk_type,
                    'severity': severity,
                    'occurrence_count': str(count),
                    'first_line': first_line,
                    'sample': sample,
                    'public_release_effect': release_effect,
                    'review_note': note,
                })
    return rows


def write_reports(root: Path, rows: list[dict]) -> None:
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Sensitive-Surface-Inventory-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Sensitive-Surface-Inventory-current.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    high_public=[r for r in rows if r.get('file_scope')=='public' and r.get('severity')=='high']
    by_scope=defaultdict(int); by_risk=defaultdict(int)
    for r in rows:
        by_scope[r['file_scope']]+=1; by_risk[r['risk_type']]+=1
    lines=['# Sensitive Surface Inventory — current','',
           'Generated by `tools/sensitive_surface_inventory.py`. This is an inventory, not a release approval. It records where contact, route, case-record, image/event, capacity, URL, and implementation-scorecard surfaces occur so public rendering can fail closed.',
           '', f'Rows: {len(rows)}', f'Public high-severity inventory rows: {len(high_public)}', '',
           '## Scope counts','']
    for k in sorted(by_scope): lines.append(f'- {k}: {by_scope[k]}')
    lines += ['', '## Risk-type counts','']
    for k in sorted(by_risk): lines.append(f'- {k}: {by_risk[k]}')
    lines += ['', '## Sample rows','']
    fields=['file','file_scope','risk_type','severity','occurrence_count','first_line','sample','public_release_effect']
    lines.append('| '+' | '.join(fields)+' |'); lines.append('| '+' | '.join(['---']*len(fields))+' |')
    for r in rows[:160]:
        lines.append('| '+' | '.join(str(r.get(f,'')).replace('|','/').replace('\n',' ')[:220] for f in fields)+' |')
    if len(rows)>160: lines.append('\n_Table truncated at 160 rows; CSV/JSON contain all rows._')
    (out/'Sensitive-Surface-Inventory-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--json', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    if args.json: print(json.dumps(rows,ensure_ascii=False,indent=2))
    else:
        public_high=sum(1 for r in rows if r.get('file_scope')=='public' and r.get('severity')=='high')
        print(f'sensitive_surface_inventory_rows={len(rows)} public_high={public_high}')
if __name__=='__main__': main()
