#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

FIELDS=['finding_id','finding_type','candidate_id','candidate_name','claim_id','source_id','domain','hazard_tokens','claim_status','public_url_release_decision','public_link_policy','capacity_state','live_referral_safe','quarantine_status','severity','status','required_action','note']
PACIFIC_TOKENS=['palau','chuuk','fsm','kiribati','nauru','niue','tuvalu','vanuatu','tonga','fiji','samoa','marshall','pohnpei','kosrae','pacific','png','papua','solomon']
HAZARDS=['service directory','counselling','counseling','legal advice','protection order','safety order','referral','intake','contact','phone','hotline','helpline','shelter','safe house','refuge','capacity','current access','availability','case management','client','staff','site','centre','center','image','route','support path']
SAFE_STATUS=['quarantined_from_service_referral_capacity_extraction','boundary','not_referral','not_capacity','caution']
BLOCK_TOKENS=['service_directory','contact','helpline','shelter','refuge','legal_advice','protection_order','current_capacity','referral','intake']

def low(v: str) -> str: return (v or '').lower()
def split(v: str): return [x for x in (v or '').split('|') if x]
def hits(text: str, toks):
    t=low(text)
    return [tok for tok in toks if tok in t]

def is_pacific_gbv_candidate(c: dict[str,str]) -> bool:
    hay='|'.join([c.get('candidate_id',''),c.get('name',''),c.get('location',''),c.get('sensitivity',''),c.get('status_current',''),c.get('office','')]).lower()
    return ('survivor_service' in c.get('sensitivity','') or 'helpline_or_crisis_contact' in c.get('sensitivity','')) and any(tok in hay for tok in PACIFIC_TOKENS)

