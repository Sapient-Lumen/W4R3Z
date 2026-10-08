#!/usr/bin/env python3
"""Build a zero-route receipt for LLMPoetry recursive branch drafts.

A zero route is a special case of the ergodic traversal rule: every selected
final word has length divisible by the number of omitted candidates in its
layer. The selected surface therefore routes deterministically to omitted
index 0 in every layer.
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

def selected_candidate(layer: dict) -> dict:
    sels = [c for c in layer.get('candidates', []) if c.get('selected') is True]
    if len(sels) != 1:
        raise SystemExit(f"layer {layer.get('layer_id')} has {len(sels)} selected candidates")
    return sels[0]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('packet')
    ap.add_argument('draft')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    packet_path = Path(args.packet)
    draft_path = Path(args.draft)
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    draft = draft_path.read_text(encoding='utf-8', errors='replace')
    transitions = []
    for index, layer in enumerate(packet.get('layers', [])):
        selected = selected_candidate(layer)
        omitted = [c for c in layer.get('candidates', []) if c.get('selected') is not True]
        if not omitted:
            raise SystemExit(f"layer {layer.get('layer_id')} has no omitted candidates")
        sf = final_word(selected.get('text', ''))
        route_index = len(sf) % len(omitted)
        chosen = omitted[route_index]
        selected_exact = f"{selected.get('candidate_id')} {selected.get('text')}"
        chosen_exact = f"{chosen.get('candidate_id')} {chosen.get('text')}"
        transitions.append({
            'index': index,
            'layer_id': layer.get('layer_id'),
            'selected_candidate_id': selected.get('candidate_id'),
            'selected_exact': selected_exact,
            'selected_final_word': sf,
            'selected_final_word_length': len(sf),
            'omitted_candidate_count': len(omitted),
            'route_index': route_index,
            'route_index_is_zero': route_index == 0,
            'chosen_candidate_id': chosen.get('candidate_id'),
            'chosen_exact': chosen_exact,
            'route_word': final_word(chosen.get('text', '')),
            'selected_sha256': sha256_text(selected_exact),
            'chosen_sha256': sha256_text(chosen_exact),
            'selected_line_in_draft': selected_exact in draft,
            'chosen_line_in_draft': chosen_exact in draft
        })
    route_sentence = ' '.join(t['route_word'] for t in transitions)
    out = {
        'schema': 'llmpoetry-zero-route-v1',
        'poem_id': packet.get('poem_id'),
        'draft_id': packet.get('draft_id'),
        'revision': packet.get('revision'),
        'turn': packet.get('turn'),
        'form_id': packet.get('form_id'),
        'branch_packet_path': packet_path.as_posix(),
        'draft_path': draft_path.as_posix(),
        'ergodic_traversal_path': packet.get('ergodic_traversal_path'),
        'zero_route_claim': packet.get('zero_route_claim'),
        'route_algorithm': 'selected_final_word_length_mod_omitted_candidate_count',
        'zero_condition': 'Every route_index must equal 0.',
        'route_sentence': route_sentence,
        'traversal_sentence_claim': packet.get('traversal_sentence_claim'),
        'route_sentence_matches_claim': route_sentence == packet.get('traversal_sentence_claim'),
        'all_route_indexes_zero': all(t['route_index'] == 0 for t in transitions),
        'all_selected_final_lengths_divisible_by_omitted_count': all(t['selected_final_word_length'] % t['omitted_candidate_count'] == 0 for t in transitions),
        'transitions': transitions,
        'disclosure_required': True,
        'non_claim': 'Zero-route consistency proves a deterministic route through omitted candidates only; it does not prove poem quality.'
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'draft_id': out['draft_id'], 'route_sentence': route_sentence, 'all_route_indexes_zero': out['all_route_indexes_zero']}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
