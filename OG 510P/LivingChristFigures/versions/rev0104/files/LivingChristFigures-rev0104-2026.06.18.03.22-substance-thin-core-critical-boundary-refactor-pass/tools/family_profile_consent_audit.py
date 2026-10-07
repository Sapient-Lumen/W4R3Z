#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['finding_id','candidate_id','candidate_name','source_id','domain','source_role','harm_proximity','public_link_policy','public_url_release_decision','consent_row_status','boundary_claim_status','risk_class','severity','status','required_action','note']
FAMILY_TOKENS=('family_profile_near','family_led_witness_profile','family-led','family_led','consent_not_generalizable_boundary')
NEEDS_BLOCK_TOKENS=('family_led_witness_profile','interview_profile_source','explicit_family_profile_public_url_block')

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def split_pipe(value: str): return [x for x in (value or '').split('|') if x]

def is_family_profile_source(src: dict) -> bool:
    text=' '.join(src.get(k,'') for k in ['harm_proximity','evidence_roles','risk_notes','data_governance_notes','source_type']).lower()
    return any(tok.lower() in text for tok in FAMILY_TOKENS)

def candidate_name_map(root: Path):
    return {r.get('candidate_id',''):r.get('name','') for r in read_csv(root/'Candidate-Ledger-current.csv')}

def consent_map(root: Path):
    return {r.get('candidate_id',''):r for r in read_csv(root/'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv')}

def boundary_claims(root: Path):
    out={}
    for r in read_csv(root/'Claim-Ledger-current.csv'):
        text=' '.join([r.get('claim_type',''),r.get('claim_status',''),r.get('claim_text',''),r.get('notes','')]).lower()
        if any(tok in text for tok in ['consent','family-story','family story','case-list','case list','public-link','public link','testimony','image','vigil-map','vigil map']):
            out.setdefault(r.get('candidate_id',''),[]).append(r.get('claim_id',''))
    return out

def run(root: Path):
    links={r.get('source_id',''):r for r in read_csv(root/'META/Public-Source-Link-Review-current.csv')}
    names=candidate_name_map(root); cons=consent_map(root); bclaims=boundary_claims(root)
    rows=[]
    for src in read_csv(root/'Source-Registry-current.csv'):
        if not is_family_profile_source(src):
            continue
        sid=src.get('source_id','')
        link=links.get(sid,{})
        cids=split_pipe(src.get('candidate_ids','')) or ['']
        role=src.get('evidence_roles','')
        text=' '.join([role,src.get('risk_notes',''),src.get('data_governance_notes',''),src.get('public_link_policy','')]).lower()
        # Internal-only policies and explicit family-led witness/profile roles must block public URL release.
        # Official aggregate/current/legal context rows may remain boundary-note-only even if their risk notes mention testimony as a prohibited extraction.
        needs_block=src.get('public_link_policy','').startswith('internal_only') or 'family_led_witness_profile' in text or 'explicit_family_profile_public_url_block' in text
        decision=link.get('public_url_release_decision','missing_link_review')
        policy=src.get('public_link_policy','')
        for cid in cids:
            consent_status='consent_row_present' if cid and cid in cons else ('no_candidate_scope' if not cid else 'missing_consent_row')
            claim_ids=bclaims.get(cid,[])
            bstatus='boundary_claim_present:'+'|'.join(claim_ids[:4]) if claim_ids else ('no_candidate_scope' if not cid else 'missing_boundary_claim')
            if needs_block:
                ok=(decision=='block_public_url' and policy.startswith('internal_only'))
                risk_class='family_profile_or_testimony_source_must_block_public_url'
                action='keep URL blocked; use only as internal boundary evidence; require external governance review before public reference'
            else:
                ok=decision in {'block_public_url','allow_only_with_boundary_note_after_manual_review'} and consent_status!='missing_consent_row' and bstatus!='missing_boundary_claim'
                risk_class='family_profile_context_requires_boundary_note_or_block'
                action='keep boundary note adjacent; no extraction of family stories, testimony, images, contacts, cases, or event logistics'
            severity='info' if ok else 'high'
            status='pass' if ok else 'fail'
            rows.append({'finding_id':f'fpca_{len(rows)+1:04d}','candidate_id':cid,'candidate_name':names.get(cid,''),'source_id':sid,'domain':src.get('domain',''),'source_role':role,'harm_proximity':src.get('harm_proximity',''),'public_link_policy':policy,'public_url_release_decision':decision,'consent_row_status':consent_status,'boundary_claim_status':bstatus,'risk_class':risk_class,'severity':severity,'status':status,'required_action':action,'note':src.get('risk_notes','') or src.get('data_governance_notes','')})
    if not rows:
        rows.append({'finding_id':'fpca_0001','candidate_id':'','candidate_name':'','source_id':'','domain':'','source_role':'summary','harm_proximity':'','public_link_policy':'','public_url_release_decision':'','consent_row_status':'no_family_profile_sources_detected','boundary_claim_status':'','risk_class':'summary','severity':'info','status':'pass','required_action':'no action','note':'No family-profile sources detected.'})
    return rows

def write_reports(root: Path, rows):
    write_csv_json_md_report(root,'META/Family-Profile-Consent-Boundary-Audit-current.csv',FIELDS,rows,'Family Profile Consent Boundary Audit','tools/family_profile_consent_audit.py',columns=['finding_id','source_id','domain','candidate_id','public_link_policy','public_url_release_decision','consent_row_status','boundary_claim_status','severity','status','required_action'],intro_lines=['Audits sources near family-chosen profiles, interviews, testimony, or family-led witness material.','The audit ensures family-profile visibility is not mistaken for public URL release, quote/story extraction, image reuse, case-list permission, contact/support use, event/vigil mapping, or general consent.'],max_md_rows=180)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} family-profile consent audit rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['source_id']} {r['candidate_id']}: {r['required_action']}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
