#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT/'CUBE-META.json').exists() else {}
REV = META.get('revision','rev0020'); REVUP=REV.upper()
DASH = ROOT/'artifacts'/'dashboard'; DASH.mkdir(parents=True, exist_ok=True)
KEYWORDS = ['poison','trust','provenance','memory','safety','alignment','contract','evidence','state']
TAIL_FIELDS = ['attack_success_rate','mean_poisoned_read_fraction','catastrophic_contract_failure_rate','catastrophic_state_failure_rate','catastrophic_evidence_failure_rate','stale_invalidation_miss_rate','contamination_read_rate','safety_flip_rate','catastrophic_mismatch_rate']

def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def relevant(obj,path):
    s=' '.join([str(obj.get('probe','')), ' '.join(obj.get('taxonomy',[]) if isinstance(obj.get('taxonomy'),list) else []), path.name]).lower()
    return any(k in s for k in KEYWORDS)

def main():
    records=[]
    for path in sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*.json')):
        if 'PROBE_SUITE' in path.name: continue
        obj=load(path)
        if not isinstance(obj,dict) or not relevant(obj,path): continue
        rows=obj.get('rows') if isinstance(obj.get('rows'),list) else []
        fields=set()
        for r in rows[:50]:
            if isinstance(r,dict): fields.update(r.keys())
        tail=[f for f in TAIL_FIELDS if f in fields]
        summary=obj.get('summary') if isinstance(obj.get('summary'),dict) else {}
        records.append({
            'artifact': str(path.relative_to(ROOT)),
            'probe': obj.get('probe',path.stem),
            'taxonomy': obj.get('taxonomy',[]),
            'rows': len(rows),
            'has_tail_metrics_block': isinstance(summary.get('tail_metrics'),dict),
            'tail_fields_present': tail,
            'tail_ready': bool(tail) or isinstance(summary.get('tail_metrics'),dict),
            'primary_metric': (summary.get('primary_metric') or {}).get('name') if isinstance(summary.get('primary_metric'),dict) else None,
        })
    summary={
        'memory_safety_artifacts': len(records),
        'tail_ready_count': sum(1 for r in records if r['tail_ready']),
        'missing_tail_count': sum(1 for r in records if not r['tail_ready']),
        'current_revision': REV,
    }
    payload={'project':'CloudtainerML','revision':REV,'probe':'memory_safety_report','summary':summary,'records':records,
             'note':'Aggregates current-revision memory/trust/provenance/safety probes and checks whether they expose attack/tail/catastrophic fields.'}
    pref=DASH/f'{REVUP}_MEMORY_SAFETY_REPORT'
    (pref.with_suffix('.json')).write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=[f'# Memory safety report — {REV}','',f'- memory/safety artifacts: {summary["memory_safety_artifacts"]}',f'- tail-ready: {summary["tail_ready_count"]}',f'- missing tail contract: {summary["missing_tail_count"]}','','## Records']
    for r in records:
        md.append(f"- `{r['probe']}` rows={r['rows']} tail_ready={r['tail_ready']} fields={', '.join(r['tail_fields_present']) or '-'}")
    (pref.with_suffix('.md')).write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
