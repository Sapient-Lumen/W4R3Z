#!/usr/bin/env python3
"""Guardrail for the package-recipe authority boundary.

This checker keeps DeriveBSD from quietly reopening the most expensive build-language
question after the archive has already narrowed it:
- no blessed in-tree general-purpose recipe evaluator
- the only native follow-on lane is RFC-0091-style restricted typed pipelines
- richer recipe ecosystems remain adapter/compiler lanes
- the risk register item is marked [DECIDED] and pinned to ADR-0289
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    'adrs/ADR-0289-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md': [
        'No general-purpose evaluator',
        'restricted typed pipeline',
        'adapter/compiler lanes',
        'Shell remains backend implementation detail',
        'RFC-0091',
    ],
    'docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md': [
        'evaluator-free',
        'restricted typed pipeline',
        'adapter/compiler lanes',
        'Shell stays backend detail, not recipe authority',
        'docs/83-evaluator-minimalism.md',
        'docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md',
        'rfcs/RFC-0091-declarative-image-pipelines.md',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        '## 1) Package recipe surface: how much language is allowed? [DECIDED]',
        'ADR-0289',
        'docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md',
        'restricted typed pipeline lane',
    ],
    'rfcs/RFC-0091-declarative-image-pipelines.md': [
        'Decision note:',
        'ADR-0289',
        'docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md',
        'restricted recipe',
    ],
    'docs/134-declarative-image-pipelines-apko-melange.md': [
        'Decision note:',
        'docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md',
        'restricted recipe lane',
        'no in-tree general-purpose recipe evaluator',
    ],
    'docs/98-archive-hygiene.md': [
        'check_package_recipe_surface_contract.py',
        'package-recipe authority boundary',
    ],
    'docs/99-llm-runbook.md': [
        'check_package_recipe_surface_contract.py',
        'Package recipe surface must stay evaluator-free',
        'restricted typed pipeline',
    ],
    'docs/00-index.md': [
        'docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md',
        'check_package_recipe_surface_contract.py',
    ],
    'docs/110-juicy-os-lessons.md': [
        'docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md',
        'restricted recipe lane',
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print('package recipe surface contract check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('package recipe surface contract check passed')
