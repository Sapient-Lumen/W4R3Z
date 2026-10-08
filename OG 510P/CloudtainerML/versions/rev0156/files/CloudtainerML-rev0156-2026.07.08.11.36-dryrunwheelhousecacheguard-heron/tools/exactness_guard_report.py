#!/usr/bin/env python3
from __future__ import annotations
import json, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper(); OUT=ROOT/'artifacts'/'dashboard'; OUT.mkdir(parents=True,exist_ok=True)
EXACT_KEYS=['target_miss','target_keep','exact_miss','exact_miss_counts','reachable','boundary_cliff','copy_error','rank_miss','rare_miss','tail_miss','route_flip','needle','distractor_leak','alias_error']
FAMILY_HINTS=['copy','needle','sparse','attention','routing','ranker','cache','boundary','operator','linear','state']

def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: return {'_error':repr(e)}

def row_keys(rows):
    ks=set()
    for r in rows[:128]:
        if isinstance(r,dict): ks.update(r.keys())
    return ks

def main():
    rows=[]
    for p in sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*.json')):
        o=load(p)
        probe=(o.get('probe') or p.stem) if isinstance(o,dict) else p.stem
        text=(probe+' '+p.name).lower()
        if not any(h in text for h in FAMILY_HINTS):
            continue
        summ=o.get('summary',{}) if isinstance(o.get('summary'),dict) else {}
        rlist=o.get('rows',[]) if isinstance(o.get('rows'),list) else []
        ks=row_keys(rlist)
        hits=sorted(k for k in EXACT_KEYS if k in ks or k in summ or k in summ.get('screen_regret_fields',[]) or k in summ.get('guard_fields',[]))
        rows.append({'file':p.relative_to(ROOT).as_posix(),'probe':probe,'rows':len(rlist),'primary_metric':(summ.get('primary_metric') or {}).get('name','') if isinstance(summ.get('primary_metric'),dict) else '', 'exactness_hits':hits,'exactness_ready':len(hits)>=2,'interpretation':summ.get('interpretation','')[:180]})
    payload={'project':'CloudtainerML','revision':REV,'probe':'exactness_guard_report','status':'pass','summary':{'current_candidate_artifacts':len(rows),'exactness_ready':sum(1 for r in rows if r['exactness_ready']),'primary_metric':{'name':'exactness_ready_fraction','direction':'higher_is_better'},'note':'Exact-copy/needle/reachability fields are promotion guards for performance probes, not security side-wing metrics.'},'rows':rows}
    prefix=OUT/f'{REVUP}_EXACTNESS_GUARD_REPORT'
    prefix.with_suffix('.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=[f'# Exactness guard report — {REV}','','This report checks whether current performance probes expose exact-copy, needle, reachability, rare-token, or route-flip guard fields.','','## Summary','']+[f'- {k}: {v}' for k,v in payload['summary'].items() if k!='primary_metric']+['','| probe | rows | metric | guard fields | ready |','|---|---:|---|---|---|']
    for r in rows: md.append(f"| `{r['probe']}` | {r['rows']} | {r['primary_metric']} | {', '.join(r['exactness_hits'])} | {r['exactness_ready']} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    trs=''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in [r['probe'],r['rows'],r['primary_metric'],', '.join(r['exactness_hits']),r['exactness_ready']])+'</tr>' for r in rows)
    prefix.with_suffix('.html').write_text(f"<!doctype html><meta charset='utf-8'><title>Exactness guard report {REV}</title><body style='font-family:system-ui;max-width:1200px;margin:2rem auto'><h1>Exactness guard report — {REV}</h1><p>Ready: {payload['summary']['exactness_ready']} / {len(rows)}</p><table border=1 cellpadding=4 cellspacing=0><tr><th>probe</th><th>rows</th><th>metric</th><th>guards</th><th>ready</th></tr>{trs}</table></body>",encoding='utf-8')
    print(json.dumps(payload['summary'],indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
