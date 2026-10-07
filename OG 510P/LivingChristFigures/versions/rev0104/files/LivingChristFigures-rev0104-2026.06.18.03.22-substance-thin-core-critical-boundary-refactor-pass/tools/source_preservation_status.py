#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['source_id','domain','source_type','candidate_ids','harm_proximity','public_link_policy','archived_copy_status','archive_url_or_archive_id','link_rot_risk','archive_need','may_auto_archive','preservation_action','status','note']
NEAR_HARM_TOKENS=('contact_path_near','case_detail_near','testimony_near','family_profile_near','image_or_vigil_near','operational_route_near','shelter_location_near','support_path_near')
RECORDED_PRESERVATION_DECISIONS={'manual_preservation_decision_recorded_no_public_archive','not_recorded_manual_preservation_recommended','not_recorded_manual_review_only_family_profile','official_public_archive_page_not_local_archive','publisher_record_archived_2020'}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def classify(row: dict) -> tuple[str,str,str,str,str]:
    harm=row.get('harm_proximity','') or ''
    policy=row.get('public_link_policy','') or ''
    near_harm=any(tok in harm for tok in NEAR_HARM_TOKENS) or policy.startswith('internal_only') or policy=='boundary_note_required_or_internal_only'
    archive_status=(row.get('archived_copy_status') or '').strip()
    archive_url=(row.get('archive_url_or_archive_id') or '').strip()
    has_archive=bool(archive_url)
    decision_recorded=archive_status in RECORDED_PRESERVATION_DECISIONS or archive_status.startswith('manual_preservation_decision_recorded')
    if near_harm:
        may='no_manual_review_only'
        if decision_recorded and archive_status.startswith('manual_preservation_decision_recorded') and not has_archive:
            need='manual_preservation_decision_recorded_no_public_archive'
            action='do not auto-crawl, mirror, or publish archive URL; keep source context internal and revisit only through manual review'
            status='pass'
            note='Sensitive or near-harm source has an explicit no-public-archive preservation decision recorded.'
        elif has_archive:
            need='archive_recorded_sensitive_do_not_expand'
            action='do_not_publish_archive_link; verify archive does not expose contact/case/route/testimony beyond source boundary'
            status='pass'
            note='Sensitive or near-harm source: preservation must be manual and public URL remains controlled.'
        else:
            need='manual_preservation_decision_needed'
            action='manual reviewer may record existence of preservation; do not auto-crawl, mirror, or publish archive URL'
            status='pass'
            note='Near-harm source lacks archive record; this is a prioritized manual task, not a release blocker.'
    elif policy in {'public_link_allowed','public_link_allowed_with_boundary_note','boundary_note_required'}:
        may='yes_context_only_after_review'
        if archive_status == 'not_recorded' and not has_archive:
            need='archive_recommended_for_context_link'
            action='safe manual capture or institutional permalink check; no extraction beyond cited public context'
            status='pass'
            note='Far-context/public-context source is suitable for non-urgent preservation planning.'
        else:
            need='archive_recorded_or_not_needed'
            action='keep archive metadata current during normal source maintenance'
            status='pass'
            note='Preservation metadata exists or is not currently needed.'
    else:
        may='manual_review_required'
        need='policy_unclear_preservation_review'
        action='repair public_link_policy before any preservation automation'
        status='pass'
        note='Unknown or restrictive link policy; fail closed for automated preservation.'
    return need,may,action,status,note

def run(root: Path):
    rows=[]
    for r in read_csv(root/'Source-Registry-current.csv'):
        need,may,action,status,note=classify(r)
        rows.append({
            'source_id':r.get('source_id',''), 'domain':r.get('domain',''), 'source_type':r.get('source_type',''), 'candidate_ids':r.get('candidate_ids',''),
            'harm_proximity':r.get('harm_proximity',''), 'public_link_policy':r.get('public_link_policy',''), 'archived_copy_status':r.get('archived_copy_status',''),
            'archive_url_or_archive_id':r.get('archive_url_or_archive_id',''), 'link_rot_risk':r.get('link_rot_risk',''), 'archive_need':need,
            'may_auto_archive':may, 'preservation_action':action, 'status':status, 'note':note
        })
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Source-Preservation-Status-current.csv',FIELDS,rows,'Source Preservation Status','tools/source_preservation_status.py',columns=['source_id','domain','public_link_policy','link_rot_risk','archive_need','may_auto_archive','preservation_action','status'],intro_lines=['Archive/preservation view only: distinct from Source-Freshness-Preservation.','No automatic crawling is authorized by this report; near-harm sources are manual-review-only.'])
    bad=[r for r in rows if r.get('status')=='fail']
    print(f"{'FAIL' if bad else 'PASS'} source preservation rows={len(rows)} fail={len(bad)}")
    if args.fail_on_fail and bad: sys.exit(1)
if __name__=='__main__': main()