def run(root: Path):
    candidates=read_csv_rows(root/'Candidate-Ledger-current.csv')
    claims=read_csv_rows(root/'Claim-Ledger-current.csv')
    sources=read_csv_rows(root/'Source-Registry-current.csv')
    link={r.get('source_id',''):r for r in read_csv_rows(root/'META/Public-Source-Link-Review-current.csv')}
    q={r.get('claim_id',''):r for r in read_csv_rows(root/'META/Public-Claim-Quarantine-current.csv')}
    cand_by_id={c.get('candidate_id',''):c for c in candidates}
    pacific_ids={c.get('candidate_id','') for c in candidates if is_pacific_gbv_candidate(c)}
    rows=[]
    def add(kind,cid,cname,claim_id,source_id,domain,haz,claim_status,decision,policy,capacity,live,qstat,severity,status,action,note):
        rows.append({'finding_id':f'pgbvc_{len(rows)+1:04d}','finding_type':kind,'candidate_id':cid,'candidate_name':cname,'claim_id':claim_id,'source_id':source_id,'domain':domain,'hazard_tokens':'|'.join(sorted(set(haz))),'claim_status':claim_status,'public_url_release_decision':decision,'public_link_policy':policy,'capacity_state':capacity,'live_referral_safe':live,'quarantine_status':qstat,'severity':severity,'status':status,'required_action':action,'note':note})
    for cl in claims:
        cid=cl.get('candidate_id','')
        if cid not in pacific_ids:
            continue
        if cl.get('claim_type')!='institutional_or_work_shape' and cl.get('claim_id')!='claim_0286':
            continue
        c=cand_by_id.get(cid,{})
        text='|'.join([cl.get('claim_text',''),cl.get('evidence_text',''),cl.get('notes',''),cl.get('claim_status',''),c.get('flags_current',''),c.get('status_current',''),c.get('capacity_state','')])
        haz=hits(text, HAZARDS)
        if not haz and cl.get('claim_id')!='claim_0286':
            continue
        qrow=q.get(cl.get('claim_id',''),{})
        status_safe=any(tok in low(cl.get('claim_status','')) for tok in SAFE_STATUS)
        qsafe=any(tok in low(qrow.get('public_wording_status','')) for tok in BLOCK_TOKENS) and 'blocked' in low(qrow.get('public_wording_status',''))
        live_ok=c.get('live_referral_safe')=='false'
        ok=status_safe and qsafe and live_ok
        add('claim_boundary',cid,cl.get('candidate_name',''),cl.get('claim_id',''),'','',haz,cl.get('claim_status',''),'','',c.get('capacity_state',''),c.get('live_referral_safe',''),qrow.get('public_wording_status','missing_quarantine_row') if qrow else 'missing_quarantine_row','info' if ok else 'high','pass' if ok else 'fail','none' if ok else 'quarantine Pacific GBV/service claim and block directory/referral/contact/legal/capacity public wording','Pacific GBV/survivor-service institutional-shape claims must remain aggregate/internal; no public directory, referral, legal advice, shelter/refuge, contact/helpline, current-capacity, case/client, staff/site, image, or route/support-path extraction')
    for src in sources:
        cids=[cid for cid in split(src.get('candidate_ids','')) if cid in pacific_ids]
        if not cids:
            continue
        hay='|'.join([src.get('evidence_roles',''),src.get('risk_notes',''),src.get('data_governance_notes',''),src.get('harm_proximity',''),src.get('public_link_policy',''),src.get('url',''),src.get('does_not_support','')])
        haz=hits(hay, HAZARDS)
        if not haz:
            continue
        lr=link.get(src.get('source_id',''),{})
        decision=lr.get('public_url_release_decision','')
        policy=src.get('public_link_policy','') or lr.get('public_link_policy','')
        safe=src.get('safe_to_recheck_automatically','')
        ok=False
        if policy.startswith('internal_only'):
            ok=(decision=='block_public_url' and safe in {'do_not_auto_recheck','manual_review_required'})
        elif policy=='public_link_allowed_with_boundary_note':
            ok=decision.startswith('allow_only_with_boundary_note') and 'no' in low(lr.get('allowed_public_use','')+lr.get('required_boundary_note',''))
        add('source_boundary','|'.join(cids),'|'.join(cand_by_id.get(c,{}).get('name','') for c in cids),'',src.get('source_id',''),src.get('domain',''),haz,'',decision,policy,'','', '', 'info' if ok else 'high','pass' if ok else 'fail','none' if ok else 'block public URL or restrict to boundary-note-only non-directory context','Pacific GBV/service-adjacent source must not become a public link, service directory, contact/referral path, legal guide, shelter/refuge cue, or current-capacity claim')
    # Explicit rev0090 closure rows.
    target_claims=[r for r in rows if r.get('finding_type')=='claim_boundary']
    high_bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    claim_0164=[r for r in rows if r.get('claim_id')=='claim_0164' and r.get('status')=='pass']
    claim_0286=[r for r in rows if r.get('claim_id')=='claim_0286' and r.get('status')=='pass']
    add('summary','','','','','','','','','','','','','info' if not high_bad and len(target_claims)>=24 and claim_0164 and claim_0286 else 'high','pass' if not high_bad and len(target_claims)>=24 and claim_0164 and claim_0286 else 'fail','none' if not high_bad else 'repair high Pacific GBV service-capacity findings',f'Pacific GBV service-capacity audit rows={len(rows)} claim_rows={len(target_claims)} high_fail={len(high_bad)} claim_0164_pass={len(claim_0164)} claim_0286_pass={len(claim_0286)}')
    return rows

def write_reports(root: Path, rows):
    write_csv_json_md_report(root,'META/Pacific-GBV-Service-Capacity-Boundary-Audit-current.csv',FIELDS,rows,'Pacific GBV Service-Capacity Boundary Audit','tools/pacific_gbv_service_capacity_audit.py',columns=['finding_id','finding_type','candidate_id','claim_id','source_id','hazard_tokens','claim_status','public_url_release_decision','public_link_policy','capacity_state','live_referral_safe','quarantine_status','severity','status','required_action'],intro_lines=['Audits Pacific GBV/survivor-service claims and sources for service-directory, contact/helpline, shelter/refuge, legal-advice, protection-order-safety, referral/intake, current-capacity, case/client, staff/site, image, and route/support-path leakage.','The audit is about release safety: aggregate institutional or standards context may remain internal evidence, but public prose must not become a directory, referral surface, legal guide, capacity claim, shelter/refuge cue, or operational support path.'],max_md_rows=260)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} Pacific GBV service-capacity boundary audit rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r.get('finding_id')} {r.get('claim_id') or r.get('source_id')}: {r.get('required_action')}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
