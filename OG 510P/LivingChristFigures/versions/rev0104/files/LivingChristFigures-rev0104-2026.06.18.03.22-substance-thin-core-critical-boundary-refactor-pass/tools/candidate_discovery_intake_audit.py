#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

AUDIT_FIELDS=['audit_id','check','discovery_id','candidate_id','severity','status','detail','recommendation']
ALLOWED_STATUS={'promoted_to_candidate','parked_related_candidate','not_promoted_context_source','rejected_duplicate','rejected_boundary_risk'}
NO_PUBLIC_ACTIONS={'no_public_expansion','no_public_expansion_boundary_index_only','boundary_index_shape_only'}

def split(v: str): return [x for x in (v or '').split('|') if x]

def run(root: Path):
    rows=read_csv_rows(root/'META/Candidate-Discovery-Log-current.csv')
    try:
        manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    except Exception:
        manifest={}
    current_rev=str(manifest.get('revision',''))
    cand_rows=read_csv_rows(root/'Candidate-Ledger-current.csv')
    cand_ids={r.get('candidate_id','') for r in cand_rows}
    cand_file_by_id={r.get('candidate_id',''): r.get('file_path','') for r in cand_rows}
    source_ids={r.get('source_id','') for r in read_csv_rows(root/'Source-Registry-current.csv')}
    office_ids={r.get('office_id','') for r in read_csv_rows(root/'Office-Card-Index-current.csv')}
    claim_rows=read_csv_rows(root/'Claim-Ledger-current.csv')
    claim_ids_by_candidate={}
    high_claim_ids_by_candidate={}
    for cr in claim_rows:
        claim_ids_by_candidate.setdefault(cr.get('candidate_id',''), set()).add(cr.get('claim_id',''))
        if cr.get('overclaim_risk')=='high' or 'quarantin' in (cr.get('claim_status','') or '').lower() or cr.get('claim_type')=='risk_boundary_or_caution':
            high_claim_ids_by_candidate.setdefault(cr.get('candidate_id',''), set()).add(cr.get('claim_id',''))
    debt_ids={r.get('candidate_id','') for r in read_csv_rows(root/'Evidence-Debt-current.csv')}
    permission_ids={r.get('candidate_id','') for r in read_csv_rows(root/'GOVERNANCE/Permission-State-Ledger-current.csv')}
    family_governance_ids={r.get('candidate_id','') for r in read_csv_rows(root/'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv')}
    acct_pairs={(r.get('candidate_id',''), r.get('office_id','')) for r in read_csv_rows(root/'META/Office-Accountability-current.csv')}
    quarantine_claim_ids={r.get('claim_id','') for r in read_csv_rows(root/'META/Public-Claim-Quarantine-current.csv')}
    strength_controlled_claim_ids=set(quarantine_claim_ids)
    for sr in read_csv_rows(root/'META/Claim-Evidence-Strength-current.csv'):
        cid0=sr.get('claim_id','')
        if (sr.get('public_release_dependency','') or '').lower()=='true' or sr.get('refresh_priority','') in {'now_or_before_any_public_claim','soon_keep_near_claim'}:
            strength_controlled_claim_ids.add(cid0)
    audit=[]
    def add(check,did,cid,severity,status,detail,rec):
        audit.append({'audit_id':f'candidate_discovery_audit_{len(audit)+1:04d}','check':check,'discovery_id':did,'candidate_id':cid,'severity':severity,'status':status,'detail':detail,'recommendation':rec})
    if not rows:
        add('discovery_log_present','','','high','fail','Candidate-Discovery-Log has no rows','record at least one candidate discovery/intake decision per candidate-discovery pass')
        return audit
    add('discovery_log_present','','','info','pass',f'{len(rows)} discovery row(s) present','keep discovery attempts visible even when not promoted')
    current_rows=[r for r in rows if current_rev and r.get('revision')==current_rev]
    if not current_rev:
        add('current_revision_known','','','high','fail','manifest revision missing or unreadable','candidate-discovery audit must know the current manifest revision')
    else:
        add('current_revision_known','','','info','pass',current_rev,'manifest revision is readable')
        add('current_revision_attempt_present','','','info' if current_rows else 'high','pass' if current_rows else 'fail',f'{len(current_rows)} discovery row(s) for {current_rev}','record at least one discovery attempt for the current release; stale attempts cannot satisfy the ongoing discovery obligation')
    promoted=0
    for r in rows:
        did=r.get('discovery_id',''); cid=r.get('proposed_candidate_id',''); status=r.get('discovery_status',''); decision=r.get('decision','')
        if status not in ALLOWED_STATUS:
            add('discovery_status_controlled',did,cid,'high','fail',f'unknown discovery_status={status!r}','use controlled discovery_status vocabulary')
        else:
            add('discovery_status_controlled',did,cid,'info','pass',status,'status uses controlled vocabulary')
        if not r.get('boundary_flags'):
            add('boundary_flags_present',did,cid,'high','fail','boundary_flags blank','record public-boundary hazards for every discovery decision')
        else:
            add('boundary_flags_present',did,cid,'info','pass',r.get('boundary_flags',''),'keep boundary discovery explicit')
        if r.get('public_layer_action') not in NO_PUBLIC_ACTIONS:
            add('public_layer_action_closed',did,cid,'high','fail',f'public_layer_action={r.get("public_layer_action")!r}','candidate discovery must not itself authorize public expansion')
        else:
            add('public_layer_action_closed',did,cid,'info','pass',r.get('public_layer_action',''),'public layer remains closed')
        for oid in split(r.get('office_ids','')):
            add('office_id_defined',did,cid,'high' if oid not in office_ids else 'info','fail' if oid not in office_ids else 'pass',oid,'define office id before promotion or mark as proposed-only outside office_ids field')
        for sid in split(r.get('source_ids','')):
            add('source_id_defined',did,cid,'high' if sid not in source_ids else 'info','fail' if sid not in source_ids else 'pass',sid,'source ids in discovery log must resolve to Source Registry when declared')
        if status=='promoted_to_candidate':
            promoted += 1
            if cid not in cand_ids:
                add('promoted_candidate_exists',did,cid,'high','fail','promoted candidate id is absent from Candidate-Ledger','add candidate ledger row or change discovery status')
            else:
                add('promoted_candidate_exists',did,cid,'info','pass','promoted candidate exists in Candidate-Ledger','keep discovery log and candidate ledger synchronized')
            if not split(r.get('source_ids','')):
                add('promoted_candidate_has_sources',did,cid,'high','fail','promoted candidate row has no source_ids','record source ids for promoted candidates')
            else:
                add('promoted_candidate_has_sources',did,cid,'info','pass',f'{len(split(r.get("source_ids","")))} source id(s)','keep promoted candidate source trail explicit')
            candidate_file=cand_file_by_id.get(cid,'')
            if not candidate_file or not (root/candidate_file).exists():
                add('promoted_candidate_file_exists',did,cid,'high','fail',candidate_file or 'blank file_path','candidate ledger must point to an existing candidate file before promotion')
            else:
                add('promoted_candidate_file_exists',did,cid,'info','pass',candidate_file,'candidate file exists')
            claim_count=len(claim_ids_by_candidate.get(cid,set()))
            add('promoted_candidate_claim_coverage',did,cid,'info' if claim_count>=2 else 'high','pass' if claim_count>=2 else 'fail',f'{claim_count} claim row(s)','promoted candidates need at least two claim rows: work-shape plus boundary/interpretive context')
            add('promoted_candidate_evidence_debt',did,cid,'info' if cid in debt_ids else 'high','pass' if cid in debt_ids else 'fail','evidence debt present' if cid in debt_ids else 'missing evidence debt','record at least one evidence-debt row for promoted candidates')
            add('promoted_candidate_permission_state',did,cid,'info' if cid in permission_ids else 'high','pass' if cid in permission_ids else 'fail','permission state present' if cid in permission_ids else 'missing permission state','record permission-state row before promotion handoff')
            missing_acct=[oid for oid in split(r.get('office_ids','')) if (cid, oid) not in acct_pairs]
            add('promoted_candidate_office_accountability',did,cid,'info' if not missing_acct else 'high','pass' if not missing_acct else 'fail','all office accountability pairs present' if not missing_acct else 'missing: '+ '|'.join(missing_acct),'each promoted candidate/office pair needs an accountability row')
            harm_text='|'.join([r.get('boundary_flags',''), cand_file_by_id.get(cid,''), ' '.join(sorted(high_claim_ids_by_candidate.get(cid,set())))])
            needs_family=any(token in harm_text for token in ['case','family','child','testimony','dna','image','names'])
            if needs_family:
                add('promoted_candidate_family_case_governance',did,cid,'info' if cid in family_governance_ids else 'high','pass' if cid in family_governance_ids else 'fail','family/case governance present' if cid in family_governance_ids else 'missing family/case governance row','harm-near promoted candidates need family/case-name-use governance')
            high_claims=high_claim_ids_by_candidate.get(cid,set())
            if high_claims:
                missing_q=sorted(high_claims-strength_controlled_claim_ids)
                add('promoted_candidate_high_claim_release_control',did,cid,'info' if not missing_q else 'high','pass' if not missing_q else 'fail','high/boundary claims have quarantine or release-dependency control' if not missing_q else 'not release-controlled: '+ '|'.join(missing_q),'run evidence_lifecycle and keep high-risk claims either in Public-Claim-Quarantine or in explicit public-release-dependency/refresh-priority control')
        if status!='promoted_to_candidate' and cid in cand_ids:
            add('nonpromoted_not_in_candidate_ledger',did,cid,'medium','fail','non-promoted discovery id already exists in Candidate-Ledger','either promote explicitly or rename/remove from candidate ledger')
    add('at_least_one_promoted_or_documented_attempt','','','info' if promoted or rows else 'high','pass' if promoted or rows else 'fail',f'promoted={promoted}; attempts={len(rows)}','future turns should record at least one discovery attempt; promotion is not required when unsafe/duplicate')
    return audit

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root, 'META/Candidate-Discovery-Intake-Audit-current.csv', AUDIT_FIELDS, rows, 'Candidate Discovery Intake Audit', 'tools/candidate_discovery_intake_audit.py', intro_lines=['Validates that discovery attempts, promoted candidates, source ids, office ids, public-layer closure, and promotion-completeness coverage are explicit.'])
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    for r in rows: print(f"{r.get('status','').upper()} {r.get('severity')} {r.get('check')} {r.get('discovery_id')} {r.get('detail')}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
