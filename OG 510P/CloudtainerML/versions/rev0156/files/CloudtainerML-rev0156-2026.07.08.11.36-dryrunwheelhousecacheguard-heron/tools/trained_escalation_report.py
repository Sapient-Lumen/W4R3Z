#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REV=json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0000')
REVUP=REV.upper()
OUT=ROOT/'artifacts'/'dashboard'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    records=[]
    for p in sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*.json')):
        try: obj=json.loads(p.read_text())
        except Exception: continue
        kind=obj.get('kind','')
        probe=obj.get('probe') or obj.get('probe_id') or p.stem
        summ=obj.get('summary',{}) if isinstance(obj.get('summary'),dict) else {}
        is_trained = kind=='trained_tiny_probe' or 'TRAIN' in p.name or 'training' in probe.lower()
        if is_trained:
            guards=summ.get('guard_fields') or summ.get('screen_regret_fields') or []
            agg=summ.get('aggregate',[])
            records.append({
                'path':str(p.relative_to(ROOT)),
                'probe':probe,
                'kind':kind or 'unknown',
                'has_primary_metric':isinstance(summ.get('primary_metric'),dict),
                'guard_field_count':len(guards),
                'aggregate_count':len(agg) if isinstance(agg,list) else 0,
                'winner':summ.get('winner_by_final_acc_then_speed') or summ.get('winner'),
            })
    payload={'project':'CloudtainerML','revision':REV,'report':'trained_escalation_report','summary':{'trained_current_artifacts':len(records),'primary_metric_ready':sum(1 for r in records if r['has_primary_metric']),'guarded':sum(1 for r in records if r['guard_field_count']>=4)},'records':records,'note':'Separates trained-tiny escalations from symbolic/native wind tunnels so the cube does not overstate toy screen evidence.'}
    (OUT/f'{REVUP}_TRAINED_ESCALATION_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=[f'# Trained escalation report — {REV}','','## Summary','']+[f'- {k}: {v}' for k,v in payload['summary'].items()]+['','## Records','']
    for r in records: md.append(f"- `{r['probe']}` → `{r['path']}` winner={r['winner']} metric={r['has_primary_metric']} guards={r['guard_field_count']}")
    (OUT/f'{REVUP}_TRAINED_ESCALATION_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(payload['summary'],indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
