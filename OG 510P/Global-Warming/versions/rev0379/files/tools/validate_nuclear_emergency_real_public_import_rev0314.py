#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv
from datetime import date
PACKAGE_DATE = date(2026, 6, 4)
ALLOWED_EFFECTS = {'no_upgrade_context','source_refresh_only','no_upgrade_reopen','future_watch_no_upgrade','red_hold','yellow_cap','reject'}
LOCAL_CLOSURE_ROLES = {'local_closure','local_artifact','capacity_proof','route_capacity_proof','exercise_passed'}
BLOCKED_CLAIM_WORDS = ('ready','green','certified','safe','sufficient','closed','passed')

def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        return r.fieldnames or [], list(r)

def parse_date(s):
    try:
        y,m,d = [int(x) for x in s.split('-')]
        return date(y,m,d)
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--source-csv', required=True)
    ap.add_argument('--output', required=True)
    ns = ap.parse_args()
    _, sources = read(ns.source_csv)
    source_ids = {r['source_id'] for r in sources}
    _, rows = read(ns.input)
    out=[]; seen=set()
    for r in rows:
        errors=[]; warnings=[]; effects=[]
        sig = r.get('signal_id','')
        sid = r.get('source_id','')
        fam = r.get('public_signal_family','')
        value = (r.get('signal_value','') or '').lower()
        role = (r.get('evidence_role','') or '').lower()
        eff = r.get('declared_readiness_effect','')
        claim = (r.get('declared_public_claim','') or '').lower()
        pub_only = (r.get('public_source_only_flag','') or '').lower() == 'yes'
        if not sig: errors.append('missing_signal_id')
        if sig in seen: errors.append('duplicate_signal_id')
        seen.add(sig)
        if sid not in source_ids: errors.append('unregistered_source_id')
        if eff not in ALLOWED_EFFECTS: errors.append('unknown_readiness_effect')
        if pub_only and role in LOCAL_CLOSURE_ROLES: errors.append('public_source_cannot_be_local_closure_or_capacity_proof')
        if 'ep03' in value and 'current' in value: errors.append('ep03_retired_cannot_be_current')
        if fam == 'event_notification':
            if not r.get('counterevidence_path','').strip(): errors.append('event_notification_requires_counterevidence_path')
            if eff not in {'no_upgrade_reopen','red_hold','yellow_cap'}: errors.append('event_notification_must_reopen_or_cap')
        if fam == 'future_exercise':
            nd = parse_date(r.get('not_before_date',''))
            if nd and PACKAGE_DATE < nd and any(w in claim for w in ('passed','complete','closed')): errors.append('future_exercise_treated_as_completed')
            if eff != 'future_watch_no_upgrade': errors.append('future_exercise_must_be_watch_no_upgrade')
        if fam in {'public_brochure','county_plan','state_strategy','state_public_context'} and role in LOCAL_CLOSURE_ROLES: errors.append('public_plan_or_brochure_cannot_be_local_artifact')
        if fam == 'public_brochure' and ('route capacity' in claim or 'evacuation ready' in claim): errors.append('public_route_brochure_cannot_prove_capacity')
        if any(w in claim for w in BLOCKED_CLAIM_WORDS) and 'blocked' not in claim and 'not ' not in claim:
            errors.append('public_signal_misused_for_positive_readiness_claim')
        if role == 'private_local_artifact' and not r.get('artifact_hash','').strip(): errors.append('private_or_local_artifact_missing_hash')
        if errors:
            verdict='reject'
        elif eff in {'no_upgrade_reopen','red_hold','yellow_cap','future_watch_no_upgrade'}:
            verdict='accept_with_hold_cap_or_watch'
            effects.append('no_readiness_upgrade')
        else:
            verdict='accept_partial_no_upgrade'
            effects.append('no_readiness_upgrade')
        if eff in {'red_hold','no_upgrade_reopen'}: effects.append('public_green_blocked')
        if eff == 'future_watch_no_upgrade': effects.append('future_result_not_inferred')
        out.append({'signal_id':sig,'source_id':sid,'public_signal_family':fam,'validator_verdict':verdict,'error_codes':';'.join(errors),'warning_codes':';'.join(warnings),'computed_effects':';'.join(sorted(set(effects))) or 'no_readiness_upgrade','created_revision':'rev0314','status':'validated'})
    fields=['signal_id','source_id','public_signal_family','validator_verdict','error_codes','warning_codes','computed_effects','created_revision','status']
    with open(ns.output,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    print(f"validated={len(out)} reject={sum(1 for r in out if r['validator_verdict']=='reject')}")
if __name__ == '__main__':
    main()
