#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper()
PROBE=ROOT/'artifacts'/'probe-results'; DASH=ROOT/'artifacts'/'dashboard'; DASH.mkdir(parents=True,exist_ok=True)
FAMILY_HINTS=('spectral','operator','meta_attention','ranker','contextualization','null_expert','moe','router','probmoe','headwise','dot_moe','manifold_power','expert_choice','copy_head','gated_bidirectional','confidence_adaptive')
COST_FIELDS={'cost_frac','budget_over','flops','wall_proxy','latency_proxy','active_compute','expected_cost'}
FAIL_FIELDS={'route_miss','alias_error','tail_miss','rank_miss','distractor_leak','false_skip','rare_miss','regret','collapse_penalty','uncertainty_error'}
rows=[]
for p in sorted(PROBE.glob(f'{REVUP}_*_SMOKE.json')):
    try: obj=json.loads(p.read_text())
    except Exception: continue
    probe=str(obj.get('probe',p.stem))
    if not any(h in (probe+' '+p.name).lower() for h in FAMILY_HINTS):
        continue
    sm=obj.get('summary',{}) if isinstance(obj.get('summary'),dict) else {}
    data=obj.get('rows',[]) if isinstance(obj.get('rows'),list) else []
    keys=set()
    for r in data[:100]:
        if isinstance(r,dict): keys |= set(r.keys())
    winners=sm.get('nonoracle_winner_counts') or sm.get('winner_counts') or {}
    rows.append({
        'artifact':p.relative_to(ROOT).as_posix(),
        'probe':probe,
        'fresh':not bool(sm.get('carry_forward_from')),
        'carry_forward_from':sm.get('carry_forward_from'),
        'row_count':len(data),
        'primary_metric':(sm.get('primary_metric') or {}).get('name'),
        'winner_diversity':len(winners) if isinstance(winners,dict) else 0,
        'winner_counts':winners,
        'cost_fields':sorted(keys & COST_FIELDS),
        'failure_fields':sorted(keys & FAIL_FIELDS),
        'readiness': min(4,len(keys&COST_FIELDS)+len(keys&FAIL_FIELDS)) + (2 if len(winners)>=2 else 0) + (1 if len(data)>=100 else 0),
        'interpretation':str(sm.get('interpretation',''))[:500]
    })
rows.sort(key=lambda x:(x['fresh'],x['readiness'],x['row_count']), reverse=True)
report={'project':'CloudtainerML','revision':REV,'probe':'operator_route_report','status':'pass','purpose':'Audit operator/router/ranker/MoE-family probes for cost fields, failure fields, and winner diversity.','summary':{'family_artifacts':len(rows),'fresh_family_artifacts':sum(1 for r in rows if r['fresh']),'readiness_top':rows[:10]},'rows':rows}
base=DASH/f'{REVUP}_OPERATOR_ROUTE_REPORT'
base.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md=[f'# Operator/router family report — {REV}','','Status: **pass**','',f"Family artifacts: {len(rows)}",f"Fresh family artifacts: {report['summary']['fresh_family_artifacts']}",'','| probe | fresh | rows | readiness | winners | cost fields | failure fields |','|---|---:|---:|---:|---:|---|---|']
for r in rows[:80]:
    md.append(f"| `{r['probe']}` | {int(r['fresh'])} | {r['row_count']} | {r['readiness']} | {r['winner_diversity']} | {', '.join(r['cost_fields'])} | {', '.join(r['failure_fields'])} |")
base.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'status':'pass','family_artifacts':len(rows),'fresh_family_artifacts':report['summary']['fresh_family_artifacts']},indent=2))
