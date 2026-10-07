#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

FIELDS=['finding_id','severity','check','scope','subject_id','detail','required_action']
NEAR_HARM={'contact_path_near','case_detail_near','image_or_vigil_near','operational_route_near','family_profile_near','testimony_near'}
INTERNAL_POLICIES={'internal_only_contact_rich','internal_only_image_sensitive','internal_only_case_extractable','internal_only_map_or_route_risk'}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def add(rows, severity, check, scope, subject_id, detail, required_action):
    rows.append({'finding_id':f'gca_{len(rows)+1:04d}','severity':severity,'check':check,'scope':scope,'subject_id':subject_id,'detail':detail,'required_action':required_action})

def split_pipe(value: str): return [x for x in (value or '').split('|') if x]

def run(root: Path):
    rows=[]
    cand={r.get('candidate_id',''):r for r in read_csv(root/'Candidate-Ledger-current.csv')}
    elig={r.get('candidate_id',''):r for r in read_csv(root/'META/Public-Export-Eligibility-current.csv')}
    snap={r.get('candidate_id',''):r for r in read_csv(root/'META/Candidate-Governance-Snapshot-current.csv')}
    queue={r.get('candidate_id',''):r for r in read_csv(root/'META/Governance-Review-Queue-current.csv')}
    public={r.get('candidate_id',''):r for r in read_csv(root/'PUBLIC/Candidate-Index-public.csv')}
    consent={r.get('candidate_id',''):r for r in read_csv(root/'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv')}
    decisions=read_csv(root/'GOVERNANCE/Governance-Decision-Ledger-current.csv')
    source={r.get('source_id',''):r for r in read_csv(root/'Source-Registry-current.csv')}
    link={r.get('source_id',''):r for r in read_csv(root/'META/Public-Source-Link-Review-current.csv')}

    if set(cand)!=set(elig): add(rows,'high','eligibility_candidate_coverage','candidate','all',f'candidate ids {len(cand)} != eligibility ids {len(elig)}','Regenerate public export eligibility.')
    if set(cand)!=set(snap): add(rows,'high','snapshot_candidate_coverage','candidate','all',f'candidate ids {len(cand)} != snapshot ids {len(snap)}','Regenerate candidate governance snapshot.')
    if set(cand)!=set(queue): add(rows,'high','queue_candidate_coverage','candidate','all',f'candidate ids {len(cand)} != queue ids {len(queue)}','Regenerate governance review queue.')
    if set(cand)!=set(public): add(rows,'high','public_index_candidate_coverage','candidate','all',f'candidate ids {len(cand)} != public index ids {len(public)}','Regenerate public-safe index.')

    for cid,c in cand.items():
        e=elig.get(cid,{}); s=snap.get(cid,{}); q=queue.get(cid,{}); p=public.get(cid,{})
        if e.get('candidate_name') and e.get('candidate_name') != c.get('name'):
            add(rows,'high','eligibility_name_parity','candidate',cid,'eligibility candidate_name differs from Candidate-Ledger name','Regenerate eligibility from Candidate-Ledger.')
        if s.get('candidate_name') and s.get('candidate_name') != c.get('name'):
            add(rows,'high','snapshot_name_parity','candidate',cid,'snapshot candidate_name differs from Candidate-Ledger name','Regenerate governance snapshot from Candidate-Ledger.')
        if p:
            for field in ['public_export_tier','public_shape_template']:
                if p.get(field) != e.get(field):
                    add(rows,'high','public_index_matches_eligibility','candidate',cid,f'public {field}={p.get(field)!r}; eligibility={e.get(field)!r}','Regenerate public index after eligibility changes.')
        if e.get('public_export_tier')=='quarantined_no_public_expansion':
            if s.get('governance_quarantine')!='true':
                add(rows,'high','quarantine_snapshot_alignment','candidate',cid,'eligibility quarantined but snapshot governance_quarantine is not true','Regenerate snapshot and check consent/governance gate.')
            if q.get('priority')!='0':
                add(rows,'high','quarantine_queue_priority','candidate',cid,'eligibility quarantined but review queue priority is not 0','Regenerate governance review queue; quarantines must be top priority.')
            if 'family_or_community' not in e.get('required_review',''):
                add(rows,'high','quarantine_review_requirement','candidate',cid,'quarantined row lacks family/community review requirement','Update eligibility generator or governance row.')
        if cid in consent:
            if e.get('public_export_tier') not in {'quarantined_no_public_expansion','boundary_index_shape_only'}:
                add(rows,'high','consent_row_restricts_public_tier','candidate',cid,'candidate has consent/governance row but public tier is not restricted','Manual governance review required before loosening tier.')
            if 'governance' not in e.get('consent_or_governance_gate','').lower():
                add(rows,'medium','consent_gate_visible','candidate',cid,'candidate has consent/governance row but eligibility gate text does not name governance','Make governance gate legible in eligibility row.')
        near=set(split_pipe(s.get('near_harm_profile',''))) | set(split_pipe(e.get('highest_harm_proximity','')))
        if near & NEAR_HARM:
            if e.get('public_url_release') not in {'no_public_urls_without_manual_link_review','internal_only_until_governance_review'}:
                add(rows,'high','near_harm_blocks_public_urls','candidate',cid,f'near-harm profile {"|".join(sorted(near & NEAR_HARM))} but public_url_release={e.get("public_url_release")!r}','Require no public URLs until manual/governance link review.')
        if int(s.get('blocked_public_url_sources') or 0) > 0 and e.get('public_url_release') not in {'no_public_urls_without_manual_link_review','internal_only_until_governance_review'}:
            add(rows,'high','blocked_urls_reflected_in_eligibility','candidate',cid,'snapshot has blocked public URL sources but eligibility does not block URLs','Regenerate eligibility/snapshot and keep URL release closed.')
        if s.get('public_claim_release') and e.get('public_claim_release') and s.get('public_claim_release') != e.get('public_claim_release'):
            add(rows,'high','claim_release_snapshot_parity','candidate',cid,'snapshot public_claim_release disagrees with eligibility','Regenerate governance snapshot from eligibility.')

    if set(source)!=set(link):
        add(rows,'high','source_link_review_coverage','source','all',f'sources {len(source)} != link reviews {len(link)}','Regenerate Public-Source-Link-Review.')
    for sid,src in source.items():
        lr=link.get(sid,{})
        policy=src.get('public_link_policy','')
        decision=lr.get('public_url_release_decision','')
        if policy in INTERNAL_POLICIES and decision != 'block_public_url':
            add(rows,'high','internal_policy_blocks_public_url','source',sid,f'{policy} has decision {decision!r}','Internal-only public-link policies must map to block_public_url.')
        if policy == 'boundary_note_required_or_internal_only' and decision != 'manual_review_required_block_until_review':
            add(rows,'high','boundary_or_internal_requires_manual','source',sid,f'{policy} has decision {decision!r}','Boundary-or-internal policy must remain manual-review-blocked until reviewed.')
        if policy == 'public_link_allowed_with_boundary_note' and decision != 'allow_only_with_boundary_note_after_manual_review':
            add(rows,'high','boundary_note_policy_decision','source',sid,f'{policy} has decision {decision!r}','Boundary-note source must not be exposed without manual review and boundary note.')
        if lr and lr.get('harm_proximity') != src.get('harm_proximity'):
            add(rows,'high','link_review_harm_parity','source',sid,'Public-Source-Link-Review harm_proximity differs from Source-Registry','Regenerate source-link review from Source-Registry.')
    if not any(r.get('decision_class')=='public_release_blocked' and r.get('status')=='active' for r in decisions):
        add(rows,'high','active_public_release_block_decision','governance','package','No active public_release_blocked governance decision found','Keep package-level public release block active until review loosens it.')
    if not any(r.get('decision_class')=='manual_review_required' and r.get('status')=='active' for r in decisions):
        add(rows,'medium','manual_review_decision_present','governance','package','No active manual_review_required governance decision found','Record the manual review requirement as an active governance decision.')
    if not rows:
        add(rows,'info','governance_consistency','package','all','PASS eligibility, public index, snapshot, review queue, consent ledger, link review, and governance decisions are mutually consistent','No action required.')
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Governance-Consistency-Audit-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Governance-Consistency-Audit-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    high=sum(1 for r in rows if r.get('severity')=='high')
    med=sum(1 for r in rows if r.get('severity')=='medium')
    lines=['# Governance Consistency Audit — current','', 'Generated by `tools/governance_consistency_audit.py`.', '', f'High findings: {high}', f'Medium findings: {med}', '']
    if high or med:
        lines.append('## Findings')
        for r in rows:
            if r.get('severity')!='info':
                lines.append(f"- **{r.get('severity')}** `{r.get('check')}` `{r.get('scope')}` `{r.get('subject_id')}` — {r.get('detail')}")
    else:
        lines.append('PASS: governance ledgers and public-index gate rows are mutually consistent under configured checks.')
    (out/'Governance-Consistency-Audit-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    for r in rows[:80]: print(f"{r.get('severity','?').upper()} {r.get('check')} {r.get('scope')} {r.get('subject_id')}: {r.get('detail')}")
    if len(rows)>80: print(f'... {len(rows)-80} more rows')
    if args.fail_on_high and any(r.get('severity')=='high' for r in rows): sys.exit(1)
if __name__=='__main__': main()
