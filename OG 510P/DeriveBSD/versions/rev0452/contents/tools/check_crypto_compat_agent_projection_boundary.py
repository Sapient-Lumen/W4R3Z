#!/usr/bin/env python3
"""Guardrail for compatibility-agent projection boundary."""
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

for rel in ['spec/crypto.op.request.schema.json', 'spec/crypto.op.receipt.schema.json']:
    schema = load_json(rel)
    cp = (schema.get('properties') or {}).get('compatibility_projection') or {}
    props = cp.get('properties') or {}
    if props.get('adapter_protocol', {}).get('enum') != ['ssh-agent', 'gpg-agent']:
        errors.append(f'{rel} compatibility_projection.adapter_protocol enum mismatch')
    if props.get('projection_scope', {}).get('enum') != ['local-session-only']:
        errors.append(f'{rel} compatibility_projection.projection_scope enum mismatch')
    if props.get('remembered_approval_scope', {}).get('enum') != ['same-lease-only']:
        errors.append(f'{rel} compatibility_projection.remembered_approval_scope enum mismatch')

req = load_json('spec/examples/crypto.op.request.compat-agent.json')
receipt = load_json('spec/examples/crypto.op.receipt.compat-agent.json')
for name, obj in [('request', req), ('receipt', receipt)]:
    cp = obj.get('compatibility_projection') or {}
    if cp.get('adapter_protocol') != 'ssh-agent':
        errors.append(f'{name} compat example must use ssh-agent adapter_protocol')
    if cp.get('projection_scope') != 'local-session-only':
        errors.append(f'{name} compat example must use local-session-only projection_scope')
    if cp.get('remembered_approval_scope') != 'same-lease-only':
        errors.append(f'{name} compat example must use same-lease-only remembered_approval_scope')

expected_req_digest = digest('spec/examples/crypto.op.request.compat-agent.json')
if receipt.get('request_digest') != expected_req_digest:
    errors.append('compat-agent receipt request_digest must match canonical request example digest')

DOC_TOKENS = {
    'adrs/ADR-0293-crypto-compatibility-agents-stay-local-session-projections-and-not-ambient-remote-authority.md': [
        'Compatibility agents are projections, not authority.',
        'The baseline projection scope is `local-session-only`.',
        'Remembered approvals stay `same-lease-only`.',
        'Remote agent forwarding is not the reviewed baseline.',
    ],
    'docs/703-crypto-compatibility-agents-stay-local-session-projections-and-not-ambient-remote-authority.md': [
        'classic compatibility sockets may exist, but they do **not** become the real authority model.',
        '`projection_scope` is `local-session-only`',
        'remembered approval stays `same-lease-only`',
        'remote forwarding is not baseline truth',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        '## 56) Crypto compatibility agents and remembered approvals boundary [DECIDED]',
        '`local-session-only`',
        '`same-lease-only`',
        'remote agent forwarding remains out of the reviewed baseline',
    ],
    'docs/306-crypto-operations-portal-and-split-keys.md': [
        'Compatibility agents are projections over the brokered path, not the authority object.',
        '`local-session-only`',
        '`same-lease-only`',
    ],
    'docs/437-split-secrets-brokers.md': [
        'The first reviewed compatibility projection is intentionally narrow:',
        '`projection_scope = local-session-only`',
        '`remembered_approval_scope = same-lease-only`',
    ],
    'docs/462-private-key-and-crypto-op-posture-by-profile.md': [
        'compatibility agents stay explicit local-session projections',
        'remembered approvals stay same-lease-only',
    ],
    'docs/164-split-crypto-domains.md': [
        'Compatibility agent forwarding is not baseline authority.',
    ],
    'docs/98-archive-hygiene.md': [
        'Run `python3 tools/check_crypto_compat_agent_projection_boundary.py` when editing crypto broker, key-policy, or compatibility-agent boundary docs:',
    ],
    'docs/99-llm-runbook.md': [
        'If `tools/check_crypto_compat_agent_projection_boundary.py` fails, keep compatibility crypto agents on the bounded projection path:',
    ],
    'docs/110-juicy-os-lessons.md': [
        'Legacy `ssh-agent` / `gpg-agent` compatibility should survive only as a typed projection over the brokered lane:',
    ],
}

for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel} missing token: {token}')

if errors:
    print('\n'.join(errors), file=sys.stderr)
    raise SystemExit(1)
