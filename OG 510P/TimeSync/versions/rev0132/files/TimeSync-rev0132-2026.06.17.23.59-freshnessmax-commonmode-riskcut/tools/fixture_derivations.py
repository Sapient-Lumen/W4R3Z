#!/usr/bin/env python3
"""Validate patch-derived fixture families.

Large negative fixtures are useful for review, but they drift easily because most
of the file is a copied positive fixture. This helper verifies that selected
negative fixtures are still exactly reproducible from a positive base plus a
small set of explicit mutations. Rendered fixtures stay in the archive for audit
and semantic-vector execution; the manifest keeps the copy-paste debt visible and
machine-checkable.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import yaml  # type: ignore

from jcs import load_json_ijson

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path('tests/fixture-derivations.yaml')


class FixtureDerivationError(ValueError):
    pass


def _load_json(rel: str) -> Any:
    return load_json_ijson((ROOT / rel).read_text(encoding='utf-8'))


def _decode_pointer(pointer: str) -> list[str]:
    if pointer == '':
        return []
    if not pointer.startswith('/'):
        raise FixtureDerivationError(f'JSON pointer must start with /: {pointer}')
    return [part.replace('~1', '/').replace('~0', '~') for part in pointer.split('/')[1:]]


def _resolve_parent(obj: Any, pointer: str) -> tuple[Any, str]:
    parts = _decode_pointer(pointer)
    if not parts:
        raise FixtureDerivationError('operation path cannot target the document root')
    cur = obj
    for part in parts[:-1]:
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except Exception as exc:  # noqa: BLE001
                raise FixtureDerivationError(f'cannot resolve list index {part!r} in {pointer}') from exc
        elif isinstance(cur, dict):
            if part not in cur:
                raise FixtureDerivationError(f'cannot resolve object member {part!r} in {pointer}')
            cur = cur[part]
        else:
            raise FixtureDerivationError(f'cannot descend through {type(cur).__name__} in {pointer}')
    return cur, parts[-1]


def apply_operations(base: Any, operations: list[dict[str, Any]]) -> Any:
    obj = copy.deepcopy(base)
    for op in operations:
        kind = op.get('op')
        path = op.get('path')
        if not isinstance(path, str):
            raise FixtureDerivationError(f'operation path must be a string: {op}')
        parent, key = _resolve_parent(obj, path)
        if kind == 'set':
            if 'value' not in op:
                raise FixtureDerivationError(f'set operation missing value for {path}')
            value = copy.deepcopy(op['value'])
            if isinstance(parent, list):
                parent[int(key)] = value
            elif isinstance(parent, dict):
                parent[key] = value
            else:
                raise FixtureDerivationError(f'cannot set member on {type(parent).__name__} at {path}')
        elif kind == 'remove':
            if isinstance(parent, list):
                del parent[int(key)]
            elif isinstance(parent, dict):
                if key not in parent:
                    raise FixtureDerivationError(f'cannot remove missing member {path}')
                del parent[key]
            else:
                raise FixtureDerivationError(f'cannot remove member on {type(parent).__name__} at {path}')
        else:
            raise FixtureDerivationError(f'unsupported fixture derivation op {kind!r}')
    return obj


def load_manifest() -> list[dict[str, Any]]:
    with (ROOT / MANIFEST).open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise FixtureDerivationError(f'{MANIFEST} must be a list')
    return data


def validate_derivations() -> list[str]:
    errors: list[str] = []
    try:
        entries = load_manifest()
    except Exception as exc:  # noqa: BLE001
        return [f'{MANIFEST}: {exc}']
    seen_ids: set[str] = set()
    seen_outputs: dict[str, str] = {}
    for entry in entries:
        did = entry.get('id', '<no-id>') if isinstance(entry, dict) else '<not-object>'
        if not isinstance(entry, dict):
            errors.append(f'{did}: fixture derivation entry is not an object')
            continue
        if not isinstance(did, str) or not did:
            errors.append('fixture derivation entry requires non-empty id')
        elif did in seen_ids:
            errors.append(f'{did}: duplicate fixture derivation id')
        else:
            seen_ids.add(did)
        base_rel = entry.get('base')
        output_rel = entry.get('output')
        if isinstance(output_rel, str):
            prior = seen_outputs.get(output_rel)
            if prior is not None:
                errors.append(f'{did}: output {output_rel} already derived by {prior}')
            else:
                seen_outputs[output_rel] = str(did)
        operations = entry.get('operations')
        if not isinstance(base_rel, str) or not isinstance(output_rel, str) or not isinstance(operations, list):
            errors.append(f'{did}: fixture derivation requires base, output, and operations')
            continue
        try:
            derived = apply_operations(_load_json(base_rel), operations)
            rendered = _load_json(output_rel)
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{did}: fixture derivation failed: {exc}')
            continue
        if derived != rendered:
            expected = json.dumps(derived, indent=2, sort_keys=True, ensure_ascii=False)
            actual = json.dumps(rendered, indent=2, sort_keys=True, ensure_ascii=False)
            errors.append(f'{did}: rendered fixture does not match declared derivation for {output_rel}')
            if len(expected) < 1000 and len(actual) < 1000:
                errors.append(f'{did}: expected derived {expected}; actual {actual}')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    base = {'a': [{'b': 1}], 'c/d': True, 'tilde~key': 'x'}
    derived = apply_operations(base, [
        {'op': 'set', 'path': '/a/0/b', 'value': 2},
        {'op': 'set', 'path': '/c~1d', 'value': False},
        {'op': 'remove', 'path': '/tilde~0key'},
    ])
    if derived != {'a': [{'b': 2}], 'c/d': False}:
        errors.append(f'fixture_derivations self-test failed: {derived!r}')
    if base['a'][0]['b'] != 1:
        errors.append('fixture_derivations self-test failed: base object was mutated')
    return errors


if __name__ == '__main__':
    failures = self_test() + validate_derivations()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync fixture derivation checks passed.')
