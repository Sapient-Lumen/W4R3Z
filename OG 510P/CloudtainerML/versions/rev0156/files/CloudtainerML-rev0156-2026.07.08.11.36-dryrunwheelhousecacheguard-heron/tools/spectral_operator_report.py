#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text()) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0000'}
REV=META.get('revision','rev0000'); REVUP=REV.upper()
PROBE=ROOT/'artifacts'/'probe-results'; DASH=ROOT/'artifacts'/'dashboard'; DASH.mkdir(parents=True,exist_ok=True)
KEYS=('spectral_operator','dct','operator_routing','sparse_lowrank_hybrid','meta_attention')
rows=[]
for p in sorted(PROBE.glob(f'{REVUP}_*_SMOKE.json')):
    try: obj=json.loads(p.read_text())
    except Exception: continue
    probe=str(obj.get('probe',p.stem)).lower()
    if not any(k in probe or k in p.name.lower() for k in KEYS):
        continue
    sm=obj.get('summary',{}) if isinstance(obj.get('summary'),dict) else {}
    data=obj.get('rows',[]) if isinstance(obj.get('rows'),list) else []
    fields=set()
    for r in data[:200]:
        if isinstance(r,dict): fields |= set(r.keys())
    winners=sm.get('nonoracle_winner_counts') or sm.get('winner_counts') or {}
    rows.append({
        'artifact':p.relative_to(ROOT).as_posix(),
        'probe':obj.get('probe'),
        'fresh':not bool(sm.get('carry_forward_from')),
        'carry_forward_from':sm.get('carry_forward_from'),
        'row_count':len(data),
        'primary_metric':(sm.get('primary_metric') or {}).get('name'),
        'winner_diversity':len(winners) if isinstance(winners,dict) else 0,
        'winner_counts':winners,
        'has_alias_field':'alias_error' in fields,
        'has_tail_field':'tail_miss' in fields,
        'has_budget_field': bool({'cost_frac','budget_over','budget_pct'} & fields),
        'has_regret_field':'regret' in fields,
        'readiness': (2 if not sm.get('carry_forward_from') else 0)+min(3,len(winners) if isinstance(winners,dict) else 0)+(1 if 'alias_error' in fields else 0)+(1 if 'tail_miss' in fields else 0)+(1 if 'regret' in fields else 0)+(1 if len(data)>=500 else 0),
        'interpretation':str(sm.get('interpretation',''))[:500],
    })
rows.sort(key=lambda r:(r['fresh'],r['readiness'],r['row_count']), reverse=True)
report={'project':'CloudtainerML','revision':REV,'probe':'spectral_operator_report','status':'pass','purpose':'Compare spectral/operator-routing probes on freshness, held-out/HPO pressure, winner diversity, and alias/tail/regret guard fields.','summary':{'spectral_family_artifacts':len(rows),'fresh_spectral_artifacts':sum(1 for r in rows if r['fresh']),'top_candidates':rows[:8]},'rows':rows}
base=DASH/f'{REVUP}_SPECTRAL_OPERATOR_REPORT'
base.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md=[f'# Spectral/operator report — {REV}','','Status: **pass**','',f"Family artifacts: {len(rows)}",f"Fresh artifacts: {report['summary']['fresh_spectral_artifacts']}",'','| probe | fresh | rows | readiness | winners | alias | tail | regret |','|---|---:|---:|---:|---:|---:|---:|---:|']
for r in rows[:80]:
    md.append(f"| `{r['probe']}` | {int(r['fresh'])} | {r['row_count']} | {r['readiness']} | {r['winner_diversity']} | {int(r['has_alias_field'])} | {int(r['has_tail_field'])} | {int(r['has_regret_field'])} |")
base.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'status':'pass','spectral_family_artifacts':len(rows),'fresh_spectral_artifacts':report['summary']['fresh_spectral_artifacts']},indent=2))
