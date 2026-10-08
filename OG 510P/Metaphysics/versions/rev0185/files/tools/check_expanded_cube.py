#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

REQUIRED = [
    'CUBE/datasets.yml','CUBE/dimensions.yml','CUBE/measures.yml','CUBE/attributes.yml',
    'CUBE/observations/artifacts.yml','CUBE/observations/claims.yml','CUBE/observations/claim_relations.yml','CUBE/observations/claim_audit.yml','CUBE/observations/debts.yml','CUBE/observations/debt_relations.yml','CUBE/observations/debt_audit.yml',
    'CUBE/observations/controls.yml','CUBE/observations/sources.yml','CUBE/observations/source_relations.yml','CUBE/observations/source_audit.yml',
    'CUBE/observations/access.yml','CUBE/observations/concepts.yml','CUBE/observations/concept_relations.yml','CUBE/observations/cube_audit.yml'
]

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    failures=[]
    for rel in REQUIRED:
        if not (root/rel).exists(): failures.append(f'missing expanded cube artifact: {rel}')
    if failures:
        print('EXPANDED CUBE CHECK FAILED')
        for f in failures: print('-', f)
        return 1
    datasets=load(root/'CUBE/datasets.yml').get('datasets', [])
    dataset_ids=[d.get('dataset_id') for d in datasets]
    needed=['ArtifactCube','ClaimCube','ClaimRelationCube','ClaimAuditCube','DebtCube','DebtRelationCube','DebtAuditCube','ControlCube','SourceCube','SourceRelationCube','SourceAuditCube','AccessCube','ConceptCube','ConceptRelationCube','CubeAuditCube']
    for n in needed:
        if n not in dataset_ids: failures.append(f'missing dataset: {n}')
    debt_rows=load(root/'CUBE/observations/debts.yml').get('debt_observations', [])
    debt_rel_rows=load(root/'CUBE/observations/debt_relations.yml').get('debt_relation_observations', [])
    debt_audit_rows=load(root/'CUBE/observations/debt_audit.yml').get('debt_audit_observations', [])
    source_rows=load(root/'CUBE/observations/sources.yml').get('source_observations', [])
    source_rel_rows=load(root/'CUBE/observations/source_relations.yml').get('source_relation_observations', [])
    source_audit_rows=load(root/'CUBE/observations/source_audit.yml').get('source_audit_observations', [])
    claim_rows=load(root/'CUBE/observations/claims.yml').get('claim_observations', [])
    claim_rel_rows=load(root/'CUBE/observations/claim_relations.yml').get('claim_relation_observations', [])
    claim_audit_rows=load(root/'CUBE/observations/claim_audit.yml').get('claim_audit_observations', [])
    concept_rows=load(root/'CUBE/observations/concepts.yml').get('concept_observations', [])
    relation_rows=load(root/'CUBE/observations/concept_relations.yml').get('concept_relation_observations', [])
    audit_rows=load(root/'CUBE/observations/cube_audit.yml').get('cube_audit_observations', [])
    if len(debt_rows) < 800: failures.append('debt observations too few for debt refactor')
    if len(debt_rel_rows) < len(debt_rows)*5: failures.append('debt relation observations fewer than expected')
    if len(debt_audit_rows) < 8: failures.append('debt audit observations too few')
    if len(source_rows) < 400: failures.append('source observations too few for source refactor')
    if len(source_rel_rows) < len(source_rows)*2: failures.append('source relation observations fewer than expected')
    if len(source_audit_rows) < 5: failures.append('source audit observations too few')
    if len(claim_rows) < 1500: failures.append('claim observations too few for claim refactor')
    if len(claim_rel_rows) < 40: failures.append('claim relation observations too few')
    if len(claim_audit_rows) < 8: failures.append('claim audit observations too few')
    if len(concept_rows) < 190: failures.append('concept observations too few')
    if len(relation_rows) < len(concept_rows): failures.append('concept relation observations fewer than concept rows')
    if len(audit_rows) < len(datasets): failures.append('cube audit observations fewer than dataset rows')
    cube=load(root/'CUBE_INDEX.yml'); exp=cube.get('expanded_dataset_index') or []
    for rel in REQUIRED[4:]:
        if rel not in exp: failures.append(f'CUBE_INDEX expanded_dataset_index missing {rel}')
    if failures:
        print('EXPANDED CUBE CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('EXPANDED CUBE CHECK PASSED')
    print(yaml.safe_dump({'datasets': len(datasets), 'debt_observations': len(debt_rows), 'debt_relation_observations': len(debt_rel_rows), 'debt_audit_observations': len(debt_audit_rows), 'source_observations': len(source_rows), 'source_relation_observations': len(source_rel_rows), 'source_audit_observations': len(source_audit_rows), 'claim_observations': len(claim_rows), 'claim_relation_observations': len(claim_rel_rows), 'claim_audit_observations': len(claim_audit_rows), 'concept_observations': len(concept_rows), 'concept_relation_observations': len(relation_rows), 'cube_audit_observations': len(audit_rows)}, sort_keys=False).rstrip())
    return 0
if __name__ == '__main__': raise SystemExit(main())
