#!/usr/bin/env python3
import csv, sys
from pathlib import Path

TRUE = {'true','1','yes','y'}
PUBLIC_STATUSES = {'public_context_only','public_feed_context'}
CANDIDATE = 'candidate_for_adjudication_no_public_claim'
HOLD = 'hold_no_upgrade'
REJECT = 'reject'
REJECT_CLAIM = 'reject_public_claim_attempt'

def truth(v): return str(v).strip().lower() in TRUE

def decide(row):
    if truth(row.get('public_claim_requested')):
        return REJECT_CLAIM, 'public_claim_must_go_through_claim_gate'
    if row.get('synthetic_status') in PUBLIC_STATUSES or not truth(row.get('local_artifact_present')):
        return REJECT, 'public_context_or_missing_local_artifact'
    hard = ['owner_named','independent_verifier_named','artifact_hash_present','scope_complete','counterevidence_path','redaction_review']
    missing = [k for k in hard if not truth(row.get(k))]
    if missing:
        # missing owner/hash can be outright rejected if there is too little artifact integrity
        if 'artifact_hash_present' in missing or 'owner_named' in missing:
            return REJECT, 'missing_' + '_'.join(missing)
        return HOLD, 'missing_' + '_'.join(missing)
    if str(row.get('artifact_date_status','')).lower() in {'undated','stale','public_event_date_only','future_schedule'}:
        return REJECT, 'bad_or_nonlocal_artifact_date_clock'
    if str(row.get('artifact_date_status','')).lower() in {'stale_or_source_clock_hold','future_relative_fixture'}:
        return HOLD, 'source_clock_or_future_fixture_hold'
    if str(row.get('cap_retest_status','')).lower() in {'open','open_cap','failed_retest','reopened_by_counterevidence','none'}:
        return HOLD, 'cap_retest_not_closed_or_counterevidence_open'
    if not truth(row.get('exercise_or_sampling_evidence_present')):
        return HOLD, 'missing_exercise_or_sampling_or_retest_evidence'
    return CANDIDATE, 'all_minimum_elements_present_candidate_only'

def main(root='.'):
    root = Path(root)
    inpath = root/'cube/nuclear-emergency-bvps-local-packet-import-fixture-rev0320.csv'
    outpath = root/'cube/nuclear-emergency-bvps-local-packet-validator-result-rev0320.csv'
    with inpath.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    out=[]
    failures=0
    for r in rows:
        decision, reason = decide(r)
        status = 'pass' if decision == r.get('expected_decision') else 'fail'
        if status == 'fail': failures += 1
        out.append({
            'packet_id': r['packet_id'],
            'packet_class': r['packet_class'],
            'expected_decision': r.get('expected_decision',''),
            'decision': decision,
            'reason': reason,
            'candidate_closure_allowed': 'true' if decision == CANDIDATE else 'false',
            'local_readiness_closure_allowed': 'false',
            'public_claim_allowed': 'false',
            'test_status': status
        })
    with outpath.open('w', newline='', encoding='utf-8') as f:
        fields = ['packet_id','packet_class','expected_decision','decision','reason','candidate_closure_allowed','local_readiness_closure_allowed','public_claim_allowed','test_status']
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
    if failures:
        print(f'{failures} validation fixture failures', file=sys.stderr)
        return 1
    print(f'validated {len(out)} packet fixture rows; all expected decisions matched')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
