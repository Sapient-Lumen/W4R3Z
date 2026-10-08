#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV=META.get('revision','rev0000'); REVUP=REV.upper(); ER=META.get('evidence_revision',REV); ERUP=ER.upper(); OUT=ROOT/'artifacts'/'dashboard'; OUT.mkdir(parents=True,exist_ok=True)
COMPILE={'hard_topk_acc','hard_threshold_0p5_acc','deployment_gap_soft_to_hard_topk','topk_edge_f1','edge_f1_threshold_0p5','rank_quality','selected','reachable'}
EXACT={'target_miss','hard_topk_target_miss','miss','reachable','depth_reachable_fraction','hard_topk_depth_reachable_fraction'}
COST={'active_edge_count','selected','cost','regret','wall_proxy','selector_cost'}
def flat(o):
 s=set()
 if isinstance(o,dict):
  for k,v in o.items():s.add(k);s|=flat(v)
 elif isinstance(o,list):
  for v in o:s|=flat(v)
 return s

def main():
 ev=json.loads((ROOT/'EVIDENCE-STATUS.json').read_text(encoding='utf-8')); q={x['id']:x for x in ev.get('lanes',[])}; rows=[]
 for p in sorted((ROOT/'artifacts'/'probe-results').glob(f'{ERUP}_*.json')):
  try:o=json.loads(p.read_text(encoding='utf-8'))
  except Exception:continue
  probe=o.get('probe',p.stem); text=(probe+' '+p.name).lower()
  if not any(x in text for x in ['gate','bridge','sparse','boundary','routing']):continue
  keys=flat(o); summary=o.get('summary',{}) if isinstance(o.get('summary'),dict) else {}; keys|=set(summary.get('guard_fields',[])) if isinstance(summary.get('guard_fields'),list) else set(); qe=q.get(probe)
  row={'artifact':p.relative_to(ROOT).as_posix(),'probe':probe,'instrumentation':{'primary':isinstance(summary.get('primary_metric'),dict),'compile_fields':bool(keys&COMPILE),'exactness_fields':bool(keys&EXACT),'cost_fields':bool(keys&COST)},'run_provenance':bool(o.get('run_provenance')),'evidence_status':qe.get('status','unreviewed') if qe else 'unreviewed','veto':qe.get('veto') if qe else None,'promotion_ready':False}
  row['promotion_ready']=all(row['instrumentation'].values()) and row['run_provenance'] and qe is None; rows.append(row)
 status='quarantine_required' if any(r['evidence_status'] in {'quarantined','negative_mislabeled','symbolic_only'} for r in rows) else 'not_ready'
 report={'project':'CloudtainerML','revision':REV,'evidence_revision':ER,'report':'hard_gate_compilation_report','status':status,'artifact_count':len(rows),'promotion_ready_count':sum(r['promotion_ready'] for r in rows),'rows':rows,'interpretation':'Instrumentation fields do not prove that a guard passed. Vetoes and provenance are mandatory.'}
 (OUT/f'{REVUP}_HARD_GATE_COMPILATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 md=[f'# Hard gate compilation report — {REV}','',f'**Status: {status}**',f'- evidence revision: `{ER}`',f'- artifacts: {len(rows)}',f'- promotion-ready: {report["promotion_ready_count"]}','','## Artifacts','']+[f"- `{r['probe']}` status={r['evidence_status']} provenance={r['run_provenance']} promotion_ready={r['promotion_ready']}" for r in rows]+['',report['interpretation']]
 (OUT/f'{REVUP}_HARD_GATE_COMPILATION_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 print(json.dumps({'status':status,'artifacts':len(rows),'promotion_ready':report['promotion_ready_count']},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
