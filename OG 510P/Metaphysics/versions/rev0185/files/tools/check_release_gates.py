#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    version=(root/'VERSION').read_text(encoding='utf-8').strip()
    gp=load(root/'RELEASE_GATE_POLICY.yml'); ac=load(root/'ACCEPTANCE_CRITERIA_MATRIX.yml'); dec=load(root/'RELEASE_DECISION_LEDGER.yml'); wv=load(root/'WAIVER_EXCEPTION_LEDGER.yml'); ra=load(root/'RISK_ACCEPTANCE_LEDGER.yml'); asc=load(root/'ASSURANCE_CASE_SKELETON.yml')
    failures=[]
    gates=gp.get('gates',[]) or []; criteria=ac.get('criteria',[]) or []; decisions=dec.get('decisions',[]) or []; waivers=wv.get('waivers',[]) or []; risks=ra.get('risk_acceptances',[]) or []; claims=asc.get('top_claims',[]) or []; args=asc.get('arguments',[]) or []
    gate_ids=[g.get('gate_id') for g in gates]; gate_set=set(gate_ids)
    crit_ids=[c.get('criterion_id') for c in criteria]; crit_set=set(crit_ids)
    dec_ids=[d.get('decision_id') for d in decisions]; dec_set=set(dec_ids)
    waiver_ids=[w.get('waiver_id') for w in waivers]; waiver_set=set(waiver_ids)
    risk_ids=[r.get('risk_acceptance_id') for r in risks]; risk_set=set(risk_ids)
    claim_ids=[c.get('assurance_claim_id') for c in claims]; claim_set=set(claim_ids)
    if len(gate_ids)!=len(gate_set): failures.append({'release_gates':'duplicate gate_id'})
    if len(crit_ids)!=len(crit_set): failures.append({'acceptance':'duplicate criterion_id'})
    if len(dec_ids)!=len(dec_set): failures.append({'decisions':'duplicate decision_id'})
    if len(waiver_ids)!=len(waiver_set): failures.append({'waivers':'duplicate waiver_id'})
    if len(risk_ids)!=len(risk_set): failures.append({'risk_acceptance':'duplicate risk_acceptance_id'})
    for g in gates:
        gid=g.get('gate_id')
        for rel in (g.get('required_artifacts') or []) + (g.get('required_tools') or []) + (g.get('evidence_artifacts') or []):
            if not (root/rel).exists(): failures.append({'gate_id':gid,'missing_artifact':rel})
        for cid in g.get('acceptance_criteria') or []:
            if cid not in crit_set: failures.append({'gate_id':gid,'missing_acceptance_criterion':cid})
        if g.get('decision_record') not in dec_set: failures.append({'gate_id':gid,'missing_decision_record':g.get('decision_record')})
        if g.get('gate_class')=='blocking' and 'GTE4' not in str(g.get('status','')): failures.append({'gate_id':gid,'blocking_gate_not_passed':g.get('status')})
    for c in criteria:
        cid=c.get('criterion_id'); gid=c.get('gate_id')
        if gid not in gate_set: failures.append({'criterion_id':cid,'missing_gate_id':gid})
        for rel in c.get('required_evidence_artifacts') or []:
            if not (root/rel).exists(): failures.append({'criterion_id':cid,'missing_evidence_artifact':rel})
        chk=c.get('required_check')
        if chk and not (root/chk).exists(): failures.append({'criterion_id':cid,'missing_required_check':chk})
        if c.get('blocking') and 'ACC4' not in str(c.get('acceptance_status','')): failures.append({'criterion_id':cid,'blocking_criterion_not_satisfied':c.get('acceptance_status')})
    active=[w for w in waivers if 'active' in str(w.get('waiver_state','')).lower() and 'no_active' not in str(w.get('waiver_state','')).lower()]
    if int(wv.get('active_waiver_count',0)) != len(active): failures.append({'waiver_ledger':'active_waiver_count_mismatch','declared':wv.get('active_waiver_count'),'actual':len(active)})
    for w in waivers:
        wid=w.get('waiver_id'); tg=w.get('target_gate')
        if tg not in (None,'none') and tg not in gate_set: failures.append({'waiver_id':wid,'missing_target_gate':tg})
        rr=w.get('risk_acceptance_ref')
        if rr and rr not in risk_set: failures.append({'waiver_id':wid,'missing_risk_acceptance_ref':rr})
        dr=w.get('decision_ref')
        if dr and dr not in dec_set: failures.append({'waiver_id':wid,'missing_decision_ref':dr})
    for r in risks:
        rid=r.get('risk_acceptance_id')
        if r.get('decision_id') not in dec_set: failures.append({'risk_acceptance_id':rid,'missing_decision_id':r.get('decision_id')})
        if 'RAC4' not in str(r.get('acceptance_status','')): failures.append({'risk_acceptance_id':rid,'operational_risk_boundary_not_recorded':r.get('acceptance_status')})
        if any('operational' in str(x).lower() and 'not' not in str(x).lower() for x in r.get('accepted_residual_risks',[]) or []): failures.append({'risk_acceptance_id':rid,'accepted_operational_risk_detected':True})
    for d in decisions:
        did=d.get('decision_id')
        seen=[]
        for gr in d.get('gate_results') or []:
            gid=gr.get('gate_id'); seen.append(gid)
            if gid not in gate_set: failures.append({'decision_id':did,'missing_gate_result_ref':gid})
            if gr.get('result')=='fail' and 'DEC4' in str(d.get('decision_status','')): failures.append({'decision_id':did,'failed_gate_allowed_release':gid})
        for wr in d.get('waiver_refs') or []:
            if wr not in waiver_set: failures.append({'decision_id':did,'missing_waiver_ref':wr})
        for rr in d.get('risk_acceptance_refs') or []:
            if rr not in risk_set: failures.append({'decision_id':did,'missing_risk_ref':rr})
        for ar in d.get('assurance_case_refs') or []:
            if ar not in claim_set: failures.append({'decision_id':did,'missing_assurance_ref':ar})
        if not set(gate_ids).issubset(set(seen)): failures.append({'decision_id':did,'gate_results_incomplete':sorted(set(gate_ids)-set(seen))})
    for c in claims:
        cid=c.get('assurance_claim_id')
        if c.get('related_decision') not in dec_set: failures.append({'assurance_claim_id':cid,'missing_related_decision':c.get('related_decision')})
        for a in c.get('supported_by_arguments') or []:
            if a not in {x.get('argument_id') for x in args}: failures.append({'assurance_claim_id':cid,'missing_argument':a})
        for rel in c.get('evidence_artifacts') or []:
            if not (root/rel).exists(): failures.append({'assurance_claim_id':cid,'missing_evidence_artifact':rel})
    for a in args:
        aid=a.get('argument_id')
        if a.get('supports_claim') not in claim_set: failures.append({'argument_id':aid,'missing_supports_claim':a.get('supports_claim')})
        for gid in a.get('gate_refs') or []:
            if gid not in gate_set: failures.append({'argument_id':aid,'missing_gate_ref':gid})
        for rel in a.get('evidence_refs') or []:
            if not (root/rel).exists(): failures.append({'argument_id':aid,'missing_evidence_ref':rel})
    summary={'gates':len(gates),'blocking_gates':sum(1 for g in gates if g.get('gate_class')=='blocking'),'criteria':len(criteria),'decisions':len(decisions),'waivers':len(waivers),'active_waivers':len(active),'risk_acceptances':len(risks),'assurance_claims':len(claims),'arguments':len(args),'failures':len(failures)}
    reports={
      'release_gate_report': {'release_gate_report_version':f'{version}-release-gate-report-v1','archive_version':version,'status':'GTE4_all_blocking_gates_passed' if not failures else 'GTE7_unsafe_gate_claim','summary':summary,'failures':failures},
      'acceptance_criteria_report': {'acceptance_criteria_report_version':f'{version}-acceptance-criteria-report-v1','archive_version':version,'status':'ACC4_acceptance_criteria_satisfied' if not failures else 'ACC7_unsafe_acceptance_claim','summary':summary,'failures':failures},
      'release_decision_report': {'release_decision_report_version':f'{version}-release-decision-report-v1','archive_version':version,'status':'DEC4_release_allowed_with_local_gate_pass' if not failures else 'DEC7_unsafe_decision_claim','summary':summary,'failures':failures},
      'waiver_exception_report': {'waiver_exception_report_version':f'{version}-waiver-exception-report-v1','archive_version':version,'status':'WVR4_no_active_waiver_used' if not failures and not active else 'WVR7_unsafe_waiver_claim','summary':summary,'failures':failures},
      'risk_acceptance_report': {'risk_acceptance_report_version':f'{version}-risk-acceptance-report-v1','archive_version':version,'status':'RAC3_local_residual_risk_accepted_with_boundaries; RAC4_operational_risk_not_accepted' if not failures else 'RAC7_unsafe_risk_acceptance_claim','summary':summary,'failures':failures},
      'assurance_case_report': {'assurance_case_report_version':f'{version}-assurance-case-report-v1','archive_version':version,'status':'ASC4_assurance_case_skeleton_checked' if not failures else 'ASC7_unsafe_assurance_claim','summary':summary,'failures':failures}
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__=='__main__': raise SystemExit(main())
