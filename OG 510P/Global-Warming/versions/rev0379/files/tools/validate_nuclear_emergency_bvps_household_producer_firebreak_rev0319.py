#!/usr/bin/env python3
import csv, sys
from pathlib import Path

def decide(row):
    public_sources={'AFN public card','Farmer public info page','Ready PA 10/50 mile page','Ohio procedure listing','Columbiana public plan table','Hancock KI page','WV State EOP under construction page','future exercise notice','public ETE table','public mass-care capacity'}
    if row['attempted_source'] in public_sources:
        return 'reject','public_context_cannot_close_local_readiness'
    if row['attempted_source']=='counterevidence report':
        return 'accept_as_reopen_signal','counterevidence_can_reopen_or_cap_but_not_close'
    if row['has_owner']!='true' or row['has_hash']!='true' or row['has_artifact_date']!='true':
        return 'reject','missing_owner_hash_or_artifact_date'
    if row['has_counterevidence_path']!='true':
        return 'reject','missing_counterevidence_path'
    if row['has_exercise_or_sampling_evidence']!='true':
        return 'hold_no_upgrade','packet_context_accepted_but_no_performance_or_sampling_evidence'
    if row['attempted_claim']=='publish public claim':
        return 'reject','redaction_and_public_claim_gate_required_before_publication'
    return 'candidate_not_auto_close','candidate_for_adjudication_only_not_automatic_closure'

def main(inp, outp):
    with open(inp, newline='', encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
        fields=list(rows[0].keys())+['decision','reason','test_status'] if rows else ['decision','reason','test_status']
    out=[]
    for row in rows:
        d,reason=decide(row)
        row=dict(row); row['decision']=d; row['reason']=reason; row['test_status']='pass' if d==row.get('expected_decision') else 'fail'; out.append(row)
    with open(outp,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    if any(r['test_status']!='pass' for r in out):
        return 1
    return 0
if __name__=='__main__':
    if len(sys.argv)!=3:
        print('usage: validate_nuclear_emergency_bvps_household_producer_firebreak_rev0319.py input.csv output.csv', file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
