#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV=META.get('revision','rev0000'); REVUP=REV.upper(); ER=META.get('evidence_revision',REV); ERUP=ER.upper()
OUT=ROOT/'artifacts'/'dashboard'; OUT.mkdir(parents=True,exist_ok=True)
TARGET={'tiny_bridge_annealed_hard_train','tiny_bridge_posttrain_sparsify','gate_compiler_frontier','blockwise_index_branch','gvr_topk_temporal'}
EXACT={'target_miss','hard_topk_target_miss','miss','misses','exact','reachable','depth_reachable_fraction','hard_topk_depth_reachable_fraction','recall'}
COST={'selector_cost','block_cost','wall_proxy','selected_blocks','candidate_count','passes','active_edge_count','cost','selected'}
COMPILE={'hard_topk_acc','hard_threshold_0p5_acc','topk_edge_f1','rank_quality','calibration_error','deployment_gap_soft_to_hard_topk','edge_f1_threshold_0p5'}
def flat(o):
    s=set()
    if isinstance(o,dict):
        for k,v in o.items(): s.add(k); s|=flat(v)
    elif isinstance(o,list):
        for v in o: s|=flat(v)
    return s

def main():
    ev=json.loads((ROOT/'EVIDENCE-STATUS.json').read_text(encoding='utf-8'))
    q={x['id']:x for x in ev.get('lanes',[])}; rows=[]
    for p in sorted((ROOT/'artifacts'/'probe-results').glob(f'{ERUP}_*.json')):
        try:o=json.loads(p.read_text(encoding='utf-8'))
        except Exception:continue
        probe=o.get('probe',p.stem)
        if probe not in TARGET:continue
        keys=flat(o); summary=o.get('summary',{}) if isinstance(o.get('summary'),dict) else {}; guard=set(summary.get('guard_fields',[])) if isinstance(summary.get('guard_fields'),list) else set(); keys|=guard
        quarantined=probe in q
        provenance=bool(o.get('run_provenance'))
        row={'artifact':p.relative_to(ROOT).as_posix(),'probe':probe,'has_primary_metric':isinstance(summary.get('primary_metric'),dict),'has_exactness_fields':bool(keys&EXACT),'has_cost_fields':bool(keys&COST),'has_compile_fields':bool(keys&COMPILE),'run_provenance':provenance,'evidence_status':q.get(probe,{}).get('status','unreviewed'),'veto':q.get(probe,{}).get('veto'),'promotion_ready':False}
        row['promotion_ready']=all([row['has_primary_metric'],row['has_exactness_fields'],row['has_cost_fields'],row['has_compile_fields'],provenance,not quarantined])
        rows.append(row)
    status='quarantine_required' if any(r['evidence_status'] in {'quarantined','negative_mislabeled','symbolic_only'} for r in rows) else ('ready' if rows and all(r['promotion_ready'] for r in rows) else 'not_ready')
    report={'project':'CloudtainerML','revision':REV,'evidence_revision':ER,'report':'sparse_index_compiler_report','status':status,'artifact_count':len(rows),'promotion_ready_count':sum(r['promotion_ready'] for r in rows),'rows':rows,'interpretation':'Field presence is instrumentation coverage, not readiness. Promotion additionally requires passing values, immutable run provenance, and no veto.'}
    (OUT/f'{REVUP}_SPARSE_INDEX_COMPILER_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    md=[f'# Sparse index/compiler report — {REV}','',f'**Status: {status}**',f'- evidence revision: `{ER}`',f'- artifacts: {len(rows)}',f'- promotion-ready: {report["promotion_ready_count"]}','','## Rows','']
    md += [f"- `{r['probe']}` status={r['evidence_status']} provenance={r['run_provenance']} exact_fields={r['has_exactness_fields']} cost_fields={r['has_cost_fields']} compile_fields={r['has_compile_fields']} promotion_ready={r['promotion_ready']}" for r in rows]
    md += ['',report['interpretation']]
    (OUT/f'{REVUP}_SPARSE_INDEX_COMPILER_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'status':status,'artifacts':len(rows),'promotion_ready':report['promotion_ready_count']},indent=2)); return 0
if __name__=='__main__':raise SystemExit(main())
