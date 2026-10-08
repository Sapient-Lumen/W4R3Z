#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / 'morphologies' / 'portfolio-contribution-shapes-v0' / 'shapes.json'
REQUIRED_TOP = ['schema_family', 'revision', 'shapes']
REQUIRED_FIELDS = ['shape_id', 'shape_class', 'label', 'one_sentence', 'truth_location', 'best_for', 'required_artifacts', 'common_failure_modes', 'prefer_when', 'avoid_when', 'related_assets']
REQUIRED_CLASSES = {'protocol_contract', 'evidence_collector', 'reference_layer', 'report_command', 'service_surface', 'corpus_atlas', 'checker_validator', 'bridge_adapter', 'pilot_program', 'stewarded_program'}

def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''

def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0

def main() -> int:
    errors = []
    if not ATLAS.exists():
        print(f'missing contribution-shape atlas file: {ATLAS.relative_to(ROOT)}', file=sys.stderr)
        return 1
    try:
        payload = json.loads(ATLAS.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'failed to parse contribution-shape atlas: {exc}', file=sys.stderr)
        return 1
    for field in REQUIRED_TOP:
        if field not in payload:
            errors.append(f'missing top-level field: {field}')
    cards = payload.get('shapes')
    if not isinstance(cards, list):
        errors.append('top-level shapes must be a list')
        cards = []
    if len(cards) < 10:
        errors.append('contribution-shape atlas must include at least ten cards')
    ids = set()
    classes = set()
    for idx, card in enumerate(cards):
        label = f'shapes[{idx}]'
        if not isinstance(card, dict):
            errors.append(f'{label} must be an object')
            continue
        for field in REQUIRED_FIELDS:
            if field not in card:
                errors.append(f'{label} missing required field {field}')
        sid = card.get('shape_id')
        if not non_empty_string(sid):
            errors.append(f'{label} shape_id must be non-empty string')
        elif sid in ids:
            errors.append(f'duplicate shape_id: {sid}')
        else:
            ids.add(sid)
        sclass = card.get('shape_class')
        if not non_empty_string(sclass):
            errors.append(f'{label} shape_class must be non-empty string')
        else:
            classes.add(sclass)
        for key in ['label', 'one_sentence', 'truth_location']:
            if not non_empty_string(card.get(key)):
                errors.append(f'{label} {key} must be non-empty string')
        for key in ['best_for', 'required_artifacts', 'common_failure_modes', 'prefer_when', 'avoid_when', 'related_assets']:
            if not non_empty_list(card.get(key)):
                errors.append(f'{label} {key} must be non-empty list')
        for asset in card.get('related_assets', []):
            if not non_empty_string(asset):
                errors.append(f'{label} related_assets entries must be non-empty paths')
                continue
            if not (ROOT / asset).exists():
                errors.append(f'{label} related asset does not exist: {asset}')
    missing = sorted(REQUIRED_CLASSES - classes)
    if missing:
        errors.append('missing required shape-class coverage: ' + ', '.join(missing))
    if errors:
        print('Contribution-shape atlas check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1
    print('Contribution-shape atlas check passed')
    print(f'Validated {len(cards)} shape cards with class coverage: {", ".join(sorted(classes))}.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
