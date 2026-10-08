#!/usr/bin/env python3
"""Validate LLMPoetry state-switch receipts."""
from __future__ import annotations
import argparse, json, hashlib, sys
from pathlib import Path

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

def run(root: Path):
    checks=[]
    files=sorted(root.glob('poems/P*/verification/state_switch_*.json'))
    add(checks, 'state_switch_file_present', bool(files))
    for sp in files:
        rel=sp.relative_to(root).as_posix()
        try:
            obj=json.loads(sp.read_text(encoding='utf-8'))
            add(checks, f'{rel}:parse', True)
        except Exception as e:
            add(checks, f'{rel}:parse', False, str(e)); continue
        packet_path=root/obj.get('branch_packet_path','')
        vector_path=root/obj.get('selector_vector_path','')
        draft_path=root/obj.get('draft_path','')
        add(checks, f'{rel}:packet_exists', packet_path.exists(), obj.get('branch_packet_path',''))
        add(checks, f'{rel}:selector_vector_exists', vector_path.exists(), obj.get('selector_vector_path',''))
        add(checks, f'{rel}:draft_exists', draft_path.exists(), obj.get('draft_path',''))
        if not (packet_path.exists() and vector_path.exists() and draft_path.exists()):
            continue
        packet=json.loads(packet_path.read_text(encoding='utf-8'))
        vector=json.loads(vector_path.read_text(encoding='utf-8'))
        draft=draft_path.read_text(encoding='utf-8', errors='replace')
        transitions=obj.get('transitions', [])
        closed=obj.get('closed_state', {}).get('lines', [])
        opened=obj.get('open_state', {}).get('lines', [])
        add(checks, f'{rel}:form_mode_state_switch', packet.get('render_mode') == 'state_switch_split', packet.get('render_mode'))
        add(checks, f'{rel}:transition_count_matches_vector', len(transitions) == len(vector.get('vector', [])) == len(closed) == len(opened), f"transitions={len(transitions)} vector={len(vector.get('vector', []))}")
        add(checks, f'{rel}:closed_to_open_line_count_preserved', obj.get('state_delta', {}).get('closed_to_open_line_count_preserved') is True)
        add(checks, f'{rel}:open_differs_from_closed', obj.get('state_delta', {}).get('open_differs_from_closed') is True)
        add(checks, f'{rel}:appended_matches_vector_shadow', obj.get('state_delta', {}).get('appended_matches_vector_shadow') is True)
        add(checks, f'{rel}:disclosure_required', obj.get('disclosure_required') is True)
        add(checks, f'{rel}:claim_present', bool(obj.get('state_switch_claim')))
        for idx, t in enumerate(transitions):
            name=f'{rel}:transition:{idx}:{t.get("candidate_id")}'
            exact=t.get('closed_exact','')
            phrase=t.get('shadow_phrase','')
            open_exact=t.get('open_exact','')
            add(checks, name+':closed_hash', t.get('closed_sha256') == sha256_text(exact))
            add(checks, name+':open_hash', t.get('open_sha256') == sha256_text(open_exact))
            add(checks, name+':open_line_contains_closed_and_phrase', exact in open_exact and phrase in open_exact, open_exact)
            add(checks, name+':closed_line_in_draft', exact in draft)
            add(checks, name+':open_line_in_draft', open_exact in draft)
        selected=[]
        for layer in packet.get('layers', []):
            sels=[c for c in layer.get('candidates', []) if c.get('selected') is True]
            if sels:
                selected.append(f"{sels[0].get('candidate_id')} {sels[0].get('text')}")
        add(checks, f'{rel}:closed_matches_selected_path', closed == selected, f'closed={closed} selected={selected}')
    return checks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args(); checks=run(Path(args.root)); ok=all(c.get('ok') for c in checks)
    print(json.dumps({'ok': ok, 'checks': checks, 'failed': [c for c in checks if not c.get('ok')]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
