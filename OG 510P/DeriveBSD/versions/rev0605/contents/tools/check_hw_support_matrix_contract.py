#!/usr/bin/env python3
"""Guardrail for the hardware support matrix boundary.

Keeps the new hardware-support story narrow and reviewable:
- `hw.support.matrix` stays a catalog artifact keyed by class summaries
- `hw.compat.report` records explicit support-matrix join state when used
- workstation trusted-UI floor / recovery-path concerns stay typed instead of prose-only
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_LEVELS = ['supported', 'conditional', 'canary-only', 'blocked', 'maintenance-only']
EXPECTED_ROLES = ['boot-storage', 'primary-network', 'trusted-display', 'trusted-input']
EXPECTED_MATCH_STATES = ['not-used', 'matched', 'miss', 'conditional']
EXPECTED_FINDING_CODES = ['support-matrix-miss', 'trusted-ui-floor-risk', 'recovery-path-missing']


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []

    matrix = load_json('spec/hw.support.matrix.schema.json')
    matrix_ex = load_json('spec/examples/hw.support.matrix.json')
    compat = load_json('spec/hw.compat.report.schema.json')
    compat_ex = load_json('spec/examples/hw.compat.report.json')

    if matrix.get('properties', {}).get('kind', {}).get('const') != 'hw.support.matrix':
        errors.append('spec/hw.support.matrix.schema.json kind.const must be hw.support.matrix')

    entry_props = matrix.get('properties', {}).get('entries', {}).get('items', {}).get('properties', {})
    levels = entry_props.get('support_level', {}).get('enum')
    if levels != EXPECTED_LEVELS:
        errors.append(f'hw.support.matrix support_level enum expected {EXPECTED_LEVELS!r}, found {levels!r}')
    roles = entry_props.get('roles', {}).get('items', {}).get('enum', [])
    for role in EXPECTED_ROLES:
        if role not in roles:
            errors.append(f'hw.support.matrix roles enum missing {role!r}')
    match_props = entry_props.get('match', {}).get('properties', {})
    for key in ['pci', 'usb', 'acpi_hids', 'smbios_chids', 'board_products']:
        if key not in match_props:
            errors.append(f'hw.support.matrix match missing selector field {key!r}')

    if matrix_ex.get('kind') != 'hw.support.matrix':
        errors.append('spec/examples/hw.support.matrix.json kind must be hw.support.matrix')
    if matrix_ex.get('identifier_posture') != 'hardware-class-summary-only':
        errors.append('spec/examples/hw.support.matrix.json must stay class-summary-first')
    if len(matrix_ex.get('entries', [])) < 2:
        errors.append('spec/examples/hw.support.matrix.json should show at least B and D style entries')

    support_matrix = compat.get('properties', {}).get('support_matrix', {})
    if support_matrix:
        match_state_enum = support_matrix.get('properties', {}).get('match_state', {}).get('enum')
        if match_state_enum != EXPECTED_MATCH_STATES:
            errors.append(f'hw.compat.report support_matrix.match_state enum expected {EXPECTED_MATCH_STATES!r}, found {match_state_enum!r}')
    else:
        errors.append('spec/hw.compat.report.schema.json must include optional support_matrix join state')

    finding_codes = compat.get('properties', {}).get('findings', {}).get('items', {}).get('properties', {}).get('code', {}).get('enum', [])
    for code in EXPECTED_FINDING_CODES:
        if code not in finding_codes:
            errors.append(f'hw.compat.report finding code enum missing {code!r}')

    support_matrix_ex = compat_ex.get('support_matrix', {})
    if support_matrix_ex.get('match_state') not in EXPECTED_MATCH_STATES:
        errors.append('spec/examples/hw.compat.report.json must use a canonical support_matrix.match_state')
    if support_matrix_ex.get('match_state') == 'matched' and not support_matrix_ex.get('matched_entry_ids'):
        errors.append('spec/examples/hw.compat.report.json matched matrix state must include matched_entry_ids')

    doc_checks = {
        'docs/320-hardware-compatibility-gates-and-safe-upgrades.md': ['`hw.support.matrix`', '`trusted-ui-floor-risk`', '`support_matrix`'],
        'docs/410-desktop-viability-checklist.md': ['`hw.support.matrix`', '`trusted-ui-floor-risk`', '`recovery-path-missing`'],
        'docs/479-hardware-compatibility-posture-by-profile.md': ['`hw.support.matrix`', '`trusted-ui-floor-risk`', '`support-matrix-miss`'],
        'docs/528-hardware-support-matrix-and-bundled-admission-boundary.md': ['`hw.support.matrix`', '`hw.compat.report`', '`trusted-display`'],
        'docs/266-open-questions-and-risk-register.md': ['ADR-0118', '`hw.support.matrix`'],
        'adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md': ['`hw.support.matrix`', '`hw.compat.report`', 'trusted UI floor'],
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
    print('Hardware support matrix contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
