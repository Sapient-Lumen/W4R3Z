#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report, read_csv_rows

REGISTRY_FIELDS=['domain_id','domain_label','trigger_signals','public_boundary','forbidden_public_expansion','review_authority','severity_floor','status','note']
MAP_FIELDS=['candidate_id','candidate_name','file_path','domain_id','domain_label','evidence_basis','source_signals','claim_signals','public_export_tier','public_shape_template','permission_state','boundary_lift_authority','review_priority','status','note']
AUDIT_FIELDS=['audit_id','check','candidate_id','domain_id','severity','status','detail','recommendation']

DOMAINS=[
 ('boundary_contact_capacity_referral','Contact, capacity, and referral boundary','helpline_or_crisis_contact|capacity_state=current_capacity|hotline/phone/call language','No live contact, intake, hours, availability, bed, hotline, support-path, or referral wording in public outputs.','live intake/contact digits/current availability/referral instructions','operator cannot lift; requires service-owner review plus governance review','high','pass','Prevents public layer from becoming a service directory.'),
 ('boundary_route_map_operational_safety','Route, map, and operational-safety boundary','operational_safety|migrant_border_or_statelessness|route/site/eviction/distress-call language','No coordinates, routes, site timing, boat traces, encampment maps, search paths, or operational instructions.','routes/maps/sites/timing/distress-call reconstruction','operator cannot lift; requires safety review and, where applicable, community/family authority','high','pass','Prevents accountability evidence from becoming a field guide.'),
 ('boundary_survivor_shelter_refuge','Survivor, shelter, and refuge boundary','survivor_service|shelter_refuge_or_safe_accommodation|GBV/safe-house/case-management language','No shelter location, referral pathway, support contact, case intake, capacity, or survivor-story expansion.','shelter/refuge intake details, case paths, survivor identifying facts','survivor-side/family/community authority plus governance review','high','pass','Keeps survivor service shape separate from operational access.'),
 ('boundary_child_youth_identity_image','Child/youth identity and image boundary','child_or_youth_vulnerability|child_privacy|child_identity_privacy|fetal_remains_privacy','No child images, names, case details, family traces, school/community identifiers, or grief imagery used as emotional currency.','child-identifying details/images/family traces','family/community authority plus governance review; often not liftable','high','pass','Protects children and youth from memorial, service, and media extraction.'),
 ('boundary_death_memorial_case_record','Death, memorial, and case-record boundary','death_or_memorial|public_database_privacy|cause_of_death_privacy|public_mortality_data_boundary','No case-number, grave-number, tribute-wall, name-roll, family lead, record-extraction, or event-map expansion.','case lists, family contacts, grave/record identifiers, tribute/event maps','family/community authority plus governance review; some boundaries not liftable','high','pass','Memory is not consent and memorial data is not an extraction license.'),
 ('boundary_state_legal_criminalization','State, legal-system, and criminalization boundary','state_or_legal_system|law_enforcement_proximity|incarcerated_labor_history|legal status','No safety scorecard, police-file extraction, legal-status exposure, litigation detail overclaim, or implementation-as-safety claim.','police/legal file details, status exposure, scorecards-as-safety','governance review; affected community/family authority where present','medium','pass','Prevents state proximity from becoming an endorsement or safety claim.'),
 ('boundary_indigenous_family_authority','Indigenous/family-led authority boundary','MMIWG|Indigenous|family-led|community authority|CARE/OCAP/UNDRIP','No case list, vigil map, red-dress/image extraction, family contact, testimony fragment, or boundary lift by operator alone.','case/name/image/testimony/event/support details','family/community/Indigenous authority required; operator alone may not lift','high','pass','Encodes family/community authority as a hard governance boundary.'),
 ('boundary_health_clinical_privacy','Health, behavioral-health, and clinical privacy boundary','medical_privacy|addiction_or_behavioral_health|clinical_ai_or_data_governance|public_health_overclaim','No diagnosis, treatment, overdose, behavioral-health, data-governance, or public-health detail that identifies or overclaims.','medical/clinical/behavioral-health identifiers; public-health overclaim','governance review and domain expert review before public expansion','medium','pass','Separates care/service interpretation from clinical or public-health claims.'),
 ('boundary_ritual_precondition_coercion','Ritual, religion, and precondition/coercion boundary','religious_or_precondition_risk|religious_ritual_or_precondition_risk|coerced reconciliation','No framing mercy as conversion, obedience, family return, coerced reconciliation, or ritual precondition.','coercive religious/precondition wording; forced-family-return claims','governance review; affected-recipient autonomy is non-negotiable','medium','pass','Keeps doorway language from becoming coercion.'),
 ('boundary_housing_encampment_location','Housing, homelessness, and encampment-location boundary','poverty_stigma|encampment_location_safety|encampment_surveillance|homelessness/housing language','No encampment location, outreach route, mortality name extraction, housing availability, or surveillance-to-service translation.','encampment maps/routes/names/current beds/surveillance links','governance review and lived-experience/community review where possible','high','pass','Prevents outreach and memorial work from exposing people or places.'),
 ('boundary_event_image_media_extraction','Event, image, and media-extraction boundary','image_risk|public_ceremony_image_risk|event_map_or_contact_surface|media_extraction_risk|donor_or_visitor_theatre_risk','No photos, ceremonies, events, donor/visitor theatre, vigil logistics, or media fragments as public proof.','images/event logistics/media fragments/visitor theatre','governance review plus family/community/survivor authority as applicable','medium','pass','Blocks the cube from turning people into proof-of-mercy scenery.'),
 ('boundary_power_funding_heroization','Power, funding, and heroization boundary','power_or_funding_frame|donor/brand/institutional dependency|office accountability risk','No heroic endorsement, donor branding, institutional self-myth, or current-capacity implication from recognition alone.','endorsement, ranking, donor brand, savior narrative','governance review; counterevidence and refusal/exit path should be visible','medium','pass','Keeps the severe metaphor from becoming a hero list.'),
]

