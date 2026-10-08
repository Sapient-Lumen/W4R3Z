#!/usr/bin/env python3
"""Build an ergodic-traversal receipt for LLMPoetry branch drafts.

The receipt proves a local state transition: selected line endings choose one
omitted candidate per layer. It is a traversal/action receipt, not a quality
claim.
"""
from __future__ import annotations
import argparse, json, re, hashlib
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def words(text: str) -> list[str]:
    return WORD_RE.findall(text)

def final_word(text: str) -> str:
    w = words(text)
    return w[-1].lower() if w else ''

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def selected_candidate(layer: dict) -> dict:
    selected = [c for c in layer.get('candidates', []) if c.get('selected') is True]
    if len(selected) != 1:
        raise SystemExit(f"layer {layer.get('layer_id')} has {len(selected)} selected candidates")
    return selected[0]

def omitted_candidates(layer: dict) -> list[dict]:
    return [c for c in layer.get('candidates', []) if c.get('selected') is not True]

def build(packet: dict) -> list[dict]:
    transitions = []
    for index, layer in enumerate(packet.get('layers', [])):
        selected = selected_candidate(layer)
        omitted = omitted_candidates(layer)
        if not omitted:
            raise SystemExit(f"layer {layer.get('layer_id')} has no omitted candidates")
        selected_final = final_word(selected.get('text', ''))
        selected_len = len(selected_final)
        route_index = selected_len % len(omitted)
        chosen = omitted[route_index]
        chosen_final = final_word(chosen.get('text', ''))
        closed_exact = f"{selected.get('candidate_id')} {selected.get('text')}"
        opened_exact = f"{chosen.get('candidate_id')} {chosen.get('text')}"
        transitions.append({
            'index': index,
            'layer_id': layer.get('layer_id'),
            'selected_candidate_id': selected.get('candidate_id'),
            'selected_text': selected.get('text', ''),
            'selected_exact': closed_exact,
            'selected_final_word': selected_final,
            'selected_final_word_length': selected_len,
            'omitted_candidate_count': len(omitted),
            'route_index': route_index,
            'chosen_candidate_id': chosen.get('candidate_id'),
            'chosen_text': chosen.get('text', ''),
            'chosen_exact': opened_exact,
            'chosen_final_word': chosen_final,
            'route_word': chosen_final,
            'selector_code': f"len({selected_final})={selected_len}; {selected_len}%{len(omitted)}={route_index}",
            'closed_sha256': sha256_text(closed_exact),
            'chosen_sha256': sha256_text(opened_exact)
        })
    return transitions

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('packet')
    ap.add_argument('draft')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    packet_path = Path(args.packet)
    draft_path = Path(args.draft)
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    draft = draft_path.read_text(encoding='utf-8', errors='replace')
    transitions = build(packet)
    route_sentence = ' '.join(t['route_word'] for t in transitions)
    out = {
        'schema': 'llmpoetry-ergodic-traversal-v1',
        'poem_id': packet.get('poem_id'),
        'draft_id': packet.get('draft_id'),
        'revision': packet.get('revision'),
        'turn': packet.get('turn'),
        'form_id': packet.get('form_id'),
        'branch_packet_path': packet_path.as_posix(),
        'draft_path': draft_path.as_posix(),
        'route_algorithm': packet.get('route_algorithm') or 'selected_final_word_length_mod_omitted_candidate_count',
        'traversal_rule': packet.get('traversal_rule') or 'For each layer, final selected word length modulo omitted-candidate count chooses one omitted candidate from the same layer.',
        'traversal_sentence': route_sentence,
        'traversal_sentence_claim': packet.get('traversal_sentence_claim'),
        'traversal_sentence_matches_claim': route_sentence == packet.get('traversal_sentence_claim'),
        'closed_state': {
            'line_count': len(transitions),
            'lines': [t['selected_exact'] for t in transitions]
        },
        'traversed_state': {
            'line_count': len(transitions),
            'lines': [t['chosen_exact'] for t in transitions],
            'route_words': [t['route_word'] for t in transitions],
            'route_sentence': route_sentence
        },
        'transitions': transitions,
        'draft_contains_traversal_sentence': route_sentence in draft,
        'draft_contains_chosen_lines': all(t['chosen_exact'] in draft for t in transitions),
        'draft_contains_selected_lines': all(t['selected_exact'] in draft for t in transitions),
        'disclosure_required': True,
        'non_claim': 'Ergodic-traversal consistency proves a deterministic route through omitted branches only; it does not prove poem quality.'
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'draft_id': out['draft_id'], 'route_sentence': route_sentence, 'transition_count': len(transitions)}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
