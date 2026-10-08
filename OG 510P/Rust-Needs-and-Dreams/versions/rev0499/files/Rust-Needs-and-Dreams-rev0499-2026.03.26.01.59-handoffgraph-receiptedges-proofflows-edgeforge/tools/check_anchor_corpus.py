#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / 'proofgrounds' / 'portfolio-scenario-matrix-v0' / 'scenarios.json'
ANCHORS = ROOT / 'proofgrounds' / 'portfolio-anchor-corpus-v0' / 'anchors.json'

REQUIRED_TOP = ['schema_family', 'revision', 'anchors']
REQUIRED_ANCHOR_FIELDS = [
    'anchor_id',
    'title',
    'anchor_class',
    'scenario_bindings',
    'representative_shape',
    'required_traits',
    'hold_constant',
    'allowed_variation',
    'minimum_artifacts',
    'primary_evidence_focus',
    'must_not_claim',
    'notes',
]
REQUIRED_CLASSES = {
    'workspace_profile',
    'release_boundary_profile',
    'intake_policy_profile',
    'native_edge_profile',
    'docs_consumer_profile',
}


def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''


def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0


def load_json(path: Path, label: str, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f'missing {label} file: {path.relative_to(ROOT)}')
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        errors.append(f'failed to parse {label}: {exc}')
        return None


def main() -> int:
    errors: list[str] = []
    scenario_data = load_json(SCENARIOS, 'scenario matrix', errors)
    anchor_data = load_json(ANCHORS, 'anchor corpus', errors)

    scenario_ids: set[str] = set()
    if isinstance(scenario_data, dict):
        for entry in scenario_data.get('scenarios', []):
            if isinstance(entry, dict) and non_empty_string(entry.get('scenario_id')):
                scenario_ids.add(entry['scenario_id'])

    if isinstance(anchor_data, dict):
        for field in REQUIRED_TOP:
            if field not in anchor_data:
                errors.append(f'missing top-level field: {field}')
        anchors = anchor_data.get('anchors')
        if not isinstance(anchors, list):
            errors.append('top-level anchors must be a list')
            anchors = []
        if len(anchors) < 5:
            errors.append('anchor corpus must include at least five anchors')
        ids: set[str] = set()
        classes: set[str] = set()
        covered_scenarios: set[str] = set()
        for idx, anchor in enumerate(anchors):
            label = f'anchors[{idx}]'
            if not isinstance(anchor, dict):
                errors.append(f'{label} must be an object')
                continue
            for field in REQUIRED_ANCHOR_FIELDS:
                if field not in anchor:
                    errors.append(f'{label} missing required field {field}')
            aid = anchor.get('anchor_id')
            aclass = anchor.get('anchor_class')
            if not non_empty_string(aid):
                errors.append(f'{label} anchor_id must be non-empty string')
            elif aid in ids:
                errors.append(f'duplicate anchor_id: {aid}')
            else:
                ids.add(aid)
            if not non_empty_string(aclass):
                errors.append(f'{label} anchor_class must be non-empty string')
            else:
                classes.add(aclass)
            if not non_empty_string(anchor.get('title')):
                errors.append(f'{label} title must be non-empty string')
            if not isinstance(anchor.get('representative_shape'), dict) or len(anchor.get('representative_shape')) == 0:
                errors.append(f'{label} representative_shape must be a non-empty object')
            for key in ['required_traits', 'hold_constant', 'allowed_variation', 'minimum_artifacts', 'primary_evidence_focus', 'must_not_claim', 'notes']:
                if not non_empty_list(anchor.get(key)):
                    errors.append(f'{label} {key} must be non-empty list')
            bindings = anchor.get('scenario_bindings')
            if not non_empty_list(bindings):
                errors.append(f'{label} scenario_bindings must be non-empty list')
            else:
                for binding in bindings:
                    if not non_empty_string(binding):
                        errors.append(f'{label} scenario_bindings entries must be non-empty strings')
                        continue
                    if binding not in scenario_ids:
                        errors.append(f'{label} binds unknown scenario_id: {binding}')
                    else:
                        covered_scenarios.add(binding)
        missing_classes = sorted(REQUIRED_CLASSES - classes)
        if missing_classes:
            errors.append('missing required anchor classes: ' + ', '.join(missing_classes))
        if scenario_ids:
            uncovered = sorted(scenario_ids - covered_scenarios)
            if uncovered:
                errors.append('anchor corpus does not cover scenario IDs: ' + ', '.join(uncovered))

    if errors:
        print('Anchor corpus check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1

    payload = json.loads(ANCHORS.read_text(encoding='utf-8'))
    count = len(payload['anchors'])
    classes = sorted({anchor['anchor_class'] for anchor in payload['anchors']})
    print('Anchor corpus check passed')
    print(f'Validated {count} anchor cards with class coverage: {", ".join(classes)}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
