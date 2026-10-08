#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def words(text: str) -> list[str]:
    return WORD_RE.findall(text)

def final_word(text: str) -> str:
    w=words(text); return w[-1].lower() if w else ''

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

def run(root: Path):
    checks=[]
    budgets=sorted(root.glob('poems/P*/verification/loss_budget_*.json'))
    add(checks, 'loss_budget_file_present', bool(budgets))
    for bp in budgets:
        rel=bp.relative_to(root).as_posix()
        try:
            b=json.loads(bp.read_text(encoding='utf-8'))
            add(checks, f'{rel}:parse', True)
        except Exception as e:
            add(checks, f'{rel}:parse', False, str(e)); continue
        packet_path=root/b.get('packet_path','')
        draft_path=root/b.get('draft_path','')
        vector_path=root/b.get('selector_vector_path','')
        add(checks, f'{rel}:packet_exists', packet_path.exists(), b.get('packet_path',''))
        add(checks, f'{rel}:draft_exists', draft_path.exists(), b.get('draft_path',''))
        add(checks, f'{rel}:selector_vector_exists', vector_path.exists(), b.get('selector_vector_path',''))
        if not (packet_path.exists() and draft_path.exists() and vector_path.exists()):
            continue
        packet=json.loads(packet_path.read_text(encoding='utf-8'))
        vec=json.loads(vector_path.read_text(encoding='utf-8'))
        selected=[]; unselected=[]
        for layer in packet.get('layers', []):
            sels=[c for c in layer.get('candidates', []) if c.get('selected') is True]
            if len(sels)==1: selected.append(sels[0])
            for c in layer.get('candidates', []):
                if c.get('selected') is not True: unselected.append(c)
        shadow=' '.join(final_word(c.get('text','')) for c in unselected)
        selected_words=words('\n'.join(c.get('text','') for c in selected))
        add(checks, f'{rel}:draft_id_matches_packet', b.get('draft_id') == packet.get('draft_id'))
        add(checks, f'{rel}:shadow_matches_packet', b.get('shadow_sentence') == shadow, shadow)
        add(checks, f'{rel}:shadow_matches_vector', vec.get('shadow_sentence') == shadow, vec.get('shadow_sentence',''))
        add(checks, f'{rel}:selected_line_count', b.get('selected_line_count') == len(selected), str(len(selected)))
        add(checks, f'{rel}:omitted_candidate_count', b.get('omitted_candidate_count') == len(unselected), str(len(unselected)))
        add(checks, f'{rel}:selected_word_count', b.get('selected_surface_word_count') == len(selected_words), str(len(selected_words)))
        # This form family tries to keep explanatory machinery out of the selected surface
        # while retaining a nontrivial hidden apparatus. These are pressure checks, not quality proofs.
        did = b.get('draft_id', 'UNKNOWN')
        add(checks, f'{rel}:{did}_selected_surface_meta_terms_zero', b.get('selected_meta_term_count') == 0, str(b.get('selected_meta_terms')))
        add(checks, f'{rel}:{did}_has_less_shadow_than_visible_but_nontrivial', 0 < b.get('hidden_to_visible_word_ratio', 0) < 1, str(b.get('hidden_to_visible_word_ratio')))
        add(checks, f'{rel}:{did}_omitted_count_matches_shadow_words', b.get('omitted_candidate_count') == b.get('shadow_word_count'), f"omitted={b.get('omitted_candidate_count')} shadow={b.get('shadow_word_count')}")
    return checks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args(); checks=run(Path(args.root)); ok=all(c.get('ok') for c in checks)
    print(json.dumps({'ok': ok, 'checks': checks, 'failed': [c for c in checks if not c.get('ok')]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
