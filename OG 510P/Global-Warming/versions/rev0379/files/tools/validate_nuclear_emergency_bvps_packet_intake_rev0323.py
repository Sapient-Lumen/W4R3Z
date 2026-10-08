#!/usr/bin/env python3
import csv, sys
from pathlib import Path

BOOL_FIELDS = ['has_hash','has_owner','has_timestamp','has_scope','has_original_artifact','has_sensitive_annex_split','has_public_surrogate','has_verifier','has_retest_or_CAP_state','has_counterevidence_path']
PUBLIC_CLASSES = {'public_schedule','public_preliminary_meeting','public_AAR_summary','public_reactor_status','public_ETE_table','public_KI_brochure','public_masscare_table','public_event_notification','public_website_screenshot','public_exercise_schedule','public_meeting_transcript','public_AAR_final','public_NRC_data_feed'}
COUNTER_CLASSES = {'counterevidence_failed_retest','counterevidence_raw_log_conflict','counterevidence_evaluator_observation'}

def truth(v): return str(v).strip().lower() == 'true'

def classify(row):
    src = row.get('input_source_class','')
    claims = truth(row.get('claims_local_closure'))
    if src in COUNTER_CLASSES:
        return 'accepted_reopen_signal'
    if claims:
        return 'reject_closure_attempt'
    if src in PUBLIC_CLASSES:
        return 'context_no_upgrade'
    if src in {'revised_template_only','hotwash_summary_only','self_attested_local_packet'}:
        return 'hold_no_upgrade'
    missing = [f for f in BOOL_FIELDS if not truth(row.get(f))]
    if missing:
        return 'hold_no_upgrade'
    if src == 'local_anonymized_packet':
        return 'candidate_for_adjudication_not_closure'
    return 'hold_no_upgrade'

def main():
    if len(sys.argv) < 3:
        print('usage: validator.py fixture.csv result.csv', file=sys.stderr)
        return 2
    inp, out = Path(sys.argv[1]), Path(sys.argv[2])
    with inp.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys()) if rows else []
    out_fields = fields + ['actual_outcome','pass','public_closure_leak']
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        for row in rows:
            actual = classify(row)
            row['actual_outcome'] = actual
            row['pass'] = str(actual == row.get('expected_outcome')).lower()
            src = row.get('input_source_class','')
            leak = (src.startswith('public') and actual in {'candidate_for_adjudication_not_closure','accepted_closure','auto_closure'})
            row['public_closure_leak'] = str(leak).lower()
            w.writerow(row)
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