SENS_MAP={
 'helpline_or_crisis_contact':['boundary_contact_capacity_referral'],
 'operational_safety':['boundary_route_map_operational_safety'],
 'migrant_border_or_statelessness':['boundary_route_map_operational_safety'],
 'survivor_service':['boundary_survivor_shelter_refuge'],
 'shelter_refuge_or_safe_accommodation':['boundary_survivor_shelter_refuge'],
 'child_or_youth_vulnerability':['boundary_child_youth_identity_image'],
 'child_privacy':['boundary_child_youth_identity_image'],
 'child_identity_privacy':['boundary_child_youth_identity_image'],
 'fetal_remains_privacy':['boundary_child_youth_identity_image'],
 'death_or_memorial':['boundary_death_memorial_case_record'],
 'public_database_privacy':['boundary_death_memorial_case_record'],
 'cause_of_death_privacy':['boundary_death_memorial_case_record'],
 'public_mortality_data_boundary':['boundary_death_memorial_case_record'],
 'state_or_legal_system':['boundary_state_legal_criminalization'],
 'law_enforcement_proximity':['boundary_state_legal_criminalization'],
 'incarcerated_labor_history':['boundary_state_legal_criminalization'],
 'medical_privacy':['boundary_health_clinical_privacy'],
 'addiction_or_behavioral_health':['boundary_health_clinical_privacy'],
 'clinical_ai_or_data_governance':['boundary_health_clinical_privacy'],
 'public_health_overclaim':['boundary_health_clinical_privacy'],
 'religious_or_precondition_risk':['boundary_ritual_precondition_coercion'],
 'religious_ritual_or_precondition_risk':['boundary_ritual_precondition_coercion'],
 'poverty_stigma':['boundary_housing_encampment_location'],
 'encampment_location_safety':['boundary_housing_encampment_location'],
 'encampment_surveillance':['boundary_housing_encampment_location'],
 'image_risk':['boundary_event_image_media_extraction'],
 'public_ceremony_image_risk':['boundary_event_image_media_extraction'],
 'event_map_or_contact_surface':['boundary_event_image_media_extraction'],
 'media_extraction_risk':['boundary_event_image_media_extraction'],
 'donor_or_visitor_theatre_risk':['boundary_event_image_media_extraction'],
 'power_or_funding_frame':['boundary_power_funding_heroization'],
}
DOMAIN_BY_ID={d[0]:d for d in DOMAINS}

