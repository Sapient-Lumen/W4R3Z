#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['finding_id','source_id','domain','candidate_ids','hazard_family','trigger_terms','harm_proximity','public_link_policy','safe_to_recheck_automatically','public_url_release_decision','severity','status','recommended_action','note']
NEAR_HARM_TOKENS=('contact_path_near','case_detail_near','testimony_near','family_profile_near','image_or_vigil_near','operational_route_near','shelter_location_near','support_path_near')
# High-confidence lexical traps only. Broad terms such as "family" or "support" alone are intentionally excluded.
PATTERNS={
    'recovery_service_location': re.compile(r'(recovery[-_ /]*(drop[-_ /]*in|center|centre)|drop[-_ /]*in[-_ /]*recovery|walk[-_ /]*in[-_ /]*recovery|harm[-_ /]*reduction|narcan|naloxone|recovery[-_ /]*support[-_ /]*services?)', re.I),
    'peer_support_group_or_crisis_path': re.compile(r'(hearing[-_ /]*voices[-_ /]*groups|peer[-_ /]*support[-_ /]*groups|in[-_ /]*crisis|support[-_ /]*circle|virtual[-_ /]*support[-_ /]*meetings?)', re.I),
    'explicit_service_contact_or_helpline': re.compile(r'(contactanos|contact[-_ /]*us|our[-_ /]*services|service[-_ /]*provider[-_ /]*enquiries|parents[-_ /]*carer[-_ /]*enquiries|helplines?|hotlines?|quick[-_ /]*exit|intake[-_ /]*path|enquir(y|ies)|contact[-_ /]*path|support[-_ /]*and[-_ /]*referral)', re.I),
    'missing_persons_or_forensic_directory': re.compile(r'(missingpersons\.icrc\.org/directory|network[-_ /]*members/.+eaaf|member[-_ /]*directory|madres[-_ /]*buscadoras|forensic[-_ /]*directory)', re.I),
    'route_or_location_operational': re.compile(r'(bus[-_ /]*route|shelter[-_ /]*location|service[-_ /]*location|safe[-_ /]*house|route[-_ /]*monitoring|missing[-_ /]*relative[-_ /]*contact|whatsapp[-_ /]*group|migrant[-_ /]*route|el[-_ /]*hierro|sea[-_ /]*arrivals|communal[-_ /]*kitchens?)', re.I),
    'housing_or_humanitarian_service_request': re.compile(r'(request[-_ /]*support|request[-_ /]*naloxone|request[-_ /]*housing|richiedi[-_ /]*un[-_ /]*alloggio|housing[-_ /]*request|protected[-_ /]*housing|humanitarian[-_ /]*corridors?|selection[-_ /]*of[-_ /]*beneficiaries|on[-_ /]*site[-_ /]*assessment|reception[-_ /]*schemes?|field[-_ /]*operations?|local[-_ /]*logistics)', re.I),
    'child_or_residential_care_location': re.compile(r'(sun[-_ /]*village|children[-_ /]*of[-_ /]*incarcerated|parents[-_ /]*incarcerated|nursing[-_ /]*(centre|center)|old[-_ /]*folks[-_ /]*home|residential[-_ /]*care)', re.I),
    'memorial_or_case_submission_surface': re.compile(r'(dying[-_ /]*homeless[-_ /]*project|let[-_ /]*us[-_ /]*know[-_ /]*about[-_ /]*a[-_ /]*death|digital[-_ /]*memorial|ante[-_ /]*mortem|migrant[-_ /]*bodies)', re.I),
    'gang_exit_or_reentry_support': re.compile(r'(homeboy[-_ /]*industries|greg[-_ /]*boyle|rehab[-_ /]*happens[-_ /]*at[-_ /]*church|decreasing[-_ /]*recidivism|justice[-_ /]*involvement)', re.I),
}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))


def public_decisions(root: Path) -> dict[str,str]:
    return {r.get('source_id',''):r.get('public_url_release_decision','') for r in read_csv(root/'META/Public-Source-Link-Review-current.csv')}


def trigger_for(row: dict) -> tuple[str,str]:
    text=' '.join(str(row.get(k,'')) for k in ['url','domain','publisher_guess','source_type','candidate_ids','seen_in_files','data_governance_notes']).replace('|',' ')
    hits=[]
    for fam,rx in PATTERNS.items():
        m=rx.search(text)
        if m:
            hits.append((fam,m.group(0)))
    if not hits: return '', ''
    return '+'.join(dict.fromkeys(f for f,_ in hits)), '|'.join(dict.fromkeys(t for _,t in hits))


def run(root: Path):
    decisions=public_decisions(root)
    rows=[]
    for src in read_csv(root/'Source-Registry-current.csv'):
        fam,terms=trigger_for(src)
        if not fam: continue
        harm=src.get('harm_proximity','') or ''
        policy=src.get('public_link_policy','') or ''
        safe=src.get('safe_to_recheck_automatically','') or ''
        decision=decisions.get(src.get('source_id',''), 'missing_link_review')
        near=any(tok in harm for tok in NEAR_HARM_TOKENS)
        internal=policy.startswith('internal_only') and decision=='block_public_url' and safe in {'do_not_auto_recheck','manual_review_required'}
        if internal and near:
            sev='info'; status='pass'; action='already internal-only/manual; keep out of public URLs and do not extract contact, route, support, capacity, case, or location details'
            note='high-confidence safety trigger is contained by near-harm classification and blocked public URL posture'
        else:
            sev='high'; status='fail'; action='reclassify source to support/contact/route/location near-harm posture or document a source-specific exception before release'
            note='high-confidence source-safety trigger still looks like ordinary public-context/public-link metadata'
        rows.append({'finding_id':f'ssnm_{len(rows)+1:04d}','source_id':src.get('source_id',''),'domain':src.get('domain',''),'candidate_ids':src.get('candidate_ids',''),'hazard_family':fam,'trigger_terms':terms,'harm_proximity':harm,'public_link_policy':policy,'safe_to_recheck_automatically':safe,'public_url_release_decision':decision,'severity':sev,'status':status,'recommended_action':action,'note':note})
    if not rows:
        rows.append({'finding_id':'ssnm_0001','source_id':'','domain':'','candidate_ids':'','hazard_family':'summary','trigger_terms':'','harm_proximity':'','public_link_policy':'','safe_to_recheck_automatically':'','public_url_release_decision':'','severity':'info','status':'pass','recommended_action':'no high-confidence source-safety near misses detected','note':'no source rows matched the near-miss trigger set'})
    return rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Source-Safety-Nearmiss-Audit-current.csv',FIELDS,rows,'Source Safety Nearmiss Audit','tools/source_safety_nearmiss_audit.py',columns=['finding_id','source_id','domain','hazard_family','harm_proximity','public_link_policy','public_url_release_decision','severity','status','recommended_action'],intro_lines=['High-confidence trap audit for source rows that look like ordinary public context but expose support, contact, route, housing, shelter, humanitarian-selection, service-location, forensic-directory, child/residential-care, memorial/case-submission, gang-exit, helpline, or recovery access paths.','This report is deliberately narrow: broad words such as family or support alone do not trigger a high finding.'],max_md_rows=160)
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} source safety nearmiss rows={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['source_id']}: {r['hazard_family']} terms={r['trigger_terms']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
