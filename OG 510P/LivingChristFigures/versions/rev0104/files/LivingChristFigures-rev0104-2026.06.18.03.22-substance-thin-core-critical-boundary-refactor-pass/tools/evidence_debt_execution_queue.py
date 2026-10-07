#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

QUEUE_FIELDS=[
    'execution_id','debt_id','candidate_id','candidate_name','priority','risk_lane','execution_order','target_claim_ids',
    'claim_context','source_need','next_concrete_action','safe_research_mode','forbidden_modes','public_release_dependency',
    'manual_review_trigger','status','note'
]
AUDIT_FIELDS=['audit_id','check','severity','status','subject_id','expected','observed','note']

PRIORITY_ORDER={'critical':0,'high':1,'medium':2,'standard':3}
URL_RE=re.compile(r'https?://|www\.', re.I)
EMAIL_RE=re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)
PHONE_RE=re.compile(r'(?<!\w)(?:\+?\d[\d\s().-]{6,}\d)(?!\w)')


def split(v: str):
    return [x for x in (v or '').split('|') if x]


def write_field_schema(root: Path, rel: str, fields: list[str], meanings: dict[str,str]):
    rows=[]
    for f in fields:
        rows.append({'field':f,'required':'yes','allowed_values_or_pattern':'nonempty text' if f not in {'target_claim_ids','claim_context'} else 'pipe-separated ids or summary text may be blank when no direct claim mapping exists','meaning':meanings.get(f,f)})
    write_csv_json_md_report(root, rel, ['field','required','allowed_values_or_pattern','meaning'], rows, Path(rel).name[:-4].replace('-',' '), 'tools/evidence_debt_execution_queue.py', columns=['field','required','allowed_values_or_pattern','meaning'], max_md_rows=80)


def risk_lane(debt):
    text=' '.join([debt.get('debt_type',''), debt.get('why_it_matters',''), debt.get('safety_constraint',''), debt.get('notes','')]).lower()
    if debt.get('priority')=='critical':
        return 'lane_0_critical_manual_first'
    if any(tok in text for tok in ['case-list','case list','family','child','testimony','image','contact','route','referral','shelter','capacity','hotline','legal','medical','dna']):
        return 'lane_1_high_sensitive_boundary'
    return 'lane_2_high_source_balance_or_claim_support'


def public_dependency(debt, q_by_cand):
    if debt.get('priority')=='critical':
        return 'blocks_public_use_until_resolved_or_requarantined'
    if debt.get('candidate_id') in q_by_cand:
        return 'blocks_or_conditions_public_claims_for_candidate'
    if 'public' in ' '.join([debt.get('why_it_matters',''),debt.get('notes','')]).lower():
        return 'review_before_any_public_wording'
    return 'internal_evidence_quality_before_promotion_or_public_use'


def source_need(debt):
    nxt=debt.get('next_best_source','').strip()
    if not nxt:
        return 'manual_triage_required_no_next_source_recorded'
    return nxt


