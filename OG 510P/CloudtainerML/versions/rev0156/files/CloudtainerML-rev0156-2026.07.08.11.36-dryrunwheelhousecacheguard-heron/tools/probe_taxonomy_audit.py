#!/usr/bin/env python3
"""Probe taxonomy report.

Classifies current-revision probe artifacts into coarse CloudtainerML buckets so
priority decisions stop mixing cache compression, agent memory, reasoning credit,
mask design, and safety audits into a single pile.
"""
from __future__ import annotations
import csv, html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REV=json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0019')
REVUP=REV.upper(); OUT=ROOT/'artifacts'/'dashboard'; PROBE=ROOT/'artifacts'/'probe-results'
RULES=[
 ('safety-tail', ['safety','alignment','provenance','sycophancy','vericache','tail','catastrophic']),
 ('kv-cache-compression', ['kv','cache','quant','precision','evict','sparse','residual','query_move','lrkv','kvarn','tensor']),
 ('persistent-agent-memory', ['memory','topic','graph','infini','real','provenance','observability']),
 ('reasoning-credit-search', ['flow','dfs','trace','rollout','reasoning','credit','rksc']),
 ('attention-architecture', ['hasse','mask','attention','qkv','delta','linear','blurry','fademem','cope','entropy']),
 ('latent-compute', ['latent','smt','projector','ttt','evidence']),
 ('meta-optimization', ['hpo','centaur','phase']),
]
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None
def classify(obj,p):
    explicit=obj.get('taxonomy') if isinstance(obj.get('taxonomy'),list) else []
    if explicit: return sorted(set(str(x) for x in explicit))
    text=' '.join([p.name,str(obj.get('probe','')),json.dumps(obj.get('summary',{}))]).lower()
    tags=[]
    for name,words in RULES:
        if any(w in text for w in words): tags.append(name)
    return tags or ['uncategorized']
def main():
    OUT.mkdir(parents=True,exist_ok=True); rows=[]; counts={}
    for p in sorted(PROBE.glob(f'{REVUP}_*.json')):
        obj=load(p)
        if not isinstance(obj,dict): continue
        tags=classify(obj,p); probe=str(obj.get('probe',''))
        for t in tags: counts[t]=counts.get(t,0)+1
        pm=(obj.get('summary') or {}).get('primary_metric',{}) if isinstance(obj.get('summary'),dict) else {}
        rows.append({'artifact':p.relative_to(ROOT).as_posix(),'probe':probe,'tags':';'.join(tags),'primary_metric':pm.get('name',''),'row_count':len(obj.get('rows',[])) if isinstance(obj.get('rows'),list) else (obj.get('summary') or {}).get('row_count',0)})
    payload={'project':'CloudtainerML','revision':REV,'probe':'probe_taxonomy_audit','summary':{'artifact_count':len(rows),'tag_counts':counts,'uncategorized_count':counts.get('uncategorized',0),'primary_metric':{'name':'uncategorized_count','direction':'lower_is_better'}},'rows':rows}
    prefix=OUT/f'{REVUP}_PROBE_TAXONOMY_AUDIT'
    prefix.with_suffix('.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    with prefix.with_suffix('.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['artifact','probe','tags','primary_metric','row_count']); w.writeheader(); w.writerows(rows)
    md=[f'# Probe taxonomy audit — {REV}','','## Tag counts','']+[f'- **{k}**: {v}' for k,v in sorted(counts.items(), key=lambda kv:(-kv[1],kv[0]))]+['','| artifact | probe | tags | metric |','|---|---|---|---|']
    for r in rows: md.append(f"| `{r['artifact']}` | {r['probe']} | {r['tags']} | {r['primary_metric']} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    trs=''.join('<tr>'+''.join(f'<td>{html.escape(str(r[k]))}</td>' for k in ['artifact','probe','tags','primary_metric'])+'</tr>' for r in rows)
    prefix.with_suffix('.html').write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>Probe taxonomy {REV}</title><style>body{{font-family:system-ui,sans-serif;max-width:1200px;margin:2rem auto}}td,th{{border:1px solid #bbb;padding:.35rem}}table{{border-collapse:collapse;width:100%}}</style></head><body><h1>Probe taxonomy audit — {REV}</h1><pre>{html.escape(json.dumps(counts,indent=2))}</pre><table><tr><th>artifact</th><th>probe</th><th>tags</th><th>metric</th></tr>{trs}</table></body></html>",encoding='utf-8')
    print(json.dumps({'status':'pass','artifact_count':len(rows),'uncategorized_count':counts.get('uncategorized',0),'tag_counts':counts},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
