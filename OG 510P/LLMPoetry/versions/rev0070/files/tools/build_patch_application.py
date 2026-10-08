#!/usr/bin/env python3
"""Build a patch-application receipt for LLMPoetry branch drafts.

The receipt proves a local machine-native transform: the current traversal
sentence supplies route words, and those words authorize concrete replacement
operations against the closed selected surface. It proves only consistency.
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

def selected_lines(packet: dict) -> dict[str, str]:
    out = {}
    for layer in packet.get('layers', []):
        sels = [c for c in layer.get('candidates', []) if c.get('selected') is True]
        if len(sels) != 1:
            raise SystemExit(f"layer {layer.get('layer_id')} has {len(sels)} selected candidates")
        c = sels[0]
        out[c.get('candidate_id')] = f"{c.get('candidate_id')} {c.get('text')}"
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('packet')
    ap.add_argument('draft')
    ap.add_argument('ergodic_traversal')
    ap.add_argument('--previous-route-receipt')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    packet_path = Path(args.packet); draft_path = Path(args.draft); traversal_path = Path(args.ergodic_traversal)
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    draft = draft_path.read_text(encoding='utf-8', errors='replace')
    traversal = json.loads(traversal_path.read_text(encoding='utf-8'))
    selected = selected_lines(packet)
    transitions = traversal.get('transitions', [])
    route_by_cid = {t.get('selected_candidate_id'): t.get('route_word') for t in transitions}
    transition_by_cid = {t.get('selected_candidate_id'): t for t in transitions}
    operations = []
    patched_lines = []
    for idx, op in enumerate(packet.get('patch_operations', [])):
        cid = op.get('candidate_id')
        before = op.get('before_exact') or selected.get(cid, '')
        find = op.get('find', '')
        replace = op.get('replace', '')
        after = op.get('after_exact') or (before.replace(find, replace, 1) if find else before)
        route_word = route_by_cid.get(cid, '')
        operations.append({
            'index': idx,
            'candidate_id': cid,
            'route_word': route_word,
            'route_word_matches_replace': route_word.lower() == replace.lower(),
            'find': find,
            'replace': replace,
            'before_exact': before,
            'after_exact': after,
            'computed_after_exact': before.replace(find, replace, 1) if find else before,
            'replacement_changes_line': after != before,
            'before_sha256': sha256_text(before),
            'after_sha256': sha256_text(after),
            'transition': transition_by_cid.get(cid, {})
        })
        patched_lines.append(after)
    previous_route_sentence = None
    previous_instruction_fulfilled = None
    if args.previous_route_receipt:
        prev_path = Path(args.previous_route_receipt)
        prev = json.loads(prev_path.read_text(encoding='utf-8'))
        previous_route_sentence = prev.get('route_sentence') or prev.get('traversal_sentence') or prev.get('traversed_state', {}).get('route_sentence')
        previous_instruction_fulfilled = bool(previous_route_sentence and 'patch the surface' in previous_route_sentence)
    out = {
        'schema': 'llmpoetry-patch-application-v1',
        'poem_id': packet.get('poem_id'),
        'draft_id': packet.get('draft_id'),
        'revision': packet.get('revision'),
        'turn': packet.get('turn'),
        'form_id': packet.get('form_id'),
        'branch_packet_path': packet_path.as_posix(),
        'draft_path': draft_path.as_posix(),
        'ergodic_traversal_path': traversal_path.as_posix(),
        'previous_route_receipt_path': Path(args.previous_route_receipt).as_posix() if args.previous_route_receipt else None,
        'previous_route_sentence': previous_route_sentence,
        'previous_instruction_fulfilled': previous_instruction_fulfilled,
        'route_sentence': traversal.get('traversal_sentence'),
        'route_sentence_matches_patch_sentence': traversal.get('traversal_sentence') == packet.get('patch_sentence_claim'),
        'patch_rule': packet.get('patch_rule'),
        'operation_count': len(operations),
        'selected_line_count': len(selected),
        'operation_count_matches_selected_lines': len(operations) == len(selected),
        'operations': operations,
        'patched_state': {
            'line_count': len(patched_lines),
            'lines': patched_lines,
            'all_lines_changed': all(op.get('replacement_changes_line') for op in operations),
            'sha256': sha256_text('\n'.join(patched_lines))
        },
        'draft_contains_patched_lines': all(line in draft for line in patched_lines),
        'draft_contains_patch_heading': '## Patch-applied state generated from traversal words' in draft,
        'draft_contains_patch_receipt_pointer': packet.get('patch_application_path', '') in draft,
        'disclosure_required': True,
        'non_claim': 'Patch-application consistency proves a deterministic surface mutation only; it does not prove poem quality.'
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'draft_id': out['draft_id'], 'operation_count': len(operations), 'route_sentence': out['route_sentence']}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
