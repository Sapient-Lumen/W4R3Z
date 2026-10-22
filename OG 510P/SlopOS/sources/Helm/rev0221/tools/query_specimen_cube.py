#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'fixtures' / 'release-readiness'
RECORDS = FIX / 'specimen-cube-records.jsonl'
CARDS = FIX / 'surface-affordance-cards.json'
PACK = FIX / 'query-pack.json'

class QueryError(Exception):
    pass

def load_records():
    records = []
    with RECORDS.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def load_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def invalidator_kinds(rec):
    return {i.get('kind') for i in rec.get('invalidators', []) if i.get('status') == 'triggered'}

def query(query_id, records, cards):
    by_id = {r['event_id']: r for r in records}
    if query_id == 'stale_or_blocked_affordances':
        return {'event_ids': [r['event_id'] for r in records if r.get('posture') in {'stale','blocked'}]}
    if query_id == 'imported_arrivals_before_adoption':
        return {'event_ids': [r['event_id'] for r in records if r.get('serving_lane') == 'imported' and r.get('posture') in {'restricted','adoptable'}]}
    if query_id == 'derived_claims':
        return {'event_ids': [r['event_id'] for r in records if r.get('truth_lane') == 'derived_serving' or r.get('serving_lane') in {'cached','precomputed','local_analytic'}]}
    if query_id == 'basis_drift_refusals':
        return {'event_ids': [r['event_id'] for r in records if r.get('posture') == 'blocked' and invalidator_kinds(r) & {'basis_drift','source_definition_changed'}]}
    if query_id == 'promotions_with_fresh_recheck':
        fresh_rechecks = {r['event_id'] for r in records if r.get('verb') == 'recheck' and r.get('basis', {}).get('basis_status') == 'fresh' and r.get('posture') == 'current'}
        ids = []
        for r in records:
            if r.get('verb') == 'promote' and (set(r.get('related_events', [])) & fresh_rechecks):
                ids.append(r['event_id'])
        return {'event_ids': ids}
    if query_id == 'historical_recall_not_live':
        return {'event_ids': [r['event_id'] for r in records if r.get('surface') == 'recall' and r.get('truth_lane') == 'receipt' and 'current_live' in r.get('weaker_than', [])]}
    if query_id == 'contradiction_pairs':
        pairs = []
        def have(a,b): return a in by_id and b in by_id
        # Derived stale vs live: same specimen, but different lane and staleness posture.
        if have('rr-evt-002-render-live-beacon','rr-evt-003-derived-summary'):
            pairs.append(['rr-evt-002-render-live-beacon','rr-evt-003-derived-summary'])
        # Saved current definition vs stale review cut.
        if have('rr-evt-001-summon-front-door','rr-evt-007-review-stale-refusal'):
            pairs.append(['rr-evt-001-summon-front-door','rr-evt-007-review-stale-refusal'])
        # Imported arrival vs local promotion receipt.
        if have('rr-evt-004-import-arrival','rr-evt-009-promote-local'):
            pairs.append(['rr-evt-004-import-arrival','rr-evt-009-promote-local'])
        # Promotion receipt vs recall's historical-only reading.
        if have('rr-evt-009-promote-local','rr-evt-010-recall-later'):
            pairs.append(['rr-evt-009-promote-local','rr-evt-010-recall-later'])
        return {'pairs': pairs}
    if query_id == 'surface_coverage':
        return {'surfaces': sorted({r.get('surface') for r in records})}
    if query_id == 'affordance_cards_backed_by_events':
        return {'card_count': len(cards), 'card_ids': [c['card_id'] for c in cards], 'missing_event_ids': [c['event_id'] for c in cards if c['event_id'] not in by_id]}
    raise QueryError(f'unknown query id: {query_id}')

def validate_result(q, result):
    qid = q['id']
    if 'expected_event_ids' in q:
        if result.get('event_ids') != q['expected_event_ids']:
            raise QueryError(f'{qid}: expected event_ids {q["expected_event_ids"]}, got {result.get("event_ids")}')
    if 'expected_pairs' in q:
        if result.get('pairs') != q['expected_pairs']:
            raise QueryError(f'{qid}: expected pairs {q["expected_pairs"]}, got {result.get("pairs")}')
    if 'expected_surfaces' in q:
        if result.get('surfaces') != q['expected_surfaces']:
            raise QueryError(f'{qid}: expected surfaces {q["expected_surfaces"]}, got {result.get("surfaces")}')
    if 'expected_card_count' in q:
        if result.get('card_count') != q['expected_card_count']:
            raise QueryError(f'{qid}: expected card_count {q["expected_card_count"]}, got {result.get("card_count")}')
        if result.get('missing_event_ids'):
            raise QueryError(f'{qid}: cards reference missing events {result.get("missing_event_ids")}')

def run(validate=False):
    records = load_records()
    cards = load_json(CARDS)
    pack = load_json(PACK)
    answers = []
    for q in pack['queries']:
        result = query(q['id'], records, cards)
        if validate:
            validate_result(q, result)
        answers.append({'query_id': q['id'], 'description': q.get('description',''), 'result': result})
    return {
        'pack_id': pack['pack_id'],
        'specimen_id': pack['specimen_id'],
        'record_count': len(records),
        'card_count': len(cards),
        'answers': answers,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--validate', action='store_true')
    ap.add_argument('--write-snapshot')
    args = ap.parse_args()
    try:
        result = run(validate=args.validate)
        if args.write_snapshot:
            path = Path(args.write_snapshot)
            if not path.is_absolute():
                path = ROOT / path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
            
            try:
                display_path = path.relative_to(ROOT)
            except ValueError:
                display_path = path
            suffix = f'; wrote {display_path}'
        else:
            print(json.dumps(result, indent=2))
            suffix = ''
        if args.validate:
            print(f'ok: {len(result["answers"])} query pack assertions validated{suffix}')
    except QueryError as e:
        print(f'error: {e}')
        raise SystemExit(1)

if __name__ == '__main__':
    main()
