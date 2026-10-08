#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'ledgers' / 'portfolio-launch-wedges-v0' / 'wedges.json'
REQUIRED_TOP = ['schema_family', 'revision', 'wedges']
REQUIRED_CARD_FIELDS = ['wedge_id', 'title', 'seam', 'wedge_kind', 'status', 'target_user', 'decision_window', 'trigger_moment', 'initial_surface', 'import_surfaces', 'proof_artifacts', 'proving_grounds', 'success_signals', 'anti_goals', 'credible_home', 'next_if_proven', 'related_assets', 'supporting_sources', 'review_horizon', 'notes']
REQUIRED_SEAMS = {
    'Build-State Evidence',
    'Package Intake + Release Boundary Review',
    'Feedback / Debug Acceptance Commons',
    'Safety-Critical + Institutional Readiness Commons',
    'Compatibility Claims',
    'Adoption Navigation + Ecosystem Atlas',
    'Tooling Contract / Semantic Context',
}
ALLOWED_STATUS = {'active', 'candidate', 'hold', 'retired'}
ALLOWED_HORIZON = {'hot', 'warm', 'cool', 'cold'}

def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''

def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0

def main() -> int:
    errors = []
    if not LEDGER.exists():
        print(f'missing wedge ledger file: {LEDGER.relative_to(ROOT)}', file=sys.stderr)
        return 1
    try:
        payload = json.loads(LEDGER.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'failed to parse wedge ledger: {exc}', file=sys.stderr)
        return 1
    for field in REQUIRED_TOP:
        if field not in payload:
            errors.append(f'missing top-level field: {field}')
    cards = payload.get('wedges')
    if not isinstance(cards, list):
        errors.append('top-level wedges must be a list')
        cards = []
    if len(cards) < len(REQUIRED_SEAMS):
        errors.append('wedge ledger must include at least one card for each required seam')
    ids = set()
    seams = set()
    for idx, card in enumerate(cards):
        label = f'wedges[{idx}]'
        if not isinstance(card, dict):
            errors.append(f'{label} must be an object')
            continue
        for field in REQUIRED_CARD_FIELDS:
            if field not in card:
                errors.append(f'{label} missing required field {field}')
        wid = card.get('wedge_id')
        if not non_empty_string(wid):
            errors.append(f'{label} wedge_id must be non-empty string')
        elif wid in ids:
            errors.append(f'duplicate wedge_id: {wid}')
        else:
            ids.add(wid)
        seam = card.get('seam')
        if not non_empty_string(seam):
            errors.append(f'{label} seam must be non-empty string')
        else:
            seams.add(seam)
        for key in ['title', 'wedge_kind', 'target_user', 'decision_window', 'trigger_moment', 'initial_surface', 'credible_home', 'next_if_proven']:
            if not non_empty_string(card.get(key)):
                errors.append(f'{label} {key} must be non-empty string')
        if card.get('status') not in ALLOWED_STATUS:
            errors.append(f'{label} status must be one of {sorted(ALLOWED_STATUS)}')
        if card.get('review_horizon') not in ALLOWED_HORIZON:
            errors.append(f'{label} review_horizon must be one of {sorted(ALLOWED_HORIZON)}')
        for key in ['import_surfaces', 'proof_artifacts', 'proving_grounds', 'success_signals', 'anti_goals', 'related_assets', 'supporting_sources', 'notes']:
            if not non_empty_list(card.get(key)):
                errors.append(f'{label} {key} must be non-empty list')
        for source in card.get('supporting_sources', []):
            if not non_empty_string(source) or not source.startswith('http'):
                errors.append(f'{label} supporting_sources entries must be non-empty URLs')
        for asset in card.get('related_assets', []):
            if not non_empty_string(asset):
                errors.append(f'{label} related_assets entries must be non-empty paths')
                continue
            if not (ROOT / asset).exists():
                errors.append(f'{label} related asset does not exist: {asset}')
    missing_seams = sorted(REQUIRED_SEAMS - seams)
    if missing_seams:
        errors.append('missing seam coverage: ' + ', '.join(missing_seams))
    if errors:
        print('Launch wedge check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1
    print('Launch wedge check passed')
    print(f'Validated {len(cards)} wedge cards covering seams: {", ".join(sorted(seams))}.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
