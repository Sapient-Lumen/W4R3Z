#!/usr/bin/env python3
"""Guardrail for hardware support promotion / qualification semantics.

Keeps `hw.support.matrix` support labels honest by requiring a tiny typed
qualification summary instead of release-note folklore.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

POSITIVE_LEVELS = ['supported', 'conditional', 'canary-only', 'maintenance-only']
STAGES = ['lab-validated', 'canary-observed', 'release-qualified', 'field-sustained']
EVIDENCE_FLOOR = [
    'boot',
    'generation-switch',
    'rollback-or-recovery',
    'trusted-ui-basic',
    'network-basic',
    'device-mediation-basic',
    'suspend-resume',
]
ALLOWED_STAGE_BY_LEVEL = {
    'supported': {'release-qualified', 'field-sustained'},
    'conditional': {'lab-validated', 'canary-observed', 'release-qualified', 'field-sustained'},
    'canary-only': {'canary-observed'},
    'maintenance-only': {'release-qualified', 'field-sustained'},
}


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []

    schema = load_json('spec/hw.support.matrix.schema.json')
    example = load_json('spec/examples/hw.support.matrix.json')

    entry_props = schema.get('properties', {}).get('entries', {}).get('items', {}).get('properties', {})
    qualification = entry_props.get('qualification', {})
    if not qualification:
        errors.append('spec/hw.support.matrix.schema.json must define entries[].qualification')
    else:
        stage_enum = qualification.get('properties', {}).get('stage', {}).get('enum')
        if stage_enum != STAGES:
            errors.append(f'hw.support.matrix qualification.stage enum expected {STAGES!r}, found {stage_enum!r}')
        evidence_enum = qualification.get('properties', {}).get('evidence_floor', {}).get('items', {}).get('enum')
        if evidence_enum != EVIDENCE_FLOOR:
            errors.append(f'hw.support.matrix qualification.evidence_floor enum expected {EVIDENCE_FLOOR!r}, found {evidence_enum!r}')

    all_of = schema.get('properties', {}).get('entries', {}).get('items', {}).get('allOf', [])
    if len(all_of) < 2:
        errors.append('spec/hw.support.matrix.schema.json should gate qualification presence with allOf if/then rules')

    for idx, entry in enumerate(example.get('entries', []), start=1):
        level = entry.get('support_level')
        qualification = entry.get('qualification')
        if level in POSITIVE_LEVELS and not qualification:
            errors.append(f'example entry {idx} ({entry.get("entry_id")}) positive support level must include qualification')
            continue
        if level == 'blocked' and qualification:
            errors.append(f'example entry {idx} ({entry.get("entry_id")}) blocked entry must not include qualification')
            continue
        if not qualification:
            continue

        stage = qualification.get('stage')
        if level in ALLOWED_STAGE_BY_LEVEL and stage not in ALLOWED_STAGE_BY_LEVEL[level]:
            errors.append(
                f'example entry {idx} ({entry.get("entry_id")}) level {level!r} requires stage in '
                f'{sorted(ALLOWED_STAGE_BY_LEVEL[level])!r}, found {stage!r}'
            )

        roles = set(entry.get('roles', []))
        verified_roles = set(qualification.get('verified_roles', []))
        evidence_floor = set(qualification.get('evidence_floor', []))
        profiles = set(entry.get('profiles', example.get('profiles', [])))

        if not roles.issubset(verified_roles):
            missing = sorted(roles - verified_roles)
            errors.append(f'example entry {idx} ({entry.get("entry_id")}) qualification.verified_roles missing roles {missing!r}')

        if 'boot-storage' in roles and 'boot' not in evidence_floor:
            errors.append(f'example entry {idx} ({entry.get("entry_id")}) boot-storage role requires evidence_floor boot')
        if {'primary-network', 'maintenance-network'} & roles and 'network-basic' not in evidence_floor:
            errors.append(f'example entry {idx} ({entry.get("entry_id")}) network role requires evidence_floor network-basic')
        if {'trusted-display', 'trusted-input'} & roles and 'trusted-ui-basic' not in evidence_floor:
            errors.append(f'example entry {idx} ({entry.get("entry_id")}) trusted UI role requires evidence_floor trusted-ui-basic')
        if {'B', 'D'} & profiles and {'trusted-display', 'trusted-input', 'boot-storage'} & roles and 'rollback-or-recovery' not in evidence_floor:
            errors.append(f'example entry {idx} ({entry.get("entry_id")}) B/D boot or trusted UI floor requires evidence_floor rollback-or-recovery')
        if 'generation-switch' not in evidence_floor and level in {'supported', 'conditional', 'canary-only', 'maintenance-only'}:
            errors.append(f'example entry {idx} ({entry.get("entry_id")}) positive support level should include generation-switch evidence')

    doc_checks = {
        'docs/320-hardware-compatibility-gates-and-safe-upgrades.md': ['`qualification`', '`generation-switch`', '`rollback-or-recovery`'],
        'docs/410-desktop-viability-checklist.md': ['`qualification`', '`trusted-ui-basic`', '`rollback-or-recovery`'],
        'docs/479-hardware-compatibility-posture-by-profile.md': ['`qualification.stage`', '`canary-only`', '`release-qualified`'],
        'docs/528-hardware-support-matrix-and-bundled-admission-boundary.md': ['promotion semantics', '`docs/529-hardware-support-promotion-and-qualification-boundary.md`'],
        'docs/529-hardware-support-promotion-and-qualification-boundary.md': ['`qualification`', '`field-sustained`', '`rollback-or-recovery`'],
        'docs/266-open-questions-and-risk-register.md': ['ADR-0119', '`qualification`'],
        'docs/99-llm-runbook.md': ['check_hw_support_promotion_contract.py', '`qualification`'],
        'adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md': ['`qualification`', '`canary-only`', '`release-qualified`'],
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
    print('Hardware support promotion contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
