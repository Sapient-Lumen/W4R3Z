#!/usr/bin/env python3
from __future__ import annotations
import json, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text())
REV=META.get('revision','rev0000'); REVUP=REV.upper()
DASH=ROOT/'artifacts'/'dashboard'; DASH.mkdir(parents=True,exist_ok=True)
KEYS=['router','routing','route','moe','expert','operator','gate','sparse']
GUARDS=['absorption_gap','deployment_loss','coordination','ablation_fragility','route_flip','rare_miss','tail_miss','regret','cost','score','gate_f1','leakage','imbalance','output_error','cancel_error']

def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: return {'_error':repr(e)}

def classify(name: str) -> str:
    n=name.lower()
    if 'absorption' in n: return 'route-selection-absorption'
    if 'directional' in n or 'suppression' in n: return 'route-coordination'
    if 'self_routing' in n or 'self-routing' in n: return 'self-routing'
    if 'contribution' in n: return 'value-geometry-guard'
    if 'operator' in n or 'spectral' in n or 'chiar' in n: return 'operator-routing'
    if 'moe' in n or 'expert' in n or 'router' in n or 'routing' in n: return 'expert-routing'
    if 'gate' in n: return 'gate-routing'
    return 'other-routing-ish'

def main() -> int:
    rows=[]
    for p in sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*.json')):
        o=load(p)
        probe=o.get('probe','') if isinstance(o,dict) else ''
        text=(probe+' '+p.name).lower()
        if not any(k in text for k in KEYS):
            continue
        summary=o.get('summary',{}) if isinstance(o.get('summary'),dict) else {}
        rowlist=o.get('rows',[]) if isinstance(o.get('rows'),list) else []
        row_keys=set()
        for r in rowlist[:64]:
            if isinstance(r,dict): row_keys.update(r.keys())
        guard_hits=sorted(k for k in GUARDS if k in row_keys or k in summary.get('screen_regret_fields',[]))
        pm=summary.get('primary_metric',{}) if isinstance(summary.get('primary_metric'),dict) else {}
        winners=summary.get('nonoracle_winner_counts') or summary.get('winner_counts') or {}
        winner_diversity=len(winners) if isinstance(winners,dict) else 0
        rows.append({
            'file':p.relative_to(ROOT).as_posix(),
            'probe':probe,
            'family':classify(probe+' '+p.name),
            'rows':len(rowlist),
            'primary_metric':pm.get('name',''),
            'winner_diversity':winner_diversity,
            'guard_hits':guard_hits,
            'guard_ready': len(guard_hits)>=4,
            'interpretation':summary.get('interpretation',''),
            'carry_forward_from':summary.get('carry_forward_from'),
        })
    family_counts={}
    for r in rows: family_counts[r['family']]=family_counts.get(r['family'],0)+1
    report={
        'project':'CloudtainerML','revision':REV,'probe':'routing_family_report','status':'pass',
        'summary':{
            'routing_artifacts':len(rows),
            'guard_ready':sum(1 for r in rows if r['guard_ready']),
            'family_counts':family_counts,
            'primary_metric':{'name':'guard_ready_fraction','direction':'higher_is_better','winner_field':'family'},
            'routing_split':'route-selection gates can fail by absorption; coordination routers should be judged by coordination/ablation-fragility; self-routing needs hidden-subspace alignment guards; operator routing needs dense/simple and exact-copy veto baselines.',
        },
        'rows':rows,
    }
    prefix=DASH/f'{REVUP}_ROUTING_FAMILY_REPORT'
    prefix.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=[f'# Routing family report — {REV}','',f"Routing-ish current artifacts: **{len(rows)}**",f"Guard-ready: **{report['summary']['guard_ready']}**",'', '## Family counts','']
    for k,v in sorted(family_counts.items()): md.append(f'- {k}: {v}')
    md += ['','## Current artifacts','','| probe | family | rows | metric | guard hits | carry |','|---|---|---:|---|---|---|']
    for r in rows:
        md.append(f"| `{r['probe']}` | {r['family']} | {r['rows']} | {r['primary_metric']} | {', '.join(r['guard_hits'])} | {r.get('carry_forward_from')} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    trs=''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in [r['probe'],r['family'],r['rows'],r['primary_metric'],', '.join(r['guard_hits']),r.get('carry_forward_from')])+'</tr>' for r in rows)
    prefix.with_suffix('.html').write_text(f"<!doctype html><meta charset='utf-8'><title>Routing Family Report {REV}</title><body style='font-family:system-ui;max-width:1200px;margin:2rem auto'><h1>Routing family report — {REV}</h1><p>Guard-ready: {report['summary']['guard_ready']} / {len(rows)}</p><table border=1 cellpadding=4 cellspacing=0><tr><th>probe</th><th>family</th><th>rows</th><th>metric</th><th>guards</th><th>carry</th></tr>{trs}</table></body>",encoding='utf-8')
    print(json.dumps({'status':'pass','routing_artifacts':len(rows),'guard_ready':report['summary']['guard_ready'],'families':family_counts},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
