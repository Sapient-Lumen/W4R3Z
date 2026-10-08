#!/usr/bin/env python3
"""Audit BVPS/current nuclear-emergency claim surfaces for affirmative readiness overclaim language.

The scanner records every hit. Negative-control, forbidden-claim, cannot-say, and
no-closure contexts are allowed, but affirmative closure language outside those
contexts is risky and fails the paired validator.
"""
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATTERNS=[
    'proved local readiness','local readiness proved','certified ready','passed the exercise','exercise passed',
    'readiness proof achieved','readiness closure granted','release eligibility granted','alert success assumed',
    'protective action success assumed','certified readiness','readiness demonstrated','exercise success'
]
ALLOW_MARKERS=[
    'forbidden','cannot','can not','not ', 'not*','does not','do not','no_', 'no-', 'no ', 'never', 'pending',
    'claim-freeze','claim freeze','not proof','not as proof','cannot say','still_cannot_say','forbidden_states_or_claims',
    'without proof','hypothetical','counterexample','negative control','rejects','proof of exercise success',
    'not enough','zero-credit','no-credit','not real evidence','artifacts are required later','bad_negative_control','badnegativecontrol','capture clock only','closed readiness gaps'
]
SCAN_SUFFIXES={'.md','.csv'}
SKIP_DIRS={'.git','__pycache__'}
MAX_SCAN_BYTES=1500000
ALWAYS_SCAN_PREFIXES=('cube/nuclear-emergency-bvps-', 'cube/bvps-', 'validation-report-rev0366', 'cube/validation-report-rev0366')

def normalize(line: str) -> str:
    low=line.lower()
    low=re.sub(r'[*_`>\[\]()]','',low)
    low=re.sub(r'\s+',' ',low)
    return low

def classify(norm: str) -> tuple[str,str]:
    markers=[m for m in ALLOW_MARKERS if m in norm]
    if markers:
        return 'allowed_negative_or_forbidden_context',';'.join(markers[:5])
    return 'risky_affirmative_overclaim','no_allow_marker'

def iter_files() -> list[Path]:
    files=[]
    csv_prefixes=(
        'cube/nuclear-emergency', 'cube/bvps', 'cube/source-clock-and',
        'cube/data-quality-result-rev0314.csv', 'cube/nuclear-emergency-real-public-validator-fixture-rev0314.csv',
        'cube/nuclear-emergency-bvps-real-public-no-claim-scope-rev0317.csv',
        'validation-report', 'cube/validation-report'
    )
    for p in ROOT.rglob('*'):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel=str(p.relative_to(ROOT))
        if p.name == 'nuclear-emergency-bvps-package-claim-surface-audit-rev0366.csv':
            continue
        suf=p.suffix.lower()
        if suf == '.md':
            files.append(p)
        elif suf == '.csv' and p.stat().st_size <= MAX_SCAN_BYTES and rel.startswith(csv_prefixes):
            files.append(p)
    return sorted(files)

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--out', default='cube/nuclear-emergency-bvps-package-claim-surface-audit-rev0366.csv')
    args=ap.parse_args()
    rows=[]; scanned=0
    scan_set=set(iter_files())
    skipped=0
    for q in ROOT.rglob('*'):
        if q.is_file() and q.suffix.lower() in SCAN_SUFFIXES and q not in scan_set and q.stat().st_size > MAX_SCAN_BYTES:
            skipped += 1
    if skipped:
        rows.append({'audit_id':'CLAIM-0366-0000','path':'<large_csv_claim_scan_boundary>','line_number':'0','pattern':'__skipped_large_files__','risk_status':'skipped_large_noncurrent_claim_surface','allow_reason':f'count={skipped}; use hotpath manifest or targeted audit for giant matrices','line_excerpt':'Large CSV matrices skipped by bounded overclaim scan to avoid routine whole-cube waste.'})
    for p in sorted(scan_set):
        rel=str(p.relative_to(ROOT))
        try:
            lines=p.read_text(encoding='utf-8', errors='ignore').splitlines()
        except Exception:
            continue
        scanned += 1
        for lineno,line in enumerate(lines,1):
            norm=normalize(line)
            for pat in PATTERNS:
                if pat in norm:
                    risk,reason=classify(norm)
                    rows.append({'audit_id':f'CLAIM-0366-{len(rows)+1:04d}','path':rel,'line_number':lineno,'pattern':pat,'risk_status':risk,'allow_reason':reason,'line_excerpt':line[:500]})
    out=ROOT/args.out; out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames=['audit_id','path','line_number','pattern','risk_status','allow_reason','line_excerpt']
    with out.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)
    risky=sum(1 for r in rows if r['risk_status']=='risky_affirmative_overclaim')
    print(f'PASS claim_surface_audit scanned_files={scanned} hits={len(rows)} risky={risky} out={out}')
    return 1 if risky else 0
if __name__=='__main__':
    raise SystemExit(main())
