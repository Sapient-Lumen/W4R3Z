#!/usr/bin/env python3
"""Build a return-diff receipt for LLMPoetry changed-return drafts.

The receipt treats a new draft as a return from a previous route instruction.
It proves only local consistency: the previous selected surface changed, the
previous route sentence is present, and the current route sentence is recovered
by the current packet's traversal algorithm.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def words(text: str) -> list[str]:
    return WORD_RE.findall(text)

def final_word(text: str) -> str:
    w = words(text)
    return w[-1].lower() if w else ''

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def selected_lines(packet: dict) -> list[dict]:
    out=[]
    for idx, layer in enumerate(packet.get('layers', [])):
        selected=[c for c in layer.get('candidates', []) if c.get('selected') is True]
        if len(selected)!=1:
            raise SystemExit(f"layer {layer.get('layer_id')} has {len(selected)} selected candidates")
        c=selected[0]
        exact=f"{c.get('candidate_id')} {c.get('text')}"
        out.append({'index':idx,'layer_id':layer.get('layer_id'),'candidate_id':c.get('candidate_id'),'text':c.get('text',''),'exact':exact,'final_word':final_word(c.get('text','')),'sha256':sha256_text(exact)})
    return out

def route_sentence(packet: dict) -> str:
    route=[]
    for layer in packet.get('layers', []):
        selected=[c for c in layer.get('candidates', []) if c.get('selected') is True][0]
        omitted=[c for c in layer.get('candidates', []) if c.get('selected') is not True]
        idx=len(final_word(selected.get('text',''))) % len(omitted)
        route.append(final_word(omitted[idx].get('text','')))
    return ' '.join(route)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('previous_packet')
    ap.add_argument('current_packet')
    ap.add_argument('current_draft')
    ap.add_argument('--previous-route-receipt', required=True)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()
    prev_path=Path(args.previous_packet); cur_path=Path(args.current_packet); draft_path=Path(args.current_draft); prev_route_path=Path(args.previous_route_receipt)
    prev=json.loads(prev_path.read_text(encoding='utf-8'))
    cur=json.loads(cur_path.read_text(encoding='utf-8'))
    draft=draft_path.read_text(encoding='utf-8', errors='replace')
    prev_route=json.loads(prev_route_path.read_text(encoding='utf-8'))
    prev_lines=selected_lines(prev); cur_lines=selected_lines(cur)
    pairs=[]
    for i, (old, new) in enumerate(zip(prev_lines, cur_lines)):
        pairs.append({'index':i,'previous':old,'current':new,'changed':old.get('exact') != new.get('exact')})
    old_route=prev_route.get('route_sentence') or prev_route.get('traversal_sentence') or prev_route.get('traversed_state',{}).get('route_sentence')
    cur_route=route_sentence(cur)
    out={
        'schema':'llmpoetry-return-diff-v1',
        'poem_id':cur.get('poem_id'),
        'previous_draft_id':prev.get('draft_id'),
        'current_draft_id':cur.get('draft_id'),
        'revision':cur.get('revision'),
        'turn':cur.get('turn'),
        'form_id':cur.get('form_id'),
        'previous_packet_path':prev_path.as_posix(),
        'current_packet_path':cur_path.as_posix(),
        'current_draft_path':draft_path.as_posix(),
        'previous_route_receipt_path':prev_route_path.as_posix(),
        'previous_route_sentence':old_route,
        'previous_instruction_required_phrase':'return changed',
        'current_route_sentence':cur_route,
        'current_route_claim':cur.get('traversal_sentence_claim'),
        'current_route_matches_claim':cur_route == cur.get('traversal_sentence_claim'),
        'current_route_contains_changed_again':'return changed again' in cur_route,
        'line_count_previous':len(prev_lines),
        'line_count_current':len(cur_lines),
        'line_count_preserved':len(prev_lines)==len(cur_lines),
        'all_selected_lines_changed':all(p.get('changed') for p in pairs) and len(prev_lines)==len(cur_lines),
        'changed_pair_count':sum(1 for p in pairs if p.get('changed')),
        'pairs':pairs,
        'current_draft_contains_current_route':cur_route in draft,
        'current_draft_mentions_return_diff':'return_diff_009.json' in draft or 'return-diff' in draft.lower(),
        'previous_instruction_fulfilled':bool(old_route and 'return changed' in old_route and cur_route == cur.get('traversal_sentence_claim') and all(p.get('changed') for p in pairs)),
        'non_claim':'Return-diff consistency proves a changed selected surface and route handoff only; it does not prove poem quality.'
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'current_draft_id': out['current_draft_id'], 'current_route_sentence': cur_route, 'changed_pair_count': out['changed_pair_count']}, indent=2, ensure_ascii=False))
if __name__ == '__main__':
    main()
