#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / 'proofgrounds' / 'portfolio-scenario-matrix-v0' / 'scenarios.json'

REQUIRED_TOP = ['schema_family', 'revision', 'scenarios']
REQUIRED_SCENARIO_FIELDS = [
    'scenario_id',
    'title',
    'scenario_class',
    'primary_tax',
    'topology',
    'environment',
    'decision_classes',
    'relevant_seams',
    'minimum_artifacts',
    'must_prove',
    'must_not_claim',
    'skip_conditions',
]
REQUIRED_CLASSES = {
    'inner_loop_workspace',
    'public_release_boundary',
    'locked_down_intake',
    'native_edge_polyglot',
}
PREFERRED_CLASSES = {'cross_target_docs_drift'}


def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''


def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0


def main() -> int:
    errors: list[str] = []
    if not MATRIX.exists():
        errors.append(f'missing matrix file: {MATRIX.relative_to(ROOT)}')
    else:
        try:
            data = json.loads(MATRIX.read_text(encoding='utf-8'))
        except Exception as exc:  # noqa: BLE001
            errors.append(f'failed to parse scenarios.json: {exc}')
            data = None

        if isinstance(data, dict):
            for field in REQUIRED_TOP:
                if field not in data:
                    errors.append(f'missing top-level field: {field}')
            scenarios = data.get('scenarios')
            if not isinstance(scenarios, list):
                errors.append('top-level scenarios must be a list')
                scenarios = []
            if len(scenarios) < 4:
                errors.append('matrix must include at least four scenarios')
            ids: set[str] = set()
            classes: set[str] = set()
            for idx, scenario in enumerate(scenarios):
                label = f'scenarios[{idx}]'
                if not isinstance(scenario, dict):
                    errors.append(f'{label} must be an object')
                    continue
                for field in REQUIRED_SCENARIO_FIELDS:
                    if field not in scenario:
                        errors.append(f'{label} missing required field {field}')
                sid = scenario.get('scenario_id')
                sclass = scenario.get('scenario_class')
                if not non_empty_string(sid):
                    errors.append(f'{label} scenario_id must be non-empty string')
                elif sid in ids:
                    errors.append(f'duplicate scenario_id: {sid}')
                else:
                    ids.add(sid)
                if not non_empty_string(sclass):
                    errors.append(f'{label} scenario_class must be non-empty string')
                else:
                    classes.add(sclass)
                for key in ['title', 'primary_tax']:
                    if not non_empty_string(scenario.get(key)):
                        errors.append(f'{label} {key} must be non-empty string')
                for key in ['decision_classes', 'relevant_seams', 'minimum_artifacts', 'must_prove', 'must_not_claim', 'skip_conditions']:
                    if not non_empty_list(scenario.get(key)):
                        errors.append(f'{label} {key} must be non-empty list')
                for key in ['topology', 'environment']:
                    if not isinstance(scenario.get(key), dict) or len(scenario.get(key)) == 0:
                        errors.append(f'{label} {key} must be a non-empty object')
            missing_classes = sorted(REQUIRED_CLASSES - classes)
            if missing_classes:
                errors.append('missing required scenario classes: ' + ', '.join(missing_classes))
            missing_preferred = sorted(PREFERRED_CLASSES - classes)
            if missing_preferred:
                errors.append('missing preferred scenario classes: ' + ', '.join(missing_preferred))

    if errors:
        print('Proving-grounds matrix check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1

    payload = json.loads(MATRIX.read_text(encoding='utf-8'))
    count = len(payload['scenarios'])
    classes = sorted({scenario['scenario_class'] for scenario in payload['scenarios']})
    print('Proving-grounds matrix check passed')
    print(f'Validated {count} scenario cards with class coverage: {", ".join(classes)}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
