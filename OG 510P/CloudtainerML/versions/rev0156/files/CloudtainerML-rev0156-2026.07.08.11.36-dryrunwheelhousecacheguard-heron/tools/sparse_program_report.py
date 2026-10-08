#!/usr/bin/env python3
from __future__ import annotations
import json, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper(); OUT=ROOT/'artifacts'/'dashboard'; OUT.mkdir(parents=True,exist_ok=True)

def main():
    src=ROOT/'artifacts'/'probe-results'/f'{REVUP}_SPARSE_ATTENTION_PROGRAM_SCHEMA_SMOKE.json'
    rows=[]; summary={}
    if src.exists():
        obj=json.loads(src.read_text(encoding='utf-8'))
        rows=obj.get('rows',[]); summary=obj.get('summary',{})
    mech={}
    reg={}
    for r in rows:
        m=r.get('mechanism','?'); g=mech.setdefault(m, {'rows':0,'direct':0,'depth_reach':0,'target_miss':0,'cost_sum':0.0})
        g['rows']+=1; g['direct']+=int(bool(r.get('direct'))); g['depth_reach']+=int(bool(r.get('depth_reach'))); g['target_miss']+=int(r.get('target_miss',0)); g['cost_sum']+=float(r.get('cost_frac',0))
        regime=r.get('regime','?'); rr=reg.setdefault(regime, {'rows':0,'miss':0}); rr['rows']+=1; rr['miss']+=int(r.get('target_miss',0))
    records=[]
    for m,g in sorted(mech.items()):
        n=max(1,g['rows'])
        records.append({'mechanism':m,'rows':g['rows'],'direct_fraction':g['direct']/n,'depth_reach_fraction':g['depth_reach']/n,'target_miss_fraction':g['target_miss']/n,'avg_cost_frac':g['cost_sum']/n})
    payload={'project':'CloudtainerML','revision':REV,'report':'sparse_program_report','status':'pass' if src.exists() else 'missing_source','summary':{'source':str(src.relative_to(ROOT)) if src.exists() else 'missing','mechanisms':len(records),'rows':len(rows),'primary_metric':{'name':'depth_reach_fraction','direction':'higher_is_better'},'note':'Normalizes sparse attention mechanisms as source/reachability/cost programs so block, bridge, sliding, periodic, and anchor schemes can be audited together.'},'records':records,'regime_miss_rates':{k:v['miss']/max(1,v['rows']) for k,v in reg.items()},'source_summary':summary}
    pref=OUT/f'{REVUP}_SPARSE_PROGRAM_REPORT'
    pref.with_suffix('.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=[f'# Sparse attention program report — {REV}','','## Summary','']+[f'- {k}: {v}' for k,v in payload['summary'].items() if k!='primary_metric']+['','| mechanism | reach depth | direct | miss | avg cost |','|---|---:|---:|---:|---:|']
    for r in records: md.append(f"| `{r['mechanism']}` | {r['depth_reach_fraction']:.3f} | {r['direct_fraction']:.3f} | {r['target_miss_fraction']:.3f} | {r['avg_cost_frac']:.3f} |")
    pref.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    trs=''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in [r['mechanism'],f"{r['depth_reach_fraction']:.3f}",f"{r['direct_fraction']:.3f}",f"{r['target_miss_fraction']:.3f}",f"{r['avg_cost_frac']:.3f}"])+'</tr>' for r in records)
    pref.with_suffix('.html').write_text(f"<!doctype html><meta charset='utf-8'><title>Sparse program report {REV}</title><body style='font-family:system-ui;max-width:1000px;margin:2rem auto'><h1>Sparse attention program report — {REV}</h1><p>Rows: {len(rows)}</p><table border=1 cellpadding=4 cellspacing=0><tr><th>mechanism</th><th>depth reach</th><th>direct</th><th>miss</th><th>avg cost</th></tr>{trs}</table></body>",encoding='utf-8')
    print(json.dumps(payload['summary'],indent=2)); return 0 if src.exists() else 1
if __name__=='__main__': raise SystemExit(main())
