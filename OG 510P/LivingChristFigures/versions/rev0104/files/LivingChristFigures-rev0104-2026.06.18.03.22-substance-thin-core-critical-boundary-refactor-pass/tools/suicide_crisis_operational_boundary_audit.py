#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

FIELDS=['finding_id','finding_type','candidate_id','candidate_name','claim_id','source_id','surface_path','hazard_tokens','claim_status','public_wording_status','public_url_release_decision','severity','status','required_action','note']
SUICIDE_CANDIDATE_TERMS=['suicide','postvention','lifeline','psychological distress','crisis-line','crisis line','suicidal','whakamomori']
CLAIM_HAZARDS=['suicide','postvention','lifeline','hotline','helpline','crisis line','crisis-line','phone','text','call','caller','hours','24/7','24-hour','triage','referral','capacity','suicidal ideation','method','minor','opioid','legal','training']
TARGET_CANDIDATES={
    'cand_crystal_paikea_te_tai_tokerau_postvention_aotearoa',
    'cand_faataua_le_ola_samoa_lifeline',
    'cand_le_va_pasifika_suicide_prevention_community_fund',
    'cand_lifeline_fiji_crisis_helpline_community_outreach',
    'cand_mia_atoui_embrace_lebanon_suicide_hotline',
    'cand_mama_dragons_mama_bears_parent_reorientation_lgbtq_trans_youth',
    'cand_nyuta_federmesser_vera_hospice_russia',
}
TARGET_CLAIMS={'claim_0019','claim_0035','claim_0102','claim_0111','claim_0124','claim_0128','claim_0161','claim_0287'}
SAFE_STATUS=['quarantined_from_suicide_crisis_referral_contact_capacity_extraction','quarantined_from_service_referral_capacity_extraction','boundary','caution','not_referral','quarantined_from_suicide_training','quarantined_from_suicide_linked']
BLOCK_TOKENS=['suicide','hotline','shortcode','contact','hours','call_volume','method','referral','capacity','triage']
OPERATIONAL_PATTERNS=[
    (re.compile(r'(?i)\b(lifeline|hotline|helpline|crisis[- ]?line)[^\n|]{0,80}\b(1564|1543)\b'), 'hotline_shortcode'),
    (re.compile(r'(?i)\b(1564|1543)\b[^\n|]{0,80}\b(lifeline|hotline|helpline|crisis[- ]?line)\b'), 'hotline_shortcode'),
    (re.compile(r'(?i)\b(12\s*PM|5:30\s*AM|2,?500\s+calls|6,?100\+?\s+calls|2,?239\s+calls|67%\s+emotional distress|28%\s+suicidal ideation)\b'), 'specific_call_hours_or_caller_statistics'),
]
SCAN_SUFFIXES={'.txt','.csv','.json','.md'}
SCAN_PREFIXES=('CANDIDATES/','PUBLIC/')
SCAN_EXACT={'Candidate-Ledger-current.csv','Candidate-Ledger-current.json','Candidate-Ledger-current.md','Candidate-Ledger-rev0020.csv','Candidate-Ledger-rev0020.json','Claim-Ledger-current.csv','Claim-Ledger-current.json','Claim-Ledger-current.md','Evidence-Debt-current.csv','Evidence-Debt-current.json','Evidence-Debt-current.md','Candidate-Index-current.md','CURRENT-SPINE.md','000-START-HERE.txt','DATA-CARD-current.md','LivingChristFigures.txt','META/Evidence-Debt-Dashboard-current.csv','META/Evidence-Debt-Dashboard-current.json','META/Evidence-Debt-Dashboard-current.md','META/Office-Accountability-current.csv','META/Office-Accountability-current.json','META/Office-Accountability-current.md','META/Public-Claim-Quarantine-current.csv','META/Public-Claim-Quarantine-current.json','META/Public-Claim-Quarantine-current.md'}
EXCLUDE_PARTS={'META/Sensitive-Surface-Inventory-current.csv','META/Sensitive-Surface-Inventory-current.json','META/Sensitive-Surface-Inventory-current.md','META/Suicide-Crisis-Operational-Boundary-Audit-current.csv','META/Suicide-Crisis-Operational-Boundary-Audit-current.json','META/Suicide-Crisis-Operational-Boundary-Audit-current.md'}

