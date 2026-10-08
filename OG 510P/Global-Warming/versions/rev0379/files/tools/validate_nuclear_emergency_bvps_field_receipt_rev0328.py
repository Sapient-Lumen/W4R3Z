#!/usr/bin/env python3
import csv, sys
from pathlib import Path

VALID_RESULTS={'reject','hold_no_upgrade','candidate_not_closure','accepted_reopen_signal','context_no_upgrade'}
PUBLIC_OR_PARTIAL={'public_archive_hit','public_archive_no_hit','ack_only','cap_only','screenshot_loose','wrong_channel','public_meeting_prelim','public_aar_excerpt','revised_template_only','public_guidance','public_rule','loose_anecdote','average_away','overshoot_ignored'}
HOLD_PREFIXES={'no_field_probe','missing_edge','missing_clock_offset','missing_redaction_verifier','missing_language_receipt','missing_afn_triage','missing_school_action_time','missing_producer_link','missing_cross_channel','missing_nonreceipt_crosscheck','missing_CAP_retest_verifier','missing_final_AAR'}
CAND_PREFIX='candidate_'
REOPEN_PREFIX='counterevidence_'
CONTEXT={'official_guidance_context','official_rule_context','public_clock_context','public_context_no_upgrade','public_language_context','cap_standard_context'}

def classify(row):
    cls=row['input_class']
    if cls in PUBLIC_OR_PARTIAL:
        return 'reject'
    if cls in HOLD_PREFIXES:
        return 'hold_no_upgrade'
    if cls.startswith(CAND_PREFIX):
        return 'candidate_not_closure'
    if cls.startswith(REOPEN_PREFIX):
        return 'accepted_reopen_signal'
    if cls in CONTEXT:
        return 'context_no_upgrade'
    return 'reject'

def main(inp, outp):
    with open(inp, newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    out=[]
    for r in rows:
        observed=classify(r)
        auto_close='false'
        pass_fail='pass' if observed==r['expected_result'] and observed in VALID_RESULTS else 'fail'
        out.append({**r,'observed_result':observed,'auto_closure':auto_close,'pass_fail':pass_fail,'validator_note':'field receipt packets are never automatic closure'})
    fields=list(out[0].keys())
    with open(outp,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
    fails=[r for r in out if r['pass_fail']!='pass']
    if fails:
        print(f'FAIL {len(fails)}')
        sys.exit(1)
    print(f'PASS {len(out)} tests')
if __name__=='__main__':
    main(sys.argv[1], sys.argv[2])
