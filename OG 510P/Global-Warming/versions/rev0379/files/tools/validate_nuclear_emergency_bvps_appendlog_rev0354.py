#!/usr/bin/env python3
import csv, sys, os
from collections import Counter
base=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
result=os.path.join(base,'cube','nuclear-emergency-bvps-appendlog-validator-result-rev0354.csv')
chain=os.path.join(base,'cube','nuclear-emergency-bvps-receipt-append-only-hash-chain-rev0354.csv')
rows=list(csv.DictReader(open(result,newline='',encoding='utf-8')))
counts=Counter(r['classification'] for r in rows)
assert len(rows)==54, len(rows)
assert counts['rejected_closure_attempt']==16, counts
assert counts['hold_no_upgrade']==14, counts
assert counts['candidate_for_adjudication_not_closure']==10, counts
assert counts['accepted_reopen_signal']==6, counts
assert counts['context_no_upgrade']==8, counts
assert all(r['observed_auto_closure']=='no' for r in rows)
chain_rows=list(csv.DictReader(open(chain,newline='',encoding='utf-8')))
assert len(chain_rows)==60
assert all(r['chain_link_status']=='ok' for r in chain_rows)
print('rev0354 appendlog validator ok')
