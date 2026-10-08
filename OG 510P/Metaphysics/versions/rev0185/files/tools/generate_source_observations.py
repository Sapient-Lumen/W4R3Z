#!/usr/bin/env python3
"""Report committed source observation counts for the local rev0184 SourceCube refactor.
The generated YAML outputs are committed in the archive; this helper verifies their presence and counts.
"""
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    sources=load(root/'CUBE/observations/sources.yml').get('source_observations', [])
    relations=load(root/'CUBE/observations/source_relations.yml').get('source_relation_observations', [])
    audit=load(root/'CUBE/observations/source_audit.yml').get('source_audit_observations', [])
    citations=load(root/'SOURCE_CITATION_INDEX.yml').get('citation_rows', [])
    normalized=load(root/'SOURCE_CROSSWALK_NORMALIZED.yml').get('source_crosswalk_entries', [])
    print(yaml.safe_dump({'source_observations': len(sources), 'source_relation_observations': len(relations), 'source_audit_observations': len(audit), 'normalized_crosswalk_entries': len(normalized), 'citation_rows': len(citations), 'boundary': 'local committed outputs; no live URL/source-currentness validation'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
