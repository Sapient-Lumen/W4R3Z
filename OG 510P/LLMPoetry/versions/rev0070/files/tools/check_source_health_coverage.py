#!/usr/bin/env python3
"""Validate every registered web/currentness source has a source-health record."""
from __future__ import annotations
import json, sys
from pathlib import Path

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': '' if detail is None else str(detail)})

def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def run(root: Path):
    checks = []
    state = load_json(root / 'STATE.json')
    registry = load_json(root / 'registries/source_registry.json')
    health = load_json(root / 'registries/source_health.json')
    add(checks, 'source_registry_revision_matches_state', registry.get('revision') == state.get('revision'), registry.get('revision'))
    add(checks, 'source_health_revision_matches_state', health.get('revision') == state.get('revision'), health.get('revision'))
    source_ids = [s.get('source_id') for s in registry.get('sources', [])]
    health_ids = [s.get('source_id') for s in health.get('sources', [])]
    add(checks, 'source_registry_ids_unique', len(source_ids) == len(set(source_ids)), f'count={len(source_ids)} unique={len(set(source_ids))}')
    add(checks, 'source_health_ids_unique', len(health_ids) == len(set(health_ids)), f'count={len(health_ids)} unique={len(set(health_ids))}')
    missing = sorted(set(source_ids) - set(health_ids))
    extra = sorted(set(health_ids) - set(source_ids))
    add(checks, 'source_health_covers_registry', not missing, f'missing={missing[:20]} count={len(missing)}')
    add(checks, 'source_health_no_unknown_sources', not extra, f'extra={extra[:20]} count={len(extra)}')
    incomplete = [h.get('source_id') for h in health.get('sources', []) if not h.get('expected_volatility') or not h.get('review_cadence_days') or not h.get('health_status')]
    add(checks, 'source_health_minimum_fields', not incomplete, incomplete[:20])
    return checks

def main(root='.'):
    checks = run(Path(root))
    ok = all(c.get('ok') for c in checks)
    print(json.dumps({'ok': ok, 'checks': checks, 'failed': [c for c in checks if not c.get('ok')]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
