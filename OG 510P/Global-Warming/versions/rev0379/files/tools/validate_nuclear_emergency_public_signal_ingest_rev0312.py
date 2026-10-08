#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv
from pathlib import Path
ALLOWED_FAMILIES={'rop_pi','action_matrix','inspection_finding','event_notification','rep_exercise','crc_capacity','plan_change','source_guidance','public_info'}
ALLOWED_EFFECTS={'no_upgrade','partial_context','yellow_cap','red_cap','reopen_counterevidence','source_refresh','reject'}
ALLOWED_CLAIMS={'allow_limited','yellow_disclose','red_block','claim_freeze','reject_claim'}
ALLOWED_REALNESS={'official_public','private_anonymized','private_site','synthetic_fixture','derived_overlay'}
ALLOWED_SENS={'public','controlled_public_summary','sensitive_security','sensitive_privacy','sensitive_route','sensitive_medical'}
REQ=['signal_id','source_id','source_record_id','source_url','captured_at','data_as_of','site_id','service_floor_id','signal_family','signal_value','evidence_role','declared_readiness_effect','declared_public_claim_effect','realness_flag','sensitivity_class','human_reviewer','validator_version','status','declared_claim']

def read(path):
    with open(path,newline='',encoding='utf-8') as f:
        r=csv.DictReader(f); return r.fieldnames or [], list(r)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--source-csv',required=True); ap.add_argument('--output',required=True); ns=ap.parse_args()
    _, sources=read(ns.source_csv); sids={r['source_id'] for r in sources}
    _, rows=read(ns.input); out=[]; seen=set()
    for row in rows:
        errors=[]; warnings=[]; effects=[]
        for f in REQ:
            if not row.get(f,'').strip(): errors.append('missing_'+f)
        sid=row.get('source_id','')
        if sid not in sids: errors.append('unregistered_source_id')
        fam=row.get('signal_family',''); val=row.get('signal_value','').lower(); role=row.get('evidence_role','').lower(); eff=row.get('declared_readiness_effect',''); claim_eff=row.get('declared_public_claim_effect',''); claim=row.get('declared_claim','').lower(); real=row.get('realness_flag','')
        if fam not in ALLOWED_FAMILIES: errors.append('unknown_signal_family')
        if eff not in ALLOWED_EFFECTS: errors.append('unknown_readiness_effect')
        if claim_eff not in ALLOWED_CLAIMS: errors.append('unknown_public_claim_effect')
        if real not in ALLOWED_REALNESS: errors.append('unknown_realness_flag')
        if row.get('sensitivity_class','') not in ALLOWED_SENS: errors.append('unknown_sensitivity_class')
        if row.get('signal_id') in seen: errors.append('duplicate_signal_id')
        seen.add(row.get('signal_id'))
        url=row.get('source_url','').lower()
        if real=='official_public' and not any(url.startswith(prefix) for prefix in ['https://www.nrc.gov','https://www.fema.gov','https://www.cdc.gov','https://www.epa.gov','https://www.ecfr.gov']): errors.append('official_public_url_not_official_domain')
        if fam=='rop_pi' and 'ep03_current' in val: errors.append('ep03_retired_cannot_be_current')
        if fam=='rop_pi' and any(x in val for x in ['gtg','white','yellow','red']) and eff not in {'yellow_cap','red_cap','reopen_counterevidence'}: errors.append('greater_than_green_pi_requires_cap')
        if fam=='action_matrix' and 'regulatory_response' in val and eff not in {'yellow_cap','red_cap','reopen_counterevidence'}: errors.append('action_matrix_regulatory_response_requires_cap')
        if fam=='inspection_finding' and any(x in val for x in ['white','yellow','red']) and eff not in {'yellow_cap','red_cap','reopen_counterevidence'}: errors.append('greater_than_green_finding_requires_cap')
        if fam=='event_notification' and any(x in val for x in ['alert','site_area','general_emergency','notification_delay']):
            if eff not in {'yellow_cap','red_cap','reopen_counterevidence'}: errors.append('event_signal_requires_counterevidence_or_cap')
            if row.get('counterevidence_path','N/A') in {'','N/A','nan'}: errors.append('event_signal_missing_counterevidence_path')
        if fam=='rep_exercise' and any(x in val for x in ['deficiency','adverse']) and eff not in {'yellow_cap','red_cap','reopen_counterevidence'}: errors.append('exercise_deficiency_requires_cap_or_reopen')
        if fam in {'source_guidance','crc_capacity','public_info'} and role=='local_artifact': errors.append('generic_public_guidance_or_brochure_cannot_be_local_artifact')
        if fam=='public_info' and ('route_brochure' in val or 'brochure' in claim) and ('capacity' in claim or 'ready' in claim): errors.append('public_brochure_cannot_prove_capacity_or_readiness')
        if role=='local_artifact' and real in {'private_anonymized','private_site'} and row.get('artifact_hash','N/A') in {'','N/A','nan'}: errors.append('private_local_artifact_missing_hash')
        if 'green_ready' in claim_eff or 'certified' in claim or 'green ready' in claim: errors.append('public_signal_misused_for_green_claim')
        if errors: verdict='reject'
        elif eff in {'yellow_cap','red_cap','reopen_counterevidence'} or warnings: verdict='accept_with_hold_or_cap'
        else: verdict='accept_partial_no_upgrade'
        if eff in {'red_cap','reopen_counterevidence'} or claim_eff in {'red_block','claim_freeze'}: effects.append('public_green_blocked')
        elif eff=='yellow_cap' or claim_eff=='yellow_disclose': effects.append('yellow_disclosure_required')
        elif eff=='source_refresh': effects.append('source_refresh_only')
        else: effects.append('no_readiness_upgrade')
        out.append({'signal_id':row.get('signal_id',''),'source_id':sid,'signal_family':fam,'signal_value':row.get('signal_value',''),'validator_verdict':verdict,'error_codes':';'.join(errors),'warning_codes':';'.join(warnings),'computed_effects':';'.join(sorted(set(effects))),'declared_readiness_effect':eff,'declared_public_claim_effect':claim_eff,'created_revision':'rev0312','status':'validated_public_signal_fixture'})
    fields=['signal_id','source_id','signal_family','signal_value','validator_verdict','error_codes','warning_codes','computed_effects','declared_readiness_effect','declared_public_claim_effect','created_revision','status']
    with open(ns.output,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    print(f'validated rows={len(out)} rejects={sum(1 for r in out if r["validator_verdict"]=="reject")}')
if __name__=='__main__': main()
