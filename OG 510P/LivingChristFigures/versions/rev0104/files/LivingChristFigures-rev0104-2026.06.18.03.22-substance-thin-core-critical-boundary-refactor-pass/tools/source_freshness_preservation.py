#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['source_id','source_date','date_first_seen','date_last_checked','last_http_status','archived_copy_status','archive_url_or_archive_id','language','jurisdiction','link_rot_risk','source_owner_type','retrieval_method','safe_to_recheck_automatically','status','note']
NEAR_HARM_TOKENS=('contact_path_near','case_detail_near','testimony_near','family_profile_near','image_or_vigil_near','operational_route_near','shelter_location_near','support_path_near')

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def is_unknown(value: str) -> bool:
    return not (value or '').strip() or (value or '').strip().lower() in {'unknown','not_recorded','not_checked_by_rev0065','not_checked_by_rev0070','not_checked_by_rev0071','not_checked_by_rev0072','not_checked_by_rev0073'}

def status_for(row: dict) -> tuple[str,str]:
    missing=[]
    for field in ['source_date','language','jurisdiction']:
        if is_unknown(row.get(field,'')): missing.append(field)
    unchecked=(row.get('last_http_status','') or '').startswith('not_checked_by_') or not row.get('last_http_status')
    near_harm=any(tok in (row.get('harm_proximity') or '') for tok in NEAR_HARM_TOKENS)
    public_policy=row.get('public_link_policy','')
    if near_harm and row.get('safe_to_recheck_automatically') not in {'do_not_auto_recheck','manual_review_required'}:
        return 'review_manual_recheck_policy', 'Near-harm source must not be automatically refreshed; confirm safe_to_recheck_automatically is manual or blocked.'
    if missing and unchecked and public_policy in {'public_link_allowed','public_link_allowed_with_boundary_note','boundary_note_required'}:
        return 'metadata_refresh_needed', 'Public-context source has unchecked live status plus missing source_date/language/jurisdiction: ' + '|'.join(missing)
    if missing:
        return 'metadata_backfill_needed', 'Missing source metadata: ' + '|'.join(missing)
    status=(row.get('last_http_status','') or '')
    if unchecked:
        return 'freshness_check_needed', 'Last check is still an inherited not_checked marker; do safe manual verification before public use.'
    if status.startswith('manual_metadata_review_no_direct_http_open_'):
        return 'manual_identity_review_recorded_no_live_http_status', 'Sensitive source identity and metadata were reviewed without direct HTTP crawl/open; this is intentional no-crawl posture, not public link-health clearance.'
    return 'tracked', 'Freshness fields are populated enough for current handoff; preservation status is tracked separately.'

def run(root: Path):
    rows=[]
    for r in read_csv(root/'Source-Registry-current.csv'):
        status,note=status_for(r)
        rows.append({field:r.get(field,'') for field in FIELDS})
        rows[-1]['status']=status
        rows[-1]['note']=note
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-policy-error', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Source-Freshness-Preservation-current.csv',FIELDS,rows,'Source Freshness Preservation','tools/source_freshness_preservation.py',columns=['source_id','source_date','date_last_checked','last_http_status','language','jurisdiction','safe_to_recheck_automatically','status','note'],intro_lines=['Freshness view only: this report no longer duplicates archive-preservation action rows.','It intentionally does not crawl sources or contact anybody.'])
    bad=[r for r in rows if r.get('status')=='review_manual_recheck_policy']
    print(f"{'FAIL' if bad else 'PASS'} source freshness rows={len(rows)} manual_policy_errors={len(bad)}")
    if args.fail_on_policy_error and bad: sys.exit(1)
if __name__=='__main__': main()
