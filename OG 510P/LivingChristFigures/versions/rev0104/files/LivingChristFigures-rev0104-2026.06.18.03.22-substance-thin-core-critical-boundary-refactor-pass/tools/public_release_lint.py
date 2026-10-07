#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

FIELDS = ['finding_id','severity','risk_type','file','line','match','release_effect','remediation']
PUBLIC_FILE_GLOB = '*'

URL_RE = re.compile(r'https?://\S+|\bwww\.[^\s)]+', re.I)
IMG_RE = re.compile(r'!\[[^\]]*\]\([^)]+\)|<img\b', re.I)
EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)
COORD_RE = re.compile(r'(?<!\d)([-+]?\d{1,2}\.\d{3,})\s*,\s*([-+]?\d{1,3}\.\d{3,})(?!\d)')
CONTACT_DIGIT_RE = re.compile(r'(?i)\b(?:hotline|helpline|lifeline|phone|call|text|sms|whatsapp|toll[- ]?free|emergency|crisis line|contact number|intake number)\b[^\n]{0,80}?\b\d[\d\s().-]{2,}\d\b')
CASE_RE = re.compile(r'(?i)\b(last seen|missing since|submit(?: a)? name|submit(?: a)? tip|report(?: a)? case|police file|case number|incident number|grave number|plot number|medical examiner number|ME number)\b')
ROUTE_RE = re.compile(r'(?i)\b(route details|distress-call pathway|distress call pathway|family-search contact prompt|living-site name|camp location|encampment location|search area|field site|exact coordinates)\b')
CAPACITY_RE = re.compile(r'(?i)\b(accepting new|open now|available now|current capacity|waiting time|service capacity is|shelter beds|referrals open)\b')
NEGATION_RE = re.compile(r'(?i)\b(do not|must not|not a|not an|not proof|not release|blocked|excluded|suppressed|redact|redacted|omit|omitted|remove|removed|exclude|excluded|suppress|suppressed|not public|not safe|not enough|not repeated|must remove|no\s+|without\s+recorded|remains blocked)\b')
POLICY_BOUNDARY_FILES = {
    'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json',
    'PUBLIC/Public-Redaction-Policy-current.md',
    'PUBLIC/Public-Safe-Prose-Templates-current.md',
    'PUBLIC/README-public-edition.md',
}


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def add(findings, severity, risk_type, rel, line, match, effect, remediation):
    findings.append({
        'finding_id': f'prl_{len(findings)+1:04d}',
        'severity': severity,
        'risk_type': risk_type,
        'file': rel,
        'line': str(line),
        'match': (match or '')[:180],
        'release_effect': effect,
        'remediation': remediation,
    })


def scan_public_file(root: Path, path: Path, findings: list[dict]) -> None:
    rel = str(path.relative_to(root))
    txt = read_text(path)
    lines = txt.splitlines()
    before = len(findings)
    for i, line in enumerate(lines, 1):
        for regex, risk in [(URL_RE,'raw_url'), (IMG_RE,'image_or_embedded_media'), (EMAIL_RE,'email_like'), (COORD_RE,'coordinate_pair'), (CONTACT_DIGIT_RE,'contact_digit_or_shortcode')]:
            for m in regex.finditer(line):
                add(findings, 'high', risk, rel, i, m.group(0), 'blocks_public_handoff', 'Remove, redact, or move to internal-only material; public layer must not carry live links/contact/image/coordinate surfaces.')
        for regex, risk in [(CASE_RE,'case_record_extraction_phrase'), (ROUTE_RE,'route_or_map_extraction_phrase'), (CAPACITY_RE,'current_capacity_claim_phrase')]:
            for m in regex.finditer(line):
                if rel in POLICY_BOUNDARY_FILES or NEGATION_RE.search(line):
                    add(findings, 'medium', risk, rel, i, m.group(0), 'allowed_boundary_language_review', 'allowed_context=policy_negation_or_boundary_statement; boundary/policy language mentions a restricted public-release shape; keep under review.')
                else:
                    add(findings, 'high', risk, rel, i, m.group(0), 'blocks_public_handoff', 'Public layer appears to expose case/route/current-capacity language outside a boundary context.')
    if len(findings) == before:
        add(findings, 'info', 'file_scanned_no_configured_findings', rel, 0, '', 'public_file_scanned', 'No configured public-lint finding in this file.')


def run(root: Path) -> list[dict]:
    pub = root / 'PUBLIC'
    findings: list[dict] = []
    if not pub.exists():
        add(findings, 'high', 'public_dir_missing', 'PUBLIC/', 0, '', 'blocks_public_handoff', 'Restore PUBLIC directory.')
        return findings
    for path in sorted(p for p in pub.glob(PUBLIC_FILE_GLOB) if p.is_file()):
        scan_public_file(root, path, findings)
    return findings


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])


def write_reports(root: Path, rows: list[dict]) -> None:
    out = root / 'META'
    write_csv(out/'Public-Release-Lint-current.csv', rows)
    (out/'Public-Release-Lint-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    high = [r for r in rows if r.get('severity') == 'high']
    med = [r for r in rows if r.get('severity') == 'medium']
    lines = ['# Public Release Lint — current', '', 'Generated by `tools/public_release_lint.py`. This is a public-layer handoff lint. High findings block public handoff; medium findings are boundary-language reminders.', '', f'High findings: {len(high)}', f'Medium findings: {len(med)}', f'Total rows: {len(rows)}', '']
    fields = ['severity','risk_type','file','line','match','release_effect','remediation']
    lines.append('| ' + ' | '.join(fields) + ' |')
    lines.append('| ' + ' | '.join(['---']*len(fields)) + ' |')
    for r in rows[:160]:
        lines.append('| ' + ' | '.join(str(r.get(f,'')).replace('|','/').replace('\n',' ')[:220] for f in fields) + ' |')
    if len(rows) > 160:
        lines.append('\n_Table truncated at 160 rows; CSV/JSON contain all rows._')
    (out/'Public-Release-Lint-current.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--fail-on-high', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rows = run(root)
    if args.write_report:
        write_reports(root, rows)
    high = [r for r in rows if r.get('severity') == 'high']
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        med = [r for r in rows if r.get('severity') == 'medium']
        print(f'public_release_lint_rows={len(rows)} high={len(high)} medium={len(med)}')
    if args.fail_on_high and high:
        sys.exit(1)

if __name__ == '__main__':
    main()
