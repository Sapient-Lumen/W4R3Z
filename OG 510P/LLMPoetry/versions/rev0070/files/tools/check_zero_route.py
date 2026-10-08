#!/usr/bin/env python3
"""Validate LLMPoetry zero-route receipts."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def words(text: str) -> list[str]:
    return WORD_RE.findall(text)

def final_word(text: str) -> str:
    w = words(text)
    return w[-1].lower() if w else ''

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

def selected_candidate(layer: dict) -> dict | None:
    sels = [c for c in layer.get('candidates', []) if c.get('selected') is True]
    return sels[0] if len(sels) == 1 else None

def run(root: Path):
    checks=[]
    files=sorted(root.glob('poems/P*/verification/zero_route_*.json'))
    add(checks, 'zero_route_file_present', bool(files))
    for zp in files:
        rel=zp.relative_to(root).as_posix()
        try:
            obj=json.loads(zp.read_text(encoding='utf-8'))
            add(checks, f'{rel}:parse', True)
        except Exception as e:
            add(checks, f'{rel}:parse', False, str(e)); continue
        packet_path=root/obj.get('branch_packet_path','')
        draft_path=root/obj.get('draft_path','')
        add(checks, f'{rel}:packet_exists', packet_path.exists(), obj.get('branch_packet_path',''))
        add(checks, f'{rel}:draft_exists', draft_path.exists(), obj.get('draft_path',''))
        if not packet_path.exists() or not draft_path.exists():
            continue
        packet=json.loads(packet_path.read_text(encoding='utf-8'))
        draft=draft_path.read_text(encoding='utf-8', errors='replace')
        add(checks, f'{rel}:packet_declares_zero_route_path', packet.get('zero_route_path') == rel, packet.get('zero_route_path'))
        add(checks, f'{rel}:draft_id_matches_packet', obj.get('draft_id') == packet.get('draft_id'))
        expected=[]
        for idx, layer in enumerate(packet.get('layers', [])):
            selected=selected_candidate(layer)
            omitted=[c for c in layer.get('candidates', []) if c.get('selected') is not True]
            if selected is None or not omitted:
                add(checks, f'{rel}:layer:{idx}:has_selected_and_omitted', False); continue
            sf=final_word(selected.get('text',''))
            route_index=len(sf) % len(omitted)
            chosen=omitted[route_index]
            selected_exact=f"{selected.get('candidate_id')} {selected.get('text')}"
            chosen_exact=f"{chosen.get('candidate_id')} {chosen.get('text')}"
            expected.append({
                'selected_candidate_id': selected.get('candidate_id'),
                'selected_exact': selected_exact,
                'selected_final_word_length': len(sf),
                'omitted_candidate_count': len(omitted),
                'route_index': route_index,
                'chosen_candidate_id': chosen.get('candidate_id'),
                'chosen_exact': chosen_exact,
                'route_word': final_word(chosen.get('text',''))
            })
        route_sentence=' '.join(e['route_word'] for e in expected)
        add(checks, f'{rel}:route_sentence_recomputed', obj.get('route_sentence') == route_sentence, route_sentence)
        add(checks, f'{rel}:route_sentence_matches_claim', obj.get('route_sentence_matches_claim') is True and packet.get('traversal_sentence_claim') == route_sentence, packet.get('traversal_sentence_claim'))
        add(checks, f'{rel}:all_route_indexes_zero', obj.get('all_route_indexes_zero') is True and all(e['route_index'] == 0 for e in expected))
        add(checks, f'{rel}:all_lengths_divisible', obj.get('all_selected_final_lengths_divisible_by_omitted_count') is True and all(e['selected_final_word_length'] % e['omitted_candidate_count'] == 0 for e in expected))
        transitions=obj.get('transitions', [])
        add(checks, f'{rel}:transition_count_matches_layers', len(transitions) == len(expected), f"transitions={len(transitions)} expected={len(expected)}")
        for i, exp in enumerate(expected):
            got=transitions[i] if i < len(transitions) else {}
            name=f'{rel}:transition:{i}:{exp.get("selected_candidate_id")}'
            add(checks, name+':route_index_zero', got.get('route_index') == 0)
            add(checks, name+':chosen_candidate_matches', got.get('chosen_candidate_id') == exp.get('chosen_candidate_id'), exp.get('chosen_candidate_id'))
            add(checks, name+':route_word_matches', got.get('route_word') == exp.get('route_word'), exp.get('route_word'))
            add(checks, name+':selected_line_in_draft', exp.get('selected_exact') in draft, exp.get('selected_exact'))
            add(checks, name+':chosen_line_in_draft', exp.get('chosen_exact') in draft, exp.get('chosen_exact'))
            add(checks, name+':selected_hash', got.get('selected_sha256') == sha256_text(got.get('selected_exact','')))
            add(checks, name+':chosen_hash', got.get('chosen_sha256') == sha256_text(got.get('chosen_exact','')))
        add(checks, f'{rel}:route_sentence_in_draft', route_sentence in draft, route_sentence)
        add(checks, f'{rel}:disclosure_required', obj.get('disclosure_required') is True)
        add(checks, f'{rel}:non_claim_present', bool(obj.get('non_claim')))
    return checks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args(); checks=run(Path(args.root)); ok=all(c.get('ok') for c in checks)
    print(json.dumps({'ok': ok, 'checks': checks, 'failed': [c for c in checks if not c.get('ok')]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
