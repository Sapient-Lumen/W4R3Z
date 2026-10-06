#!/usr/bin/env python3
"""Guardrail for hardware support conditions / known limitations boundary."""
from __future__ import annotations

import json
from pathlib import Path
from cube_digest_lib import canonical_digest

ROOT = Path(__file__).resolve().parents[1]

REASON_CODES = [
    'topology-variant-unverified',
    'peripheral-cohort-unverified',
    'firmware-cohort-unverified',
    'recovery-prerequisite',
    'operating-mode-unverified',
    'performance-floor-not-qualified',
]
POSTURES = [
    'trusted-ui-consent',
    'verified-recovery-required',
    'breakglass',
    'maintenance-window-only',
    'deny-until-qualified',
]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))




def main() -> int:
    errors: list[str] = []

    matrix_schema = load_json('spec/hw.support.matrix.schema.json')
    receipt_schema = load_json('spec/hw.support.qualification.receipt.schema.json')
    report_schema = load_json('spec/hw.compat.report.schema.json')
    matrix_ex = load_json('spec/examples/hw.support.matrix.json')
    receipt_ex = load_json('spec/examples/hw.support.qualification.receipt.json')
    report_ex = load_json('spec/examples/hw.compat.report.json')

    entry_props = (((matrix_schema.get('properties') or {}).get('entries') or {}).get('items') or {}).get('properties') or {}
    conditions = entry_props.get('conditions') or {}
    if not conditions:
        errors.append('spec/hw.support.matrix.schema.json must define entries[].conditions')
    else:
        reason_enum = (((conditions.get('items') or {}).get('properties') or {}).get('reason_code') or {}).get('enum') or []
        if reason_enum != REASON_CODES:
            errors.append(f'spec/hw.support.matrix.schema.json conditions.reason_code enum expected {REASON_CODES!r}, found {reason_enum!r}')
        posture_enum = (((conditions.get('items') or {}).get('properties') or {}).get('required_posture') or {}).get('enum') or []
        if posture_enum != POSTURES:
            errors.append(f'spec/hw.support.matrix.schema.json conditions.required_posture enum expected {POSTURES!r}, found {posture_enum!r}')
    all_of = (((matrix_schema.get('properties') or {}).get('entries') or {}).get('items') or {}).get('allOf') or []
    if not any('conditions' in json.dumps(x) for x in all_of):
        errors.append('spec/hw.support.matrix.schema.json must gate conditions presence with allOf if/then rules')

    support_claim = (receipt_schema.get('properties') or {}).get('support_claim') or {}
    if 'condition_ids' not in (support_claim.get('properties') or {}):
        errors.append('spec/hw.support.qualification.receipt.schema.json support_claim must define condition_ids')
    sc_allof = support_claim.get('allOf') or []
    if not any('condition_ids' in json.dumps(x) for x in sc_allof):
        errors.append('spec/hw.support.qualification.receipt.schema.json support_claim must gate condition_ids for non-fully-supported claims')

    report_props = report_schema.get('properties') or {}
    finding_codes = ((((report_props.get('findings') or {}).get('items') or {}).get('properties') or {}).get('code') or {}).get('enum') or []
    if 'support-condition-triggered' not in finding_codes:
        errors.append('spec/hw.compat.report.schema.json findings.code must include support-condition-triggered')
    sm_props = ((report_props.get('support_matrix') or {}).get('properties') or {})
    if 'matched_condition_ids' not in sm_props:
        errors.append('spec/hw.compat.report.schema.json support_matrix must define matched_condition_ids')

    workstation_entry = None
    for entry in matrix_ex.get('entries', []):
        if entry.get('entry_id') == 'b-laptop-intel-trusted-ui-floor-v1':
            workstation_entry = entry
            break
    if not workstation_entry:
        errors.append('spec/examples/hw.support.matrix.json missing canonical workstation trusted-UI entry')
    else:
        conditions_ex = workstation_entry.get('conditions') or []
        if not conditions_ex:
            errors.append('spec/examples/hw.support.matrix.json canonical workstation trusted-UI entry must include conditions')
        for cond in conditions_ex:
            for key in ('condition_id','reason_code','summary','required_posture'):
                if key not in cond:
                    errors.append(f'spec/examples/hw.support.matrix.json condition missing {key}')
        if workstation_entry.get('support_level') == 'conditional' and not any(c.get('reason_code') == 'topology-variant-unverified' for c in conditions_ex):
            errors.append('spec/examples/hw.support.matrix.json canonical workstation conditional entry should demonstrate topology-variant-unverified')

    cond_ids = set(receipt_ex.get('support_claim', {}).get('condition_ids') or [])
    if not cond_ids:
        errors.append('spec/examples/hw.support.qualification.receipt.json canonical conditional example must include support_claim.condition_ids')
    elif workstation_entry:
        matrix_ids = {c.get('condition_id') for c in (workstation_entry.get('conditions') or [])}
        if cond_ids != matrix_ids:
            errors.append('spec/examples/hw.support.qualification.receipt.json support_claim.condition_ids must match canonical workstation matrix entry condition ids exactly')

    receipt_digest = canonical_digest(receipt_ex)
    if receipt_digest not in (report_ex.get('support_matrix', {}).get('matched_qualification_receipt_digests') or []):
        errors.append('spec/examples/hw.compat.report.json support_matrix.matched_qualification_receipt_digests must include computed receipt digest of spec/examples/hw.support.qualification.receipt.json')
    matched_condition_ids = set(report_ex.get('support_matrix', {}).get('matched_condition_ids') or [])
    if matched_condition_ids != cond_ids:
        errors.append('spec/examples/hw.compat.report.json support_matrix.matched_condition_ids must match canonical receipt/matrix condition ids')
    if not any(f.get('code') == 'support-condition-triggered' for f in report_ex.get('findings', [])):
        errors.append('spec/examples/hw.compat.report.json findings must include support-condition-triggered')

    doc_checks = {
        'docs/320-hardware-compatibility-gates-and-safe-upgrades.md': ['`support-condition-triggered`', '`matched_condition_ids`', '`conditions[]`'],
        'docs/410-desktop-viability-checklist.md': ['`support-condition-triggered`', '`conditions[]`', '`trusted-ui-consent`'],
        'docs/479-hardware-compatibility-posture-by-profile.md': ['`support-condition-triggered`', '`matched_condition_ids`', '`conditions[]`'],
        'docs/529-hardware-support-promotion-and-qualification-boundary.md': ['`conditions[]`', '`conditional`', '`required_posture`'],
        'docs/530-hardware-support-qualification-receipt-boundary.md': ['`support_claim.condition_ids`', '`conditions[]`', '`matched_condition_ids`'],
        'docs/534-hardware-support-conditions-and-known-limitations-boundary.md': ['`conditions[]`', '`support-condition-triggered`', '`matched_condition_ids`'],
        'docs/266-open-questions-and-risk-register.md': ['ADR-0124', '`conditions[]`'],
        'docs/99-llm-runbook.md': ['check_hw_support_conditions_contract.py', '`conditions[]`'],
        'docs/98-archive-hygiene.md': ['check_hw_support_conditions_contract.py', '`support-condition-triggered`'],
        'docs/110-juicy-os-lessons.md': ['`support-condition-triggered`', '`required_posture`', 'ADR-0124'],
        'adrs/ADR-0124-hardware-support-conditions-and-known-limitations-boundary.md': ['`conditions[]`', '`support_claim.condition_ids`', '`support-condition-triggered`'],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f'{rel} missing required token: {needle}')

    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        return 1
    print('Hardware support conditions contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