def run(root: Path):
    debts=read_csv_rows(root/'Evidence-Debt-current.csv')
    candidates={r.get('candidate_id',''):r for r in read_csv_rows(root/'Candidate-Ledger-current.csv')}
    claims=read_csv_rows(root/'Claim-Ledger-current.csv')
    strengths=read_csv_rows(root/'META/Claim-Evidence-Strength-current.csv')
    qrows=read_csv_rows(root/'META/Public-Claim-Quarantine-current.csv')
    sprint_rows=read_csv_rows(root/'META/Evidence-Debt-Sprint-current.csv')
    claims_by_cand={}
    for c in claims:
        claims_by_cand.setdefault(c.get('candidate_id',''), []).append(c)
    strength_by_claim={r.get('claim_id',''):r for r in strengths}
    q_by_cand={}
    for q in qrows:
        q_by_cand.setdefault(q.get('candidate_id',''), []).append(q.get('claim_id',''))

    active=[d for d in debts if d.get('priority') in {'critical','high'}]
    active=sorted(active, key=lambda d:(PRIORITY_ORDER.get(d.get('priority',''),9), d.get('candidate_id',''), d.get('debt_id','')))
    queue=[]
    for idx,d in enumerate(active, start=1):
        cid=d.get('candidate_id','')
        cands=claims_by_cand.get(cid, [])
        direct=[]
        for c in cands:
            blob=' '.join([d.get('debt_type',''), d.get('why_it_matters',''), d.get('notes',''), c.get('claim_type',''), c.get('claim_status',''), c.get('overclaim_risk','')]).lower()
            if c.get('overclaim_risk')=='high' or 'quarantin' in c.get('claim_status','').lower() or c.get('claim_type')=='risk_boundary_or_caution' or len(direct)<3:
                direct.append(c.get('claim_id',''))
        direct=direct[:8]
        context=[]
        for claim_id in direct[:4]:
            sr=strength_by_claim.get(claim_id,{})
            if sr:
                context.append(f"{claim_id}:{sr.get('evidence_strength','')}/{sr.get('refresh_priority','')}")
            else:
                context.append(claim_id)
        lane=risk_lane(d)
        forbidden=d.get('safety_constraint','').strip() or 'no contact/case/referral/route/capacity/testimony/image extraction unless a later governance pass explicitly authorizes it'
        safe='Manual desk review of already-public, high-level, non-operational sources only; preserve aggregate/institutional context and avoid extracting person-level, access-path, live-capacity, contact, route, image, testimony, legal, medical, or referral detail.'
        if 'sensitive_boundary' in lane or d.get('priority')=='critical':
            safe='Manual sensitive-boundary review only; use high-level policy, audit, annual, or governance sources; do not crawl/contact/live-check vulnerable-service or case-near sources.'
        status='ready_for_manual_execution' if d.get('next_best_source') and cid in candidates else 'needs_triage_before_execution'
        queue.append({
            'execution_id':f'exec_debt_{idx:04d}',
            'debt_id':d.get('debt_id',''),
            'candidate_id':cid,
            'candidate_name':d.get('candidate_name') or candidates.get(cid,{}).get('name',''),
            'priority':d.get('priority',''),
            'risk_lane':lane,
            'execution_order':str(idx),
            'target_claim_ids':'|'.join(dict.fromkeys([x for x in direct if x])),
            'claim_context':'|'.join(context),
            'source_need':source_need(d),
            'next_concrete_action':d.get('next_best_source','') or 'Write a narrower next_best_source before research begins.',
            'safe_research_mode':safe,
            'forbidden_modes':forbidden,
            'public_release_dependency':public_dependency(d, q_by_cand),
            'manual_review_trigger':'before_public_wording_or_candidate_promotion' if d.get('priority')=='high' else 'before_any_public_use_or_source_expansion',
            'status':status,
            'note':'Queue row generated from Evidence-Debt-current.csv; internal execution planning only, not permission to publish or contact.',
        })

    audit=[]
    def add(check, sev, status, subject, expected, observed, note):
        audit.append({'audit_id':f'evidence_execution_audit_{len(audit)+1:04d}','check':check,'severity':sev,'status':status,'subject_id':subject,'expected':expected,'observed':observed,'note':note})
    debt_ids={d.get('debt_id','') for d in active}
    queue_ids={q.get('debt_id','') for q in queue}
    missing=sorted(debt_ids-queue_ids)
    extra=sorted(queue_ids-debt_ids)
    add('critical_high_debt_coverage','high' if missing or extra else 'info','fail' if missing or extra else 'pass','Evidence-Debt-current.csv','all critical/high debt_ids exactly once',f'missing={len(missing)} extra={len(extra)}','execution queue must cover every critical/high evidence-debt row and no non-critical spillover')
    critical=[d.get('debt_id','') for d in active if d.get('priority')=='critical']
    critical_q=[q for q in queue if q.get('priority')=='critical']
    add('critical_debt_rows_present','high' if len(critical_q)!=len(critical) else 'info','fail' if len(critical_q)!=len(critical) else 'pass','priority=critical',str(len(critical)),str(len(critical_q)),'critical evidence debts must be visible in the first execution lane')
    order_bad=[q.get('debt_id','') for q in queue if q.get('priority')=='critical' and int(q.get('execution_order','9999'))>len(critical)]
    add('critical_debts_ordered_first','high' if order_bad else 'info','fail' if order_bad else 'pass','execution_order','critical rows first','|'.join(order_bad) if order_bad else 'none','critical evidence debts must not be buried beneath lower-risk rows')
    sprint_ids={r.get('debt_id','') for r in sprint_rows}
    sprint_missing=sorted((sprint_ids & debt_ids)-queue_ids)
    add('sprint_subset_in_execution_queue','high' if sprint_missing else 'info','fail' if sprint_missing else 'pass','META/Evidence-Debt-Sprint-current.csv','all critical/high sprint debts also in full queue',str(len(sprint_missing)),'the old partial sprint surface must be a subset of the complete queue where priorities overlap')
    bad_candidate=[q.get('debt_id','') for q in queue if q.get('candidate_id') not in candidates]
    add('candidate_ids_resolve','high' if bad_candidate else 'info','fail' if bad_candidate else 'pass','candidate_id','all queue candidate ids in Candidate-Ledger',str(len(bad_candidate)),'queue rows must point to existing candidates')
    missing_fields=[]
    for q in queue:
        for field in ['safe_research_mode','forbidden_modes','public_release_dependency','next_concrete_action','source_need','risk_lane']:
            if not q.get(field): missing_fields.append(q.get('debt_id','')+':'+field)
    add('execution_boundaries_present','high' if missing_fields else 'info','fail' if missing_fields else 'pass','queue boundaries','safe mode, forbidden mode, dependency, action, source need, risk lane',str(len(missing_fields)),'every queue row must include action and safety boundaries')
    unsafe=[]
    for q in queue:
        blob=' '.join(q.values())
        if URL_RE.search(blob) or EMAIL_RE.search(blob) or PHONE_RE.search(blob):
            unsafe.append(q.get('debt_id',''))
    add('queue_contains_no_direct_contacts_or_urls','high' if unsafe else 'info','fail' if unsafe else 'pass','queue text','no URLs/emails/contact-number strings',str(len(unsafe)),'execution planning must not smuggle public URLs, contact paths, or phone-like details into the queue')
    bad_status=[q.get('debt_id','')+':'+q.get('status','') for q in queue if q.get('status')!='ready_for_manual_execution']
    add('queue_rows_ready_or_visible_triage','info','pass','queue status',f'{len(queue)} rows classified',f'ready={len(queue)-len(bad_status)} triage={len(bad_status)}','non-ready rows remain visible; none authorize public release')
    high_fail=[r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    add('evidence_debt_execution_audit_summary','info','pass' if not high_fail else 'fail','.',f'queue_rows={len(queue)} high_failures=0',f'queue_rows={len(queue)} high_failures={len(high_fail)}','summary row for release gate')
    return queue, audit


def write_reports(root: Path, queue, audit):
    write_field_schema(root, 'SCHEMA/Evidence-Debt-Execution-Queue-Fields-current.csv', QUEUE_FIELDS, {
        'execution_id':'Stable execution-queue row id for this generated queue.',
        'debt_id':'Evidence-Debt row covered by this execution row.',
        'candidate_id':'Candidate associated with the evidence debt.',
        'candidate_name':'Human-readable candidate name from the debt/candidate ledger.',
        'priority':'Original evidence-debt priority.',
        'risk_lane':'Execution lane derived from priority and sensitive-boundary terms.',
        'execution_order':'Sorted order; critical rows appear first.',
        'target_claim_ids':'Related claim ids for reviewer orientation, not publication.',
        'claim_context':'Compact evidence/refresh context for related claims.',
        'source_need':'Source class or evidence type needed to move the debt.',
        'next_concrete_action':'Manual next action copied/narrowed from the debt row.',
        'safe_research_mode':'Allowed mode for future manual work.',
        'forbidden_modes':'Actions/details that must not be pursued or extracted.',
        'public_release_dependency':'How the debt constrains public wording or promotion.',
        'manual_review_trigger':'When human review is required before any next step.',
        'status':'Execution readiness status; never a release permission.',
        'note':'Clarifying note for handoff reviewers.',
    })
    write_field_schema(root, 'SCHEMA/Evidence-Debt-Execution-Audit-Fields-current.csv', AUDIT_FIELDS, {
        'audit_id':'Stable audit row id.', 'check':'Audit check name.', 'severity':'Finding severity.', 'status':'pass/fail status.', 'subject_id':'Debt id, file, or package subject under test.', 'expected':'Expected condition.', 'observed':'Observed condition.', 'note':'Human-readable explanation.'
    })
    write_csv_json_md_report(root, 'META/Evidence-Debt-Execution-Queue-current.csv', QUEUE_FIELDS, queue, 'Evidence Debt Execution Queue', 'tools/evidence_debt_execution_queue.py', columns=['execution_id','debt_id','candidate_id','priority','risk_lane','execution_order','public_release_dependency','status','next_concrete_action'], intro_lines=[
        f'Queue rows: {len(queue)}',
        'Covers every critical/high Evidence-Debt row. This is internal manual execution planning only; it does not authorize public release, source expansion, contacting, crawling, referral routing, case extraction, images, testimony, or legal/medical guidance.',
    ], max_md_rows=180)
    write_csv_json_md_report(root, 'META/Evidence-Debt-Execution-Audit-current.csv', AUDIT_FIELDS, audit, 'Evidence Debt Execution Audit', 'tools/evidence_debt_execution_queue.py', columns=['check','severity','status','subject_id','expected','observed','note'], intro_lines=[
        f'High failures: {sum(1 for r in audit if r.get("severity")=="high" and r.get("status")!="pass")}',
        'Blocks release if critical/high evidence-debt coverage, ordering, candidate resolution, or safety-boundary constraints fail.',
    ], max_md_rows=120)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); queue,audit=run(root)
    if args.write_report: write_reports(root, queue, audit)
    high=[r for r in audit if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} evidence debt execution queue rows={len(queue)} high_fail={len(high)}")
    for r in high[:20]: print(f"HIGH {r.get('check')} {r.get('subject_id')}: {r.get('observed')}")
    if args.fail_on_high and high: sys.exit(1)
if __name__ == '__main__': main()
