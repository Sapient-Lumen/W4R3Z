#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper()
DASH=ROOT/'artifacts'/'dashboard'; DASH.mkdir(parents=True, exist_ok=True)
SIDE_TERMS={'poison','safety','sycophancy','provenance','trust','admissibility','janus','alignment','security'}
CORE_TERMS={'native','phase','performance','rank','subspace','attention','cache','kv','linear','grokking','precision','sparse','lrkv','santa','kvcat','smt','dfs','search','speed','bytes','flops','latency','ffn','moe','expert','sgatlin','compression','state','layer'}
def load(name): return json.loads((ROOT/name).read_text())
def sideish(text: str) -> bool: return any(x in text.lower() for x in SIDE_TERMS)
def coreish(text: str) -> bool: return any(x in text.lower() for x in CORE_TERMS)
ideas=load('IDEA-LEDGER.json')['ideas']; cells=load('EXPERIMENT-MATRIX.json')['cells']; sources=load('RESEARCH-SOURCE-REGISTRY.json')['sources']
probe_files=sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*_SMOKE.json'))
p0_cells=[c for c in cells if c.get('priority')=='P0']
side_p0=[c for c in p0_cells if sideish(' '.join([c.get('name',''),c.get('status',''),c.get('cheap_first_run','')]))]
core_p0=[c for c in p0_cells if coreish(' '.join([c.get('name',''),c.get('status',''),c.get('cheap_first_run','')]))]
current=[]
for p in probe_files:
    try:
        o=json.loads(p.read_text())
        sm=o.get('summary',{}) if isinstance(o.get('summary'),dict) else {}
        pm=sm.get('primary_metric',{}) if isinstance(sm,dict) else {}
        rows=o.get('rows',[]) if isinstance(o.get('rows'),list) else []
        probe=o.get('probe','')
        text=(probe+' '+p.name).lower()
        if coreish(text):
            current.append({'file':p.relative_to(ROOT).as_posix(),'probe':probe,'rows':len(rows),'primary_metric':pm,'carry_forward_from':sm.get('carry_forward_from'),'interpretation':sm.get('interpretation','')[:320]})
    except Exception as e:
        current.append({'file':p.relative_to(ROOT).as_posix(),'error':repr(e)})
report={'project':'CloudtainerML','revision':REV,'status':'pass','charter':'performance/surprise/native phase diagrams are core; security/trust remains bounded side wing','counts':{'sources':len(sources),'ideas':len(ideas),'cells':len(cells),'p0_cells':len(p0_cells),'sideish_p0_cells':len(side_p0),'coreish_p0_cells':len(core_p0),'current_native_smoke_outputs':len(probe_files),'current_coreish_outputs':len(current)},'sidewing_p0_fraction':round(len(side_p0)/max(1,len(p0_cells)),4),'current_revision_perf_probe_highlights':current,'fresh_current_probe_count':sum(1 for x in current if not x.get('carry_forward_from')),'carry_forward_probe_count':sum(1 for x in current if x.get('carry_forward_from')),'top_core_lanes':['Routing absorption vs coordination split','Directional suppression router','Contribution-weight geometry guard','Tiny copy-head trained escalation','Spectral operator routing with DCT+attention residual baseline','STAR-KV/component rank allocation','Sparse/low-rank/spectral frontier','Native C++ phase diagrams and screen-regret discipline','FFN-attention computation redistribution'],'open_warnings':['Side-wing artifacts still exist as acceptance tests, not priority drivers.','Symbolic C++ probes are not paper reproductions or trained-model evidence.']}
(DASH/f'{REVUP}_PERFORMANCE_CORE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md=[f'# Performance core report — {REV}','',f"Status: **{report['status']}**",'',f"P0 cells: {len(p0_cells)}",f"Side-wing-ish P0 cells: {len(side_p0)}",f"Side-wing P0 fraction: {report['sidewing_p0_fraction']}",'','## Current-revision performance-ish probes','']
for x in current[:80]:
    pm=x.get('primary_metric') or {}
    md.append(f"- `{x.get('probe')}` — rows={x.get('rows')} metric={pm.get('name')} carry={x.get('carry_forward_from')} — {x.get('interpretation','')}")
md += ['','## Core lanes',''] + [f'- {x}' for x in report['top_core_lanes']] + ['','## Warnings',''] + [f'- {x}' for x in report['open_warnings']]
(DASH/f'{REVUP}_PERFORMANCE_CORE_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'p0_cells':len(p0_cells),'sidewing_p0_fraction':report['sidewing_p0_fraction'],'current_native_smoke_outputs':len(probe_files)},indent=2))
