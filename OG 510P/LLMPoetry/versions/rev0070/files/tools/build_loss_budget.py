#!/usr/bin/env python3
"""Build a loss-budget receipt for selector-vector drafts.

The loss budget measures whether the selected surface is carrying less
explanatory machinery than the apparatus it compresses. It is a craft/quality
pressure aid, not a quality proof.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
META_TERMS = {
    'poem','poetry','proof','selector','vector','coordinate','coordinates','validation',
    'validate','validated','receipt','apparatus','branch','branches','disclosure','machine',
    'prompt','render','renders','metadata','packet','shadow'
}

def words(text: str) -> list[str]:
    return WORD_RE.findall(text)

def final_word(text: str) -> str:
    w = words(text)
    return w[-1].lower() if w else ''

def sha256_file(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('packet')
    ap.add_argument('draft')
    ap.add_argument('selector_vector')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    packet_path = Path(args.packet); draft_path = Path(args.draft); vector_path = Path(args.selector_vector)
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    vec = json.loads(vector_path.read_text(encoding='utf-8'))
    selected = []
    unselected = []
    for layer in packet.get('layers', []):
        sels=[c for c in layer.get('candidates', []) if c.get('selected') is True]
        if len(sels)!=1:
            raise SystemExit(f"layer {layer.get('layer_id')} has {len(sels)} selected candidates")
        selected.append(sels[0])
        for c in layer.get('candidates', []):
            if c.get('selected') is not True:
                unselected.append(c)
    selected_text = '\n'.join(c.get('text','') for c in selected)
    selected_words = [w.lower() for w in words(selected_text)]
    shadow_words = [final_word(c.get('text','')) for c in unselected]
    meta_hits = []
    for w in selected_words:
        lw=w.lower()
        if lw in META_TERMS:
            meta_hits.append(lw)
    out = {
        'schema': 'llmpoetry-loss-budget-v1',
        'poem_id': packet.get('poem_id'),
        'draft_id': packet.get('draft_id'),
        'revision': packet.get('revision'),
        'turn': packet.get('turn'),
        'packet_path': packet_path.as_posix(),
        'draft_path': draft_path.as_posix(),
        'selector_vector_path': vector_path.as_posix(),
        'selected_line_count': len(selected),
        'candidate_count': sum(len(layer.get('candidates', [])) for layer in packet.get('layers', [])),
        'omitted_candidate_count': len(unselected),
        'shadow_sentence': ' '.join(shadow_words),
        'shadow_word_count': len(shadow_words),
        'selected_surface_word_count': len(selected_words),
        'hidden_to_visible_word_ratio': round(len(shadow_words) / max(1, len(selected_words)), 4),
        'selected_meta_terms': sorted(set(meta_hits)),
        'selected_meta_term_count': len(meta_hits),
        'selected_meta_term_policy': 'This draft tries to move explanatory machinery out of the selected surface; zero selected meta-term hits is desired for this family, not a universal law.',
        'vector_shadow_matches': vec.get('shadow_sentence') == ' '.join(shadow_words),
        'draft_sha256': sha256_file(draft_path),
        'packet_sha256': sha256_file(packet_path),
        'selector_vector_sha256': sha256_file(vector_path),
        'non_claim': 'Loss-budget metrics are craft pressure only. They do not prove literary quality.'
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'draft_id': out['draft_id'], 'selected_meta_term_count': out['selected_meta_term_count'], 'hidden_to_visible_word_ratio': out['hidden_to_visible_word_ratio']}, indent=2))

if __name__ == '__main__':
    main()
