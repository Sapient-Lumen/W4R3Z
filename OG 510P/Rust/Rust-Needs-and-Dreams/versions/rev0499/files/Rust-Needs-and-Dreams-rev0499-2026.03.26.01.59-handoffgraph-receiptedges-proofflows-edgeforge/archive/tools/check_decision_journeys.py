#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'ledgers' / 'portfolio-decision-journeys-v0' / 'journeys.json'
REQUIRED_TOP = ['schema_family', 'revision', 'journeys']
REQUIRED_CARD_FIELDS = ['journey_id', 'title', 'journey_class', 'status', 'primary_decision', 'entry_seam', 'supporting_seams', 'trigger_moment', 'entry_artifacts', 'major_steps', 'decision_outputs', 'proof_of_completion', 'anti_goals', 'credible_home', 'related_assets', 'supporting_sources', 'review_horizon', 'notes']
REQUIRED_CLASSES = {
    'build_regression_triage',
    'dependency_admission_publish_review',
    'debug_issue_handoff',
    'release_boundary_review',
    'safety_readiness_evaluation',
    'conservative_default_selection',
}
ALLOWED_STATUS = {'active', 'candidate', 'hold', 'retired'}
ALLOWED_HORIZON = {'hot', 'warm', 'cool', 'cold'}
REQUIRED_SEAMS = {
    'Build-State Evidence',
    'Package Intake + Release Boundary Review',
    'Feedback / Debug Acceptance Commons',
    'Safety-Critical + Institutional Readiness Commons',
    'Compatibility Claims',
    'Adoption Navigation + Ecosystem Atlas',
    'Tooling Contract / Semantic Context',
}

def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''

def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0

def main() -> int:
    errors = []
    if not LEDGER.exists():
        print(f'missing journey ledger file: {LEDGER.relative_to(ROOT)}', file=sys.stderr)
        return 1
    try:
        payload = json.loads(LEDGER.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'failed to parse journey ledger: {exc}', file=sys.stderr)
        return 1
    for field in REQUIRED_TOP:
        if field not in payload:
            errors.append(f'missing top-level field: {field}')
    cards = payload.get('journeys')
    if not isinstance(cards, list):
        errors.append('top-level journeys must be a list')
        cards = []
    if len(cards) < len(REQUIRED_CLASSES):
        errors.append('journey ledger must include at least one card for each required journey class')
    ids = set(); classes = set(); seams = set()
    for idx, card in enumerate(cards):
        label = f'journeys[{idx}]'
        if not isinstance(card, dict):
            errors.append(f'{label} must be an object')
            continue
        for field in REQUIRED_CARD_FIELDS:
            if field not in card:
                errors.append(f'{label} missing required field {field}')
        jid = card.get('journey_id')
        if not non_empty_string(jid):
            errors.append(f'{label} journey_id must be non-empty string')
        elif jid in ids:
            errors.append(f'duplicate journey_id: {jid}')
        else:
            ids.add(jid)
        jclass = card.get('journey_class')
        if not non_empty_string(jclass):
            errors.append(f'{label} journey_class must be non-empty string')
        else:
            classes.add(jclass)
        seam = card.get('entry_seam')
        if not non_empty_string(seam):
            errors.append(f'{label} entry_seam must be non-empty string')
        else:
            seams.add(seam)
        if card.get('status') not in ALLOWED_STATUS:
            errors.append(f'{label} status must be one of {sorted(ALLOWED_STATUS)}')
        if card.get('review_horizon') not in ALLOWED_HORIZON:
            errors.append(f'{label} review_horizon must be one of {sorted(ALLOWED_HORIZON)}')
        for key in ['title', 'primary_decision', 'trigger_moment', 'credible_home']:
            if not non_empty_string(card.get(key)):
                errors.append(f'{label} {key} must be non-empty string')
        for key in ['supporting_seams', 'entry_artifacts', 'major_steps', 'decision_outputs', 'proof_of_completion', 'anti_goals', 'related_assets', 'supporting_sources', 'notes']:
            if not non_empty_list(card.get(key)):
                errors.append(f'{label} {key} must be non-empty list')
        for s in card.get('supporting_seams', []):
            if not non_empty_string(s):
                errors.append(f'{label} supporting_seams entries must be non-empty strings')
            else:
                seams.add(s)
        for source in card.get('supporting_sources', []):
            if not non_empty_string(source) or not source.startswith('http'):
                errors.append(f'{label} supporting_sources entries must be non-empty URLs')
        for asset in card.get('related_assets', []):
            if not non_empty_string(asset):
                errors.append(f'{label} related_assets entries must be non-empty paths')
                continue
            if not (ROOT / asset).exists():
                errors.append(f'{label} related asset does not exist: {asset}')
    missing_classes = sorted(REQUIRED_CLASSES - classes)
    if missing_classes:
        errors.append('missing required journey classes: ' + ', '.join(missing_classes))
    missing_seams = sorted(REQUIRED_SEAMS - seams)
    if missing_seams:
        errors.append('journey ledger missing seam coverage: ' + ', '.join(missing_seams))
    if errors:
        print('Decision journey check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1
    print('Decision journey check passed')
    print(f'Validated {len(cards)} decision journey cards with class coverage: {", ".join(sorted(classes))}.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