# rev0075: quarantine is a release posture, not a single family/death/child
# ontology. Route/contact/shelter/housing domains can also require a hard
# no-public-expansion posture, especially for migration, refuge, and location
# safety surfaces.
HARD_QUARANTINE_DOMAINS={
 'boundary_indigenous_family_authority',
 'boundary_death_memorial_case_record',
 'boundary_child_youth_identity_image',
 'boundary_route_map_operational_safety',
 'boundary_contact_capacity_referral',
 'boundary_survivor_shelter_refuge',
 'boundary_housing_encampment_location',
}

KEYWORD_MAP=[
 (r'\b(hotline|helpline|lifeline|phone|call|sms|whatsapp|intake|referral|counsell?ing line)\b','boundary_contact_capacity_referral','contact/capacity keyword'),
 (r'\b(route|routes|coordinates|distress|boat|border|crossing|eviction|camp|encampment|site|map)\b','boundary_route_map_operational_safety','route/site/operational keyword'),
 (r'\b(shelter|safe house|refuge|survivor|gbv|domestic violence|case management|safe accommodation)\b','boundary_survivor_shelter_refuge','survivor/shelter keyword'),
 (r'\b(child|children|youth|adolescent|minor|fetal|infant|school)\b','boundary_child_youth_identity_image','child/youth keyword'),
 (r'\b(death|dead|burial|grave|cemetery|memorial|tribute|missing|unidentified|exhumation|morgue)\b','boundary_death_memorial_case_record','death/memorial keyword'),
 (r'\b(police|court|legal|state|law|prison|incarcerated|status|asylum|protection order)\b','boundary_state_legal_criminalization','state/legal keyword'),
 (r'\b(indigenous|mmiwg|family-led|families of sisters|red dress|ocap|undrip|care)\b','boundary_indigenous_family_authority','Indigenous/family authority keyword'),
 (r'\b(addiction|overdose|clinical|medical|health|diagnosis|therapy|ai|data governance)\b','boundary_health_clinical_privacy','health/clinical keyword'),
 (r'\b(religious|ritual|reconciliation|conversion|precondition|family reunification)\b','boundary_ritual_precondition_coercion','ritual/precondition keyword'),
 (r'\b(homeless|housing|encampment|street medicine|outreach|mortality data)\b','boundary_housing_encampment_location','housing/encampment keyword'),
 (r'\b(image|photo|photograph|media|ceremony|vigil|event|donor|visitor|theatre|red dress)\b','boundary_event_image_media_extraction','event/image/media keyword'),
 (r'\b(funding|donor|brand|recognition|award|institution|power|capacity|benchmark|canon)\b','boundary_power_funding_heroization','power/funding/heroization keyword'),
]

def split(s): return [x for x in (s or '').split('|') if x]

def normalize_status(domain_ids):
    return 'pass' if domain_ids else 'fail'

def domain_label(domain_id): return DOMAIN_BY_ID.get(domain_id, ('',domain_id))[1]

def build_registry():
    return [dict(zip(REGISTRY_FIELDS, d)) for d in DOMAINS]

