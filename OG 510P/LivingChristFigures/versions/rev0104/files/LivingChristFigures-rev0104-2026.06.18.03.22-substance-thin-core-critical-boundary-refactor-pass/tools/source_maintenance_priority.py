#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['priority_id','source_id','domain','candidate_ids','source_type','harm_proximity','public_link_policy','public_url_release_decision','source_date','date_last_checked','last_http_status','archived_copy_status','language','jurisdiction','safe_to_recheck_automatically','maintenance_priority','review_action','automation_posture','severity','status','rationale']
NEAR_HARM_TOKENS=('contact_path_near','case_detail_near','testimony_near','family_profile_near','image_or_vigil_near','operational_route_near','shelter_location_near','support_path_near')
UNSET={'','unknown','not_recorded'}
RECORDED_PRESERVATION_DECISIONS={'manual_preservation_decision_recorded_no_public_archive','not_recorded_manual_preservation_recommended','not_recorded_manual_review_only_family_profile','official_public_archive_page_not_local_archive','publisher_record_archived_2020'}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def unset(v: str) -> bool:
    v=(v or '').strip()
    return v in UNSET or v.startswith('not_checked_by_')

def classify(row: dict, link: dict) -> tuple[str,str,str,str,str,str]:
    harm=row.get('harm_proximity','') or ''
    policy=row.get('public_link_policy','') or ''
    near_harm=any(tok in harm for tok in NEAR_HARM_TOKENS) or policy.startswith('internal_only') or policy=='boundary_note_required_or_internal_only'
    missing=[f for f in ['source_date','language','jurisdiction'] if unset(row.get(f,''))]
    unchecked=unset(row.get('last_http_status',''))
    archive_status=(row.get('archived_copy_status','') or '').strip()
    archive_url=(row.get('archive_url_or_archive_id') or '').strip()
    no_archive=archive_status=='not_recorded' and not archive_url
    preservation_decision_recorded=archive_status in RECORDED_PRESERVATION_DECISIONS or archive_status.startswith('manual_preservation_decision_recorded') or bool(archive_url)
    public_decision=link.get('public_url_release_decision','')
    safe=(row.get('safe_to_recheck_automatically') or '')
    if near_harm and safe not in {'do_not_auto_recheck','manual_review_required'}:
        return 'p0_recheck_policy_repair','set safe_to_recheck_automatically to do_not_auto_recheck/manual_review_required or justify far-context status','no_auto_crawl','high','pass','near-harm source currently not explicitly manual/blocked for recheck'
    if near_harm and public_decision!='block_public_url' and policy.startswith('internal_only'):
        return 'p0_public_url_blockage_repair','align Public-Source-Link-Review with internal-only public_link_policy','no_auto_crawl','high','pass','internal-only source must have block_public_url in link review'
    if near_harm and (missing or unchecked or no_archive):
        return 'p1_manual_sensitive_preservation','manual source owner/date/language/jurisdiction/freshness and preservation review; do not crawl or publish archive URL','manual_only','medium','pass','sensitive source has maintenance debt: '+('|'.join(missing) if missing else 'freshness/archive debt')
    if near_harm and preservation_decision_recorded:
        return 'p2_sensitive_preservation_decision_recorded','manual-sensitive preservation decision is recorded; no auto-crawl or public archive URL; revisit only on source replacement/takedown/promotion review','manual_only_watch','info','pass','sensitive source remains internal-only but is no longer an urgent metadata-ready preservation-decision gap'
    if public_decision in {'allow_only_with_boundary_note_after_manual_review','allow_after_context_review'} and (missing or unchecked):
        return 'p1_public_context_metadata_repair','backfill source date/language/jurisdiction and manually verify link health before public citation','manual_context_check','medium','pass','public-context source has metadata or freshness debt: '+('|'.join(missing) if missing else 'unchecked')
    if no_archive and row.get('link_rot_risk') in {'medium_standard_link_rot','medium_unreviewed'}:
        return 'p2_archive_planning','schedule safe manual archive/permalink check for far-context source','manual_context_check','info','pass','standard link rot risk with no archive record'
    return 'p3_tracked','no immediate action beyond normal review cadence','no_action_or_normal_review','info','pass','source is sufficiently tracked for this release scope'

def run(root: Path):
    links={r.get('source_id',''):r for r in read_csv(root/'META/Public-Source-Link-Review-current.csv')}
    rows=[]
    for r in read_csv(root/'Source-Registry-current.csv'):
        pr,action,auto,sev,status,rat=classify(r, links.get(r.get('source_id',''), {}))
        rows.append({
            'priority_id':f'smp_{len(rows)+1:04d}', 'source_id':r.get('source_id',''), 'domain':r.get('domain',''), 'candidate_ids':r.get('candidate_ids',''),
            'source_type':r.get('source_type',''), 'harm_proximity':r.get('harm_proximity',''), 'public_link_policy':r.get('public_link_policy',''),
            'public_url_release_decision':links.get(r.get('source_id',''), {}).get('public_url_release_decision','missing_link_review'),
            'source_date':r.get('source_date',''), 'date_last_checked':r.get('date_last_checked',''), 'last_http_status':r.get('last_http_status',''),
            'archived_copy_status':r.get('archived_copy_status',''), 'language':r.get('language',''), 'jurisdiction':r.get('jurisdiction',''),
            'safe_to_recheck_automatically':r.get('safe_to_recheck_automatically',''), 'maintenance_priority':pr, 'review_action':action,
            'automation_posture':auto, 'severity':sev, 'status':status, 'rationale':rat
        })
    order={'p0_recheck_policy_repair':0,'p0_public_url_blockage_repair':1,'p1_manual_sensitive_preservation':2,'p1_public_context_metadata_repair':3,'p2_sensitive_preservation_decision_recorded':4,'p2_archive_planning':5,'p3_tracked':6}
    rows.sort(key=lambda r:(order.get(r['maintenance_priority'],9), r['domain'], r['source_id']))
    for i,r in enumerate(rows,1): r['priority_id']=f'smp_{i:04d}'
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Source-Maintenance-Priority-current.csv',FIELDS,rows,'Source Maintenance Priority','tools/source_maintenance_priority.py',columns=['priority_id','source_id','domain','maintenance_priority','review_action','automation_posture','severity','status','rationale'],intro_lines=['Action queue for source-health debt. It prioritizes concrete manual work over new doctrine.','P0/P1 rows are not public expansion permission; they identify what to fix or preserve safely.'],max_md_rows=180)
    bad=[r for r in rows if r.get('status')=='fail']
    print(f"{'FAIL' if bad else 'PASS'} source maintenance priorities rows={len(rows)} fail={len(bad)}")
    if args.fail_on_fail and bad: sys.exit(1)
if __name__=='__main__': main()
