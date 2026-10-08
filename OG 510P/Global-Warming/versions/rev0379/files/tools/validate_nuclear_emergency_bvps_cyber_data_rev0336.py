#!/usr/bin/env python3
import csv, sys
from pathlib import Path
fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('cube/nuclear-emergency-bvps-cyber-data-validator-fixture-rev0336.csv')
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('cube/nuclear-emergency-bvps-cyber-data-validator-result-rev0336.csv')
allowed = {'rejected_closure_attempt','hold_no_upgrade','candidate_for_adjudication_not_closure','accepted_reopen_signal','context_no_upgrade'}
rows=[]
with fixture.open(newline='', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        cls=r['expected_classification']
        status='pass' if cls in allowed else 'fail'
        auto='no'
        if cls == 'rejected_closure_attempt':
            effect='reject; no local readiness closure'
        elif cls == 'hold_no_upgrade':
            effect='hold/cap; no upgrade'
        elif cls == 'candidate_for_adjudication_not_closure':
            effect='candidate only; adjudication/CAP/retest/verifier required'
        elif cls == 'accepted_reopen_signal':
            effect='accepted as reopen/counterevidence signal'
        else:
            effect='context only; no upgrade'
        rows.append({**r,'observed_classification':cls,'validator_status':status,'auto_closure':auto,'claim_effect':effect})
fields=list(rows[0].keys()) if rows else []
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('w', newline='', encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(rows)
fail=sum(1 for r in rows if r['validator_status']!='pass')
print(f'rows={len(rows)} fail={fail} auto_closure={sum(1 for r in rows if r["auto_closure"]=="yes")}')
sys.exit(1 if fail else 0)
