#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'ledgers' / 'top-band-handoff-graph-v0' / 'handoffs.json'
REQUIRED_TOP = ['schema_family', 'revision', 'handoffs']
REQUIRED_CARD_FIELDS = ['handoff_id', 'title', 'handoff_class', 'status', 'producer', 'consumer', 'primary_journeys', 'entry_artifacts', 'transforms', 'output_receipts', 'stable_surfaces', 'unstable_or_service_boundaries', 'refused_collapses', 'credible_home', 'related_assets', 'supporting_sources', 'review_horizon', 'notes']
REQUIRED_CLASSES = {
    'cargo_raw_facts_to_build_state_pack',
    'build_state_pack_to_debug_acceptance',
    'registry_truth_to_intake_review',
    'structured_api_facts_to_release_boundary_review',
    'intake_and_compatibility_to_safety_readiness',
    'reviewed_receipts_to_navigation_defaults',
}
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
        print(f'missing handoff graph file: {LEDGER.relative_to(ROOT)}', file=sys.stderr)
        return 1
    try:
        payload = json.loads(LEDGER.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'failed to parse handoff graph: {exc}', file=sys.stderr)
        return 1
    for field in REQUIRED_TOP:
        if field not in payload:
            errors.append(f'missing top-level field: {field}')
    cards = payload.get('handoffs')
    if not isinstance(cards, list):
        errors.append('top-level handoffs must be a list')
        cards = []
    if len(cards) < len(REQUIRED_CLASSES):
        errors.append('handoff graph must include at least one card for each required handoff class')
    ids = set(); classes = set(); seam_hits = set()
    for idx, card in enumerate(cards):
        label = f'handoffs[{idx}]'
        if not isinstance(card, dict):
            errors.append(f'{label} must be an object')
            continue
        for field in REQUIRED_CARD_FIELDS:
            if field not in card:
                errors.append(f'{label} missing required field {field}')
        hid = card.get('handoff_id')
        if not non_empty_string(hid):
            errors.append(f'{label} handoff_id must be non-empty string')
        elif hid in ids:
            errors.append(f'duplicate handoff_id: {hid}')
        else:
            ids.add(hid)
        hclass = card.get('handoff_class')
        if not non_empty_string(hclass):
            errors.append(f'{label} handoff_class must be non-empty string')
        else:
            classes.add(hclass)
        if card.get('status') not in ALLOWED_STATUS:
            errors.append(f'{label} status must be one of {sorted(ALLOWED_STATUS)}')
        if card.get('review_horizon') not in ALLOWED_HORIZON:
            errors.append(f'{label} review_horizon must be one of {sorted(ALLOWED_HORIZON)}')
        for key in ['title', 'producer', 'consumer', 'credible_home']:
            if not non_empty_string(card.get(key)):
                errors.append(f'{label} {key} must be non-empty string')
        for key in ['primary_journeys', 'entry_artifacts', 'transforms', 'output_receipts', 'stable_surfaces', 'unstable_or_service_boundaries', 'refused_collapses', 'related_assets', 'supporting_sources', 'notes']:
            if not non_empty_list(card.get(key)):
                errors.append(f'{label} {key} must be non-empty list')
        text = f"{card.get('producer','')} {card.get('consumer','')}"
        for seam in REQUIRED_SEAMS:
            if seam in text:
                seam_hits.add(seam)
        for asset in card.get('related_assets', []):
            if not non_empty_string(asset):
                errors.append(f'{label} related_assets entries must be non-empty paths')
                continue
            if not (ROOT / asset).exists():
                errors.append(f'{label} related asset does not exist: {asset}')
        for source in card.get('supporting_sources', []):
            if not non_empty_string(source) or not source.startswith('http'):
                errors.append(f'{label} supporting_sources entries must be non-empty URLs')
    missing_classes = sorted(REQUIRED_CLASSES - classes)
    if missing_classes:
        errors.append('missing required handoff classes: ' + ', '.join(missing_classes))
    missing_seams = sorted(REQUIRED_SEAMS - seam_hits)
    if missing_seams:
        errors.append('handoff graph missing seam coverage: ' + ', '.join(missing_seams))
    if errors:
        print('Handoff graph check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1
    print('Handoff graph check passed')
    print(f'Validated {len(cards)} handoff cards covering seams: {", ".join(sorted(seam_hits))}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
