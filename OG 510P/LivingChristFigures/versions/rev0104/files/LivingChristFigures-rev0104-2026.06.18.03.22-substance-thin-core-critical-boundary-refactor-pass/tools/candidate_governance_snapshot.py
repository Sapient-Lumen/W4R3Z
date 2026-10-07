#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from collections import defaultdict, Counter

SNAPSHOT_FIELDS = ['candidate_id','candidate_name','public_export_tier','public_shape_template','required_review','governance_rows','governance_quarantine','claim_count','claims_needing_human_review','highest_refresh_priority','capacity_state','source_count','blocked_public_url_sources','manual_review_url_sources','boundary_note_url_sources','near_harm_profile','public_url_release','public_claim_release','release_posture','next_governance_action']
QUEUE_FIELDS = ['queue_id','candidate_id','candidate_name','priority','queue_type','trigger','next_action','blocking_files']
NEAR_HARM = {'case_detail_near','contact_path_near','testimony_near','image_or_vigil_near','operational_route_near','family_profile_near'}


def read_csv(path: Path) -> list[dict]:
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows([{k:r.get(k,'') for k in fields} for r in rows])


def pipe(s: str) -> list[str]: return [x for x in (s or '').split('|') if x]


def run(root: Path) -> tuple[list[dict], list[dict]]:
    candidates=read_csv(root/'Candidate-Ledger-current.csv')
    eligibility={r.get('candidate_id',''):r for r in read_csv(root/'META/Public-Export-Eligibility-current.csv')}
    consent=defaultdict(list)
    for r in read_csv(root/'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv'):
        consent[r.get('candidate_id','')].append(r)
    claims=defaultdict(list)
    for r in read_csv(root/'Claim-Ledger-current.csv'):
        claims[r.get('candidate_id','')].append(r)
    lifecycle=defaultdict(list)
    for r in read_csv(root/'META/Claim-Evidence-Strength-current.csv'):
        lifecycle[r.get('candidate_id','')].append(r)
    refresh={r.get('candidate_id',''):r for r in read_csv(root/'META/Refresh-Priority-Queue-current.csv')}
    sources_by_cand=defaultdict(list)
    for s in read_csv(root/'Source-Registry-current.csv'):
        for cid in pipe(s.get('candidate_ids','')):
            sources_by_cand[cid].append(s)
    link_by_source={r.get('source_id',''):r for r in read_csv(root/'META/Public-Source-Link-Review-current.csv')}
    snapshot=[]; queue=[]
    for cand in candidates:
        cid=cand.get('candidate_id','')
        elig=eligibility.get(cid,{})
        srcs=sources_by_cand.get(cid,[])
        link_decisions=[link_by_source.get(s.get('source_id',''),{}) for s in srcs]
        blocked=sum(1 for r in link_decisions if r.get('public_url_release_decision')=='block_public_url')
        manual=sum(1 for r in link_decisions if r.get('public_url_release_decision')=='manual_review_required_block_until_review')
        boundary=sum(1 for r in link_decisions if r.get('public_url_release_decision')=='allow_only_with_boundary_note_after_manual_review')
        harms=sorted({h for s in srcs for h in pipe(s.get('harm_proximity',''))})
        human_review=sum(1 for r in lifecycle.get(cid,[]) if r.get('needs_human_review')=='true')
        gov_rows=consent.get(cid,[])
        gov_quarantine = bool(gov_rows) or elig.get('public_export_tier')=='quarantined_no_public_expansion'
        if gov_quarantine:
            release_posture='governance_quarantined_boundary_only'
            next_action='family/community or authorized governance review before public prose, public URL, image, case-name, testimony, or story expansion'
        elif human_review:
            release_posture='human_review_boundary_only'
            next_action='review lifecycle/currentness and public-claim quarantine before public prose expansion'
        elif blocked or manual:
            release_posture='source_link_blocked_or_manual_review_only'
            next_action='perform source-link review and keep URLs internal unless explicitly allowed'
        elif any(h in NEAR_HARM for h in harms):
            release_posture='near_harm_manual_review_before_expansion'
            next_action='manual near-harm review before any prose beyond safe renderer'
        else:
            release_posture='index_shape_only_lint_required'
            next_action='public lint and manual context review required before handoff'
        row={
            'candidate_id':cid,
            'candidate_name':cand.get('name',''),
            'public_export_tier':elig.get('public_export_tier','missing_eligibility'),
            'public_shape_template':elig.get('public_shape_template','missing_template'),
            'required_review':elig.get('required_review','missing_review'),
            'governance_rows':str(len(gov_rows)),
            'governance_quarantine':'true' if gov_quarantine else 'false',
            'claim_count':str(len(claims.get(cid,[]))),
            'claims_needing_human_review':str(human_review),
            'highest_refresh_priority':refresh.get(cid,{}).get('highest_refresh_priority','missing_refresh_queue'),
            'capacity_state':cand.get('capacity_state',''),
            'source_count':str(len(srcs)),
            'blocked_public_url_sources':str(blocked),
            'manual_review_url_sources':str(manual),
            'boundary_note_url_sources':str(boundary),
            'near_harm_profile':'|'.join(harms) if harms else 'not_recorded',
            'public_url_release':elig.get('public_url_release','missing_url_release'),
            'public_claim_release':elig.get('public_claim_release','missing_claim_release'),
            'release_posture':release_posture,
            'next_governance_action':next_action,
        }
        snapshot.append(row)
        if release_posture!='index_shape_only_lint_required':
            if gov_quarantine: priority='0'
            elif human_review: priority='1'
            elif blocked or manual: priority='2'
            else: priority='3'
            queue.append({
                'queue_id':f'gq_{len(queue)+1:04d}',
                'candidate_id':cid,
                'candidate_name':cand.get('name',''),
                'priority':priority,
                'queue_type':release_posture,
                'trigger':f"eligibility={row['public_export_tier']}; human_review_claims={human_review}; blocked_urls={blocked}; manual_urls={manual}; near_harm={row['near_harm_profile']}",
                'next_action':next_action,
                'blocking_files':'META/Public-Export-Eligibility-current.csv|META/Public-Source-Link-Review-current.csv|META/Claim-Evidence-Strength-current.csv|GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv',
            })
    queue.sort(key=lambda r:(int(r['priority']), r['candidate_name']))
    snapshot.sort(key=lambda r:(r['release_posture'], r['candidate_name']))
    return snapshot, queue


