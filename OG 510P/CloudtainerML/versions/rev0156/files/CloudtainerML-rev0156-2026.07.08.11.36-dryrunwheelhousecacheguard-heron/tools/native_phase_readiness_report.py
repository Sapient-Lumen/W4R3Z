#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper()
PROBE=ROOT/'artifacts'/'probe-results'; DASH=ROOT/'artifacts'/'dashboard'; DASH.mkdir(parents=True,exist_ok=True)
GUARD_FIELDS={'regret','route_miss','alias_error','budget_over','flops','rare_miss','subset_regret','load_violation','exploration_cost','route_flip_rate','rare_route_miss','mismatch_rate','bytes_fraction','wall_proxy','branch_miss','cache_miss','quality_drop','realized_cost','route_collision','old_loss_proxy','imbalance','overhead','kernel_penalty','speedup_gap','latency_proxy','tail_miss','stability_loss','expected_cost','score','abs_error','cost_frac','tail_miss','rank_miss','distractor_leak','false_skip','active_compute','uncertainty_error','collapse_penalty','posterior_entropy','absorption_gap','deployment_loss','coordination','ablation_fragility','leakage','cancel_error','output_error','gate_f1'}
items=[]
for p in sorted(PROBE.glob(f'{REVUP}_*_SMOKE.json')):
    try: obj=json.loads(p.read_text())
    except Exception as e:
        items.append({'file':p.relative_to(ROOT).as_posix(),'status':'bad-json','error':repr(e)}); continue
    sm=obj.get('summary') if isinstance(obj.get('summary'),dict) else {}
    rows=obj.get('rows') if isinstance(obj.get('rows'),list) else []
    if sm.get('carry_forward_from'):
        continue
    keys=set()
    for r in rows[:50]:
        if isinstance(r,dict): keys.update(r.keys())
    guards=sorted(keys & GUARD_FIELDS)
    winners=sm.get('nonoracle_winner_counts') or sm.get('winner_counts') or {}
    diversity=len(winners) if isinstance(winners,dict) else 0
    row_count=len(rows)
    collapse=diversity<=1
    has_cost=bool(keys & {'wall_proxy','flops','bytes_fraction','realized_cost','expected_cost','budget_over','overhead','latency_proxy'})
    has_failure=bool(keys & {'regret','route_miss','alias_error','rare_miss','route_flip_rate','rare_route_miss','branch_miss','cache_miss','route_collision','old_loss_proxy','load_violation','mismatch_rate','quality_drop'})
    readiness=0
    readiness += min(3,len(guards))
    readiness += 2 if diversity>=2 else 0
    readiness += 1 if row_count>=100 else 0
    readiness += 1 if has_cost else 0
    readiness += 1 if has_failure else 0
    readiness -= 2 if collapse else 0
    items.append({'file':p.relative_to(ROOT).as_posix(),'probe':obj.get('probe',p.stem),'row_count':row_count,'guard_fields':guards,'guard_field_count':len(guards),'winner_diversity':diversity,'collapse_warning':collapse,'has_cost_proxy':has_cost,'has_failure_proxy':has_failure,'readiness_score':readiness,'interpretation':str(sm.get('interpretation',''))[:300]})
items.sort(key=lambda x:(x.get('readiness_score',-99),x.get('row_count',0)), reverse=True)
report={'project':'CloudtainerML','revision':REV,'status':'pass','purpose':'Rank fresh native/performance probes by promotion readiness while penalizing winner collapse and missing cost/failure guard fields.','fresh_probe_count':len(items),'top_candidates':items[:20],'all_fresh':items,'recommendation':'Promote only probes with cost proxy + failure/regret proxy + at least two non-oracle winners or a documented reason for winner collapse.'}
(DASH/f'{REVUP}_NATIVE_PHASE_READINESS_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md=[f'# Native phase readiness report — {REV}','','Status: **pass**','',f'Fresh probe outputs scored: {len(items)}','','## Top candidates','']
for x in items[:25]:
    md.append(f"- `{x['probe']}` score={x['readiness_score']} rows={x['row_count']} guards={x['guard_field_count']} diversity={x['winner_diversity']} collapse={x['collapse_warning']} — {x.get('interpretation','')}")
md += ['','## Promotion rule','',report['recommendation']]
(DASH/f'{REVUP}_NATIVE_PHASE_READINESS_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'status':'pass','fresh_probe_count':len(items),'top':items[:5]},indent=2))
