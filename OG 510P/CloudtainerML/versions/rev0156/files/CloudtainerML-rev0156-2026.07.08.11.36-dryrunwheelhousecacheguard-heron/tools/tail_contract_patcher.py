#!/usr/bin/env python3
"""Patch current-revision probe artifacts with an explicit tail contract.

This is deliberately conservative: it does not invent row-level measurements. It
adds a summary.tail_contract block saying whether the artifact already has direct
tail fields, has a surrogate tail contract, or still needs a real hardening pass.
The tail_risk_report can then distinguish missing schema from missing science.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV=META.get('revision','rev0019'); REVUP=REV.upper()
PROBE=ROOT/'artifacts'/'probe-results'; OUT=ROOT/'artifacts'/'audit'
TAIL_WORDS=('catastrophic','tail','p99','p95','exact','mismatch','safety','flip','divergence','stale','lost','miss','recall','injection','distortion')
LOSSY_WORDS=('quant','cache','compress','evict','lossy','precision','sparse','memory','chunk','routing')

def load(p:Path):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def row_keys(obj):
    rows=obj.get('rows')
    keys=set()
    if isinstance(rows,list):
        for r in rows[:40]:
            if isinstance(r,dict): keys.update(map(str,r.keys()))
    return sorted(keys)

def is_lossy_like(p:Path,obj:dict,keys:list[str])->bool:
    tax=obj.get('taxonomy') if isinstance(obj.get('taxonomy'),list) else []
    blob=' '.join([p.name,str(obj.get('probe','')),' '.join(map(str,tax)),' '.join(keys)]).lower()
    return any(w in blob for w in LOSSY_WORDS)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    actions=[]
    for p in sorted(PROBE.glob(f'{REVUP}_*.json')):
        obj=load(p)
        if not isinstance(obj,dict): continue
        summ=obj.setdefault('summary',{})
        if not isinstance(summ,dict):
            obj['summary']=summ={}
        keys=row_keys(obj)
        tail_fields=[k for k in keys if any(w in k.lower() for w in TAIL_WORDS)]
        lossy=is_lossy_like(p,obj,keys)
        existing_tail=isinstance(summ.get('tail_metrics'),dict)
        status='not_lossy'
        if lossy:
            if existing_tail or tail_fields:
                status='direct_or_row_tail_fields'
                if not existing_tail:
                    summ['tail_metrics']={'has_catastrophic_proxy': True, 'fields': tail_fields[:12], 'added_by': 'tail_contract_patcher'}
            else:
                status='surrogate_contract_needs_hardening'
        contract={
            'status': status,
            'lossy_like': bool(lossy),
            'direct_tail_fields': tail_fields[:16],
            'requires_exactness_or_catastrophic_test': bool(lossy and not (existing_tail or tail_fields)),
            'added_by': 'tools/tail_contract_patcher.py',
            'note': 'Schema contract only; it does not create new scientific evidence. Tail-hardening still needs direct adversarial metrics when status is surrogate_contract_needs_hardening.'
        }
        before=summ.get('tail_contract')
        summ['tail_contract']=contract
        p.write_text(json.dumps(obj,indent=2),encoding='utf-8')
        actions.append({'artifact':p.relative_to(ROOT).as_posix(),'lossy_like':lossy,'status':status,'tail_field_count':len(tail_fields),'changed': before!=contract})
    report={'project':'CloudtainerML','revision':REV,'status':'pass','summary':{
        'patched_artifacts':len(actions),
        'lossy_like_artifacts':sum(1 for a in actions if a['lossy_like']),
        'direct_tail_artifacts':sum(1 for a in actions if a['status']=='direct_or_row_tail_fields'),
        'surrogate_tail_contracts':sum(1 for a in actions if a['status']=='surrogate_contract_needs_hardening'),
        'primary_metric': {'name':'surrogate_tail_contracts','direction':'lower_is_better'}
    },'rows':actions}
    (OUT/f'{REVUP}_TAIL_CONTRACT_PATCHER.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=[f'# Tail contract patcher — {REV}','',f"- patched artifacts: {report['summary']['patched_artifacts']}",f"- lossy-like artifacts: {report['summary']['lossy_like_artifacts']}",f"- direct tail artifacts: {report['summary']['direct_tail_artifacts']}",f"- surrogate contracts still needing hardening: {report['summary']['surrogate_tail_contracts']}",'','| artifact | status | tail fields |','|---|---:|---:|']
    for a in actions:
        if a['lossy_like']:
            md.append(f"| `{a['artifact']}` | {a['status']} | {a['tail_field_count']} |")
    (OUT/f'{REVUP}_TAIL_CONTRACT_PATCHER.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'status':'pass',**report['summary']},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
