#!/usr/bin/env python3
"""Guardrail for the supplychain-verification / release-authority boundary.

This checker keeps DeriveBSD's workflow-verification lane wired:
- `supplychain-layout-policy` constrains workflow verification but is not release authority
- `supplychain-verify-receipt` stays workflow-verification evidence only
- `release.authority.policy` may require workflow verification without outsourcing authority
- `release.publish.receipt` can summarize the workflow-verification decision
- key docs explicitly state the boundary
"""
from __future__ import annotations

from pathlib import Path

from cube_digest_lib import canonical_digest, load_json as cube_load_json

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return cube_load_json(ROOT, rel)


def digest(obj: dict) -> str:
    return canonical_digest(obj)


def main() -> int:
    errors: list[str] = []

    layout_schema = load_json('spec/supplychain.layout.policy.schema.json')
    layout_props = layout_schema.get('properties') or {}
    for key in ('layout_digest', 'trust', 'requirements', 'enforcement'):
        if key not in layout_props:
            errors.append(f'spec/supplychain.layout.policy.schema.json missing property {key}')

    receipt_schema = load_json('spec/supplychain.verify.receipt.schema.json')
    if 'authority_semantics' not in receipt_schema.get('required', []):
        errors.append('spec/supplychain.verify.receipt.schema.json missing required authority_semantics')
    receipt_props = receipt_schema.get('properties') or {}
    if receipt_props.get('authority_semantics', {}).get('const') != 'workflow-verification-evidence-only':
        errors.append('spec/supplychain.verify.receipt.schema.json authority_semantics must const to workflow-verification-evidence-only')
    for key in ('authority_semantics', 'layout_policy_digest', 'artifact_digest', 'consumed_attestations', 'result'):
        if key not in receipt_props:
            errors.append(f'spec/supplychain.verify.receipt.schema.json missing property {key}')

    authority_schema = load_json('spec/release.authority.policy.schema.json')
    supplychain_props = (((authority_schema.get('properties') or {}).get('supplychain_verification') or {}).get('properties') or {})
    for key in ('mode', 'allowed_layout_policy_digests', 'require_pass_result'):
        if key not in supplychain_props:
            errors.append(f'spec/release.authority.policy.schema.json missing supplychain_verification.{key}')

    publish_schema = load_json('spec/release.publish.receipt.schema.json')
    publish_sc_props = (((publish_schema.get('properties') or {}).get('supplychain_verification') or {}).get('properties') or {})
    for key in ('decision', 'verify_receipt_digests', 'layout_policy_digests'):
        if key not in publish_sc_props:
            errors.append(f'spec/release.publish.receipt.schema.json missing supplychain_verification.{key}')

    layout = load_json('spec/examples/supplychain.layout.policy.json')
    verify_receipt = load_json('spec/examples/supplychain.verify.receipt.json')
    authority_policy = load_json('spec/examples/release.authority.policy.json')
    publish_receipt = load_json('spec/examples/release.publish.receipt.json')

    layout_d = digest(layout)
    verify_receipt_d = digest(verify_receipt)
    authority_policy_d = digest(authority_policy)

    if verify_receipt.get('authority_semantics') != 'workflow-verification-evidence-only':
        errors.append('spec/examples/supplychain.verify.receipt.json authority_semantics must be workflow-verification-evidence-only')
    if verify_receipt.get('layout_policy_digest') != layout_d:
        errors.append('spec/examples/supplychain.verify.receipt.json layout_policy_digest != computed digest of spec/examples/supplychain.layout.policy.json')
    if verify_receipt.get('result') != 'pass':
        errors.append('spec/examples/supplychain.verify.receipt.json result must be pass')

    supplychain_policy = authority_policy.get('supplychain_verification') or {}
    if supplychain_policy.get('mode') != 'required':
        errors.append('spec/examples/release.authority.policy.json supplychain_verification.mode must be required')
    if layout_d not in (supplychain_policy.get('allowed_layout_policy_digests') or []):
        errors.append('spec/examples/release.authority.policy.json supplychain_verification.allowed_layout_policy_digests must include computed digest of spec/examples/supplychain.layout.policy.json')
    if not supplychain_policy.get('require_pass_result'):
        errors.append('spec/examples/release.authority.policy.json supplychain_verification.require_pass_result must be true')

    if publish_receipt.get('authority_policy_digest') != authority_policy_d:
        errors.append('spec/examples/release.publish.receipt.json authority_policy_digest != computed digest of spec/examples/release.authority.policy.json')
    publish_sc = publish_receipt.get('supplychain_verification') or {}
    if publish_sc.get('decision') != 'accepted':
        errors.append('spec/examples/release.publish.receipt.json supplychain_verification.decision must be accepted')
    if verify_receipt_d not in (publish_sc.get('verify_receipt_digests') or []):
        errors.append('spec/examples/release.publish.receipt.json supplychain_verification.verify_receipt_digests must include computed digest of spec/examples/supplychain.verify.receipt.json')
    if layout_d not in (publish_sc.get('layout_policy_digests') or []):
        errors.append('spec/examples/release.publish.receipt.json supplychain_verification.layout_policy_digests must include computed digest of spec/examples/supplychain.layout.policy.json')

    doc_checks = {
        'docs/202-in-toto-layouts-and-step-policy.md': [
            '`supplychain-layout-policy`',
            '`supplychain-verify-receipt`',
            '`release.publish.receipt`',
            'supplemental',
        ],
        'docs/71-attestations-dsse-in-toto-slsa.md': [
            'policy engines',
            'verification',
            'VSA',
            'attestations do not do anything unless',
        ],
        'docs/260-release-authority-policy-and-key-management.md': [
            '`release.authority.policy`',
            '`release.publish.receipt`',
            '`supplychain_verification`',
            'supplemental',
        ],
        'docs/489-supplychain-verification-evidence-and-publish-gate-boundary.md': [
            '`supplychain-layout-policy`',
            '`supplychain-verify-receipt`',
            '`release.publish.receipt`',
            '`supplychain_verification`',
        ],
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

    print('Supplychain verification authority contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
