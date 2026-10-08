#!/usr/bin/env python3
"""Validate Beaver Valley public-message lint fixture for rev0321.

Usage:
  python tools/validate_nuclear_emergency_bvps_message_lint_rev0321.py \
      --input cube/nuclear-emergency-bvps-message-lint-fixture-rev0321.csv \
      --output cube/nuclear-emergency-bvps-message-lint-result-rev0321.csv
"""
import argparse, csv, re, sys

REJECT_WORDS = re.compile(r"\b(ready|green|passed|closed|complete|certified|sufficient)\b", re.I)


def classify(row):
    triggers=[]
    text = (row.get('message_text') or '').lower()
    scenario = (row.get('scenario') or '').lower()
    channel = (row.get('channel') or '').lower()
    claim = (row.get('attempted_claim') or '').lower()
    jurisdiction = (row.get('jurisdiction') or '').lower()
    listed = (row.get('jurisdiction_listed') or '').lower()

    if 'counterevidence' in scenario or channel == 'counterevidence':
        return 'accepted_reopen_signal', 'MLR0321_020', 'counterevidence reopens affected claim or packet row'

    if 'reactor_status' in scenario or ('reactor status' in text and REJECT_WORDS.search(claim + ' ' + text)):
        return 'reject', 'MLR0321_013;MLR0321_019', 'reactor-status signal cannot close emergency-preparedness readiness'
    if 'future_exercise' in scenario or ('scheduled' in text and REJECT_WORDS.search(claim + ' ' + text)):
        return 'reject', 'MLR0321_012;MLR0321_019', 'future exercise notice cannot be passed/completed evidence'
    if 'average_away' in scenario or ('ohio had no' in text and 'green' in text):
        return 'reject', 'MLR0321_015;MLR0321_019', 'clean jurisdiction baseline cannot average away another jurisdiction blocker'
    if 'en58200' in scenario or ('en58200' in text and REJECT_WORDS.search(claim + ' ' + text)):
        return 'reject', 'MLR0321_014;MLR0321_019', 'EN58200 public text cannot close EOF corrective action'
    if channel == 'public_claim' and REJECT_WORDS.search(claim + ' ' + text):
        return 'reject', 'MLR0321_019', 'forbidden public-claim language from public context or fixtures'

    if not (row.get('authority_decision_ref') or '').strip():
        triggers.append('MLR0321_001')
    if row.get('template_revision_status') not in ('current_hashed_loaded','not_applicable'):
        triggers.append('MLR0321_002')
    if row.get('public_url_status') in ('broken','untested'):
        triggers.append('MLR0321_003')
    if row.get('ki_instruction') == 'conflict' or ('take ki' in text and ('do not take ki' in text or 'locate ki but do not take' in text)):
        triggers.append('MLR0321_004')
    if ('hancock' in jurisdiction or 'west_virginia' in jurisdiction or 'wv' in jurisdiction) and 'chester' not in listed:
        triggers.append('MLR0321_005')
    if row.get('farmer_instruction') == 'conflicts_with_PAD':
        triggers.append('MLR0321_006')
    if row.get('school_instruction') == 'early_dismissal_no_ema_coordination':
        triggers.append('MLR0321_007')
    if row.get('release_sequence_ok') != 'yes':
        triggers.append('MLR0321_008')
    if 'exercise' in scenario and 'exercise' not in text and 'drill' not in text:
        triggers.append('MLR0321_016')
    if row.get('pio_review_status') != 'reviewed_signed':
        triggers.append('MLR0321_018')

    if triggers:
        return 'reject', ';'.join(sorted(set(triggers))), 'message packet violates one or more P0/P1 rejection rules'

    holds=[]
    if row.get('language_access_ok') != 'yes':
        holds.append('MLR0321_009')
    if row.get('redaction_ok') != 'yes':
        holds.append('MLR0321_010')
    if row.get('cap_retest_status') not in ('closed_verified','not_applicable'):
        holds.append('MLR0321_011')
    if row.get('rumor_correction_path') != 'defined':
        holds.append('MLR0321_017')
    if holds:
        return 'hold_no_upgrade', ';'.join(sorted(set(holds))), 'packet may be routed but cannot upgrade or support public green claim'

    return 'candidate_for_adjudication_not_auto_close', '', 'well formed packet candidate; still requires local adjudication and public claim gate'


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    args=ap.parse_args(argv)
    with open(args.input, newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    out=[]
    failures=0
    for row in rows:
        state, rules, effect = classify(row)
        ok = (state == row.get('expected_lint_state'))
        if not ok:
            failures += 1
        out.append({
            'message_id': row.get('message_id',''),
            'expected_lint_state': row.get('expected_lint_state',''),
            'observed_lint_state': state,
            'pass_fail': 'pass' if ok else 'fail',
            'triggered_rules': rules,
            'claim_effect': effect,
        })
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames=['message_id','expected_lint_state','observed_lint_state','pass_fail','triggered_rules','claim_effect']
        w=csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(out)
    if failures:
        print(f'{failures} lint fixture expectation(s) failed', file=sys.stderr)
        return 1
    counts={}
    for r in out:
        counts[r['observed_lint_state']]=counts.get(r['observed_lint_state'],0)+1
    print('message_lint_validation_passed', counts)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
