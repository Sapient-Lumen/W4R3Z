#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['decision_id','source_id','domain','candidate_ids','harm_proximity','public_link_policy','safe_to_recheck_automatically','public_url_release_decision','source_metadata_status','archived_copy_status','archive_url_or_archive_id','manual_preservation_tier','severity','status','recommended_action','note']
NEAR_HARM_TOKENS=('contact_path_near','case_detail_near','testimony_near','family_profile_near','image_or_vigil_near','operational_route_near','shelter_location_near','support_path_near')
RECORDED_DECISIONS={'manual_preservation_decision_recorded_no_public_archive','not_recorded_manual_preservation_recommended','not_recorded_manual_review_only_family_profile','official_public_archive_page_not_local_archive','publisher_record_archived_2020'}


def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))


def unknown(v: str) -> bool:
    v=(v or '').strip()
    return (not v) or v in {'unknown','not_recorded'} or v.startswith('not_checked_by_')


def near_harm(row: dict) -> bool:
    harm=row.get('harm_proximity','') or ''
    policy=row.get('public_link_policy','') or ''
    return any(tok in harm for tok in NEAR_HARM_TOKENS) or policy.startswith('internal_only') or policy=='boundary_note_required_or_internal_only'


def metadata_status(row: dict) -> tuple[str, list[str]]:
    missing=[]
    for f in ['source_date','language','jurisdiction','last_http_status']:
        if unknown(row.get(f,'')):
            missing.append(f)
    if missing:
        return 'metadata_or_freshness_unresolved', missing
    return 'metadata_and_freshness_recorded', []


def run(root: Path):
    link_by={r.get('source_id',''):r for r in read_csv(root/'META/Public-Source-Link-Review-current.csv')}
    rows=[]
    for src in read_csv(root/'Source-Registry-current.csv'):
        if not near_harm(src):
            continue
        sid=src.get('source_id','')
        decision=link_by.get(sid,{}).get('public_url_release_decision','missing_link_review')
        meta,missing=metadata_status(src)
        arch=(src.get('archived_copy_status','') or '').strip()
        archive_url=(src.get('archive_url_or_archive_id','') or '').strip()
        safe=src.get('safe_to_recheck_automatically','') or ''
        policy=src.get('public_link_policy','') or ''
        internal=(policy.startswith('internal_only') or policy=='boundary_note_required_or_internal_only') and decision in {'block_public_url','manual_review_required_block_until_review'} and safe in {'do_not_auto_recheck','manual_review_required'}
        context_allowed=policy in {'public_link_allowed_with_boundary_note','boundary_note_required'} and decision in {'allow_only_with_boundary_note_after_manual_review','allow_after_context_review'} and safe=='manual_review_required'
        recorded=arch in RECORDED_DECISIONS or arch.startswith('manual_preservation_decision_recorded') or bool(archive_url)
        problems=[]
        tier=''
        if meta=='metadata_or_freshness_unresolved':
            tier='p1_manual_sensitive_metadata_or_freshness_unresolved'
            severity='info'; status='pass'
            action='complete source/date/language/jurisdiction/freshness review manually; do not crawl, mirror, or publish archive URL'
            note='manual-sensitive source remains urgent because metadata or freshness is unresolved: '+','.join(missing)
        elif not (internal or context_allowed):
            tier='p0_manual_sensitive_policy_repair'
            severity='high'; status='fail'
            action='block public URL or constrain to manual boundary-note context review before any preservation decision'
            note='metadata-ready sensitive source is not fully closed for public URL/recheck posture'
        elif arch=='not_recorded' and not archive_url:
            tier='p0_metadata_ready_untriaged_sensitive_source'
            severity='high'; status='fail'
            action='record a manual preservation decision or a reviewed archive status; do not leave metadata-ready sensitive rows as generic not_recorded'
            note='metadata/freshness are recorded but no preservation decision is recorded; this is the regression rev0082 closes'
        elif arch.startswith('manual_preservation_decision_recorded') and archive_url:
            tier='p0_no_public_archive_url_violation'
            severity='high'; status='fail'
            action='remove public archive URL or reclassify only after explicit permission/governance review'
            note='no-public-archive decision row must not carry archive_url_or_archive_id'
        elif recorded:
            tier='p2_sensitive_preservation_decision_recorded'
            severity='info'; status='pass'
            if context_allowed and not internal:
                action='keep manual boundary-note-only context posture; revisit only on source replacement, candidate promotion, takedown request, or scheduled manual preservation review'
                note='official/context boundary-note source is manually verified with no public archive URL; do not extract case, testimony, image, contact, event, route, or legal-advice details'
            else:
                action='keep internal-only; revisit only on source replacement, candidate promotion, takedown request, or scheduled manual preservation review'
                note='metadata/freshness are recorded and preservation decision is explicit; no auto-crawl or public archive URL is authorized'
        else:
            tier='p1_manual_sensitive_preservation_review_needed'
            severity='info'; status='pass'
            action='manual reviewer must decide whether preservation is needed and how to avoid public archive amplification'
            note='source is sensitive and does not yet have a specific preservation decision, but metadata/freshness state is not ready for automatic downgrade'
        rows.append({'decision_id':f'smpd_{len(rows)+1:04d}','source_id':sid,'domain':src.get('domain',''),'candidate_ids':src.get('candidate_ids',''),'harm_proximity':src.get('harm_proximity',''),'public_link_policy':policy,'safe_to_recheck_automatically':safe,'public_url_release_decision':decision,'source_metadata_status':meta,'archived_copy_status':arch,'archive_url_or_archive_id':archive_url,'manual_preservation_tier':tier,'severity':severity,'status':status,'recommended_action':action,'note':note})
    if not rows:
        rows.append({'decision_id':'smpd_0001','source_id':'','domain':'','candidate_ids':'','harm_proximity':'','public_link_policy':'','safe_to_recheck_automatically':'','public_url_release_decision':'','source_metadata_status':'summary','archived_copy_status':'','archive_url_or_archive_id':'','manual_preservation_tier':'no_near_harm_sources_detected','severity':'info','status':'pass','recommended_action':'no action','note':'no near-harm sources were present'})
    return rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Source-Manual-Preservation-Decision-current.csv',FIELDS,rows,'Source Manual Preservation Decision','tools/source_manual_preservation_decision.py',columns=['decision_id','source_id','domain','source_metadata_status','archived_copy_status','manual_preservation_tier','severity','status','recommended_action'],intro_lines=['Near-harm source preservation decision audit. This separates urgent manual-sensitive metadata/freshness debt from metadata-ready rows whose no-public-archive/no-auto-crawl decision has been explicitly recorded.','A recorded decision is not an archive and does not authorize public URL, mirror, crawl, contact/referral, route, service, case, image, testimony, housing, or shelter expansion.'],max_md_rows=180)
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} source manual preservation decisions rows={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['source_id']}: {r['manual_preservation_tier']} {r['note']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
