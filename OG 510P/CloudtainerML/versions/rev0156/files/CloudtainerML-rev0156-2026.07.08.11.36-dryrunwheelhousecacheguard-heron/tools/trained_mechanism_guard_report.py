#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision','rev0037')
REVUP = REV.upper()
OUT = ROOT/'artifacts'/'dashboard'
OUT.mkdir(parents=True, exist_ok=True)

EXACT_KEYS = {'reachable_fraction','depth_reachable_fraction','target_miss','topk_depth_reachable_fraction','edge_recall','topk_edge_recall','copy_acc','final_acc'}
ROUTE_KEYS = {'route_error','gain_error','source_attention_mass','distractor_attention_mass','source_gain','distractor_gain','route_flip','deployment_gap'}
SPARSITY_KEYS = {'active_edge_count','topk_edge_f1','edge_f1_threshold_0p5','true_false_prob_gap','rare_miss','route_miss'}

def flatten_keys(obj):
    keys=set()
    if isinstance(obj, dict):
        for k,v in obj.items():
            keys.add(k)
            keys |= flatten_keys(v)
    elif isinstance(obj, list):
        for v in obj[:20]: keys |= flatten_keys(v)
    return keys

def main() -> int:
    rows=[]
    for p in sorted((ROOT/'artifacts'/'probe-results').glob(f'{REVUP}_*.json')):
        try: obj=json.loads(p.read_text(encoding='utf-8'))
        except Exception: continue
        kind=obj.get('kind','')
        probe=obj.get('probe',p.stem)
        if 'trained' not in kind and 'train' not in probe:
            continue
        keys=flatten_keys(obj)
        summary=obj.get('summary') if isinstance(obj.get('summary'),dict) else {}
        guard=set(summary.get('guard_fields',[])) if isinstance(summary.get('guard_fields'), list) else set()
        row={
            'artifact': str(p.relative_to(ROOT)),
            'probe': probe,
            'kind': kind,
            'has_primary_metric': isinstance(summary.get('primary_metric'), dict),
            'has_exactness_guard': bool((keys|guard) & EXACT_KEYS),
            'has_route_gain_guard': bool((keys|guard) & ROUTE_KEYS),
            'has_sparsity_guard': bool((keys|guard) & SPARSITY_KEYS),
            'row_count': len(obj.get('rows',[])) if isinstance(obj.get('rows'), list) else None,
            'guard_fields': sorted(guard),
        }
        row['guard_score']=sum(1 for k in ['has_primary_metric','has_exactness_guard','has_route_gain_guard','has_sparsity_guard'] if row[k])
        rows.append(row)
    report={
        'project':'CloudtainerML',
        'revision':REV,
        'report':'trained_mechanism_guard_report',
        'trained_artifact_count':len(rows),
        'guard_ready_count':sum(1 for r in rows if r['guard_score']>=3),
        'exactness_ready_count':sum(1 for r in rows if r['has_exactness_guard']),
        'route_gain_ready_count':sum(1 for r in rows if r['has_route_gain_guard']),
        'sparsity_ready_count':sum(1 for r in rows if r['has_sparsity_guard']),
        'rows':rows,
    }
    (OUT/f'{REVUP}_TRAINED_MECHANISM_GUARD_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=[f'# Trained mechanism guard report — {REV}', '', f'- trained artifacts: {len(rows)}', f'- guard-ready artifacts: {report["guard_ready_count"]}', f'- exactness-ready: {report["exactness_ready_count"]}', f'- route/gain-ready: {report["route_gain_ready_count"]}', f'- sparsity-ready: {report["sparsity_ready_count"]}', '', '## Artifacts', '']
    for r in rows:
        md.append(f"- `{r['probe']}` score={r['guard_score']} rows={r['row_count']} exact={r['has_exactness_guard']} route_gain={r['has_route_gain_guard']} sparsity={r['has_sparsity_guard']} artifact=`{r['artifact']}`")
    (OUT/f'{REVUP}_TRAINED_MECHANISM_GUARD_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    (OUT/f'{REVUP}_TRAINED_MECHANISM_GUARD_REPORT.html').write_text('<html><body><pre>'+('\n'.join(md)).replace('&','&amp;').replace('<','&lt;')+'</pre></body></html>',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['trained_artifact_count','guard_ready_count','exactness_ready_count','route_gain_ready_count','sparsity_ready_count']}, indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
