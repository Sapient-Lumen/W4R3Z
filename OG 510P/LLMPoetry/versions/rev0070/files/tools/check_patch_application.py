#!/usr/bin/env python3
"""Validate LLMPoetry patch-application receipts."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

def run(root: Path):
    checks=[]
    receipts=sorted(root.glob('poems/P*/verification/patch_application_*.json'))
    add(checks, 'patch_application_file_present', bool(receipts))
    for rp in receipts:
        rel=rp.relative_to(root).as_posix()
        try:
            obj=json.loads(rp.read_text(encoding='utf-8'))
            add(checks, f'{rel}:parse', True)
        except Exception as e:
            add(checks, f'{rel}:parse', False, str(e)); continue
        packet_path=root/obj.get('branch_packet_path','')
        draft_path=root/obj.get('draft_path','')
        traversal_path=root/obj.get('ergodic_traversal_path','')
        for label,path in [('packet',packet_path),('draft',draft_path),('ergodic_traversal',traversal_path)]:
            add(checks, f'{rel}:{label}_exists', path.exists(), obj.get(f'{label}_path',''))
        if not (packet_path.exists() and draft_path.exists() and traversal_path.exists()):
            continue
        packet=json.loads(packet_path.read_text(encoding='utf-8'))
        traversal=json.loads(traversal_path.read_text(encoding='utf-8'))
        draft=draft_path.read_text(encoding='utf-8', errors='replace')
        add(checks, f'{rel}:packet_declares_patch_application_path', packet.get('patch_application_path') == rel, packet.get('patch_application_path'))
        add(checks, f'{rel}:route_sentence_matches_packet_patch_claim', obj.get('route_sentence_matches_patch_sentence') is True and traversal.get('traversal_sentence') == packet.get('patch_sentence_claim'), packet.get('patch_sentence_claim'))
        add(checks, f'{rel}:operation_count_matches_selected_lines', obj.get('operation_count_matches_selected_lines') is True)
        if obj.get('previous_route_receipt_path'):
            prev_path=root/obj.get('previous_route_receipt_path')
            add(checks, f'{rel}:previous_route_receipt_exists', prev_path.exists(), obj.get('previous_route_receipt_path'))
            add(checks, f'{rel}:previous_instruction_fulfilled', obj.get('previous_instruction_fulfilled') is True, obj.get('previous_route_sentence',''))
        transitions={t.get('selected_candidate_id'):t for t in traversal.get('transitions', [])}
        for idx, op in enumerate(obj.get('operations', [])):
            cid=op.get('candidate_id'); name=f'{rel}:operation:{idx}:{cid}'
            add(checks, name+':transition_exists', cid in transitions)
            add(checks, name+':route_word_matches_transition', op.get('route_word') == transitions.get(cid,{}).get('route_word'), str(transitions.get(cid,{}).get('route_word')))
            add(checks, name+':route_word_matches_replace', op.get('route_word_matches_replace') is True, f"{op.get('route_word')}->{op.get('replace')}")
            computed=op.get('before_exact','').replace(op.get('find',''), op.get('replace',''), 1) if op.get('find') else op.get('before_exact','')
            add(checks, name+':computed_after_matches', op.get('after_exact') == computed == op.get('computed_after_exact'), computed)
            add(checks, name+':line_changed', op.get('replacement_changes_line') is True)
            add(checks, name+':before_hash', op.get('before_sha256') == sha256_text(op.get('before_exact','')))
            add(checks, name+':after_hash', op.get('after_sha256') == sha256_text(op.get('after_exact','')))
            add(checks, name+':before_line_in_draft', op.get('before_exact','') in draft)
            add(checks, name+':after_line_in_draft', op.get('after_exact','') in draft)
        patched_lines=obj.get('patched_state',{}).get('lines',[])
        add(checks, f'{rel}:patched_state_all_lines_changed', obj.get('patched_state',{}).get('all_lines_changed') is True)
        add(checks, f'{rel}:patched_state_sha', obj.get('patched_state',{}).get('sha256') == sha256_text('\n'.join(patched_lines)))
        add(checks, f'{rel}:draft_contains_patched_lines', obj.get('draft_contains_patched_lines') is True and all(line in draft for line in patched_lines))
        add(checks, f'{rel}:draft_contains_patch_heading', obj.get('draft_contains_patch_heading') is True)
        add(checks, f'{rel}:draft_contains_patch_receipt_pointer', obj.get('draft_contains_patch_receipt_pointer') is True and rel in draft)
        add(checks, f'{rel}:disclosure_required', obj.get('disclosure_required') is True)
        add(checks, f'{rel}:non_claim_present', bool(obj.get('non_claim')))
    return checks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args(); checks=run(Path(args.root)); ok=all(c.get('ok') for c in checks)
    print(json.dumps({'ok':ok,'checks':checks,'failed':[c for c in checks if not c.get('ok')]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1
if __name__=='__main__': sys.exit(main())
