#!/usr/bin/env python3
"""Semantic-test-vector runner for TimeSync archive validation.

The archive validator still owns schema and semantic check functions.  This
module owns the mechanics of vector IDs, fixture coverage, JSON-load failure
expectations, and pass/fail accounting so those mechanics can be tested and
kept out of the monolithic validator.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

LoadJson = Callable[[str], Any]
SchemaValidate = Callable[[str, Any], list[str]]
SemanticValidate = Callable[[str, Any, Any, Any], list[str]]


def check_vector_ids(vectors: list[Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, vector in enumerate(vectors, start=1):
        if not isinstance(vector, dict):
            continue
        test_id = vector.get('id')
        if not isinstance(test_id, str) or not test_id.strip():
            errors.append(f'semantic vector #{index} missing non-empty id')
            continue
        if test_id in seen:
            errors.append(f'duplicate semantic vector id: {test_id}')
        seen.add(test_id)
    return errors


def check_example_vector_coverage(vectors: list[Any], root: Path) -> list[str]:
    errors: list[str] = []
    covered: set[str] = set()
    for vector in vectors:
        if isinstance(vector, dict) and isinstance(vector.get('path'), str):
            rel = vector['path']
            if rel.startswith('examples/') and rel.endswith('.json'):
                covered.add(rel)
    actual = sorted(
        str(path.relative_to(root))
        for path in (root / 'examples').rglob('*.json')
        if path.is_file()
    )
    for rel in actual:
        if rel not in covered:
            errors.append(f'semantic-test-vectors missing example fixture: {rel}')
    for rel in sorted(covered - set(actual)):
        errors.append(f'semantic-test-vectors references missing example fixture: {rel}')
    return errors


def run_vectors(
    vectors: list[Any],
    *,
    load_json: LoadJson,
    schema_validate: SchemaValidate,
    semantic_validate: SemanticValidate,
    catalog_index: Any,
    adapter_index: Any,
) -> list[str]:
    errors: list[str] = []
    for vector in vectors:
        if not isinstance(vector, dict):
            errors.append('semantic vector is not an object')
            continue
        vid = vector.get('id', '<no-id>')
        rel = vector.get('path')
        schema_name = vector.get('schema')
        expected = vector.get('expected')
        if not rel or not schema_name or not expected:
            errors.append(f'{vid}: missing path/schema/expected')
            continue
        try:
            obj = load_json(rel)
        except Exception as exc:  # noqa: BLE001
            if expected == 'fail_json':
                contains = vector.get('expected_error_contains')
                if contains and contains.lower() not in str(exc).lower():
                    errors.append(f'{vid}: JSON failure did not mention {contains!r}: {exc}')
                continue
            errors.append(f'{vid}: cannot load {rel}: {exc}')
            continue
        if expected == 'fail_json':
            errors.append(f'{vid}: expected JSON parse/I-JSON failure but load passed')
            continue
        schema_errors = schema_validate(schema_name, obj)
        semantic_errors = semantic_validate(schema_name, obj, catalog_index, adapter_index)
        all_errors = schema_errors + semantic_errors
        if expected == 'pass':
            if all_errors:
                errors.append(f'{vid}: expected pass but got errors: {all_errors}')
        elif expected == 'fail_schema':
            if not schema_errors:
                errors.append(f'{vid}: expected schema failure but schema passed')
            contains = vector.get('expected_error_contains')
            if contains and not any(contains.lower() in e.lower() for e in schema_errors):
                errors.append(f'{vid}: schema failure did not mention {contains!r}: {schema_errors}')
        elif expected == 'fail_semantic':
            if schema_errors:
                errors.append(f'{vid}: expected semantic failure but schema failed first: {schema_errors}')
            elif not semantic_errors:
                errors.append(f'{vid}: expected semantic failure but semantic checks passed')
            else:
                contains = vector.get('expected_error_contains')
                if contains and not any(contains.lower() in e.lower() for e in semantic_errors):
                    errors.append(f'{vid}: semantic failure did not mention {contains!r}: {semantic_errors}')
        else:
            errors.append(f'{vid}: unknown expected value {expected!r}')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    if not any('duplicate semantic vector id' in e for e in check_vector_ids([
        {'id': 'TV-X', 'path': 'examples/a.json', 'schema': 'wire-claim', 'expected': 'pass'},
        {'id': 'TV-X', 'path': 'examples/b.json', 'schema': 'wire-claim', 'expected': 'pass'},
    ])):
        errors.append('semantic_vectors self-test failed: duplicate id accepted')

    def fake_load(rel: str) -> Any:
        if rel == 'bad.json':
            raise ValueError('duplicate JSON object member name')
        return {'ok': True}

    def fake_schema(_schema: str, obj: Any) -> list[str]:
        return [] if obj.get('ok') else ['schema failed']

    def fake_semantic(_schema: str, obj: Any, _catalog: Any, _adapter: Any) -> list[str]:
        return ['semantic failed'] if obj.get('semantic_bad') else []

    if run_vectors([
        {'id': 'TV-J', 'path': 'bad.json', 'schema': 'wire-claim', 'expected': 'fail_json', 'expected_error_contains': 'duplicate'},
        {'id': 'TV-P', 'path': 'ok.json', 'schema': 'wire-claim', 'expected': 'pass'},
    ], load_json=fake_load, schema_validate=fake_schema, semantic_validate=fake_semantic, catalog_index={}, adapter_index={}):
        errors.append('semantic_vectors self-test failed: valid fake vector run rejected')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync semantic vector runner self-test passed.')
