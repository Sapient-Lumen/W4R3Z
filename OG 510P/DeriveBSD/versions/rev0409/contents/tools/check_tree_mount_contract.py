#!/usr/bin/env python3
"""Guardrail for the verified lazy tree-mount boundary.

Keeps the accepted boundary narrow and reviewable:
- `tree.mount.plan` must make projection/fallback/evidence posture explicit
- `tree.mount.receipt` must record realized posture without normalizing path-level traces
- the risk register, ADR, and core docs must all point at the same accepted boundary
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_MODES = ['materialize', 'prefetch', 'lazy']
EXPECTED_FALLBACKS = ['fail_closed', 'materialize', 'prefetch']
EXPECTED_SCOPES = ['digest-only', 'path-level']


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []

    plan = load_json('spec/tree.mount.plan.schema.json')
    receipt = load_json('spec/tree.mount.receipt.schema.json')
    plan_ex = load_json('spec/examples/tree.mount.plan.json')
    receipt_ex = load_json('spec/examples/tree.mount.receipt.json')

    projection = plan.get('properties', {}).get('projection', {})
    if plan.get('properties', {}).get('kind', {}).get('const') != 'tree.mount.plan':
        errors.append('spec/tree.mount.plan.schema.json kind.const must be tree.mount.plan')
    if 'projection' not in plan.get('required', []):
        errors.append('spec/tree.mount.plan.schema.json must require projection')
    mode_enum = projection.get('properties', {}).get('mode', {}).get('enum')
    if mode_enum != EXPECTED_MODES:
        errors.append(f'tree.mount.plan projection.mode enum expected {EXPECTED_MODES!r}, found {mode_enum!r}')
    fallback_enum = projection.get('properties', {}).get('fallback_policy', {}).get('enum')
    if fallback_enum != EXPECTED_FALLBACKS:
        errors.append(f'tree.mount.plan projection.fallback_policy enum expected {EXPECTED_FALLBACKS!r}, found {fallback_enum!r}')
    scope_enum = projection.get('properties', {}).get('fetch_evidence_scope', {}).get('enum')
    if scope_enum != EXPECTED_SCOPES:
        errors.append(f'tree.mount.plan projection.fetch_evidence_scope enum expected {EXPECTED_SCOPES!r}, found {scope_enum!r}')

    observed = receipt.get('properties', {}).get('observed', {})
    if receipt.get('properties', {}).get('kind', {}).get('const') != 'tree.mount.receipt':
        errors.append('spec/tree.mount.receipt.schema.json kind.const must be tree.mount.receipt')
    observed_required = observed.get('required', [])
    for field in ['realized_mode', 'fallback_applied', 'fetch_evidence_scope', 'constraints_ok']:
        if field not in observed_required:
            errors.append(f'tree.mount.receipt observed must require {field}')
    realized_enum = observed.get('properties', {}).get('realized_mode', {}).get('enum')
    if realized_enum != EXPECTED_MODES:
        errors.append(f'tree.mount.receipt observed.realized_mode enum expected {EXPECTED_MODES!r}, found {realized_enum!r}')
    applied_enum = observed.get('properties', {}).get('fallback_applied', {}).get('enum')
    if applied_enum != ['none', 'materialize', 'prefetch']:
        errors.append(f'tree.mount.receipt observed.fallback_applied enum drifted: {applied_enum!r}')
    observed_scope_enum = observed.get('properties', {}).get('fetch_evidence_scope', {}).get('enum')
    if observed_scope_enum != EXPECTED_SCOPES:
        errors.append(f'tree.mount.receipt observed.fetch_evidence_scope enum expected {EXPECTED_SCOPES!r}, found {observed_scope_enum!r}')

    if plan_ex.get('projection', {}).get('mode') not in EXPECTED_MODES:
        errors.append('spec/examples/tree.mount.plan.json must use a canonical projection.mode')
    if plan_ex.get('projection', {}).get('fallback_policy') not in EXPECTED_FALLBACKS:
        errors.append('spec/examples/tree.mount.plan.json must use a canonical projection.fallback_policy')
    if plan_ex.get('projection', {}).get('fetch_evidence_scope') != 'digest-only':
        errors.append('spec/examples/tree.mount.plan.json canonical example must stay digest-only by default')
    if not plan_ex.get('authority_binding', {}).get('mount_view_digest'):
        errors.append('spec/examples/tree.mount.plan.json must bind back to an upstream reviewed object via authority_binding.mount_view_digest')
    if plan_ex.get('projection', {}).get('constraints', {}).get('requires_verified_tree') is not True:
        errors.append('spec/examples/tree.mount.plan.json must require a verified tree in the canonical example')

    observed_ex = receipt_ex.get('observed', {})
    if observed_ex.get('realized_mode') != plan_ex.get('projection', {}).get('mode'):
        errors.append('spec/examples/tree.mount.receipt.json observed.realized_mode must match the canonical plan projection.mode')
    if observed_ex.get('fetch_evidence_scope') != plan_ex.get('projection', {}).get('fetch_evidence_scope'):
        errors.append('spec/examples/tree.mount.receipt.json observed.fetch_evidence_scope must match the canonical plan')
    if observed_ex.get('fetch_evidence_scope') == 'digest-only' and observed_ex.get('path_trace_digest'):
        errors.append('digest-only canonical receipt must not carry path_trace_digest')
    if observed_ex.get('constraints_ok') is not True:
        errors.append('spec/examples/tree.mount.receipt.json canonical example must show satisfied constraints')

    doc_checks = {
        'docs/299-verified-lazy-rootfs-and-on-demand-mounts.md': ['docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md', '`materialize`', '`digest-only`'],
        'docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md': ['`tree.mount.plan`', '`tree.mount.receipt`', '`path-level`', '`mount.view`'],
        'docs/266-open-questions-and-risk-register.md': ['## 29) Lazy mounts and partial fetch: integrity, side-channels, and fallback drift [DECIDED]', 'ADR-0117'],
        'docs/110-juicy-os-lessons.md': ['docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md', '`prefetch`'],
        'adrs/ADR-0117-verified-lazy-tree-mount-materialization-and-evidence-boundary.md': ['`tree.mount.plan`', '`tree.mount.receipt`', '`digest-only`'],
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
    print('Tree mount contract: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
