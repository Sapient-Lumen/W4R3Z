#!/usr/bin/env python3
"""Build a selector-vector receipt from a branch packet and selected-line selector map.

A selector vector maps each selected line's exact text/character span to a fixed
slice of the shadow sentence produced by unselected branch endings. It treats
addressability as part of the poem object, not just a validation receipt.
"""
from __future__ import annotations
import argparse, json, re, hashlib
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def final_word(text: str) -> str:
    words = WORD_RE.findall(text)
    return words[-1].lower() if words else ''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('packet')
    ap.add_argument('selector_map')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    packet = json.loads(Path(args.packet).read_text(encoding='utf-8'))
    smap = json.loads(Path(args.selector_map).read_text(encoding='utf-8'))
    shadow_words = []
    for layer in packet.get('layers', []):
        for c in layer.get('candidates', []):
            if c.get('selected') is not True:
                shadow_words.append(final_word(c.get('text','')))
    selectors = smap.get('selectors', [])
    if not selectors:
        raise SystemExit('selector map has no selectors')
    if len(shadow_words) % len(selectors) != 0:
        raise SystemExit(f'shadow word count {len(shadow_words)} not divisible by selector count {len(selectors)}')
    width = len(shadow_words) // len(selectors)
    vector = []
    for idx, sel in enumerate(selectors):
        a = idx * width
        b = a + width
        exact = sel.get('exact','')
        phrase = ' '.join(shadow_words[a:b])
        vector.append({
            'index': idx,
            'layer_id': sel.get('layer_id'),
            'candidate_id': sel.get('candidate_id'),
            'selected_exact': exact,
            'selector': {
                'selector_type': sel.get('selector_type'),
                'start': sel.get('start'),
                'end': sel.get('end'),
                'prefix': sel.get('prefix'),
                'suffix': sel.get('suffix')
            },
            'span_length': (sel.get('end') - sel.get('start')) if isinstance(sel.get('start'), int) and isinstance(sel.get('end'), int) else None,
            'selected_sha256': hashlib.sha256(exact.encode('utf-8')).hexdigest(),
            'shadow_slice': {'start_word_index': a, 'end_word_index_exclusive': b, 'words': shadow_words[a:b], 'phrase': phrase},
            'coordinate_phrase': f"{sel.get('candidate_id')}@{sel.get('start')}:{sel.get('end')} -> {phrase}"
        })
    out = {
        'schema': 'llmpoetry-selector-vector-v1',
        'poem_id': packet.get('poem_id'),
        'draft_id': packet.get('draft_id'),
        'revision': packet.get('revision'),
        'turn': packet.get('turn'),
        'branch_packet_path': str(Path(args.packet).as_posix()),
        'selector_map_path': str(Path(args.selector_map).as_posix()),
        'source_path': smap.get('source_path'),
        'shadow_sentence': ' '.join(shadow_words),
        'shadow_word_count': len(shadow_words),
        'selector_count': len(selectors),
        'shadow_words_per_selector': width,
        'vector': vector,
        'claim': packet.get('selector_vector_claim'),
        'non_claim': 'Selector-vector consistency proves addressable construction only; it does not prove poem quality.'
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'vector_count': len(vector), 'shadow_words_per_selector': width}, indent=2))

if __name__ == '__main__':
    main()
