#!/usr/bin/env python3
"""Guardrail for the hardware support qualification-freshness boundary."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from cube_digest_lib import canonical_digest

ROOT = Path(__file__).resolve().parents[1]

STAGES = [
    'lab-validated',
    'canary-observed',
    'release-qualified',
    'field-sustained',
]
REVERIFY_ON = [
    'kernel-or-kmod-change',
    'firmware-change',
    'boot-manifest-change',
    'role-regression',
    'qualification-profile-change',
    'recovery-lane-change',
]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))




def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def main() -> int:
    errors: list[str] = []

    profile_schema = load_json('spec/hw.support.qualification.profile.schema.json')
    receipt_schema = load_json('spec/hw.support.qualification.receipt.schema.json')
    compat_schema = load_json('spec/hw.compat.report.schema.json')

    if 'freshness' not in (profile_schema.get('required') or []):
        errors.append('spec/hw.support.qualification.profile.schema.json missing required freshness')
    freshness_schema = (profile_schema.get('properties') or {}).get('freshness') or {}
    if 'max_age_days_by_stage' not in (freshness_schema.get('required') or []):
        errors.append('spec/hw.support.qualification.profile.schema.json freshness must require max_age_days_by_stage')
    if 'reverify_on' not in (freshness_schema.get('required') or []):
        errors.append('spec/hw.support.qualification.profile.schema.json freshness must require reverify_on')
    stage_props = (((freshness_schema.get('properties') or {}).get('max_age_days_by_stage') or {}).get('properties') or {})
    for stage in STAGES:
        if stage not in stage_props:
            errors.append(f'spec/hw.support.qualification.profile.schema.json freshness.max_age_days_by_stage missing {stage}')
    reverify_items = ((((freshness_schema.get('properties') or {}).get('reverify_on') or {}).get('items') or {}).get('enum') or [])
    if reverify_items != REVERIFY_ON:
        errors.append(f'spec/hw.support.qualification.profile.schema.json freshness.reverify_on enum expected {REVERIFY_ON!r}, found {reverify_items!r}')

    if 'freshness' not in (receipt_schema.get('required') or []):
        errors.append('spec/hw.support.qualification.receipt.schema.json missing required freshness')
    receipt_freshness = (receipt_schema.get('properties') or {}).get('freshness') or {}
    for key in ('fresh_until', 'reverify_on'):
        if key not in (receipt_freshness.get('required') or []):
            errors.append(f'spec/hw.support.qualification.receipt.schema.json freshness must require {key}')
    receipt_reverify_items = ((((receipt_freshness.get('properties') or {}).get('reverify_on') or {}).get('items') or {}).get('enum') or [])
    if receipt_reverify_items != REVERIFY_ON:
        errors.append(f'spec/hw.support.qualification.receipt.schema.json freshness.reverify_on enum expected {REVERIFY_ON!r}, found {receipt_reverify_items!r}')

    finding_codes = (((compat_schema.get('properties') or {}).get('findings') or {}).get('items') or {}).get('properties', {}).get('code', {}).get('enum') or []
    if 'qualification-stale' not in finding_codes:
        errors.append('spec/hw.compat.report.schema.json findings.code must include qualification-stale')

    profile = load_json('spec/examples/hw.support.qualification.profile.json')
    receipt = load_json('spec/examples/hw.support.qualification.receipt.json')
    matrix = load_json('spec/examples/hw.support.matrix.json')
    report = load_json('spec/examples/hw.compat.report.json')

    profile_fresh = profile.get('freshness') or {}
    if sorted((profile_fresh.get('max_age_days_by_stage') or {}).keys()) != sorted(STAGES):
        errors.append('spec/examples/hw.support.qualification.profile.json freshness.max_age_days_by_stage must cover all qualification stages')
    if profile_fresh.get('reverify_on') != REVERIFY_ON:
        errors.append('spec/examples/hw.support.qualification.profile.json freshness.reverify_on must use the canonical trigger list')

    profile_digest = canonical_digest(profile)
    if (receipt.get('qualification') or {}).get('profile_digest') != profile_digest:
        errors.append('spec/examples/hw.support.qualification.receipt.json qualification.profile_digest must match computed digest of spec/examples/hw.support.qualification.profile.json')

    rq = receipt.get('qualification') or {}
    stage = rq.get('stage')
    last_verified_at = rq.get('last_verified_at')
    if stage not in STAGES:
        errors.append(f'spec/examples/hw.support.qualification.receipt.json qualification.stage must be one of {STAGES!r}')
    elif not last_verified_at:
        errors.append('spec/examples/hw.support.qualification.receipt.json qualification.last_verified_at must be present')
    else:
        expected_fresh_until = (
            parse_dt(last_verified_at) + timedelta(days=int((profile_fresh.get('max_age_days_by_stage') or {}).get(stage, 0)))
        ).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        rf = receipt.get('freshness') or {}
        if rf.get('fresh_until') != expected_fresh_until:
            errors.append('spec/examples/hw.support.qualification.receipt.json freshness.fresh_until must equal qualification.last_verified_at plus profile freshness.max_age_days_by_stage[stage]')
        if rf.get('reverify_on') != profile_fresh.get('reverify_on'):
            errors.append('spec/examples/hw.support.qualification.receipt.json freshness.reverify_on must match spec/examples/hw.support.qualification.profile.json freshness.reverify_on')

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
        if q.get('profile_digest') != profile_digest:
            errors.append('spec/examples/hw.support.matrix.json canonical workstation entry qualification.profile_digest must match computed digest of spec/examples/hw.support.qualification.profile.json')

    report_finding_codes = {item.get('code') for item in report.get('findings', [])}
    if 'qualification-stale' not in report_finding_codes:
        errors.append('spec/examples/hw.compat.report.json must include a qualification-stale finding in the canonical example')
    else:
        for item in report.get('findings', []):
            if item.get('code') == 'qualification-stale':
                if receipt_digest not in (item.get('refs') or []):
                    errors.append('spec/examples/hw.compat.report.json qualification-stale finding must reference the computed digest of spec/examples/hw.support.qualification.receipt.json')
    sm = report.get('support_matrix') or {}
    if receipt_digest not in (sm.get('matched_qualification_receipt_digests') or []):
        errors.append('spec/examples/hw.compat.report.json support_matrix.matched_qualification_receipt_digests must include the computed digest of spec/examples/hw.support.qualification.receipt.json')

    doc_checks = {
        'docs/320-hardware-compatibility-gates-and-safe-upgrades.md': ['`qualification-stale`', '`fresh_until`', '`reverify_on`'],
        'docs/410-desktop-viability-checklist.md': ['`qualification-stale`', '`fresh_until`'],
        'docs/479-hardware-compatibility-posture-by-profile.md': ['`qualification-stale`', '`hw.support.qualification.profile.freshness`'],
        'docs/529-hardware-support-promotion-and-qualification-boundary.md': ['`last_verified_at`', '`fresh_until`', '`qualification-stale`'],
        'docs/530-hardware-support-qualification-receipt-boundary.md': ['`fresh_until`', '`reverify_on`', '`qualification-stale`'],
        'docs/531-hardware-support-qualification-profile-boundary.md': ['`freshness`', '`max_age_days_by_stage`', '`reverify_on`'],
        'docs/532-hardware-support-qualification-freshness-boundary.md': ['`hw.support.qualification.profile`', '`fresh_until`', '`qualification-stale`'],
        'docs/266-open-questions-and-risk-register.md': ['ADR-0122', '`qualification-stale`'],
        'docs/99-llm-runbook.md': ['check_hw_support_qualification_freshness_contract.py', '`qualification-stale`'],
        'docs/98-archive-hygiene.md': ['check_hw_support_qualification_freshness_contract.py', '`fresh_until`'],
        'docs/110-juicy-os-lessons.md': ['`fresh_until`', '`qualification-stale`'],
        'adrs/ADR-0122-hardware-support-qualification-freshness-boundary.md': ['`fresh_until`', '`reverify_on`', '`qualification-stale`'],
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
    print('Hardware support qualification freshness contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
