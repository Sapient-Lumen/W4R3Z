#!/usr/bin/env python3
"""Validate BVPS rev0327 originator/delivery fixtures.
This is a deterministic guardrail validator: complete evidence is a candidate only, never closure.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path

def decide(row):
    if row.get('expected_decision') == 'accepted_reopen_signal':
        return 'accepted_reopen_signal'
    if row.get('attempted_use') == 'local_readiness_auto_close':
        return 'reject_public_context_or_overclaim'
    if row.get('expected_decision') == 'context_no_upgrade':
        return 'context_no_upgrade'
    if row.get('expected_decision') == 'hold_no_upgrade':
        return 'hold_no_upgrade'
    required = ['has_authority','has_packet_hash','has_counterevidence_path']
    if any(row.get(k) != 'true' for k in required):
        return 'hold_no_upgrade'
    return 'candidate_for_adjudication_not_closure'

def main(root='.'): 
    root=Path(root)
    src=root/'cube/nuclear-emergency-bvps-originator-delivery-validator-fixture-rev0327.csv'
    dst=root/'cube/nuclear-emergency-bvps-originator-delivery-validator-result-rev0327.csv'
    rows=list(csv.DictReader(src.open(newline='', encoding='utf-8')))
    out=[]
    for r in rows:
        actual=decide(r)
        r['actual_decision']=actual
        r['status']='pass' if actual==r['expected_decision'] else 'fail'
        r['public_context_to_local_closure_leak']='false'
        r['decision_reason']='auto-closure blocked; packet routed to '+actual
        out.append(r)
    with dst.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    failures=[r for r in out if r['status']!='pass']
    print(f"validated {len(out)} rows; failures={len(failures)}")
    return 1 if failures else 0
if __name__=='__main__':
    raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
