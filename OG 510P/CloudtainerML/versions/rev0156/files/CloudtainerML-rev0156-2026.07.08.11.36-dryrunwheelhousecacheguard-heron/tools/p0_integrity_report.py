#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision','rev0000'); REVUP=REV.upper()
AUDIT_DIR = ROOT/'artifacts'/'audit'; AUDIT_DIR.mkdir(parents=True, exist_ok=True)

def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def cell_note_exists(cell_id: str) -> bool:
    n = int(cell_id.split('-')[1])
    return any((ROOT/'docs'/'02-experiment-cells').glob(f'cell-{n:03d}*.md'))
def main() -> int:
    sources = {s['id']:s for s in load('RESEARCH-SOURCE-REGISTRY.json')['sources']}
    ideas = {i['id']:i for i in load('IDEA-LEDGER.json')['ideas']}
    cells = {c['cell_id']:c for c in load('EXPERIMENT-MATRIX.json')['cells']}
    p0_sources=[s for s in sources.values() if s.get('priority')=='P0']
    p0_ideas=[i for i in ideas.values() if i.get('priority')=='P0']
    p0_cells=[c for c in cells.values() if c.get('priority')=='P0']
    issues=[]
    for i in p0_ideas:
        missing=[sid for sid in i.get('source_ids',[]) if sid not in sources]
        if missing: issues.append({'kind':'idea_missing_sources','id':i['id'],'missing':missing})
        bound=[c['cell_id'] for c in cells.values() if c.get('idea_id')==i['id']]
        if not bound: issues.append({'kind':'p0_idea_without_cell','id':i['id']})
    for c in p0_cells:
        if c.get('idea_id') not in ideas: issues.append({'kind':'cell_missing_idea','id':c['cell_id'],'idea_id':c.get('idea_id')})
        missing=[sid for sid in c.get('source_ids',[]) if sid not in sources]
        if missing: issues.append({'kind':'cell_missing_sources','id':c['cell_id'],'missing':missing})
        if not cell_note_exists(c['cell_id']): issues.append({'kind':'cell_missing_note','id':c['cell_id']})
    # Implemented native P0s should have a current smoke output whose probe name is at least plausibly associated.
    current_outputs = sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*_SMOKE.json'))
    current_names = {p.name for p in current_outputs}
    smoke_by_cell = {
        'CELL-223': f'{REVUP}_MEMORY_POISONING_GATE_SMOKE.json',
        'CELL-224': f'{REVUP}_MAGE_STATE_TREE_PROBE_SMOKE.json',
        'CELL-225': f'{REVUP}_PREFILL_ANCHOR_EQUALCOST_PROBE_SMOKE.json',
        'CELL-226': f'{REVUP}_MEMORY_LIFECYCLE_COST_PROBE_SMOKE.json',
        'CELL-235': f'{REVUP}_MEMORY_ADMISSIBILITY_HPO_SMOKE.json',
        'CELL-236': f'{REVUP}_EXECUTION_STATE_VERIFY_PROBE_SMOKE.json',
        'CELL-237': f'{REVUP}_EVIDENCE_PROVENANCE_DAG_PROBE_SMOKE.json',
        'CELL-238': f'{REVUP}_HORIZON_MEMORY_RETRIEVAL_PROBE_SMOKE.json',
    }
    for cid, name in smoke_by_cell.items():
        if cid in cells and name not in current_names:
            issues.append({'kind':'implemented_cell_missing_current_smoke','id':cid,'expected':name})
    status = 'pass' if not issues else 'warn'
    report={
        'project':'CloudtainerML','revision':REV,'status':status,
        'p0_source_count':len(p0_sources),'p0_idea_count':len(p0_ideas),'p0_cell_count':len(p0_cells),
        'current_native_smoke_outputs':len(current_outputs),
        'issues':issues,
        'implemented_cell_smoke_map':smoke_by_cell,
        'note':'P0 integrity checks priority-source-idea-cell-note connectivity and expected current-revision outputs for newly implemented cells.'
    }
    (AUDIT_DIR/f'{REVUP}_P0_INTEGRITY_REPORT.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    md=[f'# P0 integrity report — {REV}', '', f'Status: **{status}**', '', f'- P0 sources: {len(p0_sources)}', f'- P0 ideas: {len(p0_ideas)}', f'- P0 cells: {len(p0_cells)}', f'- current native smoke outputs: {len(current_outputs)}', '', '## Issues']
    if issues:
        for issue in issues: md.append(f'- `{issue}`')
    else:
        md.append('- none')
    (AUDIT_DIR/f'{REVUP}_P0_INTEGRITY_REPORT.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
    print(json.dumps({'status':status,'issues':len(issues),'p0_sources':len(p0_sources),'p0_ideas':len(p0_ideas),'p0_cells':len(p0_cells),'current_outputs':len(current_outputs)}, indent=2))
    return 0 if status in {'pass','warn'} else 1
if __name__ == '__main__': raise SystemExit(main())
