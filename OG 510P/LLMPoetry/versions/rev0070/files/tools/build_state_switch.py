#!/usr/bin/env python3
"""Build a closed/open state-switch receipt from a selector vector.

The state switch is a craft receipt: it proves that opening the apparatus
changes the selected surface by appending fixed shadow slices recovered from
unselected branch endings. It does not judge poem quality.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def words(text: str) -> list[str]:
    return WORD_RE.findall(text)

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('packet')
    ap.add_argument('selector_vector')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    packet_path = Path(args.packet)
    vector_path = Path(args.selector_vector)
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    vector_obj = json.loads(vector_path.read_text(encoding='utf-8'))
    vector = vector_obj.get('vector', [])
    closed_lines = []
    open_lines = []
    transitions = []
    appended_words = []
    for item in vector:
        exact = item.get('selected_exact', '')
        phrase = item.get('shadow_slice', {}).get('phrase') or ' '.join(item.get('shadow_slice', {}).get('words', []))
        open_line = f"{exact} ⇢ {phrase}"
        closed_lines.append(exact)
        open_lines.append(open_line)
        appended_words.extend(words(phrase))
        transitions.append({
            'index': item.get('index'),
            'candidate_id': item.get('candidate_id'),
            'closed_exact': exact,
            'shadow_phrase': phrase,
            'open_exact': open_line,
            'closed_sha256': sha256_text(exact),
            'open_sha256': sha256_text(open_line),
            'selector': item.get('selector'),
            'shadow_slice': item.get('shadow_slice')
        })
    out = {
        'schema': 'llmpoetry-state-switch-v1',
        'poem_id': packet.get('poem_id'),
        'draft_id': packet.get('draft_id'),
        'revision': packet.get('revision'),
        'turn': packet.get('turn'),
        'form_id': packet.get('form_id'),
        'branch_packet_path': packet_path.as_posix(),
        'selector_vector_path': vector_path.as_posix(),
        'draft_path': packet.get('draft_path'),
        'state_switch_claim': packet.get('state_switch_claim'),
        'closed_state': {
            'description': 'Selected path without appended shadow slices.',
            'line_count': len(closed_lines),
            'lines': closed_lines,
            'word_count': sum(len(words(x)) for x in closed_lines)
        },
        'open_state': {
            'description': 'Selected path after disclosure opens the apparatus; each selected line receives its selector-vector shadow slice.',
            'line_count': len(open_lines),
            'lines': open_lines,
            'appended_shadow_sentence': ' '.join(appended_words),
            'appended_word_count': len(appended_words),
            'word_count': sum(len(words(x)) for x in open_lines)
        },
        'transitions': transitions,
        'state_delta': {
            'closed_to_open_line_count_preserved': len(closed_lines) == len(open_lines),
            'appended_word_count': len(appended_words),
            'open_differs_from_closed': open_lines != closed_lines,
            'vector_shadow_sentence': vector_obj.get('shadow_sentence'),
            'appended_matches_vector_shadow': ' '.join(appended_words) == vector_obj.get('shadow_sentence')
        },
        'disclosure_required': True,
        'non_claim': 'The state-switch receipt proves transform consistency only; it does not prove poem quality.'
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'draft_id': out['draft_id'], 'transition_count': len(transitions), 'appended_word_count': len(appended_words)}, indent=2))

if __name__ == '__main__':
    main()
