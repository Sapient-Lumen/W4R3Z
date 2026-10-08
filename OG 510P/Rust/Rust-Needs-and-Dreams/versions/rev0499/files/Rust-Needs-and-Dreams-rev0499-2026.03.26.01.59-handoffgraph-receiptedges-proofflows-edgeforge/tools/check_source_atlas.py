#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / 'atlases' / 'portfolio-source-atlas-v0' / 'sources.json'
REQUIRED_TOP = ['schema_family', 'revision', 'sources']
REQUIRED_CARD_FIELDS = ['source_id', 'title', 'url', 'authority_lane', 'source_kind', 'drift_horizon', 'scope', 'preferred_claim_classes', 'preferred_uses', 'known_caveats', 'refresh_signals', 'related_assets']
REQUIRED_LANES = {'official_blog', 'inside_rust_blog', 'project_goals', 'cargo_reference', 'service_docs'}
REQUIRED_CLASSES = {'ecosystem_pain', 'roadmap_and_priorities', 'machine_usable_tooling', 'service_behavior', 'security_and_registry'}
ALLOWED_HORIZON = {'hot', 'warm', 'cool', 'cold'}

def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''

def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0

def main() -> int:
    errors = []
    if not ATLAS.exists():
        print(f'missing source atlas file: {ATLAS.relative_to(ROOT)}', file=sys.stderr)
        return 1
    try:
        payload = json.loads(ATLAS.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'failed to parse source atlas: {exc}', file=sys.stderr)
        return 1
    for field in REQUIRED_TOP:
        if field not in payload:
            errors.append(f'missing top-level field: {field}')
    cards = payload.get('sources')
    if not isinstance(cards, list):
        errors.append('top-level sources must be a list')
        cards = []
    if len(cards) < 8:
        errors.append('source atlas must include at least eight cards')
    ids = set()
    lanes = set()
    classes = set()
    for idx, card in enumerate(cards):
        label = f'sources[{idx}]'
        if not isinstance(card, dict):
            errors.append(f'{label} must be an object')
            continue
        for field in REQUIRED_CARD_FIELDS:
            if field not in card:
                errors.append(f'{label} missing required field {field}')
        sid = card.get('source_id')
        if not non_empty_string(sid):
            errors.append(f'{label} source_id must be non-empty string')
        elif sid in ids:
            errors.append(f'duplicate source_id: {sid}')
        else:
            ids.add(sid)
        if not non_empty_string(card.get('title')):
            errors.append(f'{label} title must be non-empty string')
        url = card.get('url')
        if not non_empty_string(url) or not str(url).startswith('http'):
            errors.append(f'{label} url must be non-empty http URL')
        lane = card.get('authority_lane')
        if not non_empty_string(lane):
            errors.append(f'{label} authority_lane must be non-empty string')
        else:
            lanes.add(lane)
        if not non_empty_string(card.get('source_kind')):
            errors.append(f'{label} source_kind must be non-empty string')
        if card.get('drift_horizon') not in ALLOWED_HORIZON:
            errors.append(f'{label} drift_horizon must be one of {sorted(ALLOWED_HORIZON)}')
        if not non_empty_string(card.get('scope')):
            errors.append(f'{label} scope must be non-empty string')
        for key in ['preferred_claim_classes', 'preferred_uses', 'known_caveats', 'refresh_signals', 'related_assets']:
            if not non_empty_list(card.get(key)):
                errors.append(f'{label} {key} must be non-empty list')
        for cclass in card.get('preferred_claim_classes', []):
            if not non_empty_string(cclass):
                errors.append(f'{label} preferred_claim_classes entries must be non-empty strings')
            else:
                classes.add(cclass)
        for asset in card.get('related_assets', []):
            if not non_empty_string(asset):
                errors.append(f'{label} related_assets entries must be non-empty paths')
                continue
            if not (ROOT / asset).exists():
                errors.append(f'{label} related asset does not exist: {asset}')
    missing_lanes = sorted(REQUIRED_LANES - lanes)
    if missing_lanes:
        errors.append('missing required authority lanes: ' + ', '.join(missing_lanes))
    missing_classes = sorted(REQUIRED_CLASSES - classes)
    if missing_classes:
        errors.append('missing required claim-class coverage: ' + ', '.join(missing_classes))
    if errors:
        print('Source atlas check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1
    print('Source atlas check passed')
    print(f'Validated {len(cards)} source cards with lane coverage: {", ".join(sorted(lanes))}.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
