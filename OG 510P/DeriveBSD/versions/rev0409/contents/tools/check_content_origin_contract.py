#!/usr/bin/env python3
"""Guardrail for the content-origin / anti-laundering contract.

This checker keeps the archive's provenance contract wired:
- content.import.receipt requires metadata survival fields
- content.origin example exists and becomes the authoritative digest
- content.import.plan / receipt examples bind back to that digest
- key docs mention the authority boundary and laundering status explicitly
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def digest(obj: dict) -> str:
    return f"sha256:{hashlib.sha256(jcs_bytes(obj)).hexdigest()}"


def main() -> int:
    errors: list[str] = []

    schema = load_json('spec/content.import.receipt.schema.json')
    if 'metadata' not in schema.get('required', []):
        errors.append('spec/content.import.receipt.schema.json missing required metadata block')
    metadata_props = (((schema.get('properties') or {}).get('metadata') or {}).get('properties') or {})
    for key in ('authority', 'transport', 'status', 'authoritative_origin_digest'):
        if key not in metadata_props:
            errors.append(f'spec/content.import.receipt.schema.json missing metadata.{key}')

    origin = load_json('spec/examples/content.origin.json')
    plan = load_json('spec/examples/content.import.plan.json')
    receipt = load_json('spec/examples/content.import.receipt.json')
    origin_d = digest(origin)

    plan_origin = plan.get('origin') or {}
    if plan_origin.get('kind') == 'content.origin' and digest(plan_origin) != origin_d:
        errors.append('spec/examples/content.import.plan.json inline origin must match spec/examples/content.origin.json')

    receipt_origin = receipt.get('origin') or {}
    if receipt_origin.get('origin_digest') != origin_d:
        errors.append('spec/examples/content.import.receipt.json origin.origin_digest != computed digest of spec/examples/content.origin.json')

    quarantine = receipt.get('quarantine') or {}
    if quarantine.get('origin_digest') != origin_d:
        errors.append('spec/examples/content.import.receipt.json quarantine.origin_digest != computed digest of spec/examples/content.origin.json')

    metadata = receipt.get('metadata') or {}
    if metadata.get('authoritative_origin_digest') != origin_d:
        errors.append('spec/examples/content.import.receipt.json metadata.authoritative_origin_digest != computed digest of spec/examples/content.origin.json')
    if metadata.get('status') not in {'preserved', 'rehydrated', 'laundering-suspected', 'cleared-by-policy', 'not-applicable'}:
        errors.append('spec/examples/content.import.receipt.json metadata.status is invalid')

    doc_checks = {
        'docs/280-origin-labels-and-quarantine-attributes.md': [
            '`content.origin`',
            '`content.import.receipt`',
            'laundering-suspected',
            'portal / bundle',
        ],
        'docs/293-attribute-indexed-metadata-and-live-queries.md': [
            '`content.origin`',
            'authoritative',
            'pointer/cache',
            'derived surfaces',
        ],
        'docs/484-origin-label-authority-and-anti-laundering-boundary.md': [
            '`content.origin`',
            '`content.import.receipt`',
            '`authoritative_origin_digest`',
            'laundering-suspected',
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

    print('Content-origin contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
