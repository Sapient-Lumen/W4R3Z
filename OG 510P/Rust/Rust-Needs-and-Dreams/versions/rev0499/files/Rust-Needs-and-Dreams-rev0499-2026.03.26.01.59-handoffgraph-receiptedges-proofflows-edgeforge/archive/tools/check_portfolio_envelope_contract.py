#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
SPECIMENS = ROOT / 'specimens' / 'portfolio-envelope-v0'
FIXTURES = ROOT / 'fixtures' / 'portfolio-envelope-v0'
CONFIG = FIXTURES / 'portfolio-envelope-hygiene-checks.json'

REQUIRED_FIELDS = [
    'schema_family',
    'specimen_role',
    'seam',
    'subject',
    'scope',
    'authority',
    'freshness',
    'partiality',
    'imports',
    'attachments',
    'payload',
    'lineage',
    'handoff',
]


def load_json(path: Path) -> Dict[str, Any]:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def nested_get(data: Dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split('.'):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ''


def non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def validate_artifact(data: Dict[str, Any], *, rel: str) -> List[str]:
    errors: List[str] = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f'{rel}: missing required field {field}')

    if errors:
        return errors

    if not isinstance(data['lineage'], dict):
        errors.append(f'{rel}: lineage must be an object')
        return errors
    if not isinstance(data['handoff'], dict):
        errors.append(f'{rel}: handoff must be an object')
        return errors

    parents = nested_get(data, 'lineage.parents')
    if parents is None:
        errors.append(f'{rel}: lineage.parents missing')
    elif not isinstance(parents, list):
        errors.append(f'{rel}: lineage.parents must be a list')

    escalation = nested_get(data, 'handoff.escalation_target')
    if not non_empty_string(escalation):
        errors.append(f'{rel}: handoff.escalation_target must be non-empty')

    allowed_consumers = nested_get(data, 'handoff.allowed_consumers')
    if not non_empty_list(allowed_consumers):
        errors.append(f'{rel}: handoff.allowed_consumers must be non-empty')

    role = data.get('specimen_role')
    if role != 'canonical_pack':
        if not non_empty_list(parents):
            errors.append(f'{rel}: non-canonical artifacts must declare at least one lineage parent')

    if role == 'canonical_pack':
        if nested_get(data, 'handoff.lossiness_budget') != 'none_for_canonical_pack':
            errors.append(f'{rel}: canonical_pack must use lossiness_budget none_for_canonical_pack')
    elif role == 'routed_brief':
        if not non_empty_string(nested_get(data, 'scope.brief_for')):
            errors.append(f'{rel}: routed_brief must declare scope.brief_for')
        if not non_empty_list(nested_get(data, 'payload.allowed_decisions')):
            errors.append(f'{rel}: routed_brief must declare non-empty allowed_decisions')
        if not non_empty_list(nested_get(data, 'payload.prohibited_decisions')):
            errors.append(f'{rel}: routed_brief must declare non-empty prohibited_decisions')
        if not non_empty_string(escalation):
            errors.append(f'{rel}: routed_brief must declare a non-empty escalation_target')
    elif role == 'verify_receipt':
        if nested_get(data, 'payload.verdict') is None:
            errors.append(f'{rel}: verify_receipt must declare payload.verdict')
        if not non_empty_list(nested_get(data, 'payload.prohibited_conclusions')):
            errors.append(f'{rel}: verify_receipt must declare non-empty prohibited_conclusions')
    elif role == 'diff':
        if not non_empty_string(nested_get(data, 'subject.left_pack')):
            errors.append(f'{rel}: diff must declare subject.left_pack')
        if not non_empty_string(nested_get(data, 'subject.right_pack')):
            errors.append(f'{rel}: diff must declare subject.right_pack')
    elif role == 'lineage_receipt':
        if not non_empty_string(nested_get(data, 'payload.transform')):
            errors.append(f'{rel}: lineage_receipt must declare payload.transform')
        if not non_empty_list(nested_get(data, 'payload.preserved_truths')):
            errors.append(f'{rel}: lineage_receipt must declare non-empty preserved_truths')
        if not non_empty_list(nested_get(data, 'payload.omitted_truths')):
            errors.append(f'{rel}: lineage_receipt must declare non-empty omitted_truths')

    return errors


def check_positive_examples() -> List[str]:
    errors: List[str] = []
    for path in sorted(SPECIMENS.glob('*.json')):
        data = load_json(path)
        errors.extend(validate_artifact(data, rel=str(path.relative_to(ROOT))))
    return errors


def check_negative_examples(config: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = config.get('expected_invalid_cases', {})
    seen = set()
    for path in sorted((FIXTURES / 'invalid').glob('*.json')):
        rel = str(path.relative_to(FIXTURES))
        seen.add(rel)
        data = load_json(path)
        found = validate_artifact(data, rel=str(path.relative_to(ROOT)))
        if not found:
            errors.append(f'{rel}: expected invalid fixture to fail, but it passed')
            continue
        for token in expected.get(rel, []):
            if not any(token in err for err in found):
                errors.append(f'{rel}: expected failure token not found: {token}')
    for rel in expected:
        if rel not in seen:
            errors.append(f'missing expected invalid fixture {rel}')
    return errors


def main() -> int:
    config = load_json(CONFIG)
    errors: List[str] = []
    errors.extend(check_positive_examples())
    errors.extend(check_negative_examples(config))

    if errors:
        print('Portfolio envelope contract check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1

    specimen_count = len(list(SPECIMENS.glob('*.json')))
    invalid_count = len(list((FIXTURES / 'invalid').glob('*.json')))
    print('Portfolio envelope contract check passed')
    print(
        f'Validated {specimen_count} passing specimen files and {invalid_count} negative fixtures against the shared honesty rules.'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
