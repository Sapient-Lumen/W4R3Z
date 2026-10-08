#!/usr/bin/env python3
"""Tail-risk audit for CloudtainerML probe artifacts.

The cube now contains many lossy-cache or memory-selection probes. Mean metrics
alone can hide rare but decisive failures, so this report finds probe artifacts
with catastrophic/tail/exactness fields and lists where the contract is missing.
"""
from __future__ import annotations
import csv, html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REV=json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0019')
REVUP=REV.upper()
OUT=ROOT/'artifacts'/'dashboard'
PROBE=ROOT/'artifacts'/'probe-results'
TAIL_WORDS=('catastrophic','tail','p99','p95','exact','mismatch','safety','flip','divergence','stale')
LOSSY_WORDS=('quant','cache','compress','evict','lossy','precision','kvarn','vericache','sparse','memory')

def load(p:Path):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def keys_in_rows(rows):
    keys=set()
    for r in rows[:20] if isinstance(rows,list) else []:
        if isinstance(r,dict): keys.update(r.keys())
    return sorted(keys)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows=[]
    for p in sorted(PROBE.glob(f'{REVUP}_*.json')):
        obj=load(p)
        if not isinstance(obj,dict): continue
        summ=obj.get('summary') if isinstance(obj.get('summary'),dict) else {}
        probe=str(obj.get('probe',''))
        tax=[str(x) for x in obj.get('taxonomy',[]) if isinstance(obj.get('taxonomy',[]),list)]
        row_keys=keys_in_rows(obj.get('rows',[]))
        blob=' '.join([p.name, probe, ' '.join(tax), ' '.join(row_keys)]).lower()
        is_lossy=any(w in blob for w in LOSSY_WORDS)
        tail_fields=[k for k in row_keys if any(w in k.lower() for w in TAIL_WORDS)]
        summary_tail=summ.get('tail_metrics') if isinstance(summ.get('tail_metrics'),dict) else None
        summary_contract=summ.get('tail_contract') if isinstance(summ.get('tail_contract'),dict) else None
        primary=summ.get('primary_metric') if isinstance(summ.get('primary_metric'),dict) else {}
        rows.append({
            'artifact':p.relative_to(ROOT).as_posix(),
            'probe':probe,
            'taxonomy':';'.join(tax),
            'lossy_like':is_lossy,
            'row_count': len(obj.get('rows',[])) if isinstance(obj.get('rows'),list) else summ.get('row_count',0),
            'primary_metric': primary.get('name',''),
            'tail_field_count':len(tail_fields),
            'tail_fields':';'.join(tail_fields[:12]),
            'summary_tail_contract': bool(summary_tail or summary_contract),
            'status': 'tail-ready' if tail_fields or summary_tail else ('surrogate-tail-contract' if summary_contract and is_lossy else ('missing-tail-contract' if is_lossy else 'not-lossy'))
        })
    payload={'project':'CloudtainerML','revision':REV,'probe':'tail_risk_report','summary':{
        'artifact_count':len(rows),
        'lossy_like_count':sum(1 for r in rows if r['lossy_like']),
        'tail_ready_count':sum(1 for r in rows if r['status']=='tail-ready'),
        'lossy_missing_tail_contract':sum(1 for r in rows if r['status']=='missing-tail-contract'),
        'primary_metric': {'name':'lossy_missing_tail_contract','direction':'lower_is_better'}
    },'rows':rows}
    prefix=OUT/f'{REVUP}_TAIL_RISK_REPORT'
    prefix.with_suffix('.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    with prefix.with_suffix('.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()) if rows else ['artifact'])
        writer.writeheader(); writer.writerows(rows)
    md=[f'# Tail-risk report — {REV}','',f"- artifacts: {len(rows)}",f"- lossy-like artifacts: {payload['summary']['lossy_like_count']}",f"- tail-ready artifacts: {payload['summary']['tail_ready_count']}",f"- lossy missing tail contract: {payload['summary']['lossy_missing_tail_contract']}",'','| artifact | probe | status | tail fields |','|---|---|---|---|']
    for r in rows:
        if r['lossy_like'] or r['status']=='tail-ready':
            md.append(f"| `{r['artifact']}` | {r['probe']} | {r['status']} | {r['tail_fields']} |")
    prefix.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    trs=''.join('<tr>'+''.join(f'<td>{html.escape(str(r[k]))}</td>' for k in ['artifact','probe','status','tail_fields'])+'</tr>' for r in rows if r['lossy_like'] or r['status']=='tail-ready')
    prefix.with_suffix('.html').write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>Tail Risk {REV}</title><style>body{{font-family:system-ui,sans-serif;max-width:1200px;margin:2rem auto}}td,th{{border:1px solid #bbb;padding:.35rem}}table{{border-collapse:collapse;width:100%}}</style></head><body><h1>Tail-risk report — {REV}</h1><p>Lossy missing tail contract: {payload['summary']['lossy_missing_tail_contract']}</p><table><tr><th>artifact</th><th>probe</th><th>status</th><th>tail fields</th></tr>{trs}</table></body></html>",encoding='utf-8')
    print(json.dumps({'status':'pass', **payload['summary']},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
