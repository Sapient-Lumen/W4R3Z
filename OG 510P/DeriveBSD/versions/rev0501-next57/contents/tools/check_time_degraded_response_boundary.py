#!/usr/bin/env python3
"""Guardrail for explicit degraded-time response and proof-bundle joins."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def digest(rel: str) -> str:
    return 'sha256:' + hashlib.sha256(jcs_bytes(load_json(rel))).hexdigest()


errors: list[str] = []

req_schema = load_json('spec/time.requirement.schema.json')
if 'degraded_response' not in req_schema.get('required', []):
    errors.append('spec/time.requirement.schema.json must require degraded_response')
dr = (req_schema.get('properties') or {}).get('degraded_response') or {}
props = dr.get('properties') or {}
if props.get('on_degraded', {}).get('enum') != ['deny', 'repair-only', 'allow-if-proof-fresh', 'allow-breakglass-only']:
    errors.append('spec/time.requirement.schema.json degraded_response.on_degraded enum mismatch')
if props.get('on_unsynced', {}).get('enum') != ['deny', 'repair-only', 'allow-breakglass-only']:
    errors.append('spec/time.requirement.schema.json degraded_response.on_unsynced enum mismatch')

req_example = load_json('spec/examples/time.requirement.json')
dr_ex = req_example.get('degraded_response') or {}
if dr_ex.get('on_degraded') != 'allow-if-proof-fresh':
    errors.append('spec/examples/time.requirement.json degraded_response.on_degraded must be allow-if-proof-fresh')
if dr_ex.get('on_unsynced') != 'deny':
    errors.append('spec/examples/time.requirement.json degraded_response.on_unsynced must be deny')

snap_schema = load_json('spec/time.sync.snapshot.schema.json')
inputs = (((snap_schema.get('properties') or {}).get('inputs') or {}).get('properties') or {})
if 'proof_bundle_digest' not in inputs:
    errors.append('spec/time.sync.snapshot.schema.json inputs.proof_bundle_digest missing')

snap_example = load_json('spec/examples/time.sync.snapshot.json')
expected = digest('spec/examples/time.proof.bundle.json')
if ((snap_example.get('inputs') or {}).get('proof_bundle_digest')) != expected:
    errors.append('spec/examples/time.sync.snapshot.json inputs.proof_bundle_digest must match canonical time.proof.bundle example digest')

DOC_TOKENS = {
    'adrs/ADR-0292-time-requirement-degraded-time-response-stays-explicit-and-proof-bundle-bound.md': [
        'Degraded-time behavior is part of `time-requirement`, not backend/UI folklore.',
        '`allow-if-proof-fresh` binds to a real `time-proof-bundle`, not to daemon confidence text.',
        'Unsynced time never proceeds silently.',
    ],
    'docs/702-time-requirement-degraded-response-stays-explicit-and-proof-bundle-bound.md': [
        'Every reviewed `time-requirement` now carries `degraded_response`.',
        '`allow-if-proof-fresh` means exact proof, not “the daemon looked okay”',
        'Unsynced time never silently proceeds',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        '## 37) Trustworthy time: quorum failures, expiry safety, and operational response [DECIDED]',
        '`allow-if-proof-fresh` is the only ordinary degraded-time continuation lane',
        'unsynced time cannot silently continue',
    ],
    'docs/468-trustworthy-time-posture-by-profile.md': [
        'Degraded-time response now stays typed',
        '`allow-if-proof-fresh` is the only ordinary degraded-time continuation lane',
        'unsynced time cannot silently continue',
    ],
    'docs/200-secure-time-bootstrapping.md': [
        '`time.sync.snapshot` can now reference a `time-proof-bundle` by digest through `inputs.proof_bundle_digest`.',
    ],
    'docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md': [
        'explicit degraded-time response (`deny`, `repair-only`, `allow-if-proof-fresh`, `allow-breakglass-only`)',
        '`inputs.proof_bundle_digest`',
    ],
    'docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md': [
        'allow-if-proof-fresh',
        'time-sync-snapshot.inputs.proof_bundle_digest',
    ],
    'docs/308-time-monitors-and-lie-detection.md': [
        'allow a reviewed workflow to continue only under `allow-if-proof-fresh` with an exact `time-proof-bundle` join',
    ],
    'docs/98-archive-hygiene.md': [
        'check_time_degraded_response_boundary.py',
        'unsynced time cannot silently continue',
    ],
    'docs/99-llm-runbook.md': [
        'check_time_degraded_response_boundary.py',
        'degraded_response',
        'unsynced time cannot silently continue',
    ],
    'docs/00-index.md': [
        'docs/702-time-requirement-degraded-response-stays-explicit-and-proof-bundle-bound.md',
        'check_time_degraded_response_boundary.py',
    ],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('time degraded-response boundary check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('time degraded-response boundary check passed')
