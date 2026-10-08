#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

def main(root='.'):
    root=Path(root); checks=[]; problems=[]
    dirs=[p for p in (root/'poems').iterdir() if p.is_dir() and re.match(r'P\d{4}', p.name)]
    checks.append(('poem_dirs_scan', True))
    for d in dirs:
        meta=d/'metadata.json'
        if not meta.exists():
            problems.append({'dir':str(d.relative_to(root)),'problem':'missing metadata.json'}); continue
        try:
            obj=json.loads(meta.read_text())
            pid=obj.get('poem_id')
            if not d.name.startswith(pid): problems.append({'dir':str(d.relative_to(root)),'problem':'poem_id mismatch'})
            for dr in obj.get('drafts',[]):
                path=root/dr.get('path','')
                if not path.exists(): problems.append({'dir':str(d.relative_to(root)),'problem':'draft path missing','path':dr.get('path')})
        except Exception as e:
            problems.append({'dir':str(d.relative_to(root)),'problem':'metadata parse','detail':str(e)})
    checks.append(('poem_records_consistent', not problems))
    ok=all(v for _,v in checks)
    print(json.dumps({'ok':ok,'problems':problems,'checks':[{'name':n,'ok':bool(v)} for n,v in checks]}, indent=2))
    return 0 if ok else 1
if __name__=='__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
