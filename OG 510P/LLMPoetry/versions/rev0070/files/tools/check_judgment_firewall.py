#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

def run(root: Path):
    checks=[]
    state=json.loads((root/'STATE.json').read_text(encoding='utf-8'))
    current_turn=state.get('turn',{}).get('last_completed')
    add(checks,'state_current_turn_present', isinstance(current_turn,int), str(current_turn))
    judgments=[]
    for p in sorted((root/'poems').glob('P[0-9][0-9][0-9][0-9]/judgments/*.json')):
        try:
            obj=json.loads(p.read_text(encoding='utf-8'))
            obj['_path']=p.relative_to(root).as_posix()
            judgments.append(obj)
            add(checks,f'judgment_parse:{obj["_path"]}', True)
        except Exception as e:
            add(checks,f'judgment_parse:{p.relative_to(root).as_posix()}', False, str(e))
    for j in judgments:
        ct=j.get('created_turn'); tt=j.get('target_created_turn')
        ok=isinstance(ct,int) and isinstance(tt,int) and ct>tt and j.get('firewall_ok') is True
        add(checks,f'no_same_turn_judgment:{j.get("judgment_id",j.get("_path"))}', ok, f'created_turn={ct} target_created_turn={tt}')
    # Also inspect metadata embedded judgments.
    for meta_path in sorted((root/'poems').glob('P[0-9][0-9][0-9][0-9]/metadata.json')):
        try:
            meta=json.loads(meta_path.read_text(encoding='utf-8'))
            for j in meta.get('judgments',[]):
                ct=j.get('created_turn'); tt=j.get('target_created_turn')
                ok=isinstance(ct,int) and isinstance(tt,int) and ct>tt and j.get('firewall_ok') is True
                add(checks,f'metadata_no_same_turn_judgment:{j.get("judgment_id",meta_path.parent.name)}', ok, f'created_turn={ct} target_created_turn={tt}')
            latest=meta.get('drafts',[])[-1] if meta.get('drafts') else None
            if latest and latest.get('created_turn')==current_turn:
                bad=[j.get('judgment_id') for j in meta.get('judgments',[]) if j.get('draft_id')==latest.get('draft_id')]
                add(checks,f'latest_draft_unjudged_same_turn:{latest.get("draft_id")}', not bad, f'bad={bad}')
        except Exception as e:
            add(checks,f'metadata_judgment_scan:{meta_path.relative_to(root).as_posix()}', False, str(e))
    return checks

def main(root='.'):
    checks=run(Path(root))
    ok=all(c['ok'] for c in checks)
    print(json.dumps({'ok':ok,'checks':checks,'failed':[c for c in checks if not c['ok']]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__=='__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
