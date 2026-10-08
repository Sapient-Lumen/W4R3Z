#!/usr/bin/env python3
"""Validate surface/apparatus split branch-lattice drafts.

This is a form-bookkeeping validator. It checks that a draft keeps the readable
surface lean while retaining the full residue lattice in an external branch
packet. It does not judge poetic quality.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def final_word(text: str) -> str:
    words = WORD_RE.findall(text)
    return words[-1].lower() if words else ''

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

def run(root: Path):
    checks=[]
    packets=sorted(root.glob('poems/P*/branches/branch_packet_*.json'))
    split_packets=[]
    for p in packets:
        try:
            obj=json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            add(checks, f'{p.relative_to(root).as_posix()}:parse', False, str(e)); continue
        if obj.get('render_mode')=='surface_apparatus_split':
            obj['_path']=p.relative_to(root).as_posix(); split_packets.append(obj)
    add(checks, 'surface_apparatus_split_packet_present', bool(split_packets))
    for packet in split_packets:
        rel=packet['_path']; draft_path=root/packet.get('draft_path','')
        add(checks, f'{rel}:draft_exists', draft_path.exists(), packet.get('draft_path',''))
        if not draft_path.exists():
            continue
        text=draft_path.read_text(encoding='utf-8', errors='replace')
        add(checks, f'{rel}:no_inline_residue_lattice', '## Residue lattice' not in text)
        add(checks, f'{rel}:reader_switch_present', '## Reader switch' in text)
        add(checks, f'{rel}:external_pointer_present', '## External apparatus pointer' in text)
        add(checks, f'{rel}:all_candidates_not_required_inline', packet.get('all_candidates_must_appear_in_draft') is False)
        apparatus=packet.get('external_apparatus_path') or rel
        add(checks, f'{rel}:external_apparatus_path_self_or_exists', (root/apparatus).exists(), apparatus)
        sm=packet.get('selector_map_path')
        add(checks, f'{rel}:selector_map_path_exists', bool(sm) and (root/sm).exists(), str(sm))
        layers=packet.get('layers', [])
        selected=[]; unselected=[]
        for layer in layers:
            sels=[c for c in layer.get('candidates', []) if c.get('selected') is True]
            if len(sels)==1:
                selected.append(f"{sels[0].get('candidate_id')} {sels[0].get('text')}")
            for c in layer.get('candidates', []):
                if c.get('selected') is not True:
                    unselected.append(c.get('text',''))
        add(checks, f'{rel}:selected_lines_in_surface', all(s in text for s in selected), f'count={len(selected)}')
        shadow=' '.join(final_word(u) for u in unselected)
        add(checks, f'{rel}:shadow_claim_matches', shadow==packet.get('unselected_final_words_claim'), shadow)
        add(checks, f'{rel}:shadow_in_surface', shadow in text, shadow)
        unselected_inline=[u for u in unselected if u and u in text]
        add(checks, f'{rel}:unselected_candidate_texts_not_inline', not unselected_inline, f'inline={unselected_inline[:3]}')
    return checks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args(); checks=run(Path(args.root)); ok=all(c['ok'] for c in checks)
    print(json.dumps({'ok':ok,'checks':checks,'failed':[c for c in checks if not c['ok']]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__=='__main__':
    sys.exit(main())
