#!/usr/bin/env python3
"""Validate the open-question registry has one canonical live queue and no stale legacy instructions."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

STALE_LIVE_RE = re.compile(r'cold-review\s+(?:P0001[- ]?)?D00[1-9]', re.I)

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': '' if detail is None else str(detail)})

def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def qid(q):
    return q.get('id') or q.get('question_id')

def is_live(q):
    status = str(q.get('status', '')).lower()
    return status in {'live', 'open', 'open_next'} or status.startswith('live_')

def run(root: Path):
    checks = []
    state = load_json(root / 'STATE.json')
    obj = load_json(root / 'registries/open_questions.json')
    canonical = obj.get('open_questions', [])
    legacy = obj.get('questions', [])
    add(checks, 'open_questions_revision_matches_state', obj.get('revision') == state.get('revision'), obj.get('revision'))
    add(checks, 'canonical_open_questions_list', isinstance(canonical, list) and bool(canonical), len(canonical) if isinstance(canonical, list) else type(canonical).__name__)
    ids = [qid(q) for q in canonical if isinstance(q, dict)]
    add(checks, 'canonical_ids_unique', len(ids) == len(set(ids)), f'count={len(ids)} unique={len(set(ids))}')
    add(checks, 'canonical_ids_present', all(ids), ids)

    live = [q for q in canonical if isinstance(q, dict) and is_live(q)]
    live_ids = [qid(q) for q in live]
    add(checks, 'canonical_live_questions_present', len(live) >= 1, live_ids)
    stale_live = []
    for q in live:
        hay = ' '.join(str(q.get(k, '')) for k in ('question', 'recommended_next', 'default_next_action', 'default_until_answered'))
        if STALE_LIVE_RE.search(hay):
            stale_live.append(qid(q))
    add(checks, 'no_stale_cold_review_instruction_in_live_questions', not stale_live, stale_live)

    if isinstance(legacy, list):
        legacy_ids = [qid(q) for q in legacy if isinstance(q, dict)]
        add(checks, 'legacy_questions_are_live_subset', set(legacy_ids) == set(live_ids), f'legacy={legacy_ids} live={live_ids}')
        canon_by_id = {qid(q): q for q in canonical if isinstance(q, dict)}
        mismatches = []
        for q in legacy:
            if not isinstance(q, dict):
                continue
            c = canon_by_id.get(qid(q))
            if not c or c.get('status') != q.get('status') or c.get('question') != q.get('question'):
                mismatches.append(qid(q))
        add(checks, 'legacy_questions_match_canonical_live_records', not mismatches, mismatches)
    else:
        add(checks, 'legacy_questions_are_list', False, type(legacy).__name__)
    return checks

def main(root='.'):
    checks = run(Path(root))
    ok = all(c.get('ok') for c in checks)
    print(json.dumps({'ok': ok, 'checks': checks, 'failed': [c for c in checks if not c.get('ok')]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
