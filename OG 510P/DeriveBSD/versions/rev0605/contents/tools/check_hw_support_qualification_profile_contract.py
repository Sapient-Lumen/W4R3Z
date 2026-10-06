#!/usr/bin/env python3
"""Guardrail for the hardware support qualification-profile boundary."""
from __future__ import annotations

import json
from pathlib import Path
from cube_digest_lib import canonical_digest

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))




def main() -> int:
    errors: list[str] = []

    matrix_schema = load_json('spec/hw.support.matrix.schema.json')
    receipt_schema = load_json('spec/hw.support.qualification.receipt.schema.json')
    profile_schema = load_json('spec/hw.support.qualification.profile.schema.json')

    qual = ((((matrix_schema.get('properties') or {}).get('entries') or {}).get('items') or {}).get('properties') or {}).get('qualification') or {}
    if 'profile_digest' not in (qual.get('required') or []):
        errors.append('spec/hw.support.matrix.schema.json qualification must require profile_digest')
    if 'profile_digest' not in (qual.get('properties') or {}):
        errors.append('spec/hw.support.matrix.schema.json qualification must define profile_digest')

    for key in ('kind', 'profile_version', 'profile_id', 'created_at', 'target', 'scope', 'required_checks', 'acceptance'):
        if key not in (profile_schema.get('required') or []):
            errors.append(f'spec/hw.support.qualification.profile.schema.json missing required {key}')

    receipt_required = receipt_schema.get('required') or []
    for key in ('qualification', 'supporting_evidence', 'check_results'):
        if key not in receipt_required:
            errors.append(f'spec/hw.support.qualification.receipt.schema.json missing required {key}')
    receipt_qual = ((receipt_schema.get('properties') or {}).get('qualification') or {})
    if 'profile_digest' not in (receipt_qual.get('required') or []):
        errors.append('spec/hw.support.qualification.receipt.schema.json qualification must require profile_digest')
    if 'profile_digest' not in (receipt_qual.get('properties') or {}):
        errors.append('spec/hw.support.qualification.receipt.schema.json qualification must define profile_digest')
    purposes = ((((receipt_schema.get('properties') or {}).get('supporting_evidence') or {}).get('items') or {}).get('properties') or {}).get('purpose', {}).get('enum') or []
    for purpose in ('boot', 'suspend-resume'):
        if purpose not in purposes:
            errors.append(f'spec/hw.support.qualification.receipt.schema.json supporting_evidence purpose enum missing {purpose}')

    profile = load_json('spec/examples/hw.support.qualification.profile.json')
    receipt = load_json('spec/examples/hw.support.qualification.receipt.json')
    matrix = load_json('spec/examples/hw.support.matrix.json')

    profile_digest = canonical_digest(profile)

    b = None
    for entry in matrix.get('entries', []):
        if entry.get('entry_id') == 'b-laptop-intel-trusted-ui-floor-v1':
            b = entry
            break
    if not b:
        errors.append('spec/examples/hw.support.matrix.json missing canonical workstation trusted-UI entry')
    else:
        q = b.get('qualification') or {}
        if q.get('profile_digest') != profile_digest:
            errors.append('spec/examples/hw.support.matrix.json canonical workstation entry qualification.profile_digest != computed digest of spec/examples/hw.support.qualification.profile.json')

    rq = receipt.get('qualification') or {}
    if rq.get('profile_digest') != profile_digest:
        errors.append('spec/examples/hw.support.qualification.receipt.json qualification.profile_digest != computed digest of spec/examples/hw.support.qualification.profile.json')
    if b:
        q = b.get('qualification') or {}
        if rq.get('profile_digest') != q.get('profile_digest'):
            errors.append('spec/examples/hw.support.qualification.receipt.json qualification.profile_digest must match canonical workstation matrix entry')

    check_results = receipt.get('check_results') or []
    if not check_results:
        errors.append('spec/examples/hw.support.qualification.receipt.json must contain check_results')

    scope = profile.get('scope') or {}
    receipt_claim = receipt.get('support_claim') or {}
    applicable_checks = []
    for check in profile.get('required_checks', []):
        profiles = set(receipt_claim.get('profiles') or [])
        roles = set(receipt_claim.get('roles') or [])
        support_level = receipt_claim.get('support_level')
        required_profiles = set(check.get('required_profiles') or [])
        required_roles = set(check.get('required_roles') or [])
        required_support_levels = set(check.get('required_support_levels') or [])
        if required_profiles and not (profiles & required_profiles):
            continue
        if required_roles and not (roles & required_roles):
            continue
        if required_support_levels and support_level not in required_support_levels:
            continue
        applicable_checks.append(check)

    expected_check_ids = {check['check_id'] for check in applicable_checks if check.get('blocking')}
    actual_check_ids = {item.get('check_id') for item in check_results}
    if actual_check_ids != expected_check_ids:
        errors.append('spec/examples/hw.support.qualification.receipt.json check_results must exactly cover the applicable blocking check_ids from spec/examples/hw.support.qualification.profile.json for the canonical workstation example')

    evidence_by_digest = {}
    for item in receipt.get('supporting_evidence', []):
        evidence_by_digest[item.get('digest')] = item

    checks_by_id = {check['check_id']: check for check in profile.get('required_checks', [])}
    for result in check_results:
        check_id = result.get('check_id')
        status = result.get('status')
        if status not in ('pass', 'allowed-deviation'):
            errors.append(f'spec/examples/hw.support.qualification.receipt.json check_results entry {check_id} has invalid status: {status}')
            continue
        check = checks_by_id.get(check_id)
        if not check:
            errors.append(f'spec/examples/hw.support.qualification.receipt.json check_results entry {check_id} not found in spec/examples/hw.support.qualification.profile.json')
            continue
        accepted_kinds = set(check.get('accepted_evidence_kinds') or [])
        expected_purpose = check.get('purpose')
        digests = result.get('evidence_digests') or []
        if not digests:
            errors.append(f'spec/examples/hw.support.qualification.receipt.json check_results entry {check_id} must list evidence_digests')
        for digest in digests:
            ev = evidence_by_digest.get(digest)
            if not ev:
                errors.append(f'spec/examples/hw.support.qualification.receipt.json check_results entry {check_id} references unknown evidence digest: {digest}')
                continue
            if ev.get('kind') not in accepted_kinds:
                errors.append(f'spec/examples/hw.support.qualification.receipt.json evidence {digest} for {check_id} has kind {ev.get("kind")} outside accepted_evidence_kinds')
            if ev.get('purpose') != expected_purpose:
                errors.append(f'spec/examples/hw.support.qualification.receipt.json evidence {digest} for {check_id} must use purpose {expected_purpose}')

    doc_checks = {
        'docs/320-hardware-compatibility-gates-and-safe-upgrades.md': ['`qualification.profile_digest`', '`check_results[]`', '`hw.support.qualification.profile`'],
        'docs/410-desktop-viability-checklist.md': ['`qualification.profile_digest`', '`check_results[]`'],
        'docs/479-hardware-compatibility-posture-by-profile.md': ['`qualification.profile_digest`', '`hw.support.qualification.profile`'],
        'docs/529-hardware-support-promotion-and-qualification-boundary.md': ['`qualification.profile_digest`', '`hw.support.qualification.profile`'],
        'docs/530-hardware-support-qualification-receipt-boundary.md': ['`qualification.profile_digest`', '`check_results[]`', '`hw.support.qualification.profile`'],
        'docs/531-hardware-support-qualification-profile-boundary.md': ['`hw.support.qualification.profile`', '`qualification.profile_digest`', '`check_results[]`'],
        'docs/266-open-questions-and-risk-register.md': ['ADR-0121', '`qualification.profile_digest`'],
        'docs/99-llm-runbook.md': ['check_hw_support_qualification_profile_contract.py', '`qualification.profile_digest`'],
        'docs/98-archive-hygiene.md': ['check_hw_support_qualification_profile_contract.py', '`check_results[]`'],
        'docs/32-curated-references.md': ['Android Compatibility Test Suite (CTS) overview', 'Windows Hardware Lab Kit (HLK) overview', 'Red Hat Hardware Certification Test Suite User Guide'],
        'adrs/ADR-0121-hardware-support-qualification-profile-boundary.md': ['`hw.support.qualification.profile`', '`qualification.profile_digest`', '`check_results[]`'],
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
    print('Hardware support qualification profile contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
