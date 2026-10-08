#!/usr/bin/env python3
"""Report committed claim observation counts for the local rev0184 ClaimCube refactor.
The generated YAML outputs are committed in the archive; this helper verifies their presence and counts.
"""
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    claims=load(root/'CUBE/observations/claims.yml').get('claim_observations', [])
    relations=load(root/'CUBE/observations/claim_relations.yml').get('claim_relation_observations', [])
    audit=load(root/'CUBE/observations/claim_audit.yml').get('claim_audit_observations', [])
    index=load(root/'CLAIM_OBSERVATION_INDEX.yml').get('claim_observation_index', [])
    print(yaml.safe_dump({'claim_observations': len(claims), 'claim_index_rows': len(index), 'claim_relation_observations': len(relations), 'claim_audit_observations': len(audit), 'boundary': 'local committed outputs; no claim-truth/external-audit validation'}, sort_keys=False).rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