def write_md_table(path: Path, title: str, intro: str, rows: list[dict], fields: list[str], limit:int=120) -> None:
    lines=[f'# {title}','',intro,'',f'Rows: {len(rows)}','']
    if rows:
        lines.append('| '+' | '.join(fields)+' |'); lines.append('| '+' | '.join(['---']*len(fields))+' |')
        for r in rows[:limit]:
            lines.append('| '+' | '.join(str(r.get(f,'')).replace('|','/').replace('\n',' ')[:220] for f in fields)+' |')
        if len(rows)>limit: lines.append(f'\n_Table truncated at {limit} rows; CSV/JSON contain all rows._')
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')


def write_reports(root: Path, snapshot: list[dict], queue: list[dict]) -> None:
    out=root/'META'; out.mkdir(exist_ok=True)
    write_csv(out/'Candidate-Governance-Snapshot-current.csv', snapshot, SNAPSHOT_FIELDS)
    (out/'Candidate-Governance-Snapshot-current.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write_md_table(out/'Candidate-Governance-Snapshot-current.md','Candidate Governance Snapshot — current','Generated by `tools/candidate_governance_snapshot.py`. Joins eligibility, source-link review, lifecycle, consent/governance, and refresh posture into one candidate-level handoff view. Snapshot rows are release gates, not release permission.',snapshot,['candidate_id','public_export_tier','public_shape_template','release_posture','claims_needing_human_review','blocked_public_url_sources','manual_review_url_sources','near_harm_profile','next_governance_action'])
    write_csv(out/'Governance-Review-Queue-current.csv', queue, QUEUE_FIELDS)
    (out/'Governance-Review-Queue-current.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write_md_table(out/'Governance-Review-Queue-current.md','Governance Review Queue — current','Generated from the candidate governance snapshot. It lists candidates that require governance, lifecycle, source-link, or near-harm review before public prose/URL expansion.',queue,['priority','queue_type','candidate_id','trigger','next_action'])


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--json', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); snapshot, queue=run(root)
    if args.write_report: write_reports(root, snapshot, queue)
    if args.json: print(json.dumps({'snapshot':snapshot,'queue':queue}, ensure_ascii=False, indent=2))
    else:
        print(f'candidate_governance_snapshot_rows={len(snapshot)} governance_review_queue_rows={len(queue)}')
if __name__=='__main__': main()
