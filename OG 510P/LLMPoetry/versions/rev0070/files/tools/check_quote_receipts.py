#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

def main(root='.'):
    root=Path(root)
    checks=[]
    try:
        q=json.loads((root/'registries/quote_search_receipts.json').read_text())
        checks.append(('quote_receipts_parse', isinstance(q.get('receipts'), list)))
    except Exception:
        checks.append(('quote_receipts_parse', False))
    try:
        s=json.loads((root/'registries/source_receipts.json').read_text())
        checks.append(('source_receipts_parse', isinstance(s.get('receipts'), list)))
    except Exception:
        checks.append(('source_receipts_parse', False))
    try:
        poems=json.loads((root/'registries/poem_index.json').read_text()).get('poems', [])
        evidence=[p for p in poems if p.get('status') in {'evidence_candidate','admitted'}]
        checks.append(('no_evidence_poems_without_receipts_current_revision', len(evidence)==0))
    except Exception:
        checks.append(('poem_index_parse', False))
    ok=all(v for _,v in checks)
    print(json.dumps({'ok':ok,'checks':[{'name':n,'ok':v} for n,v in checks]}, indent=2))
    return 0 if ok else 1
if __name__=='__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
