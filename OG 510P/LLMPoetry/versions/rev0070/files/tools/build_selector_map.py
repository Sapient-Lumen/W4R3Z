#!/usr/bin/env python3
"""Build a selector-map receipt for selected branch lines in a rendered draft."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('packet'); ap.add_argument('draft'); ap.add_argument('--out', required=True)
    args = ap.parse_args()
    packet=json.loads(Path(args.packet).read_text(encoding='utf-8')); text=Path(args.draft).read_text(encoding='utf-8')
    selectors=[]
    for layer in packet.get('layers', []):
        selected=[c for c in layer.get('candidates', []) if c.get('selected') is True]
        if len(selected)!=1: raise SystemExit(f"layer {layer.get('layer_id')} has {len(selected)} selected candidates")
        c=selected[0]; exact=f"{c.get('candidate_id')} {c.get('text')}"; start=text.find(exact)
        if start<0: raise SystemExit(f"selected line not found: {exact}")
        end=start+len(exact)
        selectors.append({'layer_id':layer.get('layer_id'),'candidate_id':c.get('candidate_id'),'selector_type':'TextQuoteSelector+TextPositionSelector-inspired','exact':exact,'start':start,'end':end,'prefix':text[max(0,start-40):start],'suffix':text[end:min(len(text),end+40)],'source':str(Path(args.draft).as_posix())})
    out={'schema':'llmpoetry-selector-map-v1','poem_id':packet.get('poem_id'),'draft_id':packet.get('draft_id'),'revision':packet.get('revision'),'turn':packet.get('turn'),'source_path':str(Path(args.draft).as_posix()),'inspired_by':'W3C Web Annotation TextQuoteSelector and TextPositionSelector patterns; not a full Web Annotation serialization.','selectors':selectors,'non_claim':'Selector positions prove selected branch lines are addressable in this rendered draft; they do not prove poem quality.'}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True); Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'selector_count': len(selectors)}, indent=2))
if __name__ == '__main__': main()
