from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def text(rel): return (ROOT/rel).read_text(encoding='utf-8')
def rows(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
alias_text='\n'.join(str(r) for r in rows('cube/bvps-ens-ipaws-terminology-alias-audit-rev0376.csv'))
for term in ['ENS','IPAWS','WENS','EAS','WEA','public warning']:
    if term.lower() not in alias_text.lower():
        raise SystemExit(f'missing alias term {term}')
for rel in ['records-requests/bvps-rev0376/rrt-0376-009-columbiana-ema-ens-ipaws-current-plan-exercise-logs.md','records-requests/bvps-rev0376/rrt-0376-010-ohio-dps-public-records-center-ema-ens-ipaws-exercise-logs.md']:
    t=text(rel).lower()
    for term in ['ens','ipaws','corrective','retest','withheld']:
        if term not in t:
            raise SystemExit(f'{rel} missing {term}')
    if 'claim rule' not in t or 'not evidence' not in t:
        raise SystemExit(f'{rel} missing claim boundary')
print('PASS ENS/IPAWS alias gate and request packets present')
