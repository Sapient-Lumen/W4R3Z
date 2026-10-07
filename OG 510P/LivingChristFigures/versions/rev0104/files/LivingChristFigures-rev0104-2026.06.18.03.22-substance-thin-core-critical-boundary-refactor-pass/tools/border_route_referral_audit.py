#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

FIELDS=['finding_id','finding_type','candidate_id','candidate_name','claim_id','source_id','domain','hazard_tokens','claim_status','public_url_release_decision','public_link_policy','quarantine_status','severity','status','required_action','note']
HAZARDS=['route','crossing','crossing-risk','camp','site','location','timing','phone','hotline','helpline','contact','referral','shelter','accommodation','emergency','distribution','live-aid','aid instruction','map','image','capacity']
SAFE_STATUS_TOKENS=['quarantined','boundary','caution','not_referral','not_capacity','no_route','no_public','blocked']
BORDER_TOKENS=['rev0089_border_route_referral_quarantine','Calais','Grande-Synthe','Dunkirk','UK-France border','Franco-British border']

def split(v: str): return [x for x in (v or '').split('|') if x]
def low(v: str): return (v or '').lower()
def has_token(text: str, toks):
    t=low(text)
    return [tok for tok in toks if tok in t]

def run(root: Path):
    candidates=read_csv_rows(root/'Candidate-Ledger-current.csv')
    claims=read_csv_rows(root/'Claim-Ledger-current.csv')
    sources=read_csv_rows(root/'Source-Registry-current.csv')
    link_rows={r.get('source_id',''):r for r in read_csv_rows(root/'META/Public-Source-Link-Review-current.csv')}
    quarantine={r.get('claim_id',''):r for r in read_csv_rows(root/'META/Public-Claim-Quarantine-current.csv')}
    cand_by_id={r.get('candidate_id',''):r for r in candidates}
    border_ids=set()
    for c in candidates:
        hay='|'.join([c.get('candidate_id',''),c.get('name',''),c.get('location',''),c.get('sensitivity',''),c.get('office',''),c.get('work',''),c.get('flags_current','')])
        if c.get('candidate_id')=='cand_calais_grassroots_border_offices_rck_utopia56_hro_adm' or has_token(hay, BORDER_TOKENS): border_ids.add(c.get('candidate_id',''))
    rows=[]
    def add(kind,cid,cname,claim_id,source_id,domain,haz,claim_status,decision,policy,qstatus,severity,status,action,note):
        rows.append({'finding_id':f'brrba_{len(rows)+1:04d}','finding_type':kind,'candidate_id':cid,'candidate_name':cname,'claim_id':claim_id,'source_id':source_id,'domain':domain,'hazard_tokens':'|'.join(sorted(set(haz))),'claim_status':claim_status,'public_url_release_decision':decision,'public_link_policy':policy,'quarantine_status':qstatus,'severity':severity,'status':status,'required_action':action,'note':note})
    for cl in claims:
        cid=cl.get('candidate_id','')
        if cid not in border_ids: continue
        text='|'.join([cl.get('claim_text',''),cl.get('evidence_text',''),cl.get('notes',''),cl.get('claim_type','')])
        haz=has_token(text, HAZARDS)
        if not haz: continue
        status=low(cl.get('claim_status',''))
        q=quarantine.get(cl.get('claim_id',''),{})
        q_block='blocked' in low(q.get('public_wording_status','')) or 'quarantin' in low(q.get('quarantine_reason',''))
        status_safe=any(tok in status for tok in SAFE_STATUS_TOKENS)
        # Positive institutional/service-shaped claims with route/referral/contact hazards must be both status-safe and quarantined.
        positive=cl.get('claim_type','') in {'institutional_or_work_shape','capacity_or_live_referral_boundary'} or 'supported_public_shape' in status
        ok=((status_safe or q_block) and (q_block or not positive))
        add('claim_boundary',cid,cl.get('candidate_name',''),cl.get('claim_id',''),'','',haz,cl.get('claim_status',''),'','',q.get('quarantine_reason','missing_quarantine_row') if q else 'missing_quarantine_row','info' if ok else 'high','pass' if ok else 'fail','none' if ok else 'quarantine claim status and add/update Public-Claim-Quarantine row before public prose','border candidate claim contains route/referral/contact/camp/site/capacity hazards and must stay boundary/quarantine-controlled')
    for src in sources:
        cids=[cid for cid in split(src.get('candidate_ids','')) if cid in border_ids]
        if not cids: continue
        hay='|'.join([src.get('evidence_roles',''),src.get('risk_notes',''),src.get('data_governance_notes',''),src.get('harm_proximity',''),src.get('public_link_policy',''),src.get('source_type',''),src.get('url','')])
        haz=has_token(hay, HAZARDS)
        if not haz: continue
        lr=link_rows.get(src.get('source_id',''),{})
        policy=src.get('public_link_policy','') or lr.get('public_link_policy','')
        decision=lr.get('public_url_release_decision','')
        safe=src.get('safe_to_recheck_automatically','')
        blocked=(decision=='block_public_url' and policy.startswith('internal_only') and safe in {'do_not_auto_recheck','manual_review_required'})
        note='source is internal-only/manual and public URL is blocked' if blocked else 'border-hazard source lacks an internal-only/manual public-link block'
        add('source_boundary','|'.join(cids),'|'.join(cand_by_id.get(c,{}).get('name','') for c in cids),'',src.get('source_id',''),src.get('domain',''),haz,'',decision,policy,'','info' if blocked else 'high','pass' if blocked else 'fail','none' if blocked else 'block public URL and require manual no-route/no-referral/no-contact review',note)
    if not rows:
        add('summary','','','','','','','','','','','high','fail','add border-route/referral boundary rows','no border-route/referral claims or sources were audited')
    high_bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not high_bad:
        add('summary','','','','','','','','','','','info','pass','none',f'border-route/referral boundary audit passed for {len(rows)} finding row(s) before summary')
    return rows

def write_reports(root: Path, rows):
    write_csv_json_md_report(root,'META/Border-Route-Referral-Boundary-Audit-current.csv',FIELDS,rows,'Border Route Referral Boundary Audit','tools/border_route_referral_audit.py',columns=['finding_id','finding_type','candidate_id','claim_id','source_id','hazard_tokens','claim_status','public_url_release_decision','public_link_policy','quarantine_status','severity','status','required_action'],intro_lines=['Audits border-route/referral/contact/camp/site/timing/live-aid/image/capacity hazards in candidate claims and source rows.','The audit is deliberately about release safety: aggregate counterpressure and institutional shape can remain internal evidence, but public prose must not become a map, directory, referral surface, current-capacity statement, or operational guide.'],max_md_rows=220)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} border-route/referral boundary audit rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r.get('finding_id')} {r.get('claim_id') or r.get('source_id')}: {r.get('required_action')}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