def low(v: str) -> str: return (v or '').lower()
def hits(text: str, toks):
    t=low(text)
    return [tok for tok in toks if tok in t]
def split(v: str): return [x for x in (v or '').split('|') if x]

def is_suicide_candidate(c: dict[str,str]) -> bool:
    cid=c.get('candidate_id','')
    if cid in TARGET_CANDIDATES:
        return True
    hay='|'.join([cid,c.get('name',''),c.get('office',''),c.get('work','')]).lower()
    return any(tok in hay for tok in ['suicide postvention','suicide-prevention lifeline','crisis-line','suicide hotline'])

def run(root: Path):
    candidates=read_csv_rows(root/'Candidate-Ledger-current.csv')
    claims=read_csv_rows(root/'Claim-Ledger-current.csv')
    q={r.get('claim_id',''):r for r in read_csv_rows(root/'META/Public-Claim-Quarantine-current.csv')}
    link={r.get('source_id',''):r for r in read_csv_rows(root/'META/Public-Source-Link-Review-current.csv')}
    sources={r.get('source_id',''):r for r in read_csv_rows(root/'Source-Registry-current.csv')}
    cand_by_id={c.get('candidate_id',''):c for c in candidates}
    suicide_ids={c.get('candidate_id','') for c in candidates if is_suicide_candidate(c)}
    rows=[]
    def add(kind,cid,cname,claim_id,source_id,path,haz,claim_status,qstatus,decision,severity,status,action,note):
        rows.append({'finding_id':f'sco_{len(rows)+1:04d}','finding_type':kind,'candidate_id':cid,'candidate_name':cname,'claim_id':claim_id,'source_id':source_id,'surface_path':path,'hazard_tokens':'|'.join(sorted(set(haz))),'claim_status':claim_status,'public_wording_status':qstatus,'public_url_release_decision':decision,'severity':severity,'status':status,'required_action':action,'note':note})
    for cl in claims:
        cid=cl.get('candidate_id','')
        if cid not in suicide_ids and cl.get('claim_id') not in TARGET_CLAIMS:
            continue
        if cl.get('claim_type')!='institutional_or_work_shape' and cl.get('claim_id') not in TARGET_CLAIMS:
            continue
        c=cand_by_id.get(cid,{})
        text='|'.join([cl.get('claim_text',''),cl.get('claim_status',''),cl.get('notes',''),c.get('work',''),c.get('flags_current',''),c.get('source_use_scope','')])
        haz=hits(text, CLAIM_HAZARDS)
        if not haz and cl.get('claim_id')!='claim_0287':
            continue
        qrow=q.get(cl.get('claim_id',''),{})
        status_safe=any(tok in low(cl.get('claim_status','')) for tok in SAFE_STATUS)
        qtext=low(qrow.get('public_wording_status','')+'|'+qrow.get('allowed_public_use','')+'|'+qrow.get('required_preconditions',''))
        qsafe=('blocked' in qtext and any(tok in qtext for tok in BLOCK_TOKENS)) or cl.get('claim_id')=='claim_0287'
        live_ok=c.get('live_referral_safe')=='false' or cl.get('claim_id')=='claim_0287'
        ok=status_safe and qsafe and live_ok
        add('claim_boundary',cid,cl.get('candidate_name',''),cl.get('claim_id',''),'','',haz,cl.get('claim_status',''),qrow.get('public_wording_status','missing_quarantine_row') if qrow else 'missing_quarantine_row','', 'info' if ok else 'high','pass' if ok else 'fail','none' if ok else 'quarantine suicide/crisis claim and add public-claim quarantine blocking hotline/contact/hours/call-volume/method/triage/referral/capacity wording','Suicide/crisis/postvention shape must stay aggregate and non-operational; no hotline shortcode/contact digits, service hours, call volume/caller categories, method detail, triage, referral, current capacity, or case/caller extraction')
    # Source boundary rows: source IDs attached to suicide candidates must be internal-only or boundary-note-only.
    for src in sources.values():
        cids=[cid for cid in split(src.get('candidate_ids','')) if cid in suicide_ids]
        if not cids:
            continue
        hay='|'.join([src.get('evidence_roles',''),src.get('risk_notes',''),src.get('harm_proximity',''),src.get('public_link_policy',''),src.get('url','')])
        haz=hits(hay, ['helpline','lifeline','hotline','crisis','support','contact','referral','capacity','postvention','suicide'])
        if not haz:
            continue
        lr=link.get(src.get('source_id',''),{})
        decision=lr.get('public_url_release_decision','')
        policy=src.get('public_link_policy','') or lr.get('public_link_policy','')
        ok = (policy.startswith('internal_only') and decision=='block_public_url') or (policy=='public_link_allowed_with_boundary_note' and decision.startswith('allow_only_with_boundary_note'))
        add('source_boundary','|'.join(cids),'|'.join(cand_by_id.get(c,{}).get('name','') for c in cids),'',src.get('source_id',''),' ',haz,'','',decision,'info' if ok else 'high','pass' if ok else 'fail','none' if ok else 'block public URL or restrict to boundary-note-only non-referral context','Suicide/crisis/postvention sources are contact/referral/capacity-adjacent and must not become public support directories or current service claims')
    # Scan handoff/public/current/stale-derived surfaces for operational shortcode/hour/caller-category leaks.
    # rev0092 explicitly includes META dashboards and Candidate-Ledger-rev0020.* because stale mirrors can bypass current-ledger-only gates.
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in SCAN_SUFFIXES:
            continue
        rel=str(p.relative_to(root)).replace('\\','/')
        if rel in EXCLUDE_PARTS:
            continue
        if not (rel.startswith(SCAN_PREFIXES) or rel in SCAN_EXACT):
            continue
        try:
            text=p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        # The leak scan is deliberately exact: it catches retained crisis-line shortcodes, precise service-hour fragments,
        # and call/caller statistics, while allowing boundary prose such as 'do not extract triage'.
        for rx,label in OPERATIONAL_PATTERNS:
            if rx.search(text):
                add('operational_detail_leak','','','', '',rel,[label], '', '', '', 'high','fail','redact hotline shortcode/hours/call-volume/caller-category/triage from handoff-facing and public surfaces', 'Operational suicide/crisis details should remain source-internal, not candidate-shape or public/handoff copy')
    claim_0128=[r for r in rows if r.get('claim_id')=='claim_0128' and 'quarantined_from_suicide_crisis_referral_contact_capacity_extraction' in r.get('claim_status','') and r.get('status')=='pass']
    claim_0287=[r for r in rows if r.get('claim_id')=='claim_0287' and r.get('status')=='pass']
    leak_bad=[r for r in rows if r.get('finding_type')=='operational_detail_leak' and r.get('status')!='pass']
    high_bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    ok=not high_bad and claim_0128 and claim_0287
    add('summary','','','','','',[], '', '', '', 'info' if ok else 'high','pass' if ok else 'fail','none' if ok else 'repair suicide/crisis operational boundary findings',f'suicide/crisis operational audit rows={len(rows)} high_fail={len(high_bad)} leaks={len(leak_bad)} claim_0128_fixed={len(claim_0128)} claim_0287_present={len(claim_0287)}')
    return rows

def write_reports(root: Path, rows):
    write_csv_json_md_report(root,'META/Suicide-Crisis-Operational-Boundary-Audit-current.csv',FIELDS,rows,'Suicide/Crisis Operational Boundary Audit','tools/suicide_crisis_operational_boundary_audit.py',columns=['finding_id','finding_type','candidate_id','claim_id','source_id','surface_path','hazard_tokens','claim_status','public_wording_status','public_url_release_decision','severity','status','required_action'],intro_lines=['Audits suicide, lifeline/crisis-line, and postvention candidates for hotline shortcode/contact-digit, service-hours, call-volume/caller-category, method, triage, referral, current-capacity, and case/caller-detail leakage.','This is a release-safety audit, not a help directory. Aggregate office shape can stay in the working cube; public or handoff-facing prose must not become crisis referral, live service capacity, or operational support-path copy.'],max_md_rows=260)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} suicide/crisis operational boundary audit rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r.get('finding_id')} {r.get('claim_id') or r.get('source_id') or r.get('surface_path')}: {r.get('required_action')}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
