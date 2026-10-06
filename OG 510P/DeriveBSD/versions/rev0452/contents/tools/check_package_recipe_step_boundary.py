#!/usr/bin/env python3
"""Guardrail for the native restricted-pipeline step boundary.

This checker keeps the post-ADR-0289 package-recipe lane from quietly reopening
shell-shaped native authority through a generic reviewed step.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    'adrs/ADR-0290-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md': [
        'must not expose a generic authoritative `run`, `script`, or arbitrary-command step',
        'registry-backed and typed',
        'step_kind',
    ],
    'docs/700-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md': [
        'does **not** get a generic authoritative `run` / `script` / opaque-command step',
        'registry-backed and typed',
        '`step_kind`',
        'tool capsules',
    ],
    'rfcs/RFC-0091-declarative-image-pipelines.md': [
        'registry-backed `step_kind`',
        'no generic authoritative `run` / `script` / opaque command-array step',
    ],
    'docs/134-declarative-image-pipelines-apko-melange.md': [
        'native reviewed steps stay registry-backed',
        'generic `run` / `script` escape hatch',
    ],
    'docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md': [
        'docs/700-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md',
        'generic authoritative `run` / `script` step',
    ],
    'docs/98-archive-hygiene.md': [
        'check_package_recipe_step_boundary.py',
        'generic authoritative `run` / `script` / opaque-command escape hatch',
    ],
    'docs/99-llm-runbook.md': [
        'check_package_recipe_step_boundary.py',
        'Native restricted pipelines must also stay registry-backed',
    ],
    'docs/00-index.md': [
        'docs/700-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md',
        'check_package_recipe_step_boundary.py',
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print('package recipe native-step boundary check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('package recipe native-step boundary check passed')
