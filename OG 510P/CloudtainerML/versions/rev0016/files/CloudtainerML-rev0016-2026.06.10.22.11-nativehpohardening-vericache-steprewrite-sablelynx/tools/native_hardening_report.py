#!/usr/bin/env python3
"""Revision-level native hardening report.

Indexes C++ probes that are meant to harden existing questions rather than add a
new speculative lane: verifier guards, periodic rewrites, provenance sweeps, and
phase-boundary cost models. The report is intentionally lightweight so it can be
run after native_probe_audit without knowing any individual probe schema.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT/'CUBE-META.json').exists() else {}
REV=META.get('revision','rev0016'); REVUP=REV.upper()
OUT=ROOT/'artifacts'/'dashboard'
PROBE=ROOT/'artifacts'/'probe-results'
HARDENING_KEYWORDS=['VERICACHE','PERIODIC_CACHE_REWRITE','MEMORY_PROVENANCE','NATIVE_HPO','PHASE','SENSITIVITY','FRONTIER']

def load(p:Path):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def winner_summary(summary):
    for key in ['winner_counts_excluding_oracle','winner_counts','regularized_winner_counts']:
        val=summary.get(key) if isinstance(summary,dict) else None
        if isinstance(val,dict):
            return '; '.join(f'{k}:{val[k]}' for k in sorted(val, key=lambda x:(-val[x] if isinstance(val[x],(int,float)) else 0, x))[:10])
    return ''

def main()->int:
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]
    for p in sorted(PROBE.glob(f'{REVUP}_*.json')):
        obj=load(p)
        if not isinstance(obj,dict): continue
        name=p.name.upper()
        if not any(k in name for k in HARDENING_KEYWORDS): continue
        summary=obj.get('summary',{}) if isinstance(obj.get('summary'),dict) else {}
        pm=summary.get('primary_metric',{}) if isinstance(summary.get('primary_metric'),dict) else {}
        rows.append({
            'artifact':p.relative_to(ROOT).as_posix(),
            'probe':obj.get('probe',''),
            'language':obj.get('language',''),
            'row_count':len(obj.get('rows',[])) if isinstance(obj.get('rows'),list) else summary.get('row_count',0),
            'primary_metric':pm.get('name',''),
            'direction':pm.get('direction',''),
            'winner_summary':winner_summary(summary),
            'interpretation':summary.get('interpretation',''),
        })
    report={'project':'CloudtainerML','revision':REV,'probe':'native_hardening_report','summary':{'hardening_artifact_count':len(rows)},'rows':rows}
    prefix=OUT/f'{REVUP}_NATIVE_HARDENING_REPORT'
    prefix.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=[f'# Native hardening report — {REV}','',f'- artifacts: {len(rows)}','', '| artifact | probe | rows | metric | winners |','|---|---|---:|---|---|']
    for r in rows:
        md.append(f"| `{r['artifact']}` | {r['probe']} | {r['row_count']} | {r['primary_metric']} / {r['direction']} | {r['winner_summary']} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'status':'pass','hardening_artifact_count':len(rows)},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
