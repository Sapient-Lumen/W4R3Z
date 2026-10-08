#!/usr/bin/env python3
from __future__ import annotations
import json, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper()
OUT=ROOT/'artifacts'/'dashboard'; OUT.mkdir(parents=True,exist_ok=True)
PROBE=ROOT/'artifacts'/'probe-results'
EXACT={'target_miss','exact_miss','copy_error','reachable_fraction','depth_reachable_fraction','one_step_reachable_fraction','rare_miss','tail_miss','route_flip','exact_miss_counts','rank_miss','needle','alias_error'}
COST={'realized_cost','wall_proxy','kernel_penalty','selector_overhead','traffic_proxy','budget_over','cost_frac','speedup_gap'}
MECH={'route_error','gain_error','importance_error','causal_ablation_match','content_match','confound_penalty','source_attention_mass_by_target_pos_last_layer','depth_reachable_fraction'}
TRAINED_HINTS={'trained_tiny_probe','tiny_copy_head_train','tiny_boundary','tiny_routing'}

def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: return {'_error':repr(e)}

def keys_from(o):
    keys=set()
    s=o.get('summary',{}) if isinstance(o.get('summary'),dict) else {}
    for k,v in s.items():
        keys.add(k)
        if isinstance(v,list): keys.update(str(x) for x in v)
        if isinstance(v,dict): keys.update(v.keys())
    rows=o.get('rows',[]) if isinstance(o.get('rows'),list) else []
    for r in rows[:256]:
        if isinstance(r,dict): keys.update(r.keys())
    return keys

def main():
    rows=[]
    for p in sorted(PROBE.glob(f'{REVUP}_*.json')):
        o=load(p)
        if not isinstance(o,dict): continue
        probe=o.get('probe') or p.stem
        summ=o.get('summary',{}) if isinstance(o.get('summary'),dict) else {}
        ks=keys_from(o)
        exact_hits=sorted(EXACT & ks)
        cost_hits=sorted(COST & ks)
        mech_hits=sorted(MECH & ks)
        trained = (o.get('kind') in TRAINED_HINTS) or any(h in str(probe).lower() for h in TRAINED_HINTS)
        primary=isinstance(summ.get('primary_metric'),dict)
        # Promotion score is deliberately conservative: a high score means the probe is instrumented,
        # not that its winner is true.
        score=(2 if primary else 0)+(2 if exact_hits else 0)+(2 if cost_hits else 0)+(2 if mech_hits else 0)+(2 if trained else 0)
        family='trained' if trained else 'native' if o.get('kind')=='native_cxx_probe' else 'report_or_python'
        rows.append({'file':p.relative_to(ROOT).as_posix(),'probe':probe,'kind':o.get('kind',''),'family':family,'primary_metric':primary,'exactness_hits':exact_hits,'cost_hits':cost_hits,'mechanism_hits':mech_hits,'trained_evidence':trained,'promotion_score':score,'ready_for_promotion_audit':score>=6,'interpretation':str(summ.get('interpretation',''))[:240]})
    rows_sorted=sorted(rows,key=lambda r:(-r['promotion_score'],r['probe']))
    payload={'project':'CloudtainerML','revision':REV,'probe':'mechanism_promotion_report','status':'pass','summary':{'primary_metric':{'name':'promotion_score','direction':'higher_is_better'},'artifact_count':len(rows),'ready_count':sum(1 for r in rows if r['ready_for_promotion_audit']),'trained_count':sum(1 for r in rows if r['trained_evidence']),'note':'Promotion score measures instrumentation readiness: exactness/cost/mechanism/trained fields. It is not a truth score.'},'rows':rows_sorted}
    prefix=OUT/f'{REVUP}_MECHANISM_PROMOTION_REPORT'
    prefix.with_suffix('.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=[f'# Mechanism promotion report — {REV}','','This is an audit/refactor surface. It does **not** say a probe is correct; it says whether a probe exposes enough fields to be worth trusting as a promotion candidate.','','## Summary','']+[f'- {k}: {v}' for k,v in payload['summary'].items() if k!='primary_metric']+['','| score | probe | kind | exactness | cost | mechanism | trained | ready |','|---:|---|---|---|---|---|---|---|']
    for r in rows_sorted[:120]:
        md.append(f"| {r['promotion_score']} | `{r['probe']}` | {r['kind']} | {', '.join(r['exactness_hits'])} | {', '.join(r['cost_hits'])} | {', '.join(r['mechanism_hits'])} | {r['trained_evidence']} | {r['ready_for_promotion_audit']} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    trs=''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in [r['promotion_score'],r['probe'],r['kind'],', '.join(r['exactness_hits']),', '.join(r['cost_hits']),', '.join(r['mechanism_hits']),r['trained_evidence'],r['ready_for_promotion_audit']])+'</tr>' for r in rows_sorted[:200])
    prefix.with_suffix('.html').write_text(f"<!doctype html><meta charset='utf-8'><title>Mechanism promotion report {REV}</title><body style='font-family:system-ui;max-width:1200px;margin:2rem auto'><h1>Mechanism promotion report — {REV}</h1><p>Ready: {payload['summary']['ready_count']} / {len(rows)}</p><table border=1 cellpadding=4 cellspacing=0><tr><th>score</th><th>probe</th><th>kind</th><th>exact</th><th>cost</th><th>mechanism</th><th>trained</th><th>ready</th></tr>{trs}</table></body>",encoding='utf-8')
    print(json.dumps(payload['summary'],indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
