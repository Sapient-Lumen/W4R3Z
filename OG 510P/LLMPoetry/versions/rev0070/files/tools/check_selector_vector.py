#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys, hashlib
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def final_word(text: str) -> str:
    words = WORD_RE.findall(text)
    return words[-1].lower() if words else ''

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

def run(root: Path):
    checks=[]
    vectors = sorted(root.glob('poems/P*/verification/selector_vector_*.json'))
    add(checks, 'selector_vector_file_present', bool(vectors))
    for vp in vectors:
        rel = vp.relative_to(root).as_posix()
        try:
            vec = json.loads(vp.read_text(encoding='utf-8'))
            add(checks, f'{rel}:parse', True)
        except Exception as e:
            add(checks, f'{rel}:parse', False, str(e)); continue
        packet_path = root/vec.get('branch_packet_path','')
        smap_path = root/vec.get('selector_map_path','')
        source_path = root/vec.get('source_path','')
        add(checks, f'{rel}:packet_exists', packet_path.exists(), vec.get('branch_packet_path',''))
        add(checks, f'{rel}:selector_map_exists', smap_path.exists(), vec.get('selector_map_path',''))
        add(checks, f'{rel}:source_exists', source_path.exists(), vec.get('source_path',''))
        if not (packet_path.exists() and smap_path.exists() and source_path.exists()):
            continue
        packet=json.loads(packet_path.read_text(encoding='utf-8'))
        smap=json.loads(smap_path.read_text(encoding='utf-8'))
        source=source_path.read_text(encoding='utf-8', errors='replace')
        shadow=[]
        for layer in packet.get('layers', []):
            for c in layer.get('candidates', []):
                if c.get('selected') is not True:
                    shadow.append(final_word(c.get('text','')))
        selectors=smap.get('selectors', [])
        vector=vec.get('vector', [])
        add(checks, f'{rel}:shadow_sentence_matches_packet', vec.get('shadow_sentence') == ' '.join(shadow), vec.get('shadow_sentence',''))
        add(checks, f'{rel}:selector_count_matches', vec.get('selector_count') == len(selectors) == len(vector), f"selector_count={len(selectors)} vector={len(vector)}")
        width = len(shadow)//len(selectors) if selectors else None
        add(checks, f'{rel}:shadow_width_matches', vec.get('shadow_words_per_selector') == width, f'width={width}')
        for i, item in enumerate(vector):
            sel = selectors[i] if i < len(selectors) else {}
            name=f'{rel}:vector:{i}:{item.get("candidate_id")}'
            add(checks, name+':candidate_matches_selector', item.get('candidate_id') == sel.get('candidate_id'))
            start=item.get('selector',{}).get('start'); end=item.get('selector',{}).get('end'); exact=item.get('selected_exact','')
            add(checks, name+':span_valid', isinstance(start,int) and isinstance(end,int) and 0 <= start < end <= len(source), f'{start}:{end}')
            if isinstance(start,int) and isinstance(end,int) and 0 <= start < end <= len(source):
                add(checks, name+':span_extracts_exact', source[start:end] == exact)
            add(checks, name+':hash_matches', item.get('selected_sha256') == hashlib.sha256(exact.encode('utf-8')).hexdigest())
            a=item.get('shadow_slice',{}).get('start_word_index'); b=item.get('shadow_slice',{}).get('end_word_index_exclusive')
            words=item.get('shadow_slice',{}).get('words',[])
            add(checks, name+':shadow_slice_valid', isinstance(a,int) and isinstance(b,int) and shadow[a:b] == words, str(words))
            phrase=' '.join(words)
            add(checks, name+':coordinate_phrase_contains_slice', phrase in item.get('coordinate_phrase',''), item.get('coordinate_phrase',''))
    return checks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args(); checks=run(Path(args.root)); ok=all(c.get('ok') for c in checks)
    print(json.dumps({'ok': ok, 'checks': checks, 'failed': [c for c in checks if not c.get('ok')]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
