#!/usr/bin/env python3
"""Guardrail for the hardware support qualification-status boundary."""
from __future__ import annotations

import json
from pathlib import Path
from cube_digest_lib import canonical_digest

ROOT = Path(__file__).resolve().parents[1]

REASON_CODES = [
    'newer-receipt-published',
    'field-regression',
    'security-issue',
    'qualification-scope-corrected',
    'evidence-invalidated',
    'recovery-gap-found',
    'support-withdrawn',
]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))




def main() -> int:
    errors: list[str] = []

    receipt_schema = load_json('spec/hw.support.qualification.receipt.schema.json')
    report_schema = load_json('spec/hw.compat.report.schema.json')
    matrix = load_json('spec/examples/hw.support.matrix.json')
    receipt = load_json('spec/examples/hw.support.qualification.receipt.json')

    decision = (receipt_schema.get('properties') or {}).get('decision') or {}
    if 'status_effective_at' not in (decision.get('required') or []):
        errors.append('spec/hw.support.qualification.receipt.schema.json decision must require status_effective_at')
    props = decision.get('properties') or {}
    for key in ('reason_code', 'replacement_receipt_digest', 'status_effective_at'):
        if key not in props:
            errors.append(f'spec/hw.support.qualification.receipt.schema.json decision must define {key}')
    reason_enum = (props.get('reason_code') or {}).get('enum') or []
    if reason_enum != REASON_CODES:
        errors.append(f'spec/hw.support.qualification.receipt.schema.json decision.reason_code enum expected {REASON_CODES!r}, found {reason_enum!r}')
    if not decision.get('allOf'):
        errors.append('spec/hw.support.qualification.receipt.schema.json decision must define conditional requirements for superseded/revoked status')

    finding_codes = (((report_schema.get('properties') or {}).get('findings') or {}).get('items') or {}).get('properties', {}).get('code', {}).get('enum') or []
    for code in ('qualification-superseded', 'qualification-revoked'):
        if code not in finding_codes:
            errors.append(f'spec/hw.compat.report.schema.json findings.code must include {code}')

    decision_ex = receipt.get('decision') or {}
    if decision_ex.get('status') != 'accepted':
        errors.append('spec/examples/hw.support.qualification.receipt.json canonical example must remain accepted')
    if 'status_effective_at' not in decision_ex:
        errors.append('spec/examples/hw.support.qualification.receipt.json decision must include status_effective_at')
    if 'reason_code' in decision_ex:
        errors.append('spec/examples/hw.support.qualification.receipt.json accepted canonical example must not include reason_code')
    if 'replacement_receipt_digest' in decision_ex:
        errors.append('spec/examples/hw.support.qualification.receipt.json accepted canonical example must not include replacement_receipt_digest')

    receipt_digest = canonical_digest(receipt)
    workstation_entry = None
    for entry in matrix.get('entries', []):
        if entry.get('entry_id') == 'b-laptop-intel-trusted-ui-floor-v1':
            workstation_entry = entry
            break
    if not workstation_entry:
        errors.append('spec/examples/hw.support.matrix.json missing canonical workstation trusted-UI entry')
    else:
        q = workstation_entry.get('qualification') or {}
        if q.get('receipt_digest') != receipt_digest:
            errors.append('spec/examples/hw.support.matrix.json canonical workstation entry qualification.receipt_digest must match computed digest of spec/examples/hw.support.qualification.receipt.json')

    doc_checks = {
        'docs/320-hardware-compatibility-gates-and-safe-upgrades.md': ['`qualification-superseded`', '`qualification-revoked`', '`decision.status`'],
        'docs/410-desktop-viability-checklist.md': ['`qualification-superseded`', '`qualification-revoked`', '`status_effective_at`'],
        'docs/479-hardware-compatibility-posture-by-profile.md': ['`qualification-superseded`', '`qualification-revoked`', '`accepted` receipt'],
        'docs/529-hardware-support-promotion-and-qualification-boundary.md': ['`decision.status`', '`accepted` receipt'],
        'docs/530-hardware-support-qualification-receipt-boundary.md': ['`status_effective_at`', '`reason_code`', '`replacement_receipt_digest`'],
        'docs/531-hardware-support-qualification-profile-boundary.md': ['ADR-0123', '`qualification-superseded`'],
        'docs/532-hardware-support-qualification-freshness-boundary.md': ['`qualification-stale`', '`qualification-revoked`', '`qualification-superseded`'],
        'docs/533-hardware-support-qualification-status-boundary.md': ['`qualification-superseded`', '`qualification-revoked`', '`replacement_receipt_digest`'],
        'docs/266-open-questions-and-risk-register.md': ['ADR-0123', '`qualification-revoked`'],
        'docs/99-llm-runbook.md': ['check_hw_support_qualification_status_contract.py', '`qualification-revoked`'],
        'docs/98-archive-hygiene.md': ['check_hw_support_qualification_status_contract.py', '`status_effective_at`'],
        'docs/110-juicy-os-lessons.md': ['`qualification-superseded`', '`qualification-revoked`'],
        'adrs/ADR-0123-hardware-support-qualification-status-boundary.md': ['`replacement_receipt_digest`', '`qualification-revoked`', '`qualification-superseded`'],
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
    print('Hardware support qualification status contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
