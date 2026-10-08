#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv
ALLOWED_EFFECTS={'hold_or_reopen_no_upgrade','partial_context_no_upgrade','source_currentness_refresh_only_no_upgrade','future_watch_no_upgrade','reject'}
BLOCKED_WORDS=('ready','green','certified','passed exercise','sufficient')
def read(path):
    with open(path,newline='',encoding='utf-8') as f:
        r=csv.DictReader(f); return r.fieldnames or [], list(r)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True)
    ap.add_argument('--source-csv',required=True)
    ap.add_argument('--output',required=True)
    ns=ap.parse_args()
    _, sources=read(ns.source_csv); valid_sources={r['source_id'] for r in sources}
    _, rows=read(ns.input)
    out=[]; seen=set()
    for r in rows:
        errors=[]; effects=[]
        sid=r.get('source_id',''); sig=r.get('signal_id','')
        if sid not in valid_sources: errors.append('unregistered_source')
        if sig in seen: errors.append('duplicate_signal_id')
        seen.add(sig)
        if r.get('readiness_effect','') not in ALLOWED_EFFECTS: errors.append('unknown_or_upgrade_readiness_effect')
        claim=(r.get('declared_claim','') or r.get('public_signal_summary','')).lower()
        claim_effect=(r.get('claim_effect','') or '').lower()
        if any(w in claim for w in BLOCKED_WORDS) and not any(x in claim_effect for x in ['hold','block','watch','disclose','no_score']):
            errors.append('green_or_ready_claim_without_block')
        if r.get('public_signal_type')=='future_evaluated_exercise_notice' and 'passed' in claim:
            errors.append('future_exercise_treated_as_passed')
        if r.get('public_signal_type')=='event_notification' and 'closure packet' not in (r.get('counterevidence_path','') + ' ' + r.get('local_evidence_demand','')).lower():
            errors.append('event_without_closure_packet_path')
        if r.get('source_id')=='S999' and 'EP03 current' in r.get('public_signal_summary',''):
            errors.append('ep03_retired_guardrail_failed')
        if errors:
            verdict='reject'
        elif any(x in r.get('readiness_effect','') for x in ['hold','watch']) or any(x in claim_effect for x in ['hold','watch','disclose']):
            verdict='accept_with_hold_or_watch'
            effects.append('no_readiness_upgrade')
        else:
            verdict='accept_partial_no_upgrade'
            effects.append('no_readiness_upgrade')
        out.append({'signal_id':sig,'source_id':sid,'public_signal_type':r.get('public_signal_type',''),'validator_verdict':verdict,'error_codes':';'.join(errors),'computed_effects':';'.join(effects),'created_revision':'rev0313','status':'validated'})
    fields=['signal_id','source_id','public_signal_type','validator_verdict','error_codes','computed_effects','created_revision','status']
    with open(ns.output,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    print(f'validated={len(out)} rejected={sum(1 for r in out if r["validator_verdict"]=="reject")}')
if __name__=='__main__': main()
