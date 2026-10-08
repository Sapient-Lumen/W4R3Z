#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def exists(root, rel): return (root/rel).exists()

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    version=(root/'VERSION').read_text(encoding='utf-8').strip()
    graph=load(root/'CLAIM_GRAPH.yml'); evidence=load(root/'EVIDENCE_PACKET_INDEX.yml'); contr=load(root/'CONTRADICTION_LEDGER.yml'); fresh=load(root/'FRESHNESS_POLICY.yml'); defeas=load(root/'DEFEASANCE_PROPAGATION.yml')
    failures=[]
    claims=graph.get('claim_nodes',[]); claim_ids=[c.get('claim_id') for c in claims]
    if len(claim_ids)!=len(set(claim_ids)): failures.append({'claim_graph':'duplicate claim_id'})
    packets=evidence.get('packets',[]); packet_ids=[p.get('packet_id') for p in packets]
    if len(packet_ids)!=len(set(packet_ids)): failures.append({'evidence':'duplicate packet_id'})
    freshness_ids={p.get('freshness_id') for p in fresh.get('freshness_policies',[])}
    contradiction_ids={c.get('contradiction_id') for c in contr.get('contradictions',[])}
    defeasance_ids={r.get('defeasance_id') for r in defeas.get('rules',[])}
    claim_set=set(claim_ids); packet_set=set(packet_ids)
    for c in claims:
        cid=c.get('claim_id')
        for ep in c.get('evidence_packets',[]) or []:
            if ep not in packet_set: failures.append({'claim_id':cid,'missing_evidence_packet':ep})
        for rel in c.get('source_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'claim_id':cid,'missing_source_artifact':rel})
        if c.get('freshness_policy') not in freshness_ids: failures.append({'claim_id':cid,'missing_freshness_policy':c.get('freshness_policy')})
        if c.get('contradiction_state') not in contradiction_ids: failures.append({'claim_id':cid,'missing_contradiction_state':c.get('contradiction_state')})
        if c.get('defeasance_profile') not in defeasance_ids: failures.append({'claim_id':cid,'missing_defeasance_profile':c.get('defeasance_profile')})
    for e in graph.get('edges',[]) or []:
        for k in ['subject_claim','object_claim']:
            if e.get(k) not in claim_set: failures.append({'edge_id':e.get('edge_id'),'missing_'+k:e.get(k)})
    for p in packets:
        pid=p.get('packet_id')
        for k in ['supports_claims','constrains_claims']:
            for cid in p.get(k,[]) or []:
                if cid not in claim_set: failures.append({'packet_id':pid,'missing_'+k:cid})
        for rel in p.get('source_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'packet_id':pid,'missing_source_artifact':rel})
        if p.get('freshness_policy') not in freshness_ids: failures.append({'packet_id':pid,'missing_freshness_policy':p.get('freshness_policy')})
    for c in contr.get('contradictions',[]) or []:
        if c.get('claim_id') not in claim_set: failures.append({'contradiction_id':c.get('contradiction_id'),'missing_claim_id':c.get('claim_id')})
        if not c.get('disposition'): failures.append({'contradiction_id':c.get('contradiction_id'),'missing_disposition':True})
    for r in defeas.get('rules',[]) or []:
        for k in ['defeated_claims','propagate_to']:
            for cid in r.get(k,[]) or []:
                if cid not in claim_set: failures.append({'defeasance_id':r.get('defeasance_id'),'missing_'+k:cid})
        if not r.get('required_action'): failures.append({'defeasance_id':r.get('defeasance_id'),'missing_required_action':True})
    summary={'claim_nodes':len(claims),'edges':len(graph.get('edges',[]) or []),'evidence_packets':len(packets),'contradictions':len(contr.get('contradictions',[]) or []),'freshness_policies':len(fresh.get('freshness_policies',[]) or []),'defeasance_rules':len(defeas.get('rules',[]) or []),'failures':len(failures)}
    reports={
      'claim_graph_report': {'claim_graph_report_version':f'{version}-claim-graph-report-v1','archive_version':version,'status':'CG5_claim_graph_report_passed' if not failures else 'CG7_unsafe_claim_graph_claim','summary':summary,'failures':failures},
      'evidence_packet_report': {'evidence_packet_report_version':f'{version}-evidence-packet-report-v1','archive_version':version,'status':'EVP5_evidence_packet_report_passed' if not failures else 'EVP7_unsafe_evidence_packet_claim','summary':summary,'failures':failures},
      'contradiction_report': {'contradiction_report_version':f'{version}-contradiction-report-v1','archive_version':version,'status':'CTR5_contradiction_report_passed' if not failures else 'CTR7_unsafe_contradiction_claim','summary':summary,'failures':failures},
      'freshness_report': {'freshness_report_version':f'{version}-freshness-report-v1','archive_version':version,'status':'FRS5_freshness_report_passed' if not failures else 'FRS7_unsafe_freshness_claim','summary':summary,'failures':failures},
      'defeasance_report': {'defeasance_report_version':f'{version}-defeasance-report-v1','archive_version':version,'status':'DFP5_defeasance_report_passed' if not failures else 'DFP7_unsafe_defeasance_claim','summary':summary,'failures':failures}
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__=='__main__': raise SystemExit(main())
