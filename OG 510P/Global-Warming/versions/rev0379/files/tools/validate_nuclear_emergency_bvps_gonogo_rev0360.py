#!/usr/bin/env python3
"""Validate go/no-go result distribution and no-auto-closure invariant."""
import argparse, csv, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    args=p.parse_args(); root=Path(args.root)
    path=root/'cube/nuclear-emergency-bvps-gonogo-validator-result-rev0360.csv'
    rows=list(csv.DictReader(open(path, newline='', encoding='utf-8')))
    bad=[r for r in rows if r.get('auto_closure_allowed')!='no' or r.get('pass_fail')!='pass']
    counts={}
    for r in rows: counts[r['actual_state']]=counts.get(r['actual_state'],0)+1
    expected={'rejected_closure_attempt':16,'hold_no_upgrade':14,'candidate_for_adjudication_not_closure':10,'accepted_reopen_signal':6,'context_no_upgrade':8}
    if bad or counts!=expected:
        print({'bad':len(bad),'counts':counts,'expected':expected}); return 2
    print({'status':'pass','rows':len(rows),'counts':counts,'auto_closures':0}); return 0
if __name__=='__main__': sys.exit(main())
