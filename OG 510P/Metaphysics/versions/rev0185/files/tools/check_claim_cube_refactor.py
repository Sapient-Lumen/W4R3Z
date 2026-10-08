#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, collections

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    claims=load(root/'CUBE/observations/claims.yml').get('claim_observations', [])
    index=load(root/'CLAIM_OBSERVATION_INDEX.yml').get('claim_observation_index', [])
    relations=load(root/'CUBE/observations/claim_relations.yml').get('claim_relation_observations', [])
    audit=load(root/'CUBE/observations/claim_audit.yml').get('claim_audit_observations', [])
    datasets=[d.get('dataset_id') for d in load(root/'CUBE/datasets.yml').get('datasets', [])]
    for ds in ['ClaimCube','ClaimRelationCube','ClaimAuditCube']:
        if ds not in datasets: failures.append(f'missing dataset: {ds}')
    if len(claims) != len(index): failures.append(f'claim observation/index mismatch: {len(claims)} vs {len(index)}')
    if len(claims) < 1500: failures.append(f'claim observations too few for rev0184 refactor: {len(claims)}')
    if len(relations) < 40: failures.append(f'claim relations too few: {len(relations)}')
    if len(audit) < 8: failures.append(f'claim audit rows too few: {len(audit)}')
    ids=[r.get('claim_observation_id') for r in claims]
    if len(ids) != len(set(ids)): failures.append('duplicate claim observation IDs')
    rids=[r.get('claim_relation_observation_id') for r in relations]
    if len(rids) != len(set(rids)): failures.append('duplicate claim relation IDs')
    cg=load(root/'CLAIM_GRAPH.yml')
    rel_by_src=collections.defaultdict(list)
    for r in relations: rel_by_src[r.get('source_id')].append(r)
    for node in cg.get('claim_nodes', []) or []:
        cid=node.get('claim_id')
        if not cid: continue
        kinds={r.get('relation_type') for r in rel_by_src.get(cid, [])}
        if 'supported_by_evidence_packet' not in kinds and 'has_supporting_evidence_packet' not in kinds:
            failures.append(f'claim node {cid} lacks evidence-packet relation')
        if not any('contradiction' in k for k in kinds):
            failures.append(f'claim node {cid} lacks contradiction relation')
        if not any('defeated_by' in k for k in kinds):
            failures.append(f'claim node {cid} lacks defeasance relation')
    for rel in ['CLAIM_OBSERVATION_INDEX.yml','CLAIM_RELATION_MAP.yml','CLAIM_AUDIT_LEDGER.yml','CUBE/observations/claim_relations.yml','CUBE/observations/claim_audit.yml']:
        if not (root/rel).exists(): failures.append(f'missing claim refactor artifact: {rel}')
    if failures:
        print('CLAIM CUBE REFACTOR CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('CLAIM CUBE REFACTOR CHECK PASSED')
    print(yaml.safe_dump({'claim_observations': len(claims), 'claim_relation_observations': len(relations), 'claim_audit_observations': len(audit), 'claim_graph_nodes': len(cg.get('claim_nodes', []) or []), 'status': 'local claim-cube structural/refactor check only'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
