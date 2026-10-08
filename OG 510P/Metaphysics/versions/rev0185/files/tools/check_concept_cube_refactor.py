#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, re, collections

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    version=(root/'VERSION').read_text(encoding='utf-8').strip()
    concepts=load(root/'CUBE/observations/concepts.yml').get('concept_observations', [])
    relations=load(root/'CUBE/observations/concept_relations.yml').get('concept_relation_observations', [])
    docs=[p for p in (root/'docs').glob('*.md') if re.match(r'^\d+-', p.name)]
    if len(concepts) < len(docs): failures.append(f'concept observations fewer than numbered docs: {len(concepts)} < {len(docs)}')
    ids=[c.get('concept_id') for c in concepts]
    dup=[x for x,c in collections.Counter(ids).items() if c>1]
    if dup: failures.append('duplicate concept_id values: '+', '.join(dup[:20]))
    rowids=[c.get('concept_observation_id') for c in concepts]
    dup_rows=[x for x,c in collections.Counter(rowids).items() if c>1]
    if dup_rows: failures.append('duplicate concept_observation_id values')
    idset=set(ids)
    for c in concepts:
        for field in ['concept_id','canonical_file','family','subfamily','hard_cases','failure_modes','needed_tests','query_boundary']:
            if not c.get(field): failures.append(f'{c.get("concept_id")}: missing {field}')
        if c.get('canonical_file') and not (root/c['canonical_file']).exists(): failures.append(f'{c.get("concept_id")}: canonical file missing {c.get("canonical_file")}')
    if len(relations) < len(concepts): failures.append(f'relation observations fewer than concept observations: {len(relations)} < {len(concepts)}')
    family_prefix='family.'
    for r in relations:
        if not r.get('concept_relation_observation_id') or not r.get('source_concept_id') or not r.get('relation_type') or not r.get('target_concept_id'):
            failures.append('relation row missing required relation fields')
            continue
        if r['source_concept_id'] not in idset: failures.append(f'relation source missing concept: {r["source_concept_id"]}')
        tgt=r['target_concept_id']
        if tgt not in idset and not str(tgt).startswith(family_prefix): failures.append(f'relation target missing concept/family: {tgt}')
    if not any(c.get('concept_id')=='operator.process' for c in concepts): failures.append('operator.process canonical concept missing')
    if not any(r.get('relation_type')=='audits' for r in relations): failures.append('audits relation missing')
    if failures:
        print('CONCEPT CUBE REFACTOR CHECK FAILED')
        for f in failures[:100]: print('-', f)
        return 1
    print('CONCEPT CUBE REFACTOR CHECK PASSED')
    print(yaml.safe_dump({'concept_observations': len(concepts), 'relation_observations': len(relations), 'numbered_docs': len(docs), 'status': 'local structural/concept-routing check only'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
