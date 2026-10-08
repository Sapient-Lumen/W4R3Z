#!/usr/bin/env python3
"""Promotion-readiness report for CloudtainerML performance probes.

The cube now has many symbolic/native screens. This report prevents cheap winners
from silently becoming priorities by requiring primary metrics, cost/regret/failure
fields, fresh-vs-carry-forward status, and a clear next escalation type.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text())
REV=META.get('revision','rev0000'); REVUP=REV.upper()
OUT=ROOT/'artifacts'/'dashboard'; OUT.mkdir(parents=True,exist_ok=True)
PERF_TERMS=['ffn','attention','kv','rank','low','sparse','moe','expert','linear','state','layer','compression','flops','latency','isoflops','sgatlin','frontier','conv','gated','subspace','router','routing','gate','contribution','operator']
GUARD_FIELDS={'regret','speedup_gap','kernel_penalty','route_miss','alias_error','realized_cost','wall_proxy','wall_time_proxy','tail_error','critical_miss','attention_shift','rare_feature_fail','interference_error','latency_proxy','flops_proxy','bytes_fraction','state_bytes_proxy','abs_error','cost_frac','tail_miss','rank_miss','distractor_leak','false_skip','active_compute','uncertainty_error','collapse_penalty','posterior_entropy','absorption_gap','deployment_loss','coordination','ablation_fragility','leakage','cancel_error','output_error','gate_f1'}

def load(p: Path):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def freshness(obj):
    s=obj.get('summary',{}) if isinstance(obj,dict) else {}
    return 'carry-forward' if isinstance(s,dict) and s.get('carry_forward_from') else 'fresh'

def classify_next(probe: str, guard_fields: set, rows: int, fresh: str):
    p=probe.lower()
    if fresh!='fresh': return 'carry-forward: inspect only unless still P0'
    if 'starkv' in p or 'rank' in p: return 'harden with real random matrices/SVD + HPO sweep'
    if 'ffn_attention' in p or 'sgatlin' in p: return 'graduate to tiny trained one-layer transformer task'
    if 'state_expansion' in p: return 'harden with associative-recall generator and equal-byte state accounting'
    if 'critical_layer' in p: return 'tiny trained compression/ablation sweep'
    if guard_fields: return 'phase-sweep hardening candidate'
    return 'needs guard fields before promotion'

def main():
    rows=[]
    for p in sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*_SMOKE.json')):
        obj=load(p)
        if not isinstance(obj,dict): continue
        probe=str(obj.get('probe',''))
        text=(probe+' '+p.name).lower()
        if not any(t in text for t in PERF_TERMS):
            continue
        data_rows=obj.get('rows',[]) if isinstance(obj.get('rows'),list) else []
        fields=set()
        for r in data_rows[:2000]:
            if isinstance(r,dict): fields.update(k for k in r.keys() if k in GUARD_FIELDS)
        pm=obj.get('summary',{}).get('primary_metric',{}) if isinstance(obj.get('summary'),dict) else {}
        fresh=freshness(obj)
        guard_ready=bool(fields & GUARD_FIELDS)
        promotion_score=(2 if fresh=='fresh' else 0)+(2 if pm else 0)+(2 if guard_ready else 0)+(1 if len(data_rows)>=50 else 0)
        rows.append({'artifact':p.relative_to(ROOT).as_posix(),'probe':probe,'freshness':fresh,'row_count':len(data_rows),'primary_metric':pm.get('name',''),'direction':pm.get('direction',''),'guard_fields':sorted(fields),'guard_ready':guard_ready,'promotion_score':promotion_score,'next_escalation':classify_next(probe,fields,len(data_rows),fresh),'interpretation':str(obj.get('summary',{}).get('interpretation',''))[:260]})
    rows.sort(key=lambda r:(r['promotion_score'], r['freshness']=='fresh', r['row_count']), reverse=True)
    report={'project':'CloudtainerML','revision':REV,'probe':'performance_promotion_report','status':'pass','summary':{'current_performance_artifacts':len(rows),'fresh_performance_artifacts':sum(1 for r in rows if r['freshness']=='fresh'),'guard_ready_artifacts':sum(1 for r in rows if r['guard_ready']),'top_candidates':[r['probe'] for r in rows[:8]]},'rows':rows,'interpretation':'Use this as a promotion guard: current fresh probes with metrics and failure/cost fields are candidates for HPO or tiny-trained escalation. Carry-forward probes are continuity, not new evidence.'}
    prefix=OUT/f'{REVUP}_PERFORMANCE_PROMOTION_REPORT'
    prefix.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=[f'# Performance promotion report — {REV}','',f"Status: **{report['status']}**",'',f"- performance artifacts: {len(rows)}",f"- fresh performance artifacts: {report['summary']['fresh_performance_artifacts']}",f"- guard-ready artifacts: {report['summary']['guard_ready_artifacts']}",'','| score | probe | fresh | rows | metric | guard fields | next |','|---:|---|---|---:|---|---|---|']
    for r in rows[:40]:
        md.append(f"| {r['promotion_score']} | `{r['probe']}` | {r['freshness']} | {r['row_count']} | {r['primary_metric']} / {r['direction']} | {', '.join(r['guard_fields'])} | {r['next_escalation']} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'status':'pass',**report['summary']},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
