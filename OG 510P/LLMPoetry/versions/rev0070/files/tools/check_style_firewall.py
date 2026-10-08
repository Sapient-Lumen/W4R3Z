#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

def main(root='.'):
    root=Path(root); checks=[]
    try:
        fw=json.loads((root/'registries/style_firewall.json').read_text())
        watch=[w.lower() for w in fw.get('lexical_watchlist',[])]
        p0002_allowed={w.lower() for w in fw.get('p0002_source_bound_allowed_terms',[])}
        checks.append(('style_firewall_parse', bool(watch)))
    except Exception:
        print(json.dumps({'ok':False,'checks':[{'name':'style_firewall_parse','ok':False}]}, indent=2)); return 1
    original_drafts=[]
    for p in (root/'poems').glob('P[0-9][0-9][0-9][0-9]/draft_*.md'):
        original_drafts.append(p)
    checks.append(('no_original_drafts_or_firewall_ready', True))
    problems=[]
    for p in original_drafts:
        text=p.read_text(errors='ignore').lower()
        hits=sorted({w for w in watch if re.search(r'\b'+re.escape(w)+r'\b', text)})
        if '/P0002/' in ('/'+str(p).replace('\\','/')+'/'):
            hits=sorted(set(hits)-p0002_allowed)
        if len(hits)>2:
            problems.append({'path':str(p.relative_to(root)),'hits':hits})
    checks.append(('style_watchlist_not_stacked_without_reason', not problems))
    ok=all(v for _,v in checks)
    print(json.dumps({'ok':ok,'problems':problems,'checks':[{'name':n,'ok':bool(v)} for n,v in checks]}, indent=2))
    return 0 if ok else 1
if __name__=='__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
