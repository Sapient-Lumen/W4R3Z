#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

def main(root='.'):
    root=Path(root); checks=[]
    try:
        obj=json.loads((root/'registries/human_questions.json').read_text())
        qs=obj.get('questions',[])
        checks.append(('human_questions_parse', isinstance(qs,list)))
        checks.append(('human_questions_have_defaults', all(q.get('default_until_answered') for q in qs)))
        checks.append(('nonblocking_or_reasoned', all(q.get('blocks_work') is False or q.get('blocking_reason') for q in qs)))
    except Exception:
        checks.append(('human_questions_parse', False))
    checks.append(('human_questions_md_present', (root/'HUMAN_QUESTIONS.md').exists()))
    ok=all(v for _,v in checks)
    print(json.dumps({'ok':ok,'checks':[{'name':n,'ok':bool(v)} for n,v in checks]}, indent=2))
    return 0 if ok else 1
if __name__=='__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
