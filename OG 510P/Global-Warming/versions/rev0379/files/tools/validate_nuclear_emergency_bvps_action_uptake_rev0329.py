#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path

def b(v: str) -> bool:
    return str(v).strip().lower() in {'1','true','yes','y'}

def classify(row):
    public_context_only=b(row.get('public_context_only',''))
    if b(row.get('uses_public_context_as_closure','')):
        return 'rejected_closure_attempt','public/context artifact attempted to close local action uptake'
    if b(row.get('counterevidence_present','')):
        return 'accepted_reopen_signal','counterevidence or wrong-action signal routes to reopen/CAP path'
    if public_context_only:
        return 'context_no_upgrade','public context may educate or route but cannot upgrade readiness'
    required = ['has_local_packet','has_hash','has_timestamp','has_owner','has_behavior_probe','has_message_linkage','has_privacy_redaction']
    missing=[k for k in required if not b(row.get(k,''))]
    if missing:
        return 'hold_no_upgrade','missing required fields: '+ ';'.join(missing)
    if not b(row.get('has_verifier','')) or not b(row.get('has_cap_retest','')):
        return 'hold_no_upgrade','missing verifier or CAP/retest linkage'
    return 'candidate_for_adjudication','complete enough for adjudication; not closure'

def main(argv=None):
    argv=argv or sys.argv[1:]
    if len(argv)!=2:
        print('usage: validate_nuclear_emergency_bvps_action_uptake_rev0329.py INPUT_CSV OUTPUT_CSV', file=sys.stderr)
        return 2
    src=Path(argv[0]); dst=Path(argv[1])
    with src.open(newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    out=[]
    for r in rows:
        status, reason = classify(r)
        out.append({**r,'result_status':status,'reason':reason,'auto_closes_local_readiness':'false','public_claim_effect':'block_or_hold_until_adjudicated' if status!='context_no_upgrade' else 'context_only_no_upgrade'})
    fieldnames=list(out[0].keys()) if out else []
    with dst.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(out)
    counts={}
    for r in out: counts[r['result_status']]=counts.get(r['result_status'],0)+1
    print(counts)
    return 0
if __name__=='__main__':
    raise SystemExit(main())
