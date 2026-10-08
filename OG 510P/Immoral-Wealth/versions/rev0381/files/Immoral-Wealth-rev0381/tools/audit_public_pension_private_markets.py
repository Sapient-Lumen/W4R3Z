#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[1]
CASE = 'us-state-local-public-pension-risk-rev0318'
REV = 'rev0368'
ledger = json.loads((ROOT/'cases/VERIFIED_CLAIM_EDGE_LEDGER.json').read_text())
edges = [e for e in ledger.get('verified_claim_edges', []) if e.get('case_id') == CASE]
new_edges = [e for e in edges if e.get('created_revision') == REV]
problems = []
required_sources = {'S454','S570','S571','S572','S573'}
seen = set()
for e in new_edges:
    seen.update(e.get('source_ids') or [])
    for k in ['verified_claim_edge_id','claim_atom_id','bounded_claim','relationship_code','exact_locator','does_not_prove','reversal_rule']:
        if not e.get(k): problems.append(f"missing {k} in {e.get('verified_claim_edge_id')}")
if len(new_edges) < 16: problems.append(f'expected at least 16 rev0368 public-pension edges, found {len(new_edges)}')
missing = required_sources - seen
if missing: problems.append(f'missing source coverage: {sorted(missing)}')
score = json.loads((ROOT/f'cases/{CASE}-scoreboard.json').read_text())
if ((score.get('gate_20_subgates') or {}).get('20E_public_upside_recovery') or {}).get('status') != 'watch': problems.append('20E public-upside recovery must be watch')
print(json.dumps({'revision_current':REV,'case_id':CASE,'new_edge_count':len(new_edges),'total_case_edges':len(edges),'sources_seen':sorted(seen),'problem_count':len(problems),'problems':problems}, indent=2))
if problems: sys.exit(1)
