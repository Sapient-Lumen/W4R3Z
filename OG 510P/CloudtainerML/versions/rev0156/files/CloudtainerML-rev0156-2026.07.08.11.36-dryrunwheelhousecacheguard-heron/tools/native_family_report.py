#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REV=json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0014')
REVUP=REV.upper()
OUT=ROOT/'artifacts'/'dashboard'
PROBE=ROOT/'artifacts'/'probe-results'

def load(p):
    try: return json.loads(p.read_text())
    except Exception: return None

def compact_winners(s):
    for key in ['winner_counts','winner_counts_excluding_oracle','winners','best_policy_by_regime_budget']:
        v=s.get(key)
        if isinstance(v,dict):
            if key.startswith('best'):
                counts={}
                for item in v.values():
                    if isinstance(item,dict): w=item.get('best_policy') or item.get('winner')
                    else: w=item
                    counts[str(w)]=counts.get(str(w),0)+1
                v=counts
            return '; '.join(f'{k}:{v[k]}' for k in sorted(v,key=lambda x:(-v[x],x))[:8] if isinstance(v.get(k),(int,float,str)))
    return ''

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    native_audit=load(ROOT/'artifacts'/'audit'/f'{REVUP}_NATIVE_PROBE_AUDIT.json') or {}
    native_outputs={r.get('output') for r in native_audit.get('results',[]) if isinstance(r,dict)}
    rows=[]
    for rel in sorted(native_outputs):
        if not rel: continue
        p=ROOT/rel; obj=load(p) or {}; summ=obj.get('summary') if isinstance(obj.get('summary'),dict) else {}
        pm=summ.get('primary_metric') if isinstance(summ.get('primary_metric'),dict) else {}
        rows.append({'output':rel,'probe':obj.get('probe',''),'revision':obj.get('revision',''),'row_count':len(obj.get('rows',[])) if isinstance(obj.get('rows'),list) else summ.get('row_count',0),'primary_metric':pm.get('name',''),'direction':pm.get('direction',''),'winner_summary':compact_winners(summ)})
    report={'project':'CloudtainerML','revision':REV,'native_output_count':len(rows),'rows':rows}
    (OUT/f'{REVUP}_NATIVE_FAMILY_REPORT.json').write_text(json.dumps(report,indent=2))
    md=[f'# Native family report — {REV}','',f'- native outputs: {len(rows)}','', '| output | probe | rows | primary metric | winners |','|---|---:|---:|---|---|']
    for r in rows:
        md.append(f"| `{r['output']}` | {r['probe']} | {r['row_count']} | {r['primary_metric']} / {r['direction']} | {r['winner_summary']} |")
    (OUT/f'{REVUP}_NATIVE_FAMILY_REPORT.md').write_text('\n'.join(md)+'\n')
    print(json.dumps({'status':'pass','native_output_count':len(rows)},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
