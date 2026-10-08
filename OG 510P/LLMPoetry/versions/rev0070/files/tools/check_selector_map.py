#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
def add(checks,name,ok,detail=''): checks.append({'name':name,'ok':bool(ok),'detail':detail})
def run(root: Path):
    checks=[]; files=list(root.glob('poems/P*/verification/selector_map_*.json'))
    for rel in sorted(files):
        rels=rel.relative_to(root).as_posix()
        try: obj=json.loads(rel.read_text(encoding='utf-8')); add(checks,f'{rels}:parse',True)
        except Exception as e: add(checks,f'{rels}:parse',False,str(e)); continue
        source_path=root/obj.get('source_path',''); add(checks,f'{rels}:source_exists',source_path.exists(),obj.get('source_path',''))
        if not source_path.exists(): continue
        text=source_path.read_text(encoding='utf-8',errors='replace'); seen=[]
        for i,sel in enumerate(obj.get('selectors', [])):
            exact=sel.get('exact',''); start=sel.get('start'); end=sel.get('end'); name=f'{rels}:selector:{i}:{sel.get("candidate_id")}'
            add(checks,name+':exact_nonempty',bool(exact))
            add(checks,name+':positions_valid',isinstance(start,int) and isinstance(end,int) and 0 <= start < end <= len(text),f'{start}:{end}')
            if isinstance(start,int) and isinstance(end,int) and 0 <= start < end <= len(text):
                add(checks,name+':position_matches_exact',text[start:end]==exact)
                add(checks,name+':exact_occurs_at_or_before_position',text.find(exact) <= start and text.find(exact) >= 0,f'first={text.find(exact)} start={start}')
                seen.append((start,end))
        add(checks,f'{rels}:selectors_present',len(obj.get('selectors', []))>=1)
        add(checks,f'{rels}:selector_positions_unique',len(seen)==len(set(seen)))
    add(checks,'selector_map_file_present',bool(files))
    return checks
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); args=ap.parse_args(); checks=run(Path(args.root)); ok=all(c['ok'] for c in checks)
    print(json.dumps({'ok':ok,'checks':checks,'failed':[c for c in checks if not c['ok']]}, indent=2, ensure_ascii=False)); return 0 if ok else 1
if __name__=='__main__': sys.exit(main())
