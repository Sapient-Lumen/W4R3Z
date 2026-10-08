#!/usr/bin/env python3
"""Lint current-facing TimeSync documents against receipt-derived revision identity.

Historical archive files intentionally retain older revision identifiers.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

CURRENT_HEADING_FILES = [
    'README.md',
    'START_HERE.md',
    'INDEX.md',
    'VALIDATION-REPORT.md',
    'tests/acceptance-tests.md',
    'tests/TRACEABILITY-MATRIX.md',
    'transport/ADAPTER-CATALOG.md',
    'profiles/README.md',
    'profiles/PROFILE-CATALOG.md',
    'schema/README.md',
    'evaluator/README.md',
    'evaluator/EVIDENCE-CLASS-CATALOG.md',
]


def expected_revision() -> str:
    receipt = json.loads((ROOT / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
    revision = receipt.get('revision') if isinstance(receipt, dict) else None
    if not isinstance(revision, str):
        raise ValueError('REVISION-RECEIPT.json does not contain a string revision')
    return revision


def first_nonempty_line(path: Path) -> str:
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            return line.strip()
    return ''


def main() -> int:
    errors: list[str] = []
    try:
        expected = expected_revision()
    except Exception as exc:  # noqa: BLE001
        print(f'Revision reference lint failed: {exc}')
        return 1
    for rel in CURRENT_HEADING_FILES:
        path = ROOT / rel
        if not path.exists():
            errors.append(f'missing current-facing document: {rel}')
            continue
        head = first_nonempty_line(path)
        if expected not in head:
            errors.append(f'{rel}: first heading must mention {expected}; got {head!r}')

    for path in sorted((ROOT / 'profiles').glob('P*.md')):
        head = first_nonempty_line(path)
        if expected not in head:
            errors.append(f'{path.relative_to(ROOT)}: first heading must mention {expected}; got {head!r}')

    # Ensure the retained rev0090 temporal-coherence spec remains present.
    for n in range(62, 63):
        matches = list((ROOT / 'spec').glob(f'{n}-*.md'))
        if not matches:
            errors.append(f'missing rev0090 spec {n}')

    if errors:
        print('Revision reference lint failed:')
        for error in errors:
            print(f'- {error}')
        return 1
    print(f'Revision reference lint passed for {expected}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
