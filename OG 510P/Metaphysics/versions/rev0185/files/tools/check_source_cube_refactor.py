#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, collections

def load(p):
    with open(p,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    sources=load(root/'CUBE/observations/sources.yml').get('source_observations', [])
    relations=load(root/'CUBE/observations/source_relations.yml').get('source_relation_observations', [])
    normalized=load(root/'SOURCE_CROSSWALK_NORMALIZED.yml').get('source_crosswalk_entries', [])
    citations=load(root/'SOURCE_CITATION_INDEX.yml').get('citation_rows', [])
    families=load(root/'SOURCE_FAMILY_MAP.yml').get('family_rows', [])
    datasets=[d.get('dataset_id') for d in load(root/'CUBE/datasets.yml').get('datasets', [])]
    if len(normalized) < 100: failures.append(f'normalized crosswalk entries too few: {len(normalized)}')
    if len(citations) < 300: failures.append(f'source citation rows too few: {len(citations)}')
    if len(sources) < len(normalized)+len(citations): failures.append('source observations do not cover normalized crosswalk plus citations')
    if len(relations) < len(sources)*2: failures.append('source relations fewer than two per source row')
    for needed in ['SourceCube','SourceRelationCube','SourceAuditCube']:
        if needed not in datasets: failures.append(f'missing dataset {needed}')
    ids=[r.get('source_observation_id') for r in sources]
    dup=[x for x,c in collections.Counter(ids).items() if c>1]
    if dup: failures.append('duplicate source_observation_id values')
    source_ids=[r.get('source_id') for r in sources]
    if any(not x for x in source_ids): failures.append('source rows with missing source_id')
    if any(not r.get('source_family') or not r.get('claim_boundary') or not r.get('freshness_state') for r in sources): failures.append('source rows missing family/boundary/freshness fields')
    rel_ids=[r.get('source_relation_observation_id') for r in relations]
    if any(not x for x in rel_ids): failures.append('source relation rows with missing IDs')
    srcset=set(source_ids)
    for r in relations:
        if r.get('source_id') not in srcset: failures.append(f'source relation with missing source_id: {r.get("source_id")}')
        if not r.get('relation_type') or not r.get('target_id') or not r.get('claim_boundary'): failures.append('source relation row missing relation_type/target/boundary')
    if len(families) < 5: failures.append('too few source families')
    if failures:
        print('SOURCE CUBE REFACTOR CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('SOURCE CUBE REFACTOR CHECK PASSED')
    print(yaml.safe_dump({'source_observations': len(sources), 'source_relation_observations': len(relations), 'normalized_crosswalk_entries': len(normalized), 'citation_rows': len(citations), 'source_families': len(families), 'status': 'local source-cube structural/refactor check only'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
