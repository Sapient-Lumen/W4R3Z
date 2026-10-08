#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper()
DASH=ROOT/'artifacts'/'dashboard'; DASH.mkdir(parents=True,exist_ok=True)
PROBE=ROOT/'artifacts'/'probe-results'
CORE_HINTS=('hpo','rank','router','routing','gate','contribution','moe','rope','sparse','lowrank','precision','star','via','speculative','frontier','attention','ffn','linear','performance','speed','cost','latency','wall','operator','spectral','dct','meta','ranker','null')
GUARD_FIELDS=('regret','speedup_gap','kernel_penalty','route_miss','alias_error','tail_error','wall_proxy','expected_cost','mismatch_rate','imbalance','stability_loss','overhead','bytes_fraction','latency_proxy','score','abs_error','cost_frac','tail_miss','rank_miss','distractor_leak','false_skip','active_compute','uncertainty_error','collapse_penalty','posterior_entropy','absorption_gap','deployment_loss','coordination','ablation_fragility','leakage','cancel_error','output_error','gate_f1')
items=[]
for p in sorted(PROBE.glob(f'{REVUP}_*_SMOKE.json')):
    try:
        obj=json.loads(p.read_text())
    except Exception as e:
        items.append({'file':p.relative_to(ROOT).as_posix(),'error':repr(e)}); continue
    sm=obj.get('summary',{}) if isinstance(obj.get('summary'),dict) else {}
    rows=obj.get('rows',[]) if isinstance(obj.get('rows'),list) else []
    keys=set()
    for r in rows[:20]:
        if isinstance(r,dict): keys.update(r.keys())
    pm=sm.get('primary_metric',{}) if isinstance(sm.get('primary_metric'),dict) else {}
    name=str(obj.get('probe',p.stem))
    coreish=any(h in (name+' '+p.name).lower() for h in CORE_HINTS)
    guard=sorted(k for k in keys if k in GUARD_FIELDS)
    winners=sm.get('nonoracle_winner_counts') or sm.get('winner_counts') or {}
    max_win=max(winners.values()) if isinstance(winners,dict) and winners else 0
    collapse = isinstance(winners,dict) and len(winners)<=1
    items.append({
        'file':p.relative_to(ROOT).as_posix(), 'probe':name, 'rows':len(rows), 'fresh':not bool(sm.get('carry_forward_from')), 'carry_forward_from':sm.get('carry_forward_from'),
        'coreish':coreish, 'primary_metric':pm, 'guard_fields':guard, 'guard_field_count':len(guard), 'winner_diversity':len(winners) if isinstance(winners,dict) else 0,
        'max_nonoracle_win':max_win, 'collapse_warning':collapse, 'interpretation':str(sm.get('interpretation',''))[:360]
    })
fresh=[x for x in items if x.get('fresh')]
corefresh=[x for x in fresh if x.get('coreish')]
guard_ready=[x for x in items if x.get('guard_field_count',0)>=3]
weak=[x for x in fresh if x.get('guard_field_count',0)<3]
report={'project':'CloudtainerML','revision':REV,'status':'pass','purpose':'performance-first hardening report: fresh probes, cost/tail guard fields, winner collapse warnings','counts':{'current_smoke_outputs':len(items),'fresh_outputs':len(fresh),'fresh_coreish_outputs':len(corefresh),'guard_ready_outputs':len(guard_ready),'fresh_missing_guards':len(weak)},'fresh_outputs':fresh,'guard_ready_outputs':[{'probe':x.get('probe'),'file':x.get('file'),'guard_fields':x.get('guard_fields')} for x in guard_ready[:80]],'promotion_warnings':[{'probe':x.get('probe'),'file':x.get('file'),'guard_fields':x.get('guard_fields'),'interpretation':x.get('interpretation')} for x in weak], 'recommendation':'Promote probes only after they expose at least score + cost/wall + tail/regret/route-miss fields, and after non-oracle winner collapse is checked.'}
(DASH/f'{REVUP}_PERFORMANCE_HARDENING_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md=[f'# Performance hardening report — {REV}','',f"Status: **{report['status']}**",'',f"Current smoke outputs: {len(items)}",f"Fresh outputs: {len(fresh)}",f"Fresh performance-ish outputs: {len(corefresh)}",f"Guard-ready outputs: {len(guard_ready)}",f"Fresh missing guard depth: {len(weak)}",'','## Fresh outputs','']
for x in fresh:
    pm=x.get('primary_metric') or {}
    md.append(f"- `{x.get('probe')}` — rows={x.get('rows')} metric={pm.get('name')} guards={', '.join(x.get('guard_fields') or [])} winners={x.get('winner_diversity')} collapse={x.get('collapse_warning')} — {x.get('interpretation','')}")
md += ['','## Promotion rule','',report['recommendation']]
(DASH/f'{REVUP}_PERFORMANCE_HARDENING_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'fresh_outputs':len(fresh),'fresh_coreish_outputs':len(corefresh),'guard_ready_outputs':len(guard_ready),'fresh_missing_guards':len(weak)},indent=2))
