
#!/usr/bin/env python3
"""Validate rev0349 preflight rehearsal / receipt / claim-lint controls."""
from pathlib import Path
import csv, sys
ROOT = Path(__file__).resolve().parents[1]
CUBE = ROOT / 'cube'

def rows(name):
    with open(CUBE/name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

checks=[]
receipts=rows('nuclear-emergency-bvps-intake-receipt-ledger-rev0349.csv')
checks.append(('60_receipts', len(receipts)==60, len(receipts)))
checks.append(('no_receipt_auto_closure', all(r.get('may_count_as_closure')=='no' for r in receipts), ''))
lint=rows('nuclear-emergency-bvps-claim-embargo-lint-result-rev0349.csv')
checks.append(('54_lint_tests', len(lint)==54, len(lint)))
checks.append(('no_lint_auto_closure', all(r.get('auto_closure_allowed')=='no' for r in lint), ''))
canary=rows('nuclear-emergency-bvps-replay-canary-negative-control-rev0349.csv')
checks.append(('18_canaries', len(canary)==18, len(canary)))
checks.append(('no_canary_auto_closure', all(r.get('auto_closure_allowed')=='no' for r in canary), ''))
snap=rows('nuclear-emergency-bvps-preflight-snapshot-seal-rev0349.csv')
checks.append(('snapshot_has_files', len(snap) >= 60, len(snap)))
fail=[c for c in checks if not c[1]]
for name,ok,detail in checks:
    print(f'{"PASS" if ok else "FAIL"} {name} {detail}')
if fail:
    sys.exit(1)
