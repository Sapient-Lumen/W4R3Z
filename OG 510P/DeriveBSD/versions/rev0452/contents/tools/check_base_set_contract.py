#!/usr/bin/env python3
"""Guardrail for the canonical native base-set boundary.

Keeps the accepted boundary narrow and reviewable:
- `base.set` exists as a native schema/example
- the canonical set-class split stays intentionally small in v0
- pkgbase remains an adapter/import-export lane rather than the native source of truth
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SET_CLASSES = ['kernel', 'userland', 'toolchain']
EXPECTED_SOURCE_KINDS = ['derive.plan', 'adapter.pkgbase-import']


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []

    schema = load_json('spec/base.set.schema.json')
    example = load_json('spec/examples/base.set.json')
    patchset_schema = load_json('spec/patchset.manifest.schema.json')

    if schema.get('properties', {}).get('kind', {}).get('const') != 'base.set':
        errors.append('spec/base.set.schema.json kind.const must be base.set')

    set_classes = schema.get('properties', {}).get('set_class', {}).get('enum')
    if set_classes != EXPECTED_SET_CLASSES:
        errors.append(f'spec/base.set.schema.json set_class enum expected {EXPECTED_SET_CLASSES!r}, found {set_classes!r}')

    source_kinds = schema.get('properties', {}).get('source_authority', {}).get('properties', {}).get('kind', {}).get('enum')
    if source_kinds != EXPECTED_SOURCE_KINDS:
        errors.append(f'spec/base.set.schema.json source_authority.kind enum expected {EXPECTED_SOURCE_KINDS!r}, found {source_kinds!r}')

    if example.get('kind') != 'base.set':
        errors.append('spec/examples/base.set.json kind must be base.set')
    if example.get('set_class') not in EXPECTED_SET_CLASSES:
        errors.append('spec/examples/base.set.json set_class must use the canonical v0 split')
    if example.get('source_authority', {}).get('kind') != 'derive.plan':
        errors.append('spec/examples/base.set.json canonical example must stay native (`derive.plan`) rather than adapter-first')
    if not example.get('contents', {}).get('root_tree_digest'):
        errors.append('spec/examples/base.set.json contents.root_tree_digest is required in the canonical example')

    target_kinds = patchset_schema.get('properties', {}).get('target', {}).get('properties', {}).get('kind', {}).get('enum')
    if target_kinds != ['base.set', 'host.generation']:
        errors.append('spec/patchset.manifest.schema.json target.kind enum drifted; patchsets must still target base.set or host.generation')

    doc_checks = {
        'docs/111-packaged-base-pkgbase.md': ['`base.set`', 'adapter lane', 'source of truth'],
        'docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md': ['`base.set`', '`pkgbase`', 'derive.plan'],
        'docs/266-open-questions-and-risk-register.md': ['## 3) Kernel/userland split: pkgbase vs “derive base” [DECIDED]', 'ADR-0116'],
        'adrs/ADR-0116-derived-base-sets-and-pkgbase-adapter-boundary.md': ['`base.set`', '`pkgbase`', '`kernel`'],
        'rfcs/RFC-0079-packaged-base-and-sets.md': ['ADR-0116', '`base.set`'],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f'{rel} missing required token: {needle}')

    if errors:
        for err in errors:
            print(f'ERROR: {err}')
        return 1
    print('Base set contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
