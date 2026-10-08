#!/usr/bin/env python3
"""Basic metrics for LLMPoetry poem drafts.

Dependency-free on purpose. This does not judge quality.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

def poem_lines(text: str):
    lines = []
    for raw in text.splitlines():
        if raw.strip().startswith('#'):
            continue
        if raw.strip() == '':
            continue
        lines.append(raw.rstrip('\n'))
    return lines

def final_word(line: str):
    words = WORD_RE.findall(line)
    return words[-1].lower() if words else None

def metrics(path: Path, ban_terms=None):
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = poem_lines(text)
    words = WORD_RE.findall(text)
    line_word_counts = [len(WORD_RE.findall(line)) for line in lines]
    initials = ''.join((line.lstrip()[:1] or '') for line in lines)
    finals = [final_word(line) for line in lines]
    lower = text.lower()
    hits = []
    for term in ban_terms or []:
        t = term.lower()
        if t in lower:
            hits.append({'term': term, 'count': lower.count(t)})
    return {
        'path': str(path),
        'line_count_nonblank_nonheading': len(lines),
        'word_count': len(words),
        'line_word_counts': line_word_counts,
        'line_initials': initials,
        'final_words': finals,
        'banlist_hits': hits,
    }

def load_ban_terms(root: Path):
    p = root / 'registries' / 'banlist.json'
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding='utf-8'))
    return [x['term'] for x in data.get('terms', []) if 'term' in x]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path', help='Poem markdown path')
    ap.add_argument('--root', default='.', help='Cube root for banlist lookup')
    ap.add_argument('--no-banlist', action='store_true')
    args = ap.parse_args()
    path = Path(args.path)
    ban_terms = [] if args.no_banlist else load_ban_terms(Path(args.root))
    print(json.dumps(metrics(path, ban_terms), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
