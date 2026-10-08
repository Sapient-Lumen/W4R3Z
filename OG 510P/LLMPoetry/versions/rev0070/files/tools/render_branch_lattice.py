#!/usr/bin/env python3
"""Render LLMPoetry branch-lattice packets as poem drafts.

The renderer is dependency-free. It can produce either a full inline lattice
(D002 style) or a surface/apparatus split (D003 style) where the branch packet
remains external and addressable. It does not judge poetic quality. Rev0017 also supports a state_switch_split mode.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def final_word(text: str) -> str:
    words = WORD_RE.findall(text)
    return words[-1].lower() if words else ''

def selected_candidate(layer):
    selected = [c for c in layer.get('candidates', []) if c.get('selected') is True]
    if len(selected) != 1:
        raise ValueError(f"layer {layer.get('layer_id')} has {len(selected)} selected candidates")
    return selected[0]

def first_rejected(layer):
    for c in layer.get('candidates', []):
        if c.get('selected') is not True:
            return c
    raise ValueError(f"layer {layer.get('layer_id')} has no rejected candidate")

def unselected_final_words(packet: dict) -> list[str]:
    out = []
    for layer in packet.get('layers', []):
        for c in layer.get('candidates', []):
            if c.get('selected') is not True:
                out.append(final_word(c.get('text', '')))
    return out

def unselected_candidates(layer: dict) -> list[dict]:
    return [c for c in layer.get('candidates', []) if c.get('selected') is not True]

def traversal_transitions(packet: dict) -> list[dict]:
    """Compute an optional ergodic traversal from selected line endings.

    Algorithm: for each selected line, take the final word length modulo the
    number of omitted candidates in that layer. That index chooses one omitted
    candidate. The final words of those chosen omitted candidates form the
    traversal sentence. This makes the selected surface an address machine.
    """
    transitions = []
    for layer in packet.get('layers', []):
        selected = selected_candidate(layer)
        omitted = unselected_candidates(layer)
        if not omitted:
            raise ValueError(f"layer {layer.get('layer_id')} has no omitted candidates")
        selected_final = final_word(selected.get('text', ''))
        code = len(selected_final) % len(omitted)
        chosen = omitted[code]
        transitions.append({
            'layer_id': layer.get('layer_id'),
            'selected_candidate_id': selected.get('candidate_id'),
            'selected_text': selected.get('text', ''),
            'selected_final_word': selected_final,
            'selected_final_word_length': len(selected_final),
            'omitted_count': len(omitted),
            'route_index': code,
            'chosen_candidate_id': chosen.get('candidate_id'),
            'chosen_text': chosen.get('text', ''),
            'chosen_final_word': final_word(chosen.get('text', ''))
        })
    return transitions

def traversal_sentence(packet: dict) -> str:
    return ' '.join(t['chosen_final_word'] for t in traversal_transitions(packet))

def render_full_lattice(packet: dict) -> str:
    title = packet.get('render_title') or 'P0001 draft_002 — Branch Selector / TRACE'
    prompt = packet.get('prompt_text', '')
    lines = [f"# {title}", "", "## Prompt", prompt, "", "## Selected path"]
    for layer in packet.get('layers', []):
        c = selected_candidate(layer)
        lines.append(f"{c.get('candidate_id')} {c.get('text')}")
    shadow = ' '.join(unselected_final_words(packet))
    lines += ["", "## Shadow sentence from unselected final words", shadow]
    lines += ["", "## First-rejected counterpath"]
    for layer in packet.get('layers', []):
        c = first_rejected(layer)
        lines.append(f"{c.get('candidate_id')} {c.get('text')}")
    lines += ["", "## Residue lattice"]
    for layer in packet.get('layers', []):
        lines.append(f"### {layer.get('layer_id')} layer")
        if layer.get('function'):
            lines.append(f"function: {layer.get('function')}")
        for c in layer.get('candidates', []):
            mark = 'x' if c.get('selected') is True else ' '
            note = c.get('selection_note') if c.get('selected') is True else c.get('rejection_note')
            suffix = f" // {note}" if note else ''
            lines.append(f"[{mark}] {c.get('candidate_id')} {c.get('text')}{suffix}")
        lines.append("")
    lines += [
        "## Machine-readable non-claim",
        packet.get('non_claim') or 'The packet validates the form, not the poem.',
        "",
        "## Disclosure condition",
        packet.get('disclosure_condition') or "This draft is machine-authored and packet-rendered. Hiding that fact removes the form.",
    ]
    return "\n".join(lines).rstrip() + "\n"

def render_surface_apparatus_split(packet: dict) -> str:
    title = packet.get('render_title') or 'P0001 draft_003 — Surface/Apparatus Split / SPLIT'
    prompt = packet.get('prompt_text', '')
    apparatus_path = packet.get('external_apparatus_path') or packet.get('packet_path') or 'poems/P0001/branches/branch_packet_003.json'
    selector_map = packet.get('selector_map_path') or 'poems/P0001/verification/selector_map_003.json'
    shadow = ' '.join(unselected_final_words(packet))
    lines = [f"# {title}", "", "## Prompt", prompt, "", "## Surface path"]
    for layer in packet.get('layers', []):
        c = selected_candidate(layer)
        lines.append(f"{c.get('candidate_id')} {c.get('text')}")
    lines += [
        "",
        "## Shadow sentence from external apparatus",
        shadow,
        "",
        "## Reader switch",
        "Closed: five selected lines and one shadow sentence.",
        f"Open `{apparatus_path}`: fifteen omitted branch endings give the shadow its words.",
        f"Open `{selector_map}`: the selected path has exact text and character spans.",
        "Hide the packet and the poem becomes decorative.",
        "",
        "## External apparatus pointer",
        "The full residue lattice is not printed here. It remains machine-readable in the branch packet and must travel with the draft.",
        "",
        "## Machine-readable non-claim",
        packet.get('non_claim') or 'The packet validates the form, not the poem.',
        "",
        "## Disclosure condition",
        packet.get('disclosure_condition') or "This draft is machine-authored and packet-rendered. Hiding that fact removes the form.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _number_word(n: int) -> str:
    words = {
        0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
        6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
        11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen',
        16: 'sixteen', 17: 'seventeen', 18: 'eighteen'
    }
    return words.get(n, str(n))

def render_selector_vector_split(packet: dict) -> str:
    title = packet.get('render_title') or 'P0001 draft — Selector Vector'
    prompt = packet.get('prompt_text', '')
    apparatus_path = packet.get('external_apparatus_path') or packet.get('packet_path') or 'poems/P0001/branches/branch_packet.json'
    selector_map = packet.get('selector_map_path') or 'poems/P0001/verification/selector_map.json'
    selector_vector = packet.get('selector_vector_path') or 'poems/P0001/verification/selector_vector.json'
    shadow_words = unselected_final_words(packet)
    shadow = ' '.join(shadow_words)
    layer_count = len(packet.get('layers', []))
    omitted_count = len(shadow_words)
    slice_width = omitted_count // max(1, layer_count) if layer_count else 0
    slice_label = 'triplets' if slice_width == 3 else f"{slice_width}-word slices"
    lines = [f"# {title}", "", "## Prompt", prompt, "", "## Surface path"]
    for layer in packet.get('layers', []):
        c = selected_candidate(layer)
        lines.append(f"{c.get('candidate_id')} {c.get('text')}")
    lines += [
        "",
        "## Shadow sentence from external apparatus",
        shadow,
        "",
        "## Selector-vector switch",
        f"Closed: {_number_word(layer_count)} selected lines and one shadow sentence.",
        f"Open `{selector_vector}`: exact spans of the selected lines fetch the shadow in {_number_word(layer_count)} {slice_label}.",
        f"Open `{apparatus_path}`: {_number_word(omitted_count)} omitted branch endings supply the {slice_label}.",
        f"Open `{selector_map}`: the selected path is anchored by exact text plus character start/end positions.",
        packet.get('reader_switch_claim') or "Hide the vector and the surface forgets what it lost.",
        "",
        "## External apparatus pointer",
        packet.get('external_pointer') or "The residue lattice and the coordinate-to-shadow vector are not printed here. They must travel with the draft.",
        "",
        "## Machine-readable non-claim",
        packet.get('non_claim') or 'The packet validates the form, not the poem.',
        "",
        "## Disclosure condition",
        packet.get('disclosure_condition') or "This draft is machine-authored and packet-rendered. Hiding that fact removes the form.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_state_switch_split(packet: dict) -> str:
    """Render a closed/open state-switch draft.

    The closed state is the selected path. The open state appends the fixed
    shadow-sentence slice recoverable from the unselected branch endings. This
    remains dependency-free: selector maps/vectors are built after rendering.
    """
    title = packet.get('render_title') or 'P0001 draft — Glitch State Switch'
    prompt = packet.get('prompt_text', '')
    apparatus_path = packet.get('external_apparatus_path') or packet.get('packet_path') or 'poems/P0001/branches/branch_packet.json'
    selector_map = packet.get('selector_map_path') or 'poems/P0001/verification/selector_map.json'
    selector_vector = packet.get('selector_vector_path') or 'poems/P0001/verification/selector_vector.json'
    state_switch = packet.get('state_switch_path') or 'poems/P0001/verification/state_switch.json'
    shadow_words = unselected_final_words(packet)
    shadow = ' '.join(shadow_words)
    layers = packet.get('layers', [])
    layer_count = len(layers)
    if layer_count and len(shadow_words) % layer_count != 0:
        raise ValueError(f"shadow word count {len(shadow_words)} not divisible by selected layer count {layer_count}")
    width = len(shadow_words) // max(1, layer_count) if layer_count else 0
    slice_label = 'triplets' if width == 3 else f"{width}-word slices"
    selected = []
    for layer in layers:
        c = selected_candidate(layer)
        selected.append((c.get('candidate_id'), c.get('text')))
    lines = [f"# {title}", "", "## Prompt", prompt, "", "## Closed state"]
    for cid, line in selected:
        lines.append(f"{cid} {line}")
    lines += ["", "## Shadow sentence from external apparatus", shadow, "", "## Open state generated from branch loss"]
    for idx, (cid, line) in enumerate(selected):
        a = idx * width
        b = a + width
        phrase = ' '.join(shadow_words[a:b])
        lines.append(f"{cid} {line} ⇢ {phrase}")
    transitions = []
    if packet.get('ergodic_traversal_path') or packet.get('traversal_sentence_claim'):
        transitions = traversal_transitions(packet)
        lines += [
            "",
            "## Traversal state generated from selected endings",
            packet.get('traversal_rule') or "Rule: final selected word length modulo omitted-candidate count chooses one omitted candidate from the same layer."
        ]
        for t in transitions:
            lines.append(
                f"{t['selected_candidate_id']} {t['selected_final_word']} [{t['selected_final_word_length']} % {t['omitted_count']} = {t['route_index']}] -> {t['chosen_candidate_id']} {t['chosen_text']}"
            )
        lines += ["", "## Traversal sentence", traversal_sentence(packet)]
    if packet.get('patch_operations'):
        route_words = {t.get('selected_candidate_id'): t.get('route_word') or t.get('chosen_final_word') for t in transitions}
        patched = []
        lines += [
            "",
            "## Patch-applied state generated from traversal words",
            packet.get('patch_rule') or "Rule: each traversal route word authorizes one replacement against its closed selected line."
        ]
        for op in packet.get('patch_operations', []):
            cid = op.get('candidate_id')
            before = op.get('before_exact')
            if not before:
                for layer in layers:
                    c = selected_candidate(layer)
                    if c.get('candidate_id') == cid:
                        before = f"{c.get('candidate_id')} {c.get('text')}"
                        break
            find = op.get('find', '')
            replace = op.get('replace', '')
            after = op.get('after_exact') or (before.replace(find, replace, 1) if before and find else '')
            route_word = route_words.get(cid, op.get('route_word', ''))
            lines.append(f"{cid} {find} -> {replace} [{route_word}]: {after}")
            if after:
                patched.append(after)
        if packet.get('patch_sentence_claim'):
            lines += ["", "## Patch sentence", packet.get('patch_sentence_claim')]
        lines += ["", "## Patched surface"]
        lines.extend(patched)
    lines += [
        "",
        "## State-switch pointer",
        f"Closed: {_number_word(layer_count)} selected lines without their rejected endings.",
        f"Open `{state_switch}`: the selected lines return with {_number_word(layer_count)} {slice_label} appended from loss.",
        f"Open `{selector_vector}`: exact character spans bind selected lines to those slices.",
        f"Open `{apparatus_path}`: {_number_word(len(shadow_words))} omitted branch endings supply the open-state words.",
        f"Open `{selector_map}`: the closed-state selected path is anchored by exact text plus character start/end positions.",
        packet.get('reader_switch_claim') or "Glitch is treated as state transition: the closed surface survives, but opening the apparatus changes its tense.",
        "",
        "## External apparatus pointer",
        packet.get('external_pointer') or "The residue lattice, selector map, selector vector, loss budget, and state-switch receipt are required parts of this draft object.",
        "",
        "## Machine-readable non-claim",
        packet.get('non_claim') or 'The packet validates construction, not poem quality.',
        "",
        "## Disclosure condition",
        packet.get('disclosure_condition') or "This draft is machine-authored and packet-rendered. Disclosure is the operation that moves the poem from closed to open state.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render(packet: dict) -> str:
    mode = packet.get('render_mode', 'full_lattice')
    if mode == 'surface_apparatus_split':
        return render_surface_apparatus_split(packet)
    if mode == 'selector_vector_split':
        return render_selector_vector_split(packet)
    if mode == 'state_switch_split':
        return render_state_switch_split(packet)
    if mode in {'full_lattice', 'rendered_branch_lattice'}:
        return render_full_lattice(packet)
    raise ValueError(f"unknown render_mode: {mode}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('packet')
    ap.add_argument('--out')
    args = ap.parse_args()
    packet = json.loads(Path(args.packet).read_text(encoding='utf-8'))
    text = render(packet)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding='utf-8')
    else:
        print(text, end='')

if __name__ == '__main__':
    main()
