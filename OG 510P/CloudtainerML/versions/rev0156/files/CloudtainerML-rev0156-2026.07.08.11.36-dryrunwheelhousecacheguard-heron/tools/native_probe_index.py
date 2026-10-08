#!/usr/bin/env python3
"""Native C++ probe index and refactor audit.

This is a lighter-weight companion to native_probe_audit.py. It does not compile;
it indexes source files, declared probe outputs, top comments, line counts, and
current-revision smoke artifacts. It exists because the native lane is now large
enough that reentry needs a map, not just a compile receipt.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REV = json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0015')
REVUP = REV.upper()
OUT = ROOT/'artifacts'/'dashboard'

def load_json(p: Path):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    audit = load_json(ROOT/'artifacts'/'audit'/f'{REVUP}_NATIVE_PROBE_AUDIT.json') or {}
    by_source = {r.get('source'): r for r in audit.get('results',[]) if isinstance(r,dict)}
    rows=[]
    for p in sorted((ROOT/'experiments').glob('*/*.cpp')):
        rel=p.relative_to(ROOT).as_posix()
        txt=p.read_text(encoding='utf-8',errors='replace')
        first_comment=''
        for line in txt.splitlines()[:8]:
            if line.strip().startswith('//'):
                first_comment=line.strip().lstrip('/').strip(); break
        includes=len(re.findall(r'^#include', txt, flags=re.M))
        audit_row=by_source.get(rel,{})
        out_rel=audit_row.get('output','')
        obj=load_json(ROOT/out_rel) if out_rel else None
        summary=obj.get('summary',{}) if isinstance(obj,dict) else {}
        pm=summary.get('primary_metric',{}) if isinstance(summary,dict) else {}
        rows.append({
            'source': rel,
            'lines': len(txt.splitlines()),
            'includes': includes,
            'top_comment': first_comment,
            'compiled': bool(audit_row and audit_row.get('compile',{}).get('returncode')==0),
            'ran': bool(audit_row and audit_row.get('run',{}).get('returncode')==0),
            'output': out_rel,
            'probe': obj.get('probe','') if isinstance(obj,dict) else '',
            'rows': len(obj.get('rows',[])) if isinstance(obj,dict) and isinstance(obj.get('rows'),list) else summary.get('row_count',0),
            'primary_metric': pm.get('name',''),
            'direction': pm.get('direction',''),
            'rev_marker_ok': f'"revision": "{REV}"' in txt or f'revision\": \"{REV}' in txt or REV in txt[:250],
        })
    payload={'project':'CloudtainerML','revision':REV,'probe':'native_probe_index','summary':{'cpp_count':len(rows),'compiled_count':sum(1 for r in rows if r['compiled']),'ran_count':sum(1 for r in rows if r['ran']),'rev_marker_missing':sum(1 for r in rows if not r['rev_marker_ok'])},'rows':rows}
    prefix=OUT/f'{REVUP}_NATIVE_PROBE_INDEX'
    prefix.with_suffix('.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=[f'# Native C++ probe index — {REV}','',f"C++ probes: **{len(rows)}**",f"Compiled in audit: **{payload['summary']['compiled_count']}**",'', '| source | lines | probe | rows | metric | note |','|---|---:|---|---:|---|---|']
    for r in rows:
        md.append(f"| `{r['source']}` | {r['lines']} | {r['probe']} | {r['rows']} | {r['primary_metric']} / {r['direction']} | {r['top_comment']} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    trs=''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in [r['source'],r['lines'],r['probe'],r['rows'],r['primary_metric']+'/'+r['direction'],r['top_comment']])+'</tr>' for r in rows)
    h=f"<!doctype html><html><head><meta charset='utf-8'><title>Native Probe Index {REV}</title><style>body{{font-family:system-ui,sans-serif;max-width:1200px;margin:2rem auto}}td,th{{border:1px solid #bbb;padding:.35rem;vertical-align:top}}table{{border-collapse:collapse;width:100%}}</style></head><body><h1>Native C++ probe index — {REV}</h1><p>Compiled: {payload['summary']['compiled_count']} / {len(rows)}</p><table><tr><th>source</th><th>lines</th><th>probe</th><th>rows</th><th>metric</th><th>note</th></tr>{trs}</table></body></html>"
    prefix.with_suffix('.html').write_text(h,encoding='utf-8')
    print(json.dumps({'status':'pass', **payload['summary']}, indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
