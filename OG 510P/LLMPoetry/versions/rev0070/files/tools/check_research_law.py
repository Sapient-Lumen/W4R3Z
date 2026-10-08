#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

SURFACES = ['START_HERE.md','AGENTS.md','docs/00-office/BOOT_CARD.md','docs/00-office/RESEARCH_EVERY_TURN_LAW.md','docs/10-method/RESEARCH_POLICY.md','CONTEXT_PACK.json','FRONTIER_TICKET.json']
NEEDLES = ['web research','web pulse','Every LLMPoetry turn','research pulse']

def main(root='.'):
    root=Path(root)
    checks=[]
    law=root/'registries/research_law.json'
    try:
        obj=json.loads(law.read_text())
        checks.append(('research_law_json', obj.get('law_id')=='LAW-R1'))
        checks.append(('research_law_scope_every_turn', 'Every LLMPoetry' in obj.get('scope','') or 'Every LLMPoetry' in obj.get('requirement','')))
        checks.append(('research_law_enforcement_declared', bool(obj.get('enforcement'))))
    except Exception:
        checks.append(('research_law_json', False))
    for rel in SURFACES:
        p=root/rel
        text=p.read_text(errors='ignore') if p.exists() else ''
        checks.append((f'propagated:{rel}', p.exists() and any(n in text for n in NEEDLES)))
    ok=all(v for _,v in checks)
    print(json.dumps({'ok':ok,'checks':[{'name':n,'ok':v} for n,v in checks]}, indent=2))
    return 0 if ok else 1
if __name__=='__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
