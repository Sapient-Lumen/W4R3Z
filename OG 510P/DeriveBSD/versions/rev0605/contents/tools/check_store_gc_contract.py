#!/usr/bin/env python3
"""Guardrail for store retention / GC profile defaults and rollback coverage wiring.

This checker keeps the retention lane narrow and wired:
- product profiles carry a stable `store_retention` default for A–D
- `keep_generations` stays a preference while `rollback_floor_generations` is the hard safety floor
- the canonical GC example records whether rollback coverage was preserved
"""
from __future__ import annotations

import json
from pathlib import Path
from cube_digest_lib import canonical_digest

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_STORE_RETENTION = {
    'fleet_host': 'rollback-floor-policy-gated',
    'workstation': 'trusted-ui-visible-space-pressure-rollback-floor',
    'general_os': 'pins-and-generations-explicit-admin',
    'appliance_factory': 'offline-auditable-rollback-floor',
}


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))



def main() -> int:
    errors: list[str] = []

    profiles = load_json('spec/examples/product.profiles.json')['profiles']
    for pid, expected in EXPECTED_STORE_RETENTION.items():
        got = ((profiles.get(pid) or {}).get('defaults') or {}).get('store_retention')
        if got != expected:
            errors.append(f"{pid}.defaults.store_retention expected {expected!r}, found {got!r}")

    plan_schema = load_json('spec/store.gc.plan.schema.json')
    cprops = (((plan_schema.get('properties') or {}).get('constraints') or {}).get('properties') or {})
    if 'rollback_floor_generations' not in cprops:
        errors.append('spec/store.gc.plan.schema.json missing constraints.rollback_floor_generations')
    eprops = (((plan_schema.get('properties') or {}).get('expect') or {}).get('properties') or {})
    for field in ('bootable_generations_before', 'bootable_generations_after_est'):
        if field not in eprops:
            errors.append(f'spec/store.gc.plan.schema.json missing expect.{field}')

    receipt_schema = load_json('spec/store.gc.receipt.schema.json')
    rcov = (receipt_schema.get('properties') or {}).get('rollback_coverage') or {}
    if (rcov.get('properties') or {}).get('status', {}).get('enum') != ['preserved', 'reduced', 'violated', 'not-applicable']:
        errors.append('spec/store.gc.receipt.schema.json rollback_coverage.status enum drifted')

    plan = load_json('spec/examples/store.gc.plan.json')
    receipt = load_json('spec/examples/store.gc.receipt.json')
    if plan.get('constraints', {}).get('mode') != 'dry-run':
        errors.append('spec/examples/store.gc.plan.json canonical example must stay dry-run')
    floor = plan.get('constraints', {}).get('rollback_floor_generations')
    keep = plan.get('constraints', {}).get('keep_generations')
    if not isinstance(floor, int) or floor < 1:
        errors.append('spec/examples/store.gc.plan.json constraints.rollback_floor_generations must be a positive integer')
    if not isinstance(keep, int) or keep < 1:
        errors.append('spec/examples/store.gc.plan.json constraints.keep_generations must be a positive integer')
    if isinstance(floor, int) and isinstance(keep, int) and floor > keep:
        errors.append('spec/examples/store.gc.plan.json rollback_floor_generations must not exceed keep_generations in the canonical example')

    expect = plan.get('expect') or {}
    before = expect.get('bootable_generations_before')
    after_est = expect.get('bootable_generations_after_est')
    if isinstance(before, int) and isinstance(after_est, int) and after_est > before:
        errors.append('spec/examples/store.gc.plan.json expect.bootable_generations_after_est must not exceed expect.bootable_generations_before')
    if isinstance(floor, int) and isinstance(after_est, int) and after_est < floor:
        errors.append('spec/examples/store.gc.plan.json expect.bootable_generations_after_est must preserve the rollback floor in the canonical example')

    if receipt.get('plan_digest') != canonical_digest(plan):
        errors.append('spec/examples/store.gc.receipt.json plan_digest != computed digest of spec/examples/store.gc.plan.json')
    cov = receipt.get('rollback_coverage') or {}
    if cov.get('status') != 'preserved':
        errors.append('spec/examples/store.gc.receipt.json rollback_coverage.status must be preserved in the canonical example')
    if cov.get('required_floor') != floor:
        errors.append('spec/examples/store.gc.receipt.json rollback_coverage.required_floor must match plan constraints.rollback_floor_generations')
    if isinstance(cov.get('bootable_generations_after'), int) and isinstance(floor, int) and cov['bootable_generations_after'] < floor:
        errors.append('spec/examples/store.gc.receipt.json rollback_coverage.bootable_generations_after must preserve the rollback floor in the canonical example')
    if 'pin/incident-2026-02-25' not in (cov.get('protected_refs') or []):
        errors.append('spec/examples/store.gc.receipt.json rollback_coverage.protected_refs must mention the incident pin in the canonical example')

    doc_checks = {
        'docs/175-pins-roots-and-garbage-collection.md': ['`store.gc.plan`', '`store.gc.receipt`', 'rollback floor'],
        'docs/404-zfs-boot-environments-as-system-generations.md': ['`rollback_floor_generations`', 'bootable'],
        'docs/426-store-gc-plans-and-receipts.md': ['`rollback_floor_generations`', '`rollback_coverage`', 'keep_generations'],
        'docs/411-product-profiles-as-compilation-target.md': ['store retention', '`store_retention`'],
        'docs/496-store-retention-and-gc-posture-by-profile.md': ['`store_retention`', '`rollback_floor_generations`', '`rollback_coverage`'],
        'adrs/ADR-0086-store-retention-and-gc-posture-by-profile.md': ['store_retention', 'rollback_floor_generations', 'rollback_coverage'],
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
    print('Store GC contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
