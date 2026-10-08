#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'ledgers' / 'portfolio-hypothesis-ledger-v0' / 'hypotheses.json'
REQUIRED_TOP = ['schema_family','revision','hypotheses']
REQUIRED_CARD_FIELDS = ['hypothesis_id','title','claim_class','status','statement','supporting_sources','related_seams','related_assets','affected_loops','leading_indicators','downgrade_triggers','falsifiers','review_horizon','notes']
REQUIRED_CLASSES = {'one_project_ranking','multi_project_ranking','frontier_posture','anti_tacit_knowledge','staging_claim','portfolio_hygiene','proof_discipline'}
ALLOWED_STATUS = {'active','narrowed','degraded','superseded','retired'}
ALLOWED_HORIZON = {'hot','warm','cool','cold'}
ALLOWED_LOOPS = {'watchcard','packet','stewardship','canon','hygiene'}

def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''

def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0

def main() -> int:
    errors=[]
    if not LEDGER.exists():
        print(f'missing ledger file: {LEDGER.relative_to(ROOT)}', file=sys.stderr); return 1
    try:
        payload=json.loads(LEDGER.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'failed to parse ledger: {exc}', file=sys.stderr); return 1
    for field in REQUIRED_TOP:
        if field not in payload: errors.append(f'missing top-level field: {field}')
    cards=payload.get('hypotheses')
    if not isinstance(cards,list):
        errors.append('top-level hypotheses must be a list'); cards=[]
    if len(cards)<7: errors.append('hypothesis ledger must include at least seven cards')
    ids=set(); classes=set()
    for idx,card in enumerate(cards):
        label=f'hypotheses[{idx}]'
        if not isinstance(card,dict): errors.append(f'{label} must be an object'); continue
        for field in REQUIRED_CARD_FIELDS:
            if field not in card: errors.append(f'{label} missing required field {field}')
        hid=card.get('hypothesis_id')
        if not non_empty_string(hid): errors.append(f'{label} hypothesis_id must be non-empty string')
        elif hid in ids: errors.append(f'duplicate hypothesis_id: {hid}')
        else: ids.add(hid)
        if not non_empty_string(card.get('title')): errors.append(f'{label} title must be non-empty string')
        cclass=card.get('claim_class')
        if not non_empty_string(cclass): errors.append(f'{label} claim_class must be non-empty string')
        else: classes.add(cclass)
        if card.get('status') not in ALLOWED_STATUS: errors.append(f'{label} status must be one of {sorted(ALLOWED_STATUS)}')
        if card.get('review_horizon') not in ALLOWED_HORIZON: errors.append(f'{label} review_horizon must be one of {sorted(ALLOWED_HORIZON)}')
        if not non_empty_string(card.get('statement')): errors.append(f'{label} statement must be non-empty string')
        loops = card.get('affected_loops', [])
        if not non_empty_list(loops):
            errors.append(f'{label} affected_loops must be non-empty list')
        else:
            for loop in loops:
                if loop not in ALLOWED_LOOPS:
                    errors.append(f'{label} affected_loops entries must be one of {sorted(ALLOWED_LOOPS)}')
        for key in ['supporting_sources','related_seams','related_assets','leading_indicators','downgrade_triggers','falsifiers','notes']:
            if not non_empty_list(card.get(key)): errors.append(f'{label} {key} must be non-empty list')
        for source in card.get('supporting_sources',[]):
            if not non_empty_string(source) or not source.startswith('http'): errors.append(f'{label} supporting_sources entries must be non-empty URLs')
        for asset in card.get('related_assets',[]):
            if not non_empty_string(asset): errors.append(f'{label} related_assets entries must be non-empty paths'); continue
            if not (ROOT / asset).exists(): errors.append(f'{label} related asset does not exist: {asset}')
    missing_classes=sorted(REQUIRED_CLASSES - classes)
    if missing_classes: errors.append('missing required claim classes: ' + ', '.join(missing_classes))
    if errors:
        print('Hypothesis ledger check FAILED', file=sys.stderr)
        for err in errors: print(f'- {err}', file=sys.stderr)
        return 1
    print('Hypothesis ledger check passed')
    print(f'Validated {len(cards)} hypothesis cards with class coverage: {", ".join(sorted(classes))}.')
    return 0
if __name__ == '__main__': raise SystemExit(main())
