"""Shared guardrail helpers for removable-media post-detach checkers.

This module is deliberately tiny and dependency-light.  The r504-r516 checker
series grew a lot of identical JSON loading, nested-field, schema-validation,
negative-fixture, and text-token assertions.  New guardrails can use this
module without changing the historical scripts, reducing copy/paste drift while
keeping each checker readable and directly runnable.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, Sequence

from jsonschema import Draft202012Validator


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def nested_value(obj, path: Sequence[object]):
    cur = obj
    for part in path:
        cur = cur[part]
    return cur


def validation_errors(validator: Draft202012Validator, obj: object) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def require_json_values(root: Path, requirements: dict[str, Iterable[tuple[Sequence[object], object]]]) -> None:
    for rel, checks in requirements.items():
        obj = load_json(root, rel)
        for path, expected in checks:
            actual = nested_value(obj, path)
            if actual != expected:
                dotted = '.'.join(map(str, path))
                fail(f"{rel}: {dotted} = {actual!r}, expected {expected!r}")


def require_tokens(root: Path, requirements: dict[str, Iterable[str]], label: str = 'token') -> None:
    for rel, tokens in requirements.items():
        text = (root / rel).read_text(encoding='utf-8')
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing {label} {token!r}")


def require_invalid_fixtures_fail(
    root: Path,
    schema_rel: str,
    invalid_dir: str,
    expected_names: Sequence[str],
) -> None:
    schema = load_json(root, schema_rel)
    validator = Draft202012Validator(schema)
    invalid_root = root / invalid_dir
    if not invalid_root.is_dir():
        fail(f"Missing invalid fixture directory {invalid_dir}")
    fixture_names = sorted(p.name for p in invalid_root.glob('*.json'))
    expected_sorted = sorted(expected_names)
    if fixture_names != expected_sorted:
        fail(f"Invalid fixture set mismatch: {fixture_names} != {expected_sorted}")
    for path in sorted(invalid_root.glob('*.json')):
        obj = json.loads(path.read_text(encoding='utf-8'))
        if not validation_errors(validator, obj):
            fail(f"Invalid fixture unexpectedly validates: {path.relative_to(root)}")



def require_absent_tokens(root: Path, requirements: dict[str, Iterable[str]], label: str = 'forbidden token') -> None:
    """Fail if any file contains a token that should stay out of redacted fixtures/docs.

    This is intentionally simple: newer post-detach guardrails use it as a
    cheap audit pass for accidental raw path, locator, user, host, or secret
    samples in canonical positive fixtures and support docs.
    """
    for rel, tokens in requirements.items():
        text = (root / rel).read_text(encoding='utf-8')
        for token in tokens:
            if token in text:
                fail(f"{rel} contains {label} {token!r}")


def require_hygiene_entry(root: Path, checker_name: str) -> None:
    hygiene = (root / 'tools' / 'hygiene.py').read_text(encoding='utf-8')
    if checker_name not in hygiene:
        fail(f"tools/hygiene.py must include {checker_name}")

def require_positive_fixture_valid(root: Path, schema_rel: str, example_rel: str) -> None:
    """Validate the canonical positive fixture against its schema."""
    schema = load_json(root, schema_rel)
    example = load_json(root, example_rel)
    validator = Draft202012Validator(schema)
    errs = validation_errors(validator, example)
    if errs:
        fail(f"Positive fixture {example_rel} failed {schema_rel}: {errs}")



def require_guardrail_contract(
    root: Path,
    *,
    schema_rel: str,
    example_rel: str,
    invalid_dir: str,
    expected_invalid_fixtures: Sequence[str],
    json_requirements: dict[str, Iterable[tuple[Sequence[object], object]]] | None = None,
    text_requirements: dict[str, Iterable[str]] | None = None,
    checker_name: str | None = None,
    label: str = 'guardrail token',
) -> None:
    """Run the standard post-detach guardrail package checks.

    Newer receipt guardrails all need the same package validation: the
    canonical positive fixture must validate, the red corpus must be exact and
    rejected, selected JSON joins must carry the posture/digest, docs must keep
    required tokens, and the checker must be wired into hygiene.  Keeping this
    sequence in one helper reduces copy/paste drift while preserving the
    explicit per-checker requirement tables.
    """
    require_positive_fixture_valid(root, schema_rel, example_rel)
    require_invalid_fixtures_fail(root, schema_rel, invalid_dir, expected_invalid_fixtures)
    if json_requirements:
        require_json_values(root, json_requirements)
    if text_requirements:
        require_tokens(root, text_requirements, label=label)
    if checker_name:
        require_hygiene_entry(root, checker_name)