def run(root: Path):
    candidates=read_csv_rows(root/'Candidate-Ledger-current.csv')
    elig={r.get('candidate_id',''):r for r in read_csv_rows(root/'META/Public-Export-Eligibility-current.csv')}
    perm={r.get('candidate_id',''):r for r in read_csv_rows(root/'GOVERNANCE/Permission-State-Ledger-current.csv')}
    claims=read_csv_rows(root/'Claim-Ledger-current.csv')
    srcs=read_csv_rows(root/'Source-Registry-current.csv')
    claim_by_c=defaultdict(list); source_by_c=defaultdict(list)
    for r in claims: claim_by_c[r.get('candidate_id','')].append(r)
    for r in srcs:
        for cid in split(r.get('candidate_ids','')): source_by_c[cid].append(r)
    map_rows=[]; candidate_domains={}
    for c in candidates:
        cid=c.get('candidate_id',''); text=' '.join([c.get(k,'') for k in ['name','office','work','why','flags_current','evidence_text','status_current','capacity_state','sensitivity','file_path']]).lower()
        domains=defaultdict(list)
        for s in split(c.get('sensitivity','')):
            for d in SENS_MAP.get(s, []): domains[d].append(f'sensitivity:{s}')
        if 'current_capacity' in (c.get('capacity_state','') or '') or 'current capacity' in text:
            domains['boundary_contact_capacity_referral'].append('capacity_state/current-capacity language')
        for pat, did, reason in KEYWORD_MAP:
            if re.search(pat, text, re.I): domains[did].append(reason)
        # public eligibility templates are themselves boundary signals.
        e=elig.get(cid,{})
        tmpl=e.get('public_shape_template','')
        if 'route' in tmpl: domains['boundary_route_map_operational_safety'].append('public_shape_template:'+tmpl)
        if 'survivor' in tmpl: domains['boundary_survivor_shelter_refuge'].append('public_shape_template:'+tmpl)
        if 'death' in tmpl or 'memorial' in tmpl: domains['boundary_death_memorial_case_record'].append('public_shape_template:'+tmpl)
        if 'mmiwg' in tmpl: domains['boundary_indigenous_family_authority'].append('public_shape_template:'+tmpl)
        if 'street_medicine' in tmpl: domains['boundary_housing_encampment_location'].append('public_shape_template:'+tmpl)
        if not domains:
            domains['boundary_power_funding_heroization'].append('fallback: every office requires anti-heroization boundary review')
        # source and claim signals are summarized so the map remains evidence-linked without exposing URLs.
        ssignals=[]
        for s in source_by_c.get(cid,[]):
            hp=s.get('harm_proximity','') or s.get('public_link_policy','')
            if hp: ssignals.append(hp)
        csignals=[]
        for cl in claim_by_c.get(cid,[]):
            ctype=cl.get('claim_type','')
            if ctype: csignals.append(ctype)
        for did in sorted(domains):
            review='standard_manual_review'
            if DOMAIN_BY_ID[did][6]=='high' or e.get('public_export_tier')=='quarantined_no_public_expansion': review='boundary_review_before_any_public_expansion'
            p=perm.get(cid,{})
            map_rows.append({
                'candidate_id':cid,
                'candidate_name':c.get('name',''),
                'file_path':c.get('file_path',''),
                'domain_id':did,
                'domain_label':domain_label(did),
                'evidence_basis':'|'.join(sorted(set(domains[did]))),
                'source_signals':'|'.join(sorted(set(ssignals)))[:500],
                'claim_signals':'|'.join(sorted(set(csignals)))[:500],
                'public_export_tier':e.get('public_export_tier',''),
                'public_shape_template':tmpl,
                'permission_state':p.get('community_authority_status', p.get('permission_state','')),
                'boundary_lift_authority':p.get('boundary_lift_authority',''),
                'review_priority':review,
                'status':'pass',
                'note':'heuristic boundary-domain inheritance; audit surface, not public-release permission',
            })
        candidate_domains[cid]=set(domains)
    audit=[]
    def add(check,cid,did,sev,status,detail,rec):
        audit.append({'audit_id':f'boundary_domain_audit_{len(audit)+1:04d}','check':check,'candidate_id':cid,'domain_id':did,'severity':sev,'status':status,'detail':detail,'recommendation':rec})
    for c in candidates:
        cid=c.get('candidate_id',''); ds=candidate_domains.get(cid,set())
        add('candidate_has_boundary_domain',cid,'','info' if ds else 'high','pass' if ds else 'fail',f'{len(ds)} domain(s) inherited','add at least one domain before handoff')
        for s in split(c.get('sensitivity','')):
            expected=SENS_MAP.get(s,[])
            missing=[d for d in expected if d not in ds]
            if expected:
                add('sensitivity_signal_domain_coverage',cid,'|'.join(expected),'info' if not missing else 'high','pass' if not missing else 'fail',f'sensitivity {s} mapped; missing={"|".join(missing)}','update SENS_MAP or candidate sensitivity')
    # public posture cross-checks
    elig_rows=list(elig.values())
    for e in elig_rows:
        cid=e.get('candidate_id','')
        ds=candidate_domains.get(cid,set())
        if e.get('public_export_tier')=='quarantined_no_public_expansion' and not (ds & HARD_QUARANTINE_DOMAINS):
            add('quarantined_candidate_has_hard_boundary_domain',cid,'','high','fail','quarantined candidate lacks a hard quarantine boundary domain','review eligibility and domain map')
    all_domains={d[0] for d in DOMAINS}
    used=set().union(*candidate_domains.values()) if candidate_domains else set()
    for did in sorted(all_domains):
        add('domain_registry_used_by_candidate','',did,'info','pass' if did in used else 'low',f'domain used={did in used}','unused domains are allowed but should be reviewed')
    if not any(r['severity']=='high' and r['status']!='pass' for r in audit):
        add('boundary_domain_summary','', '', 'info','pass',f'{len(candidates)} candidates mapped to {len(map_rows)} candidate/domain rows across {len(used)} used domains','do not treat map as public release permission')
    return build_registry(), map_rows, audit

