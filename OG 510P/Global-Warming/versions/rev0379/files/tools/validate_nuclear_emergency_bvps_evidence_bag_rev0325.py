#!/usr/bin/env python3
"""Validate rev0325 BVPS live evidence-bag fixtures.

No accepted state is closure. Public/context/archive sources can only contextualize, hold,
reopen, or reject overclaim. Complete local/anonymized bags become candidates for
adjudication, not readiness closure.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path

PUBLIC_CLASSES = {'public_context','public_archive','public_verification_tool','public_schedule','public_AAR','public_event_notification'}

def truth(v):
    return str(v).strip().lower() == 'true'

def classify(row):
    source = row.get('source_class','')
    claims = truth(row.get('claims_local_closure'))
    self_attested = truth(row.get('self_attested'))
    counter = truth(row.get('counterevidence'))
    if claims:
        return 'reject_closure_attempt', 'claims local closure before adjudication/CAP/retest/verifier gate'
    if self_attested:
        return 'reject_closure_attempt', 'self-attested packet cannot close or candidate a claim'
    if counter:
        return 'accepted_reopen_signal', 'counterevidence accepted for reopen triage, not closure'
    if source in PUBLIC_CLASSES:
        return 'context_no_upgrade', 'public/context/archive source cannot close local evidence'
    missing = []
    for f in ['bag_manifest_present','original_hash_present','redacted_hash_present','clock_drift_ok','sensitive_annex_split','public_surrogate_present','cap_fields_complete']:
        if not truth(row.get(f)):
            missing.append(f)
    try:
        chain_count = int(str(row.get('chain_events_count','0')).strip() or '0')
    except ValueError:
        chain_count = 0
    if chain_count < 1:
        missing.append('chain_events_count')
    if truth(row.get('missing_raw_log')):
        missing.append('missing_raw_log')
    if truth(row.get('source_uses_public_archive')) and not truth(row.get('original_hash_present')):
        missing.append('public_archive_without_local_hash')
    if missing:
        return 'hold_no_upgrade', 'missing or weak evidence fields: ' + ';'.join(sorted(set(missing)))
    return 'candidate_for_adjudication_not_closure', 'complete local/anonymized bag shape; still requires board adjudication and no auto-closure'

def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 2:
        print('usage: validate_nuclear_emergency_bvps_evidence_bag_rev0325.py fixture.csv result.csv', file=sys.stderr)
        return 2
    inp, out = map(Path, argv)
    with inp.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys()) if rows else []
    out_fields = fields + ['actual_decision','pass','public_context_to_local_closure_leak','decision_reason']
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        failures = 0
        for row in rows:
            actual, reason = classify(row)
            row['actual_decision'] = actual
            row['pass'] = str(actual == row.get('expected_decision')).lower()
            leak = (row.get('source_class') in PUBLIC_CLASSES and actual == 'candidate_for_adjudication_not_closure') or actual in {'accepted_closure','auto_closure','green'}
            row['public_context_to_local_closure_leak'] = str(leak).lower()
            row['decision_reason'] = reason
            if row['pass'] != 'true':
                failures += 1
            w.writerow(row)
    print(f'validated {len(rows)} evidence-bag fixtures; failures={failures}')
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
