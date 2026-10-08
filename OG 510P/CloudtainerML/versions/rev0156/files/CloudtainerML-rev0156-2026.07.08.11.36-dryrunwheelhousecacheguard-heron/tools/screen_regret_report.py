#!/usr/bin/env python3
"""Screen/regret audit for performance probes.

Many CloudtainerML probes are cheap screens. This report extracts common regret,
realized-cost, kernel-penalty, route-miss, and alias-error fields from current
revision native smoke outputs so cheap winners are not mistaken for full winners.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper()
OUT=ROOT/'artifacts'/'dashboard'; OUT.mkdir(parents=True,exist_ok=True)
FIELDS=['regret','speedup_gap','kernel_penalty','route_miss','alias_error','realized_cost','wall_proxy','wall_time_proxy','score','abs_error','cost_frac','budget_over','tail_miss','rank_miss','distractor_leak','false_skip','active_compute','uncertainty_error','collapse_penalty','posterior_entropy','absorption_gap','deployment_loss','coordination','ablation_fragility','leakage','cancel_error','output_error','gate_f1']

def load(p):
    try: return json.loads(p.read_text())
    except Exception: return None

def mean(vals): return sum(vals)/len(vals) if vals else None

def quantile(vals,q):
    if not vals: return None
    vals=sorted(vals); idx=min(len(vals)-1,max(0,int(round(q*(len(vals)-1)))))
    return vals[idx]

def main():
    rows=[]
    for p in sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*_SMOKE.json')):
        obj=load(p)
        if not isinstance(obj,dict): continue
        vals={k:[] for k in FIELDS}
        for r in obj.get('rows',[]) if isinstance(obj.get('rows'),list) else []:
            if not isinstance(r,dict): continue
            for k in FIELDS:
                v=r.get(k)
                if isinstance(v,(int,float)): vals[k].append(float(v))
        present={k:v for k,v in vals.items() if v}
        if not present: continue
        pm=obj.get('summary',{}).get('primary_metric',{}) if isinstance(obj.get('summary'),dict) else {}
        rows.append({
            'artifact':p.relative_to(ROOT).as_posix(),
            'probe':obj.get('probe',''),
            'primary_metric':pm.get('name',''),
            'fields_present':sorted(present),
            'stats':{k:{'mean':mean(v),'p90':quantile(v,0.90),'max':max(v)} for k,v in present.items()},
            'screen_guard_ready': any(k in present for k in ['regret','speedup_gap','kernel_penalty','realized_cost','wall_proxy','wall_time_proxy','budget_over','cost_frac'])
        })
    report={
        'project':'CloudtainerML','revision':REV,'probe':'screen_regret_report','status':'pass',
        'summary':{
            'current_smoke_artifacts':len(list((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*_SMOKE.json'))),
            'screen_audited_artifacts':len(rows),
            'guard_ready_count':sum(1 for r in rows if r['screen_guard_ready'])
        },
        'rows':rows,
        'interpretation':'Cheap screens need regret/cost/kernel fields before promotion. This audit does not score truth; it tells us which probes expose reversal surfaces.'
    }
    prefix=OUT/f'{REVUP}_SCREEN_REGRET_REPORT'
    prefix.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=[f'# Screen regret report — {REV}','',f"Status: **{report['status']}**",'',f"- current smoke artifacts: {report['summary']['current_smoke_artifacts']}",f"- audited artifacts: {len(rows)}",f"- guard-ready artifacts: {report['summary']['guard_ready_count']}",'','| probe | metric | fields | guard-ready |','|---|---|---|---:|']
    for r in rows:
        md.append(f"| `{r['probe']}` | {r['primary_metric']} | {', '.join(r['fields_present'])} | {int(r['screen_guard_ready'])} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'status':'pass',**report['summary']},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