def write_reports(root: Path, registry, map_rows, audit_rows):
    write_csv_json_md_report(root,'META/Boundary-Domain-Registry-current.csv',REGISTRY_FIELDS,registry,'Boundary Domain Registry','tools/boundary_domain_map.py',columns=['domain_id','domain_label','severity_floor','review_authority','public_boundary'],intro_lines=[f'Domains: {len(registry)}','Boundary domains are internal governance codes, not public categories.'])
    write_csv_json_md_report(root,'META/Candidate-Boundary-Domain-Map-current.csv',MAP_FIELDS,map_rows,'Candidate Boundary Domain Map','tools/boundary_domain_map.py',columns=['candidate_id','domain_id','public_export_tier','review_priority','status','evidence_basis'],intro_lines=[f'Candidate/domain rows: {len(map_rows)}','This map makes boundary inheritance auditable across candidate sensitivities, public eligibility, permission state, and office-accountability signals.'])
    high=sum(1 for r in audit_rows if r.get('severity')=='high' and r.get('status')!='pass')
    write_csv_json_md_report(root,'META/Boundary-Domain-Coverage-Audit-current.csv',AUDIT_FIELDS,audit_rows,'Boundary Domain Coverage Audit','tools/boundary_domain_map.py',columns=['check','candidate_id','domain_id','severity','status','detail'],intro_lines=[f'Rows: {len(audit_rows)}',f'High failures: {high}','Zero high failures required by release gate.'])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); registry,map_rows,audit=run(root)
    if args.write_report: write_reports(root,registry,map_rows,audit)
    high=[r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} boundary domain map candidates={len({r['candidate_id'] for r in map_rows})} rows={len(map_rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['check']} {r['candidate_id']}: {r['detail']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
