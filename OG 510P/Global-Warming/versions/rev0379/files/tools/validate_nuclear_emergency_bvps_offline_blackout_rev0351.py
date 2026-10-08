#!/usr/bin/env python3
import csv, sys
from collections import Counter
path = sys.argv[1] if len(sys.argv)>1 else 'cube/nuclear-emergency-bvps-offline-blackout-validator-result-rev0351.csv'
with open(path, newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
counts=Counter(r['classification'] for r in rows)
assert len(rows)==54, len(rows)
assert counts['rejected_closure_attempt']==16, counts
assert counts['hold_no_upgrade']==14, counts
assert counts['candidate_for_adjudication_not_closure']==10, counts
assert counts['accepted_reopen_signal']==6, counts
assert counts['context_no_upgrade']==8, counts
assert all(r['auto_closure_allowed']=='no' for r in rows)
assert all(r['validator_pass']=='yes' for r in rows)
print('rev0351 offline blackout validator: pass')
