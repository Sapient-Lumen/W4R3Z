#!/usr/bin/env python3
"""Validate LLMPoetry return-diff receipts."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
WORD_RE=re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def words(text): return WORD_RE.findall(text)
def final_word(text):
    w=words(text); return w[-1].lower() if w else ''
def sha256_text(text): return hashlib.sha256(text.encode('utf-8')).hexdigest()
def add(checks,name,ok,detail=''): checks.append({'name':name,'ok':bool(ok),'detail':detail})
def selected_lines(packet):
    out=[]
    for idx, layer in enumerate(packet.get('layers', [])):
        sels=[c for c in layer.get('candidates', []) if c.get('selected') is True]
        if len(sels)!=1: raise ValueError(f"{layer.get('layer_id')} selected count {len(sels)}")
        c=sels[0]; exact=f"{c.get('candidate_id')} {c.get('text')}"
        out.append({'index':idx,'layer_id':layer.get('layer_id'),'candidate_id':c.get('candidate_id'),'text':c.get('text',''),'exact':exact,'final_word':final_word(c.get('text','')),'sha256':sha256_text(exact)})
    return out
def route_sentence(packet):
    out=[]
    for layer in packet.get('layers', []):
        sels=[c for c in layer.get('candidates', []) if c.get('selected') is True]
        omitted=[c for c in layer.get('candidates', []) if c.get('selected') is not True]
        if len(sels)!=1 or not omitted: continue
        idx=len(final_word(sels[0].get('text',''))) % len(omitted)
        out.append(final_word(omitted[idx].get('text','')))
    return ' '.join(out)

def run(root: Path):
    checks=[]; files=sorted(root.glob('poems/P*/verification/return_diff_*.json'))
    add(checks,'return_diff_file_present',bool(files))
    for rp in files:
        rel=rp.relative_to(root).as_posix()
        try:
            obj=json.loads(rp.read_text(encoding='utf-8')); add(checks,f'{rel}:parse',True)
        except Exception as e:
            add(checks,f'{rel}:parse',False,str(e)); continue
        prev_path=root/obj.get('previous_packet_path',''); cur_path=root/obj.get('current_packet_path',''); draft_path=root/obj.get('current_draft_path',''); prev_route_path=root/obj.get('previous_route_receipt_path','')
        for label,path in [('previous_packet',prev_path),('current_packet',cur_path),('current_draft',draft_path),('previous_route_receipt',prev_route_path)]:
            add(checks,f'{rel}:{label}_exists',path.exists(),str(path.relative_to(root)) if path.exists() else str(path))
        if not (prev_path.exists() and cur_path.exists() and draft_path.exists() and prev_route_path.exists()): continue
        prev=json.loads(prev_path.read_text(encoding='utf-8')); cur=json.loads(cur_path.read_text(encoding='utf-8')); draft=draft_path.read_text(encoding='utf-8',errors='replace'); prev_route=json.loads(prev_route_path.read_text(encoding='utf-8'))
        add(checks,f'{rel}:current_packet_declares_path',cur.get('return_diff_path')==rel,cur.get('return_diff_path'))
        old_route=prev_route.get('route_sentence') or prev_route.get('traversal_sentence') or prev_route.get('traversed_state',{}).get('route_sentence')
        cur_route=route_sentence(cur)
        add(checks,f'{rel}:previous_route_sentence_matches_receipt',obj.get('previous_route_sentence')==old_route,old_route)
        add(checks,f'{rel}:previous_route_requires_changed','return changed' in (old_route or ''),old_route or '')
        add(checks,f'{rel}:current_route_recomputed',obj.get('current_route_sentence')==cur_route,cur_route)
        add(checks,f'{rel}:current_route_matches_claim',obj.get('current_route_matches_claim') is True and cur.get('traversal_sentence_claim')==cur_route,cur.get('traversal_sentence_claim'))
        prev_lines=selected_lines(prev); cur_lines=selected_lines(cur)
        add(checks,f'{rel}:line_count_preserved',obj.get('line_count_preserved') is True and len(prev_lines)==len(cur_lines),f'{len(prev_lines)}->{len(cur_lines)}')
        pairs=obj.get('pairs',[])
        add(checks,f'{rel}:pair_count_matches',len(pairs)==len(prev_lines)==len(cur_lines),f'pairs={len(pairs)}')
        changed=[]
        for i,(old,new) in enumerate(zip(prev_lines,cur_lines)):
            got=pairs[i] if i < len(pairs) else {}
            changed.append(old.get('exact')!=new.get('exact'))
            add(checks,f'{rel}:pair:{i}:previous_hash',got.get('previous',{}).get('sha256')==old.get('sha256'))
            add(checks,f'{rel}:pair:{i}:current_hash',got.get('current',{}).get('sha256')==new.get('sha256'))
            add(checks,f'{rel}:pair:{i}:changed_flag',got.get('changed')==(old.get('exact')!=new.get('exact')))
            add(checks,f'{rel}:pair:{i}:current_line_in_draft',new.get('exact') in draft,new.get('exact'))
        add(checks,f'{rel}:all_selected_lines_changed',obj.get('all_selected_lines_changed') is True and all(changed))
        add(checks,f'{rel}:current_draft_contains_route',obj.get('current_draft_contains_current_route') is True and cur_route in draft,cur_route)
        add(checks,f'{rel}:draft_mentions_return_diff',obj.get('current_draft_mentions_return_diff') is True and ('return_diff' in draft or 'return-diff' in draft.lower()))
        add(checks,f'{rel}:previous_instruction_fulfilled_flag',obj.get('previous_instruction_fulfilled') is True)
        add(checks,f'{rel}:non_claim_present',bool(obj.get('non_claim')))
    return checks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args(); checks=run(Path(args.root)); ok=all(c['ok'] for c in checks)
    print(json.dumps({'ok':ok,'checks':checks,'failed':[c for c in checks if not c['ok']]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1
if __name__=='__main__': sys.exit(main())
