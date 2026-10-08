#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / 'proofgrounds' / 'portfolio-exemplar-federation-v0' / 'exemplars.json'
SCEN = ROOT / 'proofgrounds' / 'portfolio-scenario-matrix-v0' / 'scenarios.json'
ANC = ROOT / 'proofgrounds' / 'portfolio-anchor-corpus-v0' / 'anchors.json'
REQUIRED_TOP = ['schema_family', 'revision', 'exemplars']
REQUIRED_FIELDS = [
    'exemplar_id',
    'title',
    'exemplar_class',
    'scenario_bindings',
    'anchor_bindings',
    'workspace_posture',
    'privacy_posture',
    'renewal_cadence',
    'required_artifacts',
    'comparison_invariants',
    'allowed_variation',
    'public_twin_strategy',
    'must_not_claim',
    'notes',
]
REQUIRED_CLASSES = {
    'public_inner_loop_exemplar',
    'public_release_boundary_exemplar',
    'restricted_shadow_exemplar',
    'public_native_edge_exemplar',
    'cross_target_docs_exemplar',
}

def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''

def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0

def main() -> int:
    errors: list[str] = []
    for p in [EX, SCEN, ANC]:
        if not p.exists():
            errors.append(f'missing required file: {p.relative_to(ROOT)}')
    if errors:
        print('Exemplar federation check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1

    try:
        payload = json.loads(EX.read_text(encoding='utf-8'))
        scenarios = json.loads(SCEN.read_text(encoding='utf-8'))
        anchors = json.loads(ANC.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'failed to parse exemplar federation inputs: {exc}', file=sys.stderr)
        return 1

    scenario_ids = {s.get('scenario_id') for s in scenarios.get('scenarios', []) if isinstance(s, dict)}
    anchor_ids = {a.get('anchor_id') for a in anchors.get('anchors', []) if isinstance(a, dict)}

    for field in REQUIRED_TOP:
        if field not in payload:
            errors.append(f'missing top-level field: {field}')
    exemplars = payload.get('exemplars')
    if not isinstance(exemplars, list):
        errors.append('top-level exemplars must be a list')
        exemplars = []
    if len(exemplars) < 5:
        errors.append('federation must include at least five exemplars')

    ids: set[str] = set()
    classes: set[str] = set()
    covered_scenarios: set[str] = set()
    for idx, card in enumerate(exemplars):
        label = f'exemplars[{idx}]'
        if not isinstance(card, dict):
            errors.append(f'{label} must be an object')
            continue
        for field in REQUIRED_FIELDS:
            if field not in card:
                errors.append(f'{label} missing required field {field}')
        eid = card.get('exemplar_id')
        klass = card.get('exemplar_class')
        if not non_empty_string(eid):
            errors.append(f'{label} exemplar_id must be non-empty string')
        elif eid in ids:
            errors.append(f'duplicate exemplar_id: {eid}')
        else:
            ids.add(eid)
        if not non_empty_string(card.get('title')):
            errors.append(f'{label} title must be non-empty string')
        if not non_empty_string(klass):
            errors.append(f'{label} exemplar_class must be non-empty string')
        else:
            classes.add(klass)
        if not isinstance(card.get('workspace_posture'), dict) or len(card.get('workspace_posture')) == 0:
            errors.append(f'{label} workspace_posture must be a non-empty object')
        for key in ['scenario_bindings', 'anchor_bindings', 'required_artifacts', 'comparison_invariants', 'allowed_variation', 'must_not_claim', 'notes']:
            if not non_empty_list(card.get(key)):
                errors.append(f'{label} {key} must be non-empty list')
        for key in ['privacy_posture', 'renewal_cadence', 'public_twin_strategy']:
            if not non_empty_string(card.get(key)):
                errors.append(f'{label} {key} must be non-empty string')
        for sid in card.get('scenario_bindings', []):
            if sid not in scenario_ids:
                errors.append(f'{label} binds unknown scenario_id: {sid}')
            else:
                covered_scenarios.add(sid)
        for aid in card.get('anchor_bindings', []):
            if aid not in anchor_ids:
                errors.append(f'{label} binds unknown anchor_id: {aid}')

    missing_classes = sorted(REQUIRED_CLASSES - classes)
    if missing_classes:
        errors.append('missing required exemplar classes: ' + ', '.join(missing_classes))
    missing_scenarios = sorted(s for s in scenario_ids if s not in covered_scenarios)
    if missing_scenarios:
        errors.append('federation does not cover all current scenario_ids: ' + ', '.join(missing_scenarios))

    if errors:
        print('Exemplar federation check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1

    print('Exemplar federation check passed')
    print(f'Validated {len(exemplars)} exemplar cards with class coverage: {", ".join(sorted(classes))}.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
