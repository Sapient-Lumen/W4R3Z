#!/usr/bin/env python3
"""Generate local concept and concept-relation observations from numbered docs.
This package includes generated outputs already; this script is a reproducible local helper, not an external ontology validator.
"""
from pathlib import Path
import re, yaml, collections, sys
VERSION = Path('VERSION').read_text(encoding='utf-8').strip() if Path('VERSION').exists() else 'rev0182'
# For rev0182 the generated files are committed; run this script from the archive root to inspect counts.
def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}
def main():
    root = Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    concepts = load(root/'CUBE/observations/concepts.yml').get('concept_observations', [])
    relations = load(root/'CUBE/observations/concept_relations.yml').get('concept_relation_observations', [])
    print(yaml.safe_dump({'concept_observations': len(concepts), 'concept_relation_observations': len(relations), 'boundary': 'local committed outputs; generation logic is documented in docs/188'}, sort_keys=False).rstrip())
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
