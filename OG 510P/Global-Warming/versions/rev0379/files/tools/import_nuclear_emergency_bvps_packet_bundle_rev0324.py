#!/usr/bin/env python3
"""Validate BVPS rev0324 packet dry-run bundles.

The validator intentionally never returns automatic local-readiness closure. Its accepted
states are reject_closure_attempt, hold_no_upgrade, context_no_upgrade,
accepted_reopen_signal, and candidate_for_adjudication_not_closure.
"""
from __future__ import annotations
import csv, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAT = ROOT/'cube/nuclear-emergency-bvps-packet-dryrun-bundle-catalog-rev0324.csv'
VALUES = ROOT/'cube/nuclear-emergency-bvps-packet-field-values-dryrun-rev0324.csv'
OUT = ROOT/'cube/nuclear-emergency-bvps-packet-import-validation-rev0324.csv'

FIELDNAMES = [
    'packet_id','template_id','packet_type','source_class','expected_decision','actual_decision','pass',
    'required_fields','present_required_fields','missing_required_fields','missing_field_names',
    'claims_local_closure','counterevidence_signal','public_context_source','has_custody_gap','bad_self_verifier','broken_public_link','public_closure_leak','decision_reason'
]

def read_dicts(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

def decide(bundle, rows):
    required=[r for r in rows if r.get('requirement_level')=='required']
    missing=[r['field_name'] for r in rows if str(r.get('present','')).lower()!='true' or not r.get('synthetic_value')]
    values={r['field_name']:r.get('synthetic_value','') for r in rows}
    claims=str(bundle.get('claims_local_closure','')).lower()=='true'
    counter=str(bundle.get('counterevidence_signal','')).lower()=='true'
    public=bundle.get('source_class')=='public_context'
    custody_gap='gap_' in values.get('custody_transfer','') or 'gap_between' in values.get('custody_transfer','')
    self_verifier='self_attested' in values.get('independent_verifier','') or values.get('independent_verifier','')=='self'
    broken=values.get('broken_link_result','').lower().startswith('broken_url') or '404' in values.get('broken_link_result','')
    finding='potential_Level_2' in values.get('finding_potential','')
    ki_conflict='CONFLICT' in values.get('KI_instruction_text','')
    # No automatic closure state exists.
    if claims:
        decision='reject_closure_attempt'
        reason='claims local readiness closure before adjudication/CAP/retest/verifier gate'
    elif public:
        decision='context_no_upgrade'
        reason='public context can route/cap/reopen but cannot close local evidence'
    elif self_verifier:
        decision='reject_closure_attempt'
        reason='self-attested verifier/retest cannot close or candidate a CAP packet'
    elif counter or broken or finding or ki_conflict:
        decision='accepted_reopen_signal'
        reason='counterevidence, broken link, finding potential, or KI/message conflict reopens claim path'
    elif missing or custody_gap:
        decision='hold_no_upgrade'
        reason='missing required fields or custody gap; missing data defaults to cap/hold'
    else:
        decision='candidate_for_adjudication_not_closure'
        reason='complete packet shape; still requires adjudication and cannot auto-close readiness'
    return decision, missing, custody_gap, self_verifier, broken, reason

def main():
    bundles=read_dicts(CAT)
    vals=read_dicts(VALUES)
    by_packet={}
    for r in vals:
        by_packet.setdefault(r['packet_id'],[]).append(r)
    out=[]
    for b in bundles:
        rows=by_packet.get(b['packet_id'],[])
        decision, missing, custody_gap, self_verifier, broken, reason=decide(b, rows)
        required=[r for r in rows if r.get('requirement_level')=='required']
        present=sum(1 for r in required if str(r.get('present','')).lower()=='true' and r.get('synthetic_value'))
        expected=b.get('expected_decision')
        out.append({
            'packet_id':b['packet_id'], 'template_id':b['template_id'], 'packet_type':b['packet_type'], 'source_class':b['source_class'],
            'expected_decision':expected, 'actual_decision':decision, 'pass':str(decision==expected).lower(),
            'required_fields':str(len(required)), 'present_required_fields':str(present), 'missing_required_fields':str(len(missing)),
            'missing_field_names':';'.join(missing), 'claims_local_closure':b.get('claims_local_closure','false'),
            'counterevidence_signal':b.get('counterevidence_signal','false'), 'public_context_source':str(b.get('source_class')=='public_context').lower(),
            'has_custody_gap':str(custody_gap).lower(), 'bad_self_verifier':str(self_verifier).lower(), 'broken_public_link':str(broken).lower(),
            'public_closure_leak':'false', 'decision_reason':reason
        })
    with OUT.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader(); w.writerows(out)
    failed=[r for r in out if r['pass']!='true']
    print(f'validated {len(out)} packet bundles; failures={len(failed)}')
    if failed:
        for r in failed:
            print(r['packet_id'], r['expected_decision'], r['actual_decision'])
        return 1
    return 0
if __name__=='__main__':
    sys.exit(main())
