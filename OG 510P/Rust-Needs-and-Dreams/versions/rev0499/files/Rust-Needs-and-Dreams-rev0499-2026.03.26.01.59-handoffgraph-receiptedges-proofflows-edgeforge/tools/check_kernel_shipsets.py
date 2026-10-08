#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'ledgers' / 'top-band-kernel-shipsets-v0' / 'shipsets.json'
REQUIRED_TOP = ['schema_family', 'revision', 'shipsets']
REQUIRED_CARD_FIELDS = ['shipset_id', 'title', 'seam', 'status', 'shipset_kind', 'kernel_codename', 'credible_home', 'repo_modules', 'initial_commands', 'import_surfaces', 'primary_journeys', 'proof_artifacts', 'proving_grounds', 'maintenance_burdens', 'refused_expansions', 'exit_criteria', 'related_assets', 'supporting_sources', 'review_horizon', 'notes']
REQUIRED_SEAMS = {
    'Build-State Evidence',
    'Package Intake + Release Boundary Review',
    'Feedback / Debug Acceptance Commons',
    'Safety-Critical + Institutional Readiness Commons',
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
        print(f'missing kernel shipset ledger file: {LEDGER.relative_to(ROOT)}', file=sys.stderr)
        return 1
    try:
        payload = json.loads(LEDGER.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'failed to parse kernel shipset ledger: {exc}', file=sys.stderr)
        return 1
    for field in REQUIRED_TOP:
        if field not in payload:
            errors.append(f'missing top-level field: {field}')
    cards = payload.get('shipsets')
    if not isinstance(cards, list):
        errors.append('top-level shipsets must be a list')
        cards = []
    ids = set(); seams = set()
    for idx, card in enumerate(cards):
        label = f'shipsets[{idx}]'
        if not isinstance(card, dict):
            errors.append(f'{label} must be an object')
            continue
        for field in REQUIRED_CARD_FIELDS:
            if field not in card:
                errors.append(f'{label} missing required field {field}')
        sid = card.get('shipset_id')
        if not non_empty_string(sid):
            errors.append(f'{label} shipset_id must be non-empty string')
        elif sid in ids:
            errors.append(f'duplicate shipset_id: {sid}')
        else:
            ids.add(sid)
        seam = card.get('seam')
        if not non_empty_string(seam):
            errors.append(f'{label} seam must be non-empty string')
        else:
            seams.add(seam)
        for key in ['title', 'shipset_kind', 'kernel_codename', 'credible_home']:
            if not non_empty_string(card.get(key)):
                errors.append(f'{label} {key} must be non-empty string')
        if card.get('status') not in ALLOWED_STATUS:
            errors.append(f'{label} status must be one of {sorted(ALLOWED_STATUS)}')
        if card.get('review_horizon') not in ALLOWED_HORIZON:
            errors.append(f'{label} review_horizon must be one of {sorted(ALLOWED_HORIZON)}')
        for key in ['repo_modules', 'initial_commands', 'import_surfaces', 'primary_journeys', 'proof_artifacts', 'proving_grounds', 'maintenance_burdens', 'refused_expansions', 'exit_criteria', 'related_assets', 'supporting_sources', 'notes']:
            if not non_empty_list(card.get(key)):
                errors.append(f'{label} {key} must be non-empty list')
        for asset in card.get('related_assets', []):
            if not non_empty_string(asset):
                errors.append(f'{label} related_assets entries must be non-empty paths')
                continue
            if not (ROOT / asset).exists():
                errors.append(f'{label} related asset does not exist: {asset}')
        for source in card.get('supporting_sources', []):
            if not non_empty_string(source) or not source.startswith('http'):
                errors.append(f'{label} supporting_sources entries must be non-empty URLs')
    missing_seams = sorted(REQUIRED_SEAMS - seams)
    if missing_seams:
        errors.append('kernel shipset ledger missing seam coverage: ' + ', '.join(missing_seams))
    if errors:
        print('Kernel shipset check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1
    print('Kernel shipset check passed')
    print(f'Validated {len(cards)} shipset cards covering seams: {", ".join(sorted(seams))}.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
